#!/usr/bin/env python3
"""Prioritize a candidate catalogue into a curriculum (tcs-curriculum).

priority = sum(w_i * score_i) over {impact, frequency, gap, urgency, compliance} (scores 0-5)
then: filter out-of-scope -> dedupe by subject cluster (keep the richest original) -> audience quotas -> tiers.

Usage:
  prioritize.py <candidates.yaml|.xlsx|.csv> [--pack security-awareness | --config prof.yaml]
                [--weights impact=.3,frequency=.25,...] [--quotas standard=10,it=5,executives=5]
                [--tier2 15] [--existing "Title A;Title B"] [--sheet Courses]
                [--course-id my-course] [--title "..."] [--lang en-US]
                --out curriculum.yaml [--md prioritization.md] [--top 20]

Input files are opened read-only. Deterministic: same input + config -> same output.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = SKILL_DIR.parents[1]
DIMS = ("impact", "frequency", "gap", "urgency", "compliance")

COLUMN_SYNONYMS = {
    "id": ["#", "id", "no", "no.", "code", "course id", "catalog #"],
    "title": ["course", "title", "course title", "name", "module", "subject"],
    "topic": ["topic", "category", "theme", "area"],
    "audience": ["target audience", "audience", "roles", "role", "who"],
    "label": ["priority", "priority (si-ware)", "status", "requirement", "mandatory"],
    "region": ["region", "jurisdiction", "country"],
    "format": ["format", "style", "type", "media type"],
    "media_count": ["videos", "video count", "media", "media count"],
    "alternatives": ["alternative versions", "alternatives", "duplicates", "see also"],
    "languages": ["languages", "language count", "locales"],
    "description": ["brief description", "description", "summary"],
    "cluster": ["cluster", "subject cluster", "group"],
    "prerequisite": ["dependency (take first)", "prerequisite", "prerequisites", "depends on", "dependency"],
}


# ---------------------------------------------------------------- config
def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


SEGMENT_ALIASES = {"exec": "executives", "execs": "executives", "executive": "executives", "leadership": "executives",
                   "staff": "standard", "all": "standard", "all-staff": "standard", "standard-users": "standard",
                   "it-department": "it", "technical": "it"}
NATIVE_KEYS = {"weights", "quotas", "segments", "filters", "scoring", "clusters", "title_noise", "existing", "family_cap",
               "families", "pack_families", "format_map", "minutes_per_lesson"}


def adapt_profile(over: dict, cfg: dict) -> dict:
    """Accept a domain-pack prioritization.yaml written in a looser/descriptive shape and map what we understand:
    weights; quotas (segment aliases); audiences{seg: [labels]} -> extra segment match strings; clusters{id: {members}}
    -> subject families (soft family cap); tiers{tier2: n}. Native keys pass through unchanged."""
    out = {k: v for k, v in over.items() if k in NATIVE_KEYS and not (k == "clusters" and _is_member_clusters(v))}
    seg_ids = [s["id"] for s in cfg.get("segments", [])]
    alias = lambda k: k if k in seg_ids else SEGMENT_ALIASES.get(str(k).lower(), k)
    if isinstance(over.get("quotas"), dict):
        out["quotas"] = {alias(k): int(v) for k, v in over["quotas"].items()}
    if isinstance(over.get("audiences"), dict):
        segs = [dict(s, match=list(s.get("match", []))) for s in (out.get("segments") or cfg.get("segments", []))]
        for k, labels in over["audiences"].items():
            sid = alias(k)
            seg = next((s for s in segs if s["id"] == sid), None)
            if seg is None:
                seg = {"id": sid, "match": []}
                segs.insert(0, seg)
            seg["match"] += [str(x).lower() for x in labels if str(x).lower() not in seg["match"]]
        out["segments"] = segs
    if _is_member_clusters(over.get("clusters")):
        out["pack_families"] = {cid: [str(m).lower() for m in (v.get("members") or [])] for cid, v in over["clusters"].items()}
    tiers = over.get("tiers")
    if isinstance(tiers, dict) and isinstance(tiers.get("tier2"), int):
        out["tiers"] = {"tier2": tiers["tier2"]}
    return out


def _is_member_clusters(v) -> bool:
    return isinstance(v, dict) and any(isinstance(x, dict) and "members" in x for x in v.values())


def load_config(pack: str | None, config: str | None) -> tuple[dict, str]:
    """default <- templates/prioritization.<pack>.yaml <- domains/<pack>/prioritization.yaml | pack.yaml:prioritization <- --config"""
    cfg = yaml.safe_load((SKILL_DIR / "templates" / "prioritization.default.yaml").read_text())
    origins = ["default"]
    if pack:
        tmpl = SKILL_DIR / "templates" / f"prioritization.{pack}.yaml"
        if tmpl.exists():
            cfg = deep_merge(cfg, yaml.safe_load(tmpl.read_text()) or {})
            origins.append(str(tmpl.relative_to(PLUGIN_ROOT)))
        dom = PLUGIN_ROOT / "domains" / pack / "prioritization.yaml"
        pack_yaml = PLUGIN_ROOT / "domains" / pack / "pack.yaml"
        over = None
        if dom.exists():
            over, src = yaml.safe_load(dom.read_text()) or {}, dom
        elif pack_yaml.exists():
            p = (yaml.safe_load(pack_yaml.read_text()) or {}).get("prioritization")
            if isinstance(p, dict):
                over, src = p, pack_yaml
        if over:
            cfg = deep_merge(cfg, adapt_profile(over, cfg))
            origins.append(str(src.relative_to(PLUGIN_ROOT)))
        if len(origins) == 1:
            print(f"warning: no prioritization profile for pack '{pack}', using defaults", file=sys.stderr)
    if config:
        over = yaml.safe_load(Path(config).read_text()) or {}
        cfg = deep_merge(cfg, adapt_profile(over, cfg))
        origins.append(config)
    return cfg, " + ".join(origins)


def parse_kv(text: str | None, cast=float) -> dict:
    if not text:
        return {}
    if Path(text).exists():
        return yaml.safe_load(Path(text).read_text()) or {}
    out = {}
    for part in text.split(","):
        k, _, v = part.partition("=")
        out[k.strip()] = cast(v)
    return out


# ---------------------------------------------------------------- input
def _norm_header(h) -> str:
    return re.sub(r"\s+", " ", str(h or "").strip().lower())


def map_columns(header: list) -> dict:
    hn = [_norm_header(h) for h in header]
    mapping = {}
    for field, syns in COLUMN_SYNONYMS.items():
        for s in syns:
            if s in hn and hn.index(s) not in mapping.values():
                mapping[field] = hn.index(s)
                break
    if "title" not in mapping:
        raise SystemExit(f"could not find a title column in header {header}")
    return mapping


def rows_from_table(rows: list[list]) -> list[dict]:
    # header = first row having >= 3 non-empty cells and a title-like column
    for hi, r in enumerate(rows[:20]):
        cells = [_norm_header(c) for c in r]
        if sum(1 for c in cells if c) >= 3 and any(c in COLUMN_SYNONYMS["title"] for c in cells):
            break
    else:
        raise SystemExit("no header row found in the first 20 rows")
    cmap = map_columns(rows[hi])
    items = []
    for n, r in enumerate(rows[hi + 1:], start=1):
        if not r or all(c in (None, "") for c in r):
            continue
        rec = {f: r[i] if i < len(r) else None for f, i in cmap.items()}
        if not rec.get("title"):
            continue
        rec["id"] = str(rec.get("id") if rec.get("id") not in (None, "") else n)
        items.append(rec)
    return items


def load_candidates(path: str, sheet: str | None) -> list[dict]:
    p = Path(path)
    suf = p.suffix.lower()
    if suf in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        if sheet:
            ws = wb[sheet]
        else:  # the sheet with a title-like header and the most rows
            best = None
            for w in wb.worksheets:
                rows = list(w.iter_rows(values_only=True, max_row=20))
                ok = any(any(_norm_header(c) in COLUMN_SYNONYMS["title"] for c in r) for r in rows)
                if ok and (best is None or (w.max_row or 0) > (best.max_row or 0)):
                    best = w
            if best is None:
                raise SystemExit("no sheet with a title/course column")
            ws = best
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        wb.close()
        return rows_from_table(rows)
    if suf == ".csv":
        with p.open(newline="", encoding="utf-8-sig") as fh:
            return rows_from_table([list(r) for r in csv.reader(fh)])
    data = yaml.safe_load(p.read_text())
    items = data.get("candidates", data) if isinstance(data, dict) else data
    out = []
    for n, it in enumerate(items, start=1):
        it = dict(it)
        it["id"] = str(it.get("id", n))
        out.append(it)
    return out


# ---------------------------------------------------------------- scoring
def low(x) -> str:
    return str(x or "").strip().lower()


def subject_key(title: str, noise: list[str]) -> str:
    t = low(title)
    for pat in noise:
        t = re.sub(pat, " ", t)
    t = re.sub(r"[^a-z0-9؀-ۿ]+", " ", t)
    toks = [w[:-1] if w.endswith("s") and len(w) > 3 else w for w in t.split()]
    return " ".join(sorted(set(toks)))


def tokens(title: str) -> set[str]:
    return {w for w in re.sub(r"[^a-z0-9]+", " ", low(title)).split() if len(w) > 2}


def norm_text(x) -> str:
    """lowercase, punctuation -> spaces (keeps &), so 'Multi-Factor (MFA) Fatigue' matches 'mfa fatigue'."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w&\u0600-\u06ff]+", " ", low(x))).strip()


def kw_hit(kw: str, text: str) -> bool:
    """whole-word match on normalised text; tolerates a plural 's'."""
    k = norm_text(kw)
    return re.search(r"(?<![a-z0-9])" + re.escape(k) + r"s?(?![a-z0-9])", norm_text(text)) is not None


def kw_score(text: str, table: dict, default: float, penalty: float = 0.0) -> tuple[float, str | None]:
    best, hit = None, None
    for kw, val in (table or {}).items():
        if kw_hit(kw, text) and (best is None or val - penalty > best):
            best, hit = float(val) - penalty, kw
    if best is None or best < default:
        return default, None
    return best, hit


def segments_for(item: dict, segs: list[dict]) -> tuple[str, list[str]]:
    aud = low(item.get("audience"))
    hay = f"{aud} | {low(item.get('title'))}"
    default = next((s["id"] for s in segs if s.get("default")), segs[-1]["id"])
    dflt_tokens = next((s.get("match", []) for s in segs if s.get("default")), [])
    found = []  # (position, id)
    for s in segs:
        if s.get("default"):
            continue
        pos = [hay.find(m) for m in s.get("match", []) if m in hay]
        if pos:
            found.append((min(pos), s["id"]))
    found.sort()
    special = [sid for _, sid in found]
    starts_default = any(aud.startswith(t) for t in dflt_tokens)
    has_default = any(t in aud for t in dflt_tokens) or not special
    eligible = ([default] if has_default else []) + special
    preferred = default if (starts_default or not special) else special[0]
    eligible = [preferred] + [e for e in eligible if e != preferred]
    return preferred, eligible


def score_item(it: dict, cfg: dict) -> dict:
    sc = cfg["scoring"]
    title, topic = low(it.get("title")), low(it.get("topic"))
    tpen = float(sc.get("topic_penalty", 1.5))  # topic keywords count less than title keywords
    scores, why = {}, []
    if isinstance(it.get("scores"), dict) and all(d in it["scores"] for d in DIMS):
        return {d: float(it["scores"][d]) for d in DIMS}, ["scores given"]
    for d in ("impact", "frequency", "urgency"):
        table = sc["keywords"].get(d)
        a, hit = kw_score(title, table, sc["default"][d])
        b, hit_t = kw_score(topic, table, sc["default"][d], tpen)
        scores[d] = max(a, b)
        if hit and a >= b:
            why.append(f"{d}:{hit}")
        elif hit_t:
            why.append(f"{d}:topic '{hit_t}'")
    # frequency also from audience breadth
    fa, hit = kw_score(low(it.get("audience")), sc.get("audience_frequency"), 0)
    if fa > scores["frequency"]:
        scores["frequency"] = fa
        why.append(f"frequency:audience '{hit}'")
    comp_label, hit = kw_score(low(it.get("label")), sc.get("label_compliance"), -1.0)
    if comp_label < 0:  # no label keyword -> default; a matched label may score below the default (e.g. optional = 1)
        comp_label = float(sc["default"]["compliance"])
    comp_kw, hit2 = kw_score(title, sc["keywords"].get("compliance"), 0)
    scores["compliance"] = max(comp_label, comp_kw)
    if hit or hit2:
        why.append(f"compliance:{hit or hit2}")
    scores["gap"] = float(sc["default"]["gap"])
    return scores, why


def richness(it: dict, cfg: dict) -> float:
    fmt = low(it.get("format"))
    r = float(cfg["scoring"].get("richness_format", {}).get(fmt, 1))
    try:
        r += min(float(it.get("media_count") or 0), 3) * 0.5
    except (TypeError, ValueError):
        pass
    try:
        r += min(float(it.get("languages") or 0), 50) / 100
    except (TypeError, ValueError):
        pass
    return r


# ---------------------------------------------------------------- main algorithm
def prioritize(items: list[dict], cfg: dict) -> list[dict]:
    flt = cfg["filters"]
    noise = cfg.get("title_noise", [])
    existing = [low(e) for e in cfg.get("existing", [])]
    existing_tokens = [tokens(e) for e in existing]
    by_title = {low(it["title"]): it for it in items}

    # 1. filter + score
    for it in items:
        it["_reason"] = []
        topic, label, region = low(it.get("topic")), low(it.get("label")), low(it.get("region"))
        decision = None
        if low(it["title"]) in existing or low(it["id"]) in existing:
            decision, why = "previously-built", "already built (existing list)"
        elif any(x in topic for x in flt.get("exclude_topics", [])):
            decision, why = "out-of-scope", f"topic '{it.get('topic')}' outside remit"
        elif any(x in label for x in flt.get("exclude_labels", [])):
            decision, why = "out-of-scope", f"label '{it.get('label')}'"
        elif flt.get("allowed_regions") and region and not any(x in region for x in flt["allowed_regions"]):
            decision, why = "out-of-scope", f"region '{it.get('region')}' not in scope"
        elif flt.get("require_media") and str(it.get("media_count", "1")).strip() in ("0", "0.0"):
            decision, why = "out-of-scope", "text-only original (no media)"
        it["decision"] = decision
        if decision:
            it["_reason"].append(why)
        it["scores"], why = score_item(it, cfg)
        it["_why"] = why
        it["_rich"] = richness(it, cfg)
        it["segment"], it["_eligible"] = segments_for(it, cfg["segments"])

    # foundational hubs: items many others list as prerequisite get a frequency bonus
    indeg: dict[str, int] = {}
    for it in items:
        pre = low(it.get("prerequisite"))
        if pre and pre not in ("none", "-", "—"):
            indeg[pre] = indeg.get(pre, 0) + 1
    fb = cfg["scoring"].get("foundation_bonus", {3: 1.0, 1: 0.5})
    spen = float(cfg["scoring"].get("specialisation_penalty", 1.0))
    # subject families: profile `families` ({id: [members]} or {id: {match, cap}}) first, then the pack's clusters;
    # within each source the longest matching member wins
    fams = cfg.get("families") or {}
    by_len = lambda pairs: sorted(pairs, key=lambda x: -len(x[0]))
    fam_members = by_len((str(m).lower(), cid) for cid, f in fams.items() for m in (f.get("match", []) if isinstance(f, dict) else f)) + \
        by_len((m, cid) for cid, ms in (cfg.get("pack_families") or {}).items() for m in ms)
    cfg["_family_caps"] = {cid: int(f["cap"]) for cid, f in fams.items() if isinstance(f, dict) and "cap" in f}
    for it in items:  # a specialisation (has a prerequisite) reaches fewer people than its parent subject
        pre = low(it.get("prerequisite"))
        is_special = bool(pre and pre not in ("none", "-", "—"))
        named = next((cid for m, cid in fam_members if kw_hit(m, it["title"])), None)  # pack-defined subject families
        it["family"] = named or (pre if is_special else low(it["title"]))
        if is_special and spen:
            it["scores"]["frequency"] = max(0.0, it["scores"]["frequency"] - spen)
            it["_why"].append(f"frequency:-{spen:g} specialisation of '{it.get('prerequisite')}'")
    for it in items:
        n = indeg.get(low(it["title"]), 0)
        bonus = max([float(v) for k, v in fb.items() if n >= int(k)] or [0])
        if bonus:
            it["scores"]["frequency"] = min(5.0, it["scores"]["frequency"] + bonus)
            it["_why"].append(f"frequency:+{bonus:g} prerequisite of {n}")

    # 2. subject clusters: alternatives column (union-find) + explicit clusters + normalized title
    parent = {it["id"]: it["id"] for it in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    keyed: dict[str, str] = {}
    for it in items:
        for alt in re.split(r"[;\n]", str(it.get("alternatives") or "")):
            other = by_title.get(low(alt))
            if other and other["segment"] == it["segment"]:
                union(it["id"], other["id"])
        for cid, pats in (cfg.get("clusters") or {}).items():
            if any(re.search(p, low(it["title"])) for p in pats):
                it.setdefault("cluster", cid)
        key = f"{it['segment']}::{it.get('cluster') or subject_key(it['title'], noise)}"
        if key in keyed:
            union(it["id"], keyed[key])
        else:
            keyed[key] = it["id"]

    # gap: subjects related to existing builds get gap=1
    for it in items:
        tk = tokens(it["title"])
        for e, et in zip(existing, existing_tokens):
            if it["decision"] != "previously-built" and et and len(tk & et) / max(1, len(et)) >= 0.5:
                it["scores"]["gap"] = 1.0
                it["_why"].append(f"gap:related to existing '{e}'")
    clusters: dict[str, list[dict]] = {}
    for it in items:
        clusters.setdefault(find(it["id"]), []).append(it)
    ex_clusters = {find(it["id"]) for it in items if it["decision"] == "previously-built"}
    w = cfg["weights"]
    for it in items:
        if find(it["id"]) in ex_clusters and it["decision"] != "previously-built":
            it["scores"]["gap"] = 0.5
            it["_why"].append("gap:subject already built")
        it["priority"] = round(sum(w[d] * it["scores"][d] for d in DIMS), 3)

    # 3. dedupe: keep the richest (then highest priority) live member per cluster
    for members in clusters.values():
        live = [m for m in members if not m["decision"]]
        if len(live) < 2:
            continue
        live.sort(key=lambda m: (-m["_rich"], -m["priority"], int(m["id"]) if str(m["id"]).isdigit() else 0))
        keep = live[0]
        # the kept item represents the whole subject: it inherits the best score of its cluster per dimension
        for d in DIMS:
            keep["scores"][d] = max(m["scores"][d] for m in live)
        keep["priority"] = round(sum(w[d] * keep["scores"][d] for d in DIMS), 3)
        for m in live[1:]:
            m["decision"] = "deprioritised-duplicate"
            m["_reason"].append(f"duplicate subject of '{keep['title']}' (kept richer original)")

    # 4. quotas (greedy by priority; preferred segment first, eligible fallbacks next)
    quotas = dict(cfg.get("quotas") or {})
    left = dict(quotas)
    live = sorted([it for it in items if not it["decision"]],
                  key=lambda m: (-m["priority"], -m["_rich"], str(m["id"]).zfill(6)))
    rank = 0
    fam_cap = int(cfg.get("family_cap", 0) or 0)  # max top picks per subject family (parent + specialisations)
    fam_used: dict[str, int] = {}
    for it in live:
        fam = it.get("family") or low(it["title"])  # global: also caps exec/IT variants of a staff subject
        cap = cfg["_family_caps"].get(fam, fam_cap)
        if cap and fam_used.get(fam, 0) >= cap:
            it["_reason"].append(f"family cap {cap} reached for '{fam}'")
            continue
        for seg in it["_eligible"]:
            if left.get(seg, 0) > 0:
                fam_used[fam] = fam_used.get(fam, 0) + 1
                left[seg] -= 1
                rank += 1
                it.update(decision="include", tier="Top", rank=rank, segment=seg)
                it["_reason"].append(f"top-{quotas[seg]} in {seg} quota")
                break
    # soft cap: never leave a quota empty because of the family cap
    for it in live:
        if it["decision"]:
            continue
        for seg in it["_eligible"]:
            if left.get(seg, 0) > 0:
                left[seg] -= 1
                rank += 1
                it.update(decision="include", tier="Top", rank=rank, segment=seg)
                it["_reason"].append(f"top-{quotas[seg]} in {seg} quota (family cap relaxed)")
                break
    unfilled = {k: v for k, v in left.items() if v > 0}
    if unfilled:
        print(f"note: quotas not filled (not enough eligible items): {unfilled}", file=sys.stderr)
    tier2 = int((cfg.get("tiers") or {}).get("tier2", 15))
    for it in live:
        if it["decision"]:
            continue
        rank += 1
        if tier2 > 0:
            it.update(decision="tier-2", tier="Tier 2", rank=rank)
            tier2 -= 1
        else:
            it.update(decision="tier-3", tier="Tier 3", rank=rank)
        it["_reason"].append("quota full; ranked by priority")
    return items


# ---------------------------------------------------------------- output
def slug(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", low(s))).strip("-") or "course"


def to_curriculum(items: list[dict], cfg: dict, args) -> dict:
    included = sorted([i for i in items if i["decision"] == "include"], key=lambda i: i["rank"])
    seg_order = [s for s in (cfg.get("quotas") or {})]
    modules, objectives = [], []
    fmap = cfg.get("format_map", {})
    mins = float(cfg.get("minutes_per_lesson", 5))
    for seg in seg_order:
        group = [i for i in included if i["segment"] == seg]
        for chunk_start in range(0, len(group), 12):
            chunk = group[chunk_start:chunk_start + 12]
            if not chunk:
                continue
            m = len(modules) + 1
            lessons = []
            for li, it in enumerate(chunk, start=1):
                oid = f"O{len(objectives) + 1}"
                objectives.append({"id": oid, "bloom": "apply", "type": "behavior",
                                   "text": f"DRAFT: apply safe practice for '{it['title']}' (refine in tcs-curriculum step 3)"})
                lessons.append({
                    "id": f"M{m}L{li}", "title": str(it["title"]), "objective_ids": [oid],
                    "formats": [fmap.get(low(it.get("format")), fmap.get("default", "explainer"))],
                    "duration_min": mins, "status": "planned",
                    "rationale": f"P={it['priority']} rank {it['rank']}; " + "; ".join(it["_why"][:4]),
                })
            modules.append({"id": f"M{m}", "title": f"{seg.title()} track", "lessons": lessons})
    if not modules:
        raise SystemExit("nothing included — check filters/quotas")
    pr_items = []
    for it in sorted(items, key=lambda i: (i.get("rank") or 10**6, -i["priority"])):
        rec = {"id": str(it["id"]), "title": str(it["title"]), "audience": it["segment"],
               "scores": {d: round(float(it["scores"][d]), 2) for d in DIMS},
               "priority": it["priority"], "decision": it["decision"],
               "reason": "; ".join(it["_reason"] + it["_why"][:3]) or "-"}
        if it.get("cluster"):
            rec["cluster"] = it["cluster"]
        if it.get("tier"):
            rec["tier"] = it["tier"]
        if it.get("rank"):
            rec["rank"] = it["rank"]
        pr_items.append(rec)
    lang = args.lang
    return {
        "schema_version": "1.0",
        "course": {
            "id": slug(args.course_id or args.title or Path(args.input).stem),
            "title": args.title or f"Prioritized curriculum from {Path(args.input).name}",
            "domain": args.pack or "general", **({"domain_pack": args.pack} if args.pack else {}),
            "audience": {"level": "mixed", "roles": seg_order},
            "languages": {"primary": lang},
            "total_minutes": round(mins * len(included), 1),
            "targets": ["video"],
        },
        "objectives": objectives,
        "modules": modules,
        "prioritization": {"weights": cfg["weights"], "quotas": cfg.get("quotas") or {}, "items": pr_items},
        "approval": {"status": "draft"},
    }


def to_markdown(items: list[dict], top: int) -> str:
    inc = sorted([i for i in items if i.get("rank")], key=lambda i: i["rank"])[:top]
    lines = ["| rank | id | title | segment | P | I | F | G | U | C | why |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in inc:
        s = i["scores"]
        lines.append(f"| {i['rank']} | {i['id']} | {i['title']} | {i['segment']} | {i['priority']} | "
                     f"{s['impact']:g} | {s['frequency']:g} | {s['gap']:g} | {s['urgency']:g} | {s['compliance']:g} | "
                     f"{'; '.join(i['_why'][:3])} |")
    dup = [i for i in items if i["decision"] == "deprioritised-duplicate"]
    lines += ["", f"Deprioritised duplicates: {len(dup)}; out-of-scope: "
              f"{sum(1 for i in items if i['decision'] == 'out-of-scope')}; previously built: "
              f"{sum(1 for i in items if i['decision'] == 'previously-built')}"]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--pack")
    ap.add_argument("--config")
    ap.add_argument("--weights", help="k=v,... or a yaml file")
    ap.add_argument("--quotas", help="segment=n,... or a yaml file")
    ap.add_argument("--tier2", type=int)
    ap.add_argument("--existing", help="';'-separated titles/ids already built")
    ap.add_argument("--sheet")
    ap.add_argument("--course-id")
    ap.add_argument("--title")
    ap.add_argument("--lang", default="en-US")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args(argv)

    cfg, origin = load_config(args.pack, args.config)
    if args.weights:
        cfg["weights"] = {**cfg["weights"], **parse_kv(args.weights)}
    if args.quotas:
        cfg["quotas"] = parse_kv(args.quotas, int)
    if args.tier2 is not None:
        cfg.setdefault("tiers", {})["tier2"] = args.tier2
    if args.existing:
        cfg["existing"] = [e.strip() for e in args.existing.split(";") if e.strip()]
    for s in cfg["segments"]:
        if s["id"] not in cfg["quotas"] and not s.get("default"):
            cfg["quotas"][s["id"]] = 0
    tot = sum(cfg["weights"][d] for d in DIMS)
    if abs(tot - 1) > 0.01:
        print(f"note: weights sum to {tot:.2f}; normalising", file=sys.stderr)
        cfg["weights"] = {d: cfg["weights"][d] / tot for d in DIMS}

    items = prioritize(load_candidates(args.input, args.sheet), cfg)
    cur = to_curriculum(items, cfg, args)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(yaml.safe_dump(cur, sort_keys=False, allow_unicode=True, width=120))
    md = to_markdown(items, args.top)
    if args.md:
        Path(args.md).write_text(f"# Prioritization ({origin})\n\n" + md)
    print(md)
    print(f"wrote {args.out} (profile: {origin})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
