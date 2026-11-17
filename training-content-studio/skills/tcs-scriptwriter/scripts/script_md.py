#!/usr/bin/env python3
"""script.md tooling for tcs-scriptwriter (format in references/script-contract.md).

  script_md.py budget  --minutes 3 --level beginner --lang en-US [--scenes 9]
  script_md.py check   <lesson>.script.md [--json]
  script_md.py to-storyboard <lesson>.script.md --out <lesson>.storyboard.json [--aspect 16:9] [--speakable]

`to-storyboard` writes the *script stage* of storyboard.json: schema-valid, narration + claims per scene,
placeholder template `statement` (or `decision` for branching choices) and notes "script-stage: …".
tcs-storyboard then assigns real templates/props. Exit 1 on errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from speakable import has_digits, speakable  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
ENUMS = json.loads((ROOT / "schemas" / "enums.json").read_text())
LEVEL_WPM = {"beginner": 130, "beginner-intermediate": 135, "mixed": 135, "intermediate": 140, "advanced": 155}
AR_FACTOR = 0.9
LEAD, HOLD, PAUSE = 0.35, 0.75, 0.28
RESERVED = {"visual", "claim", "note", "template", "choice", "lead", "hold", "min", "sfx", "transition"}
STORY_FORMATS = {"cartoon", "comic", "branching"}
BASE_PERSONAS = {"host", "learner", "manager", "mentor", "customer", "rookie", "colleague", "exec", "support"}
DEFAULT_INSTR = {
    "en-US": "Warm, confident corporate trainer speaking American English to colleagues. Clear, friendly, natural pace, brief pauses between list items. Never robotic.",
    "en-GB": "Warm, confident corporate trainer speaking British English to colleagues. Clear, friendly, natural pace. Never robotic.",
    "ar-EG": "Warm, friendly corporate trainer speaking natural Egyptian Arabic (Cairene colloquial) to colleagues. Conversational, clear, natural pace; read English product names in English. Never formal MSA, never robotic.",
    "ar-MSA": "Warm, clear corporate trainer speaking Modern Standard Arabic with a neutral accent. Measured pace, friendly, not stiff; read English product names in English.",
}
# fallback only; assets/voices.yaml (slots) and domains/*/personas.yaml (voice) win when present
PERSONA_VOICE = {"host": "marin", "learner": "ash", "manager": "onyx", "mentor": "echo", "customer": "coral",
                 "rookie": "ballad", "colleague": "sage", "exec": "cedar", "support": "nova", "vex": "verse"}


def voice_registry() -> tuple[dict, dict]:
    """(narrator slots per language, persona -> {voice, instructions}) from assets/ and domain packs."""
    narr, pers = {}, {}
    vf = ROOT / "assets" / "voices.yaml"
    if vf.exists():
        slots = (yaml.safe_load(vf.read_text(encoding="utf-8")) or {}).get("slots", {})
        for lang, prov in (slots.get("narrator") or {}).items():
            if isinstance(prov, dict) and prov.get("openai"):
                narr[lang] = prov["openai"]
        for k, v in slots.items():
            if k != "narrator" and isinstance(v, dict) and isinstance(v.get("openai"), dict):
                pers[k] = v["openai"]
    for f in sorted((ROOT / "domains").glob("*/personas.y*ml")) if (ROOT / "domains").exists() else []:
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        for pid, pv in (d.get("personas") or {}).items():
            if isinstance(pv, dict) and isinstance(pv.get("voice"), dict):
                pers.setdefault(pid, pv["voice"])
    return narr, pers


def wpm_for(level: str, lang: str, override: int | None = None) -> int:
    w = override or LEVEL_WPM.get(level, 135)
    return round(w * AR_FACTOR) if lang.startswith("ar") and not override else w


def budget(minutes: float, level: str, lang: str, scenes: int | None = None, wpm: int | None = None) -> dict:
    w = wpm_for(level, lang, wpm)
    total_s = minutes * 60
    n = scenes or max(4, round(total_s / 18))
    speak_s = total_s - n * (LEAD + HOLD) - n * PAUSE
    words = int(speak_s * w / 60)
    return {"wpm": w, "target_s": total_s, "scenes": n, "speaking_s": round(speak_s, 1), "words_total": words,
            "words_per_scene": round(words / n), "scene_s_range": [5, 35]}


def count_words(text: str) -> int:
    return len([t for t in re.sub(r"\^", " ", text).split() if re.search(r"\w", t)])


def parse(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("script.md must start with a YAML front matter block (--- … ---)")
    meta = yaml.safe_load(m.group(1)) or {}
    scenes, cur = [], None
    for ln_no, raw in enumerate(m.group(2).splitlines(), start=m.group(1).count("\n") + 3):
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("<!--"):
            continue
        h = re.match(r"^##\s+([a-z][a-z0-9_]*)\s*(?:\|\s*([^|]*))?(?:\|\s*(.*))?$", line)
        if h:
            cur = {"id": h.group(1), "beat": (h.group(2) or "").strip(),
                   "objective_ids": [o.strip() for o in (h.group(3) or "").split(",") if o.strip()],
                   "narration": [], "claims": [], "choices": [], "line": ln_no}
            scenes.append(cur)
            continue
        if line.startswith("#"):
            continue
        if cur is None:
            continue
        kv = re.match(r"^\s*([a-z][a-z0-9_]*)(\.ar)?\s*:\s*(.*)$", line)
        if not kv:
            if cur["narration"]:  # continuation of previous spoken line
                cur["narration"][-1]["text"] += " " + line.strip()
            continue
        key, is_ar, val = kv.group(1), bool(kv.group(2)), kv.group(3).strip()
        if key == "claim":
            cm = re.match(r"^(.*?)\s*\[([^\]]+)\]\s*$", val)
            if not cm:
                cur["claims"].append({"text": val, "_untagged": True})
                continue
            tags = [t.strip() for t in cm.group(2).split(",")]
            c = {"text": cm.group(1).strip()}
            if any(t.lower() in ("general", "general_knowledge", "gk") for t in tags):
                c["general_knowledge"] = True
            srcs = [t for t in tags if re.match(r"^S\d{2,}(#[A-Za-z0-9._-]+)?$", t)]
            if srcs:
                c["source_ids"] = srcs
            if not srcs and not c.get("general_knowledge"):
                c["_untagged"] = True
            cur["claims"].append(c)
        elif key == "choice":
            ch = re.match(r"^(.*?)\s*->\s*([a-z][a-z0-9_]*)\s*(\((correct|best|good)\))?\s*$", val)
            if ch:
                cur["choices"].append({"label": ch.group(1).strip(), "next": ch.group(2), "correct": bool(ch.group(3))})
        elif key in RESERVED:
            if key in ("lead", "hold", "min"):
                cur[key] = float(val)
            else:
                cur[key] = val
        else:
            opts = {}
            om = re.search(r"\s*\{([^{}]*)\}\s*$", val)
            if om:
                opts = yaml.safe_load("{" + om.group(1) + "}") or {}
                val = val[: om.start()].strip()
            if is_ar and cur["narration"] and cur["narration"][-1]["who"] == key:
                cur["narration"][-1]["text_ar"] = val
                continue
            ln = {"who": key, "text": val}
            for k in ("pause", "pre", "instr"):
                if k in opts:
                    ln[k] = opts[k]
            cur["narration"].append(ln)
    return {"meta": meta, "scenes": scenes}


def scene_seconds(sc: dict, wpm: int) -> float:
    words = sum(count_words(n["text"]) for n in sc["narration"])
    pauses = sum(n.get("pause", PAUSE) + n.get("pre", 0) for n in sc["narration"])
    return round(sc.get("lead", LEAD) + words * 60 / wpm + pauses + sc.get("hold", HOLD), 1)


def check(doc: dict) -> tuple[list[str], list[str], dict]:
    errs, warns = [], []
    meta, scenes = doc["meta"], doc["scenes"]
    for k in ("course_id", "lesson_id", "title", "language"):
        if not meta.get(k):
            errs.append(f"front matter: missing {k}")
    lang = meta.get("language", "en-US")
    formats = meta.get("formats") or [meta.get("format", "explainer")]
    for f in formats:
        if f not in ENUMS["formats"]:
            errs.append(f"unknown format {f!r} (enums.formats)")
    w = wpm_for(meta.get("level", "mixed"), lang, meta.get("wpm"))
    voices = set((meta.get("voices") or {}).keys()) | {"narrator"}
    cast = set(meta.get("cast") or [])
    known_who = voices | cast | BASE_PERSONAS | set(meta.get("extra_personas") or [])
    ids, total = set(), 0.0
    if not scenes:
        errs.append("no scenes (## <scene_id> | <beat> | <objectives>)")
    for sc in scenes:
        sid = sc["id"]
        if sid in ids:
            errs.append(f"{sid}: duplicate scene id")
        ids.add(sid)
        if not sc["narration"]:
            errs.append(f"{sid}: no narration lines")
        if not sc["claims"]:
            errs.append(f"{sid}: no claim lines (every scene needs ≥1 claim; use [general] for intros/outros)")
        for c in sc["claims"]:
            if c.get("_untagged"):
                errs.append(f"{sid}: claim without [S..] or [general] tag: {c['text'][:60]}")
        for n in sc["narration"]:
            if n["who"] not in known_who:
                errs.append(f"{sid}: speaker {n['who']!r} is not narrator, a voices key or a cast persona")
            if has_digits(n["text"]):
                warns.append(f"{sid}: digits in narration (run --speakable or write numbers as words): {n['text'][:60]}")
            for sent in re.split(r"(?<=[.!?؟])\s+", n["text"]):
                if count_words(sent) > 25:
                    warns.append(f"{sid}: sentence > 25 words: {sent[:60]}…")
            if lang.startswith("ar") and not re.search(r"[؀-ۿ]", n["text"]):
                errs.append(f"{sid}: language {lang} but line has no Arabic: {n['text'][:40]}")
        if any(f in STORY_FORMATS for f in formats) and sc["beat"] in ("story", "scene", "mistake", "consequence"):
            if not any(n["who"] != "narrator" for n in sc["narration"]):
                warns.append(f"{sid}: story beat without character dialogue")
        secs = scene_seconds(sc, w)
        sc["_seconds"] = secs
        total += secs
        if secs < 5 or secs > 35:
            warns.append(f"{sid}: estimated {secs}s (keep scenes 5–35 s; split or merge)")
    for sc in scenes:
        for ch in sc["choices"]:
            if ch["next"] not in ids:
                errs.append(f"{sc['id']}: choice -> unknown scene {ch['next']}")
        if sc["choices"] and not any(c["correct"] for c in sc["choices"]):
            warns.append(f"{sc['id']}: decision has no (correct) choice")
    target = meta.get("target_min")
    stats = {"wpm": w, "est_seconds": round(total, 1), "scenes": len(scenes),
             "cues": sum(n["text"].count("^") for s in scenes for n in s["narration"]),
             "words": sum(count_words(n["text"]) for s in scenes for n in s["narration"])}
    if target:
        ratio = total / (target * 60)
        stats["vs_target"] = round(ratio, 2)
        if ratio < 0.85 or ratio > 1.15:
            warns.append(f"estimated {total:.0f}s vs target {target * 60:.0f}s ({ratio:.0%}) — adjust word count")
    return errs, warns, stats


LANG_LINE = {"en-US": "Speak American English.", "en-GB": "Speak British English.",
             "ar-EG": "Speak natural Egyptian Arabic (Cairene colloquial).", "ar-MSA": "Speak clear Modern Standard Arabic."}


def default_voices(lang: str, who: set[str]) -> dict:
    narr, pers = voice_registry()
    n = narr.get(lang, {})
    v = {"narrator": {"provider": "openai", "voice": n.get("voice", "marin"), "model": n.get("model", "gpt-4o-mini-tts"),
                      "instructions": n.get("instructions", DEFAULT_INSTR[lang]), "lang": lang}}
    for p in sorted(who - {"narrator"}):
        reg = pers.get(p, {})
        acting = reg.get("instructions", f"You voice the '{p}' character: natural, expressive, in character.")
        v[p] = {"provider": "openai", "voice": reg.get("voice", PERSONA_VOICE.get(p, "alloy")), "model": "gpt-4o-mini-tts",
                "instructions": f"{LANG_LINE[lang]} {acting}", "lang": lang}
    return v


def to_storyboard(doc: dict, aspect: str = "16:9", make_speakable: bool = False) -> dict:
    meta, scenes = doc["meta"], doc["scenes"]
    lang = meta["language"]
    formats = meta.get("formats") or [meta.get("format", "explainer")]
    w = wpm_for(meta.get("level", "mixed"), lang, meta.get("wpm"))
    who = {n["who"] for s in scenes for n in s["narration"]}
    voices = default_voices(lang, who)
    voices.update(meta.get("voices") or {})
    cast = sorted(set(meta.get("cast") or []) | (who - {"narrator"}))
    sb = {"schema_version": "1.0", "course_id": meta["course_id"], "lesson_id": str(meta["lesson_id"]),
          "title": meta["title"], "language": lang, "direction": "rtl" if lang.startswith("ar") else "ltr",
          "aspect": meta.get("aspect", aspect), "fps": 30, "formats": formats[:2], "wpm": w,
          "objective_ids": meta.get("objective_ids") or sorted({o for s in scenes for o in s["objective_ids"]}),
          "theme": {"preset": meta.get("theme", "neutral"), "logo": None},
          "voices": voices, "cast": cast, "scenes": []}
    if meta.get("subtitle_languages"):
        sb["subtitle_languages"] = meta["subtitle_languages"]
    for sc in scenes:
        narr = []
        for n in sc["narration"]:
            ln = dict(n)
            if make_speakable:
                ln["text"] = speakable(ln["text"], lang)
            narr.append(ln)
        claims = [{k: v for k, v in c.items() if not k.startswith("_")} for c in sc["claims"]]
        hint = sc.get("template", "")
        note = f"script-stage: template TBD (beat={sc['beat'] or '-'}{', hint=' + hint if hint else ''})"
        if sc["choices"]:
            template = "decision"
            props = {"prompt": re.sub(r"\^", "", sc["narration"][-1]["text"]).strip() if sc["narration"] else sc["beat"],
                     "choices": [{"id": f"c{i + 1}", "label": c["label"], "next": c["next"], "correct": c["correct"]}
                                 for i, c in enumerate(sc["choices"])]}
        else:
            template, props = "statement", {"text": (sc["beat"] or sc["id"]).replace("_", " ").capitalize()}
        out = {"id": sc["id"], "template": template, "props": props, "narration": narr, "claims": claims,
               "duration_hint_s": max(1, scene_seconds(sc, w)), "notes": note}
        if sc["objective_ids"]:
            out["objective_ids"] = sc["objective_ids"]
        if sc.get("visual"):
            out["visual"] = sc["visual"]
        for k in ("lead", "hold", "min"):
            if k in sc:
                out["min_s" if k == "min" else k] = sc[k]
        if sc.get("transition") in ("fade", "cut", "slide"):
            out["transition"] = sc["transition"]
        sb["scenes"].append(out)
    return sb


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("budget")
    b.add_argument("--minutes", type=float, required=True)
    b.add_argument("--level", default="mixed", choices=sorted(LEVEL_WPM))
    b.add_argument("--lang", default="en-US")
    b.add_argument("--scenes", type=int)
    b.add_argument("--wpm", type=int)
    c = sub.add_parser("check")
    c.add_argument("script")
    c.add_argument("--json", action="store_true")
    t = sub.add_parser("to-storyboard")
    t.add_argument("script")
    t.add_argument("--out", required=True)
    t.add_argument("--aspect", default="16:9", choices=["16:9", "9:16", "1:1"])
    t.add_argument("--speakable", action="store_true", help="convert digits in narration to words")
    a = ap.parse_args(argv)
    if a.cmd == "budget":
        print(json.dumps(budget(a.minutes, a.level, a.lang, a.scenes, a.wpm), indent=1))
        return 0
    doc = parse(Path(a.script).read_text(encoding="utf-8"))
    errs, warns, stats = check(doc)
    if a.cmd == "check":
        if a.json:
            print(json.dumps({"errors": errs, "warnings": warns, "stats": stats}, ensure_ascii=False, indent=1))
        else:
            for e in errs:
                print("ERROR", e)
            for w in warns:
                print("WARN ", w)
            print(f"{'FAIL' if errs else 'OK'}: {stats}")
        return 1 if errs else 0
    if errs:
        for e in errs:
            print("ERROR", e)
        return 1
    sb = to_storyboard(doc, a.aspect, a.speakable)
    Path(a.out).write_text(json.dumps(sb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
