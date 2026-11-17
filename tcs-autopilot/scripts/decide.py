#!/usr/bin/env python3
"""tcs-autopilot decision engine: request (+flags, +sources summary) -> decisions.json, decisions.md, curriculum.draft.yaml.

Usage:
  decide.py "<request>" [--sources PATH ...] [--lang ar|en|both] [--targets video,deck,lesson,scorm,jobaid]
            [--aspect 16:9|9:16|1:1] [--review none|skeleton|final] [--budget 5$|200k] [--domain PACK]
            [--renderer openmontage|remotion|none] [--sources-summary sources.yaml] [--rules decision-rules.yaml]
            --out runs/<run-id> [--print]

Deterministic: same inputs -> byte-identical outputs (no clock, no randomness; `created` is not written here).
Explicit flags > request wording > sources > rules > defaults. Every decision records signal, confidence, source and
the alternative it rejected.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = SKILL_DIR.parents[1]
ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
LATIN_RE = re.compile(r"[A-Za-z]")
TARGET_ALIASES = {"video": "video", "mp4": "video", "vertical": "video-vertical", "video-vertical": "video-vertical", "9:16": "video-vertical",
                  "deck": "deck", "pptx": "deck", "slides": "deck", "lesson": "lesson", "html": "lesson", "scorm": "scorm",
                  "jobaid": "jobaid", "job-aid": "jobaid", "pdf": "jobaid"}


# ------------------------------------------------------------------ helpers
def is_arabic_text(s: str) -> bool:
    return bool(ARABIC_RE.search(s))


def find(pattern: str, text: str) -> str | None:
    """Return the matched text. Arabic patterns: substring. English: case-insensitive regex with word boundaries."""
    if is_arabic_text(pattern):
        return pattern if pattern in text else None
    m = re.search(r"(?<![A-Za-z0-9])(?:" + pattern + r")(?![A-Za-z0-9])", text, re.IGNORECASE)
    return m.group(0) if m else None


def match(pattern: str, text: str) -> bool:
    return find(pattern, text) is not None


def first_hit(patterns: list[str], text: str) -> str | None:
    for p in patterns:
        h = find(p, text)
        if h:
            return h
    return None


def count_hits(patterns: list[str], text: str) -> list[str]:
    return [h for p in patterns for h in [find(p, text)] if h]


def slugify(s: str, fallback: str = "course") -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:48].strip("-") or fallback


class Decisions:
    def __init__(self):
        self.items: list[dict] = []

    def add(self, key, value, signal, confidence, source, alternative=None, name=None, critical=False):
        d = {"key": key, "value": value, "signal": signal, "confidence": round(float(confidence), 2), "source": source}
        if name:
            d["name"] = name
        if alternative:
            d["alternative_rejected"] = alternative
        if critical:
            d["critical"] = True
        self.items.append(d)
        return d

    def get(self, key, name=None):
        for d in reversed(self.items):
            if d["key"] == key and (name is None or d.get("name") == name):
                return d
        return None


# ------------------------------------------------------------------ language
def decide_language(req: str, flags, rules, sources_summary, D: Decisions) -> dict:
    L = rules["language"]
    letters = [c for c in req if c.isalpha()]
    ar_share = sum(1 for c in letters if ARABIC_RE.match(c)) / max(1, len(letters))
    req_is_ar = ar_share >= L["arabic_ratio"]
    egyptian = first_hit(L["egyptian_cues"], req)
    mena = first_hit(L["mena_cues"], req)
    ar_variant = "ar-EG" if egyptian else L["arabic_default"]
    en_variant = "en-GB" if first_hit(L["en_gb_cues"], req) else L["english_default"]

    if flags.lang:
        if flags.lang == "ar":
            prim, subs, sig, src, conf = ar_variant, [en_variant], "--lang ar", "flag", 1.0
        elif flags.lang == "en":
            prim, subs, sig, src, conf = en_variant, [], "--lang en", "flag", 1.0
        else:  # both
            prim = ar_variant if req_is_ar else en_variant
            other = en_variant if req_is_ar else ar_variant
            D.add("language", {"primary": prim, "secondary": [other], "subtitles": [other]},
                  f"--lang both; request script {'Arabic' if req_is_ar else 'Latin'} ({ar_share:.0%} Arabic letters)", 1.0, "flag",
                  "single language")
            return {"primary": prim, "secondary": [other], "subtitles": [other]}
        alt = "Arabic primary" if prim.startswith("en") else "English primary"
    elif first_hit(L["explicit_ar"], req):
        prim, subs, sig, src, conf, alt = ar_variant, [en_variant], "request asks for Arabic", "request", 0.95, "English primary"
    elif first_hit(L["explicit_en"], req):
        prim, subs, sig, src, conf, alt = en_variant, [], "request asks for English", "request", 0.95, "Arabic primary"
    elif req_is_ar:
        prim, subs, conf = ar_variant, [en_variant], 0.9
        sig = f"request written in Arabic script ({ar_share:.0%} of letters)" + (f"; Egyptian cue '{egyptian}'" if egyptian else "")
        src, alt = "request", "English primary"
    elif mena:
        prim, subs, conf = ar_variant, [en_variant], 0.65
        sig, src, alt = f"MENA context cue '{mena}' in an English request", "rule", "English primary"
    else:
        prim, subs, conf = en_variant, [], 0.85
        sig, src, alt = "request written in English, no MENA cue", "request", "Arabic primary + English subtitles"
    out = {"primary": prim, "subtitles": subs}
    D.add("language", out, sig, conf, src, alt)
    return out


# ------------------------------------------------------------------ audience & level
def jargon_density(text: str, terms: list[str]) -> float:
    words = re.findall(r"[A-Za-z\u0600-\u06FF][\w/-]*", text)
    hits = sum(1 for t in terms if match(t, text))
    return hits / max(1, len(words))


def decide_audience(req, rules, topic_text, D: Decisions) -> dict:
    A = rules["audience"]
    cue, phrase = None, None
    for c in A["cues"]:
        hit = first_hit(c["patterns"], req)
        if hit:
            cue, phrase = c, hit
            break
    if cue is None:
        cue = dict(A["default"], patterns=[])
    density = jargon_density(topic_text, A["technical_terms"])
    lvl_raw = cue["level"]
    explicit = None
    for lvl, pats in A["explicit_level"].items():
        h = first_hit(pats, req)
        if h:
            explicit = (lvl, h)
            break
    res = A["level_resolution"]
    if explicit:
        level, lsig, lconf, lsrc = explicit[0], f"wording '{explicit[1]}'", 0.95, "request"
    elif lvl_raw == "technical":
        tech_topic = density >= A["technical_topic_density"]
        level = res["technical_with_technical_topic"] if tech_topic else res["technical_otherwise"]
        lsig = f"technical audience + jargon density {density:.2f} ({'technical' if tech_topic else 'non-technical'} topic)"
        lconf, lsrc = 0.7, "rule"
    elif lvl_raw == "mixed":
        level, lsig, lconf, lsrc = res["mixed"], f"mixed audience ('{phrase or 'no cue'}'), jargon density {density:.2f}", cue["confidence"], "rule"
    else:
        level, lsig, lconf, lsrc = lvl_raw, f"audience cue '{phrase}'", cue["confidence"], "request"
    aud = {"id": cue["id"], "segment": cue["segment"], "roles": cue["roles"], "level": level, "phrase": phrase}
    D.add("audience", {"id": cue["id"], "roles": cue["roles"], "segment": cue["segment"]},
          f"wording '{phrase}'" if phrase else "no audience wording in request -> general staff",
          cue["confidence"], "request" if phrase else "default",
          "general staff" if phrase else "specific role (none named)", critical=True)
    D.add("level", level, lsig, lconf, lsrc, "intermediate" if level != "intermediate" else "beginner")
    return aud


# ------------------------------------------------------------------ topic, type
LEAD_EN = [r"^(please\s+)?(can you\s+)?(create|make|build|produce|design|write|prepare)\s+(me\s+)?(a|an|some)?\s*(short\s+|quick\s+|brief\s+)?"
           r"(micro-?learning\s+)?(course|lesson|training|module|video|deck|series|program(me)?)?\s*(on|about|for|covering)?\s*",
           r"^(teach|train|explain|show|educate|introduce|help|onboard|walk)\s+(through\s+)?"]
LEAD_AR = ["توعية", "تدريب", "شرح", "تعليم", "كيفية", "دورة", "درس", "عن", "حول", "فيديو", "برنامج"]


def extract_topic(req: str, aud_phrase: str | None) -> tuple[str, bool]:
    t = req.strip().strip(".!?؟")
    if is_arabic_text(t) and not LATIN_RE.search(t):
        words = t.split()
        drop = set(LEAD_AR)
        out = [w for w in words if w not in drop and not (aud_phrase and w == aud_phrase)]
        if out and out[0].startswith("بال"):
            out[0] = out[0][1:]
        return " ".join(out) or t, False
    for p in LEAD_EN:
        t = re.sub(p, "", t, flags=re.IGNORECASE)
    if aud_phrase:
        t = re.sub(r"(\s+(to|for|with)\s+(our|my|the|all)?\s*)?\b(" + re.escape(aud_phrase) + r")\b", "", t, count=1, flags=re.IGNORECASE)
    t = re.sub(r"\s+(to|for)\s*$", "", t.strip(), flags=re.IGNORECASE)
    how = bool(re.match(r"^\s*how\s+to\s+", t, re.IGNORECASE))
    t = re.sub(r"^\s*how\s+to\s+", "", t, flags=re.IGNORECASE)
    t = re.sub(r"^(our|my|the|a|an)\s+", "", t.strip(), flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip(" ,;:-")
    return t or req, how


def decide_type(req, rules, sources_summary) -> tuple[str, str, float, dict]:
    OT = rules["objective_types"]
    votes = {k: 0.0 for k in OT["precedence"]}
    hits = {}
    for k, pats in OT["patterns"].items():
        h = count_hits(pats, req)
        votes[k] += len(h)
        if h:
            hits[k] = h
    if sources_summary:
        kinds: dict[str, int] = {}
        for f in sources_summary.get("facts", []) or []:
            kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
        tot = sum(kinds.values())
        for kind, n in kinds.items():
            t = OT["fact_kind_votes"].get(kind)
            if t and tot:
                votes[t] += 3 * n / tot
                hits.setdefault(t, []).append(f"sources:{kind}x{n}")
    best = max(votes.values())
    if best == 0:
        return "concept", "no type wording -> concept", 0.4, votes
    winners = [k for k in OT["precedence"] if votes[k] == best]
    t = winners[0]
    total = sum(votes.values())
    conf = min(0.95, 0.5 + 0.45 * best / total) if total else 0.5
    sig = f"{t}: " + ", ".join(f"'{h}'" for h in hits.get(t, [])[:4])
    if len(winners) > 1:
        sig += f" (tie with {', '.join(winners[1:])}; precedence)"
        conf = min(conf, 0.55)
    return t, sig, conf, votes


# ------------------------------------------------------------------ objectives
OBJ_TEMPLATES = {
    "en": {
        "procedure": [("remember", "Identify what you need before you {topic}", "Before you start"),
                      ("apply", "Complete the steps to {topic} correctly", "Step by step"),
                      ("analyze", "Check your work and fix common errors when you {topic}", "Check and fix"),
                      ("evaluate", "Decide how to handle exceptions when you {topic}", "Exceptions"),
                      ("understand", "Explain the rules behind how you {topic}", "Why it works this way")],
        "policy": [("understand", "Explain what the {topic} requires and why", "What changes and why"),
                   ("apply", "Apply the {topic} to everyday decisions", "Applying it day to day"),
                   ("evaluate", "Decide how to handle exceptions and edge cases under the {topic}", "Exceptions and edge cases"),
                   ("remember", "Identify who to contact and how to report issues under the {topic}", "Getting help"),
                   ("analyze", "Check a team practice against the {topic}", "Spot the gaps")],
        "behavior": [("analyze", "Spot the warning signs of {topic} in realistic situations", "Spot the signs"),
                     ("evaluate", "Decide the safest response when you meet {topic}", "Make the call"),
                     ("apply", "Report suspected {topic} through the right channel", "Report it"),
                     ("understand", "Explain why {topic} works on people", "Why it works"),
                     ("evaluate", "Judge a colleague's response to {topic} and suggest a better one", "Coach a colleague")],
        "concept": [("understand", "Explain what {topic} is and why it matters", "What it is"),
                    ("understand", "Describe the key parts of {topic}", "Key parts"),
                    ("apply", "Apply {topic} to an example from your work", "In your work"),
                    ("analyze", "Distinguish {topic} from related ideas", "What it is not"),
                    ("evaluate", "Judge when {topic} is the right approach", "When to use it")],
        "structure": [("understand", "Describe how the parts of {topic} fit together", "The big picture"),
                      ("understand", "Classify examples into the parts of {topic}", "Sorting it out"),
                      ("analyze", "Analyze how a change in one part of {topic} affects the others", "Connections"),
                      ("remember", "Name the main parts of {topic}", "The parts"),
                      ("evaluate", "Assess where your work sits within {topic}", "Where you fit")],
        "recall": [("remember", "Recall the key terms of {topic}", "Key terms"),
                   ("remember", "Match each {topic} item to its meaning", "Match it"),
                   ("apply", "Use {topic} terms correctly in context", "Use it"),
                   ("remember", "List the most important {topic} facts", "Must-know facts"),
                   ("understand", "Explain the {topic} terms that are easy to confuse", "Easy to confuse")],
        "adoption": [("understand", "Explain why {topic} matters to your role", "Why it matters"),
                     ("apply", "Apply {topic} in one weekly task", "First habit"),
                     ("evaluate", "Assess your progress with {topic} and pick the next step", "Next step"),
                     ("apply", "Use {topic} with your team", "With your team"),
                     ("analyze", "Spot what blocks {topic} in your work", "Blockers")],
    },
    "ar": {
        "procedure": [("remember", "حدّد ما تحتاجه قبل {topic}", "قبل أن تبدأ"), ("apply", "نفّذ خطوات {topic} بشكل صحيح", "خطوة بخطوة"),
                      ("analyze", "راجع عملك وصحّح الأخطاء الشائعة في {topic}", "راجع وصحّح"), ("evaluate", "قرّر كيف تتعامل مع الاستثناءات في {topic}", "الاستثناءات"),
                      ("understand", "اشرح القواعد وراء {topic}", "لماذا بهذه الطريقة")],
        "policy": [("understand", "اشرح ما تتطلبه {topic} ولماذا", "ما الذي تغيّر ولماذا"), ("apply", "طبّق {topic} في قراراتك اليومية", "التطبيق اليومي"),
                   ("evaluate", "قرّر كيف تتعامل مع الحالات الاستثنائية في {topic}", "الحالات الاستثنائية"),
                   ("remember", "حدّد بمن تتصل وكيف تبلّغ عن المشكلات المتعلقة بـ{topic}", "طلب المساعدة"),
                   ("analyze", "قارن ممارسات الفريق مع {topic}", "اكتشف الفجوات")],
        "behavior": [("analyze", "اكتشف علامات {topic} في مواقف واقعية", "اكتشف العلامات"), ("evaluate", "قرّر التصرف الأكثر أمانًا عند مواجهة {topic}", "اتخذ القرار"),
                     ("apply", "أبلغ عن {topic} المشتبه به عبر القناة الصحيحة", "أبلغ عنه"), ("understand", "اشرح لماذا ينجح {topic} في خداع الناس", "لماذا ينجح"),
                     ("evaluate", "قيّم تصرف زميل تجاه {topic} واقترح تصرفًا أفضل", "ساعد زميلك")],
        "concept": [("understand", "اشرح ما هو {topic} ولماذا يهم", "ما هو"), ("understand", "صف الأجزاء الرئيسية لـ{topic}", "الأجزاء الرئيسية"),
                    ("apply", "طبّق {topic} على مثال من عملك", "في عملك"), ("analyze", "ميّز {topic} عن الأفكار المشابهة", "ما ليس هو"),
                    ("evaluate", "قيّم متى يكون {topic} هو النهج المناسب", "متى تستخدمه")],
        "structure": [("understand", "صف كيف تترابط أجزاء {topic}", "الصورة الكاملة"), ("understand", "صنّف أمثلة حسب أجزاء {topic}", "التصنيف"),
                      ("analyze", "حلّل أثر تغيير جزء من {topic} على باقي الأجزاء", "الترابط"), ("remember", "سمِّ الأجزاء الرئيسية لـ{topic}", "الأجزاء"),
                      ("evaluate", "قيّم موقع عملك داخل {topic}", "أين أنت")],
        "recall": [("remember", "تذكّر المصطلحات الأساسية في {topic}", "المصطلحات"), ("remember", "طابق كل عنصر من {topic} مع معناه", "طابِق"),
                   ("apply", "استخدم مصطلحات {topic} بشكل صحيح", "استخدمها"), ("remember", "عدّد أهم حقائق {topic}", "حقائق أساسية"),
                   ("understand", "اشرح مصطلحات {topic} التي يسهل الخلط بينها", "يسهل الخلط")],
        "adoption": [("understand", "اشرح لماذا يهم {topic} في دورك", "لماذا يهم"), ("apply", "طبّق {topic} في مهمة أسبوعية", "أول عادة"),
                     ("evaluate", "قيّم تقدمك في {topic} واختر الخطوة التالية", "الخطوة التالية"), ("apply", "استخدم {topic} مع فريقك", "مع فريقك"),
                     ("analyze", "اكتشف ما يعيق {topic} في عملك", "العوائق")],
    },
}


def parse_count(req: str, words: str) -> int | None:
    m = re.search(r"\b(\d{1,2})[\s-]*(" + words + r")\b", req, re.IGNORECASE)
    return int(m.group(1)) if m else None


def decide_objectives(req, otype, topic, lang_primary, rules, sources_summary, D: Decisions) -> list[dict]:
    Ln = rules["length"]
    explicit_lessons = parse_count(req, r"lessons?|modules?|parts?|episodes?")
    seeds = []
    if sources_summary:
        for s in sources_summary.get("sources", []) or []:
            for ch in s.get("chunks", []) or []:
                seeds.append((s["id"], ch.get("id"), ch["summary"]))
    if explicit_lessons:
        n, sig, src, conf = explicit_lessons, f"wording '{explicit_lessons} lessons'", "request", 0.9
    elif seeds:
        n = max(Ln["min_objectives"], min(Ln["max_objectives"], len(seeds)))
        sig, src, conf = f"{len(seeds)} source sections -> {n} objectives (clamped {Ln['min_objectives']}-{Ln['max_objectives']})", "sources", 0.75
    else:
        n, sig, src, conf = Ln["default_objectives"], "no sources/count wording -> default objective set for type", "default", 0.55
    n = max(1, min(n, 12))
    lang = "ar" if lang_primary.startswith("ar") else "en"
    tmpl = OBJ_TEMPLATES[lang][otype]
    objs = []
    for i in range(n):
        bloom, text, ltitle = tmpl[i % len(tmpl)]
        o = {"id": f"O{i + 1}", "text": text.format(topic=topic), "bloom": bloom, "type": otype, "lesson_title": ltitle}
        if i < len(seeds):
            o["source_ids"] = [f"{seeds[i][0]}#{seeds[i][1]}" if seeds[i][1] else seeds[i][0]]
            o["source_hint"] = seeds[i][2][:120]
        objs.append(o)
    D.add("objectives", [{k: o[k] for k in ("id", "text", "bloom")} for o in objs],
          f"type={otype} (Bloom matched: know->remember/understand, do->apply, decide->analyze/evaluate); {sig}", conf, src,
          "single broad objective", critical=True)
    return objs


# ------------------------------------------------------------------ formats & targets
def decide_formats(req, otype, aud, rules, D: Decisions) -> tuple[list[str], dict]:
    FT = rules["formats_by_type"][otype]
    software = first_hit(rules["software_cues"], req)
    visual = first_hit(rules["visual_cues"], req)
    pinned = [f for f, pats in rules["explicit_formats"].items() if first_hit(pats, req)]
    extras = {"assessment": FT.get("assessment", "knowledge-check"), "evidence": bool(FT.get("evidence")), "broll": False}
    if otype == "procedure" and not software:
        base = list(FT.get("formats_non_software", FT["formats"]))
        why = f"procedure without software cue -> {base}"
    else:
        base = list(FT["formats"])
        why = f"{otype}" + (f" + software cue '{software}'" if otype == "procedure" else "") + f" -> {base}"
    if otype == "concept" and visual:
        extras["broll"] = True
        why += f"; visual subject '{visual}' -> + B-roll scenes"
    conf, src, alt = 0.75, "rule", None
    seg_rule = rules["segment_overrides"].get(aud["segment"])
    if seg_rule:
        secondary = seg_rule.get("secondary_by_type", {}).get(otype)
        if not secondary:
            secondary = next((f for f in base if f in seg_rule.get("keep_secondary", [])), None)
        alt = f"{base} (type default)"
        base = [seg_rule["primary"]] + ([secondary] if secondary else [])
        why += f"; {aud['id']} audience -> {seg_rule['primary']} primary" + (f" + {secondary}" if secondary else "")
        conf = 0.75
    if pinned:
        alt = f"{base} (rule)"
        base = (pinned + [f for f in base if f not in pinned])[:2]
        why = f"request wording pins {pinned}; " + why
        conf, src = 0.95, "request"
    base = base[: rules["blend"]["max_per_lesson"]]
    D.add("formats", base, why, conf, src, alt or _alt_format(otype, rules))
    D.add("other", {"assessment": extras["assessment"], "evidence": extras["evidence"], "broll": extras["broll"]},
          f"assessment for {otype}" + ("; compliance evidence (completion + attestation)" if extras["evidence"] else ""), 0.8, "rule",
          "no assessment", name="assessment")
    if len(base) == 2:
        D.add("blend", base, f"primary {base[0]} + secondary {base[1]} (max {rules['blend']['max_per_lesson']}/lesson, "
                             f"{rules['blend']['max_per_course']}/course)", 0.8, "rule", "single format")
    return base, extras


def _alt_format(otype, rules):
    others = [t for t in rules["formats_by_type"] if t != otype]
    return f"{rules['formats_by_type'][others[0]]['formats']} ({others[0]} rule)"


def decide_targets(formats, n_lessons, extras, flags, rules, D: Decisions) -> tuple[list[str], list[str]]:
    if flags.targets:
        tg = []
        for t in flags.targets.split(","):
            t = TARGET_ALIASES.get(t.strip().lower())
            if t and t not in tg:
                tg.append(t)
        D.add("targets", tg, f"--targets {flags.targets}", 1.0, "flag", "derived from formats")
    else:
        tg, why = [], []
        for f in formats:
            for t in rules["format_targets"].get(f, []):
                if t not in tg:
                    tg.append(t)
            why.append(f"{f}->{'+'.join(rules['format_targets'].get(f, []))}")
        video_fmt = any("video" in rules["format_targets"].get(f, []) and f != "narrated-deck" for f in formats)
        if rules.get("video_nudge_cut") and video_fmt and "video-vertical" not in tg:
            tg.append("video-vertical")
            why.append("video format -> + 9:16 nudge cut")
        if n_lessons >= rules["scorm_min_lessons"] or extras.get("evidence"):
            tg.append("scorm")
            why.append(f"{n_lessons} lessons" + (" + compliance evidence" if extras.get("evidence") else "") + " -> + SCORM")
        D.add("targets", tg, "; ".join(why), 0.8, "rule", "video only")
    if flags.aspect:
        aspects = [flags.aspect] + (["9:16"] if "video-vertical" in tg and flags.aspect != "9:16" else [])
        D.add("aspect", aspects, f"--aspect {flags.aspect}", 1.0, "flag", "16:9 primary")
    else:
        aspects = ["16:9"] + (["9:16"] if "video-vertical" in tg else [])
        D.add("aspect", aspects, "16:9 master" + (" + 9:16 nudge cut" if "9:16" in aspects else ""), 0.8, "rule", "9:16 only")
    return tg, aspects


# ------------------------------------------------------------------ domain pack
def discover_packs(rules) -> dict[str, list[str]]:
    packs = {k: list(v) for k, v in (rules.get("domain_packs") or {}).items()}
    droot = PLUGIN_ROOT / "domains"
    if droot.is_dir():
        for d in sorted(droot.iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")):
                continue
            kws = []
            for name in ("pack.yaml", "domain.yaml", "pack.yml"):
                p = d / name
                if p.exists():
                    try:
                        data = yaml.safe_load(p.read_text()) or {}
                    except yaml.YAMLError:
                        data = {}
                    m = data.get("match") or {}
                    kws = list(m.get("keywords", []) if isinstance(m, dict) else m) + list(data.get("keywords", [])) \
                        + list(data.get("detect_keywords", []))
                    kws = [re.escape(str(k)) if not is_arabic_text(str(k)) else str(k) for k in kws]
                    break
            merged = packs.setdefault(d.name, [])
            merged.extend(k for k in kws if k not in merged)
    return packs


def decide_domain(req, otype, flags, rules, D: Decisions) -> tuple[str, str]:
    packs = discover_packs(rules)
    exists = lambda p: (PLUGIN_ROOT / "domains" / p).is_dir()
    if flags.domain:
        pack = flags.domain
        D.add("domain", pack, f"--domain {pack}", 1.0, "flag", critical=True)
        D.add("domain_pack", pack, "--domain flag" + ("" if exists(pack) else " (pack folder missing -> renderers use _template)"),
              1.0, "flag", rules["fallback_pack"])
        return pack, pack
    best, best_hits = None, []
    for name in sorted(packs):
        h = count_hits(packs[name], req)
        if len(h) > len(best_hits):
            best, best_hits = name, h
    domain = rules["domain_by_type"].get(otype, "general")
    if best:
        conf = min(0.95, 0.7 + 0.1 * len(best_hits))
        D.add("domain", best, f"pack keywords {best_hits[:4]}", conf, "rule", domain, critical=True)
        D.add("domain_pack", best, f"matched {len(best_hits)} keyword(s)" + ("" if exists(best) else "; pack folder not built yet -> _template assets"),
              conf, "rule", rules["fallback_pack"])
        return best, best
    conf = 0.6 if otype != "concept" else 0.45
    D.add("domain", domain, f"no pack keyword; inferred from objective type '{otype}'", conf, "rule", "a specific domain pack", critical=True)
    D.add("domain_pack", rules["fallback_pack"], "no domain pack matched", 0.7, "default", "closest pack")
    return domain, rules["fallback_pack"]


# ------------------------------------------------------------------ guardrails, estimate
def high_stakes(req, rules) -> list[str]:
    return [f"{k}:{h}" for k, pats in rules["high_stakes"].items() for h in [first_hit(pats, req)] if h]


def parse_budget(b: str | None) -> dict | None:
    if not b:
        return None
    s = b.strip().lower().replace(",", "")
    m = re.match(r"^\$?\s*([\d.]+)\s*(\$|usd)?$", s)
    if m and ("$" in s or "usd" in s):
        return {"usd": float(m.group(1)), "raw": b}
    m = re.match(r"^([\d.]+)\s*(k|m)?\s*(tok|tokens)?$", s)
    if m:
        mult = {"k": 1e3, "m": 1e6}.get(m.group(2) or "", 1)
        return {"tokens": int(float(m.group(1)) * mult), "raw": b}
    raise SystemExit(f"cannot parse --budget '{b}' (use e.g. 5$ or 200k)")


def estimate(lessons: list[dict], n_langs: int, rules) -> dict:
    E = rules["estimate"]
    tokens, minutes, images = 0, 0.0, 0
    for les in lessons:
        t = E["tokens_base_per_lesson"] + sum(E["tokens_per_format"].get(f, 5000) for f in les["formats"])
        t *= 1 + E["extra_language_factor"] * max(0, n_langs - 1)
        tokens += int(t)
        minutes += les["duration_min"] * n_langs
        images += sum(E["images_per_lesson"].get(f, 0) for f in les["formats"])
    usd = tokens / 1e6 * E["usd_per_mtok"] + minutes * E["tts_usd_per_min"] + images * E["usd_per_image"]
    return {"tokens": tokens, "usd": round(usd, 2), "tts_minutes": round(minutes, 1), "images": images}


def over(est, budget) -> bool:
    if not budget:
        return False
    return (budget.get("usd") is not None and est["usd"] > budget["usd"]) or \
           (budget.get("tokens") is not None and est["tokens"] > budget["tokens"])


# ------------------------------------------------------------------ main
def build(req: str, flags, rules: dict, sources_summary: dict | None) -> dict:
    D = Decisions()
    warnings, flagged_top = [], []
    has_sources = bool(flags.sources) or bool(sources_summary and sources_summary.get("sources"))
    run_id = Path(flags.out).name

    lang = decide_language(req, flags, rules, sources_summary, D)
    otype, tsig, tconf, votes = decide_type(req, rules, sources_summary)
    # audience phrase is needed to strip it from the topic
    aud = decide_audience(req, rules, req, D)
    topic, how_to = extract_topic(req, aud.get("phrase"))
    if how_to and otype not in ("procedure",) and votes.get("procedure", 0) >= votes.get(otype, 0):
        otype = "procedure"
    D.add("other", otype, tsig, tconf, "request" if not sources_summary else "sources",
          ", ".join(f"{k}={v:g}" for k, v in votes.items() if v and k != otype) or "concept (default)", name="objective_type")
    domain, pack = decide_domain(req, otype, flags, rules, D)
    objs = decide_objectives(req, otype, topic, lang["primary"], rules, sources_summary, D)
    formats, extras = decide_formats(req, otype, aud, rules, D)

    # length & pace
    Ln = rules["length"]
    per = Ln["minutes_by_type"][otype]
    total_req = parse_count(req, r"min(ute)?s?")
    m_secs = re.search(r"\b(\d{2,3})[\s-]*(sec(ond)?s?)\b", req, re.IGNORECASE) if not total_req else None
    secs_req = int(m_secs.group(1)) if m_secs else None
    lo, hi = Ln["minutes_band"]
    single = False
    if secs_req:  # "90-second micro-drama" -> one micro-lesson holding all objectives
        per = round(secs_req / 60, 1)
        single = True
        D.add("length", {"lessons": 1, "minutes_per_lesson": per, "total_minutes": per},
              f"wording '{secs_req} seconds' -> one micro-lesson", 0.9, "request", "microlearning default")
    elif total_req:
        per = max(lo, min(hi, round(total_req / max(1, len(objs)), 1)))
        if total_req < lo * len(objs):  # too short for this many lessons -> fewer objectives
            keep = max(1, total_req // lo)
            objs = objs[:keep]
            warnings.append(f"requested {total_req} min -> trimmed to {keep} objective(s)/lesson(s)")
        D.add("length", {"lessons": len(objs), "minutes_per_lesson": per, "total_minutes": round(per * len(objs), 1)},
              f"wording '{total_req} minutes'", 0.9, "request", "microlearning default")
    else:
        D.add("length", {"lessons": len(objs), "minutes_per_lesson": per, "total_minutes": per * len(objs)},
              f"microlearning: 1 objective/lesson, {per} min for {otype} (band {lo}-{hi}), <= {Ln['max_lessons_per_module']} lessons/module",
              0.75, "rule", "one long lesson")
    level = aud["level"]
    wpm_base = rules["wpm"].get(level, 140)
    ar = lang["primary"].startswith("ar")
    wpm = int(round(wpm_base * (rules["wpm"]["arabic_factor"] if ar else 1)))
    D.add("wpm", wpm, f"{level} {wpm_base} wpm" + (" x0.9 Arabic" if ar else ""), 0.8, "rule", f"{wpm_base + 15} wpm")
    verb = rules["verbosity"]["executive"] if aud["segment"] == "executive" else rules["verbosity"].get(level, "standard")
    D.add("verbosity", verb, f"{aud['id']} / {level}", 0.7, "rule", "detailed")

    # plan skeleton
    lessons = []
    if single:
        lessons.append({"module": "M1", "id": "M1L1", "title": objs[0]["lesson_title"],
                        "objective_ids": [o["id"] for o in objs], "formats": list(formats), "duration_min": per,
                        **({"source_ids": objs[0]["source_ids"]} if objs[0].get("source_ids") else {})})
    for i, o in enumerate([] if single else objs):
        m = i // Ln["max_lessons_per_module"] + 1
        lessons.append({"module": f"M{m}", "id": f"M{m}L{i % Ln['max_lessons_per_module'] + 1}", "title": o["lesson_title"],
                        "objective_ids": [o["id"]], "formats": list(formats), "duration_min": per,
                        **({"source_ids": o["source_ids"]} if o.get("source_ids") else {})})
    targets, aspects = decide_targets(formats, len(lessons), extras, flags, rules, D)

    renderer = flags.renderer or ("openmontage" if os.environ.get("OPENMONTAGE_ROOT") else "remotion")
    if not any(t in targets for t in ("video", "video-vertical", "deck")):
        renderer = "none"
    D.add("renderer", renderer, "--renderer" if flags.renderer else
          ("OPENMONTAGE_ROOT set" if renderer == "openmontage" else "standalone kit (tcs-render-remotion); no OPENMONTAGE_ROOT"),
          1.0 if flags.renderer else 0.6, "flag" if flags.renderer else "rule", "openmontage" if renderer != "openmontage" else "remotion")

    # guardrails
    scope, pause_after = "full", {"none": None, "skeleton": "plan", "final": "qa"}[flags.review]
    stakes = high_stakes(req, rules)
    if not has_sources:
        warnings.append("No sources supplied: content will be general knowledge; every claim is labelled general_knowledge "
                        "and listed in REPORT.md.")
        D.add("other", "general_knowledge", "no --sources and no sources.yaml", 0.9, "default", "grounded content", name="grounding")
        if stakes:
            scope, pause_after = "plan-only", "plan"
            D.add("scope", "plan-only", f"high-stakes topic {stakes} with no sources -> plan only; request sources", 0.95, "rule",
                  "full production from general knowledge")
            flagged_top.append(f"High-stakes topic ({', '.join(stakes)}) and no sources: produced the plan only. "
                               "Re-run with --sources <official material>.")
    if sources_summary and sources_summary.get("conflicts"):
        facts = {f["id"]: f for f in sources_summary.get("facts", [])}
        srcs = {s["id"]: s for s in sources_summary.get("sources", [])}
        for c in sources_summary["conflicts"]:
            def rank(fid):
                f = facts.get(fid, {})
                s = srcs.get(f.get("source_id"), {})
                return (f.get("date") or s.get("date") or "", s.get("authority", 0))
            chosen = max(c["fact_ids"], key=rank) if c.get("fact_ids") else None
            D.add("conflict-resolution", {"fact_ids": c["fact_ids"], "chosen": chosen},
                  f"{c['note']} -> most recent, then most authoritative", 0.7, "sources",
                  ", ".join(f for f in c["fact_ids"] if f != chosen))
    budget = parse_budget(flags.budget)
    n_langs = 1 + len(lang.get("secondary", []))
    est = estimate(lessons, n_langs, rules)
    est_initial = dict(est)
    steps = []
    while over(est, budget):
        if any(len(les["formats"]) > 1 for les in lessons):
            for les in lessons:
                les["formats"] = les["formats"][:1]
            steps.append("dropped secondary format")
        elif "video-vertical" in targets:
            targets.remove("video-vertical")
            steps.append("dropped 9:16 nudge cut")
        elif n_langs > 1:
            n_langs = 1
            steps.append("dropped secondary language (subtitles only)")
        elif len(lessons) > 1:
            dropped = lessons.pop()
            objs = [o for o in objs if o["id"] not in dropped["objective_ids"]]
            steps.append(f"dropped lesson {dropped['id']}")
        else:
            steps.append("cannot reduce further — over budget, flagged")
            flagged_top.append(f"Estimated cost {est['usd']}$ / {est['tokens']} tokens exceeds budget {budget['raw']} even at minimum scope.")
            break
        est = estimate(lessons, n_langs, rules)
    if steps and "scorm" in targets and len(lessons) < rules["scorm_min_lessons"] and not extras.get("evidence") and not flags.targets:
        targets.remove("scorm")
        steps.append("dropped SCORM (single lesson)")
    if steps:
        D.add("budget-tradeoff", steps, f"estimate {est_initial['usd']}$ / {est_initial['tokens']} tok > budget {budget['raw']}", 0.9,
              "flag", "exceed budget")

    # low-confidence critical decisions
    for d in D.items:
        if d.get("critical") and d["confidence"] < rules["critical_confidence"]:
            d["flagged"] = True
            if flags.review == "none":
                flagged_top.append(f"Low confidence ({d['confidence']}) on critical decision '{d['key']}' = {json.dumps(d['value'], ensure_ascii=False)[:80]}"
                                   f" ({d['signal']}). Proceeded without review.")

    course_id = slugify(topic if not is_arabic_text(topic) else run_id, fallback=slugify(run_id, "course"))
    title = topic[:1].upper() + topic[1:] if not is_arabic_text(topic) else req.strip()
    if otype == "procedure" and not is_arabic_text(topic):
        title = f"How to {topic}"
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "request": req,
        "decisions": D.items,
        "flags": {k: v for k, v in vars(flags).items() if v not in (None, [], False) and k not in ("out", "rules", "print")},
        "summary": {
            "course_id": course_id, "title": title, "topic": topic, "objective_type": otype, "domain": domain, "domain_pack": pack,
            "audience": {k: aud[k] for k in ("id", "segment", "roles", "level")}, "language": lang, "formats": formats,
            "assessment": extras["assessment"], "evidence": extras["evidence"], "targets": targets, "aspects": aspects,
            "wpm": wpm, "verbosity": verb, "renderer": renderer, "has_sources": has_sources,
        },
        "plan": {"objectives": objs, "lessons": lessons},
        "estimate": est,
        "scope": scope,
        "pause_after": pause_after,
        "warnings": warnings,
        "flagged_top": flagged_top,
    }


def to_curriculum(res: dict, review: str) -> dict:
    s, p = res["summary"], res["plan"]
    mods: dict[str, list] = {}
    for les in p["lessons"]:
        mods.setdefault(les["module"], []).append({k: v for k, v in les.items() if k != "module"} | {"status": "planned"})
    langs = {"primary": s["language"]["primary"]}
    for k in ("secondary", "subtitles"):
        if s["language"].get(k):
            langs[k] = s["language"][k]
    level = s["audience"]["level"]
    course = {
        "id": s["course_id"], "title": s["title"], "domain": s["domain"], "domain_pack": s["domain_pack"],
        "audience": {"level": level if level in ("beginner", "intermediate", "advanced", "mixed", "beginner-intermediate") else "mixed",
                     "roles": s["audience"]["roles"], "segments": [s["audience"]["segment"]]},
        "languages": langs, "total_minutes": round(sum(l["duration_min"] for l in p["lessons"]), 1),
        "verbosity": s["verbosity"], "wpm": max(90, min(200, s["wpm"])), "targets": s["targets"], "aspects": s["aspects"],
        "renderer": s["renderer"],
    }
    if s["evidence"]:
        course["compliance"] = ["completion + attestation evidence"]
    if s["language"]["primary"].startswith("ar"):
        course["title_ar"] = s["title"]
    objectives = [{k: o[k] for k in ("id", "text", "bloom", "type") if k in o} | ({"source_ids": o["source_ids"]} if o.get("source_ids") else {})
                  for o in p["objectives"]]
    return {
        "schema_version": "1.0", "course": course, "objectives": objectives,
        "modules": [{"id": m, "title": f"Module {m[1:]}", "lessons": ls} for m, ls in mods.items()],
        "approval": {"status": "draft" if review != "none" else "auto-approved", "by": "tcs-autopilot"},
    }


def to_markdown(res: dict) -> str:
    out = [f"# Decisions — {res['run_id']}", "", f"Request: {res['request']}", ""]
    if res["flagged_top"]:
        out += ["> **Needs attention**"] + [f"> - {f}" for f in res["flagged_top"]] + [""]
    out += ["| decision | value | signal | confidence | source | alternative rejected |", "|---|---|---|---|---|---|"]
    for d in res["decisions"]:
        v = d["value"]
        if isinstance(v, list) and v and isinstance(v[0], dict):
            v = "; ".join(f"{o.get('id')}: {o.get('text')} ({o.get('bloom')})" for o in v)
        elif not isinstance(v, str):
            v = json.dumps(v, ensure_ascii=False)
        key = d["key"] + (f" ({d['name']})" if d.get("name") else "") + (" ⚑" if d.get("flagged") else "")
        cell = lambda x: str(x).replace("|", "\\|").replace("\n", " ")
        out.append(f"| {cell(key)} | {cell(v)} | {cell(d['signal'])} | {d['confidence']:.2f} | {d['source']} | {cell(d.get('alternative_rejected', '-'))} |")
    e = res["estimate"]
    out += ["", f"Estimate: ~{e['tokens']:,} tokens, ~${e['usd']} (TTS {e['tts_minutes']} min, {e['images']} images). "
                f"Scope: {res['scope']}. Pause after: {res['pause_after'] or 'none'}."]
    if res["warnings"]:
        out += ["", "Warnings:"] + [f"- {w}" for w in res["warnings"]]
    return "\n".join(out) + "\n"


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("request")
    ap.add_argument("--sources", nargs="*", default=[])
    ap.add_argument("--lang", choices=["ar", "en", "both"])
    ap.add_argument("--targets")
    ap.add_argument("--aspect", choices=["16:9", "9:16", "1:1"])
    ap.add_argument("--review", choices=["none", "skeleton", "final"], default="none")
    ap.add_argument("--budget")
    ap.add_argument("--domain")
    ap.add_argument("--renderer", choices=["openmontage", "remotion", "none"])
    ap.add_argument("--sources-summary")
    ap.add_argument("--rules", default=str(SKILL_DIR / "decision-rules.yaml"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--print", action="store_true", help="print decisions.md to stdout")
    return ap.parse_args(argv)


def run(argv=None) -> dict:
    flags = parse_args(argv)
    rules = yaml.safe_load(Path(flags.rules).read_text())
    ss = yaml.safe_load(Path(flags.sources_summary).read_text()) if flags.sources_summary else None
    res = build(flags.request, flags, rules, ss)
    out = Path(flags.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "decisions.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    (out / "decisions.md").write_text(to_markdown(res))
    (out / "curriculum.draft.yaml").write_text(yaml.safe_dump(to_curriculum(res, flags.review), sort_keys=False, allow_unicode=True, width=120))
    if flags.print:
        print(to_markdown(res))
    return res


if __name__ == "__main__":
    r = run()
    s = r["summary"]
    print(f"{r['run_id']}: {s['objective_type']} | {s['audience']['level']} | {s['language']['primary']} | formats={s['formats']} "
          f"| targets={s['targets']} | lessons={len(r['plan']['lessons'])} | pack={s['domain_pack']} | pause_after={r['pause_after']}")
