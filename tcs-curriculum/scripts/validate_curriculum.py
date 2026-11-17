#!/usr/bin/env python3
"""Validate curriculum.yaml: JSON Schema (schemas/curriculum.schema.json) + instructional-design rules.

Usage: validate_curriculum.py curriculum.yaml [--sources sources.yaml] [--json] [--strict]
Exit 0 = no errors (warnings allowed unless --strict), 1 = errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
SCHEMA = PLUGIN_ROOT / "schemas" / "curriculum.schema.json"

# Bloom level -> typical measurable verbs (first word of the objective text)
BLOOM_VERBS = {
    "remember": {"list", "name", "identify", "recall", "recognize", "recognise", "state", "define", "label", "locate"},
    "understand": {"explain", "describe", "summarize", "summarise", "classify", "compare", "interpret", "outline", "distinguish", "paraphrase"},
    "apply": {"apply", "use", "perform", "complete", "submit", "configure", "demonstrate", "follow", "execute", "carry", "report", "set", "create"},
    "analyze": {"analyze", "analyse", "fix", "resolve", "differentiate", "examine", "spot", "detect", "investigate", "diagnose", "break", "check", "troubleshoot"},
    "evaluate": {"evaluate", "decide", "judge", "assess", "choose", "justify", "prioritize", "prioritise", "select", "critique", "verify"},
    "create": {"create", "design", "plan", "develop", "compose", "build", "draft", "propose"},
}
VAGUE = {"understand", "know", "learn", "appreciate", "be aware", "familiarize", "familiarise"}
MAX_FORMATS_COURSE = 3
MICRO_MIN, MICRO_MAX, MAX_LESSONS_PER_MODULE = 3, 7, 6


def validate(cur: dict, sources: dict | None = None) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    try:
        import jsonschema
        schema = json.loads(SCHEMA.read_text())
        v = jsonschema.Draft202012Validator(schema)
        for e in sorted(v.iter_errors(cur), key=lambda e: list(e.path)):
            errors.append(f"schema: {'/'.join(map(str, e.path)) or '<root>'}: {e.message[:200]}")
    except ImportError:
        warns.append("jsonschema not installed — schema check skipped")
    if errors:
        return errors, warns  # semantic checks assume a well-formed document

    objs = {o["id"]: o for o in cur["objectives"]}
    if len(objs) != len(cur["objectives"]):
        errors.append("duplicate objective ids")
    covered: set[str] = set()
    lesson_ids: set[str] = set()
    course_formats: set[str] = set()
    total = 0.0
    for m in cur["modules"]:
        if len(m["lessons"]) > MAX_LESSONS_PER_MODULE:
            warns.append(f"{m['id']}: {len(m['lessons'])} lessons > {MAX_LESSONS_PER_MODULE} (microlearning rule) — split the module")
        for les in m["lessons"]:
            lid = les["id"]
            if lid in lesson_ids:
                errors.append(f"duplicate lesson id {lid}")
            lesson_ids.add(lid)
            if not lid.startswith(m["id"] + "L"):
                errors.append(f"lesson {lid} is not under module {m['id']} (expected {m['id']}L<n>)")
            for oid in les["objective_ids"]:
                if oid not in objs:
                    errors.append(f"{lid}: objective {oid} not defined")
                covered.add(oid)
            if len(les["objective_ids"]) > 2:
                warns.append(f"{lid}: {len(les['objective_ids'])} objectives — microlearning targets 1 per lesson")
            course_formats.update(les["formats"])
            d = float(les["duration_min"])
            total += d
            if not (MICRO_MIN <= d <= MICRO_MAX):
                warns.append(f"{lid}: {d:g} min outside microlearning band {MICRO_MIN}-{MICRO_MAX} min")
            if len(set(les["formats"])) != len(les["formats"]):
                errors.append(f"{lid}: repeated format")
    if len(course_formats) > MAX_FORMATS_COURSE:
        errors.append(f"course blends {len(course_formats)} formats {sorted(course_formats)} > {MAX_FORMATS_COURSE}")
    for oid in objs:
        if oid not in covered:
            errors.append(f"objective {oid} is not taught by any lesson")
    tm = float(cur["course"]["total_minutes"])
    if total and abs(tm - total) / total > 0.15:
        warns.append(f"course.total_minutes={tm:g} but lessons sum to {total:g}")

    for o in cur["objectives"]:
        text = o["text"].strip()
        if text.upper().startswith("DRAFT"):
            warns.append(f"{o['id']}: draft objective text — rewrite as a measurable objective")
            continue
        first = re.split(r"[\s,]+", text.lower(), maxsplit=1)[0]
        verb = (o.get("verb") or first).lower()
        if any(text.lower().startswith(v) for v in VAGUE):
            warns.append(f"{o['id']}: vague verb '{first}' — use a measurable verb")
        elif verb not in BLOOM_VERBS[o["bloom"]] and not any(verb in s for s in BLOOM_VERBS.values()):
            warns.append(f"{o['id']}: verb '{verb}' not in the Bloom verb list (check level '{o['bloom']}')")

    pr = cur.get("prioritization")
    if pr:
        s = sum(float(pr["weights"][k]) for k in ("impact", "frequency", "gap", "urgency", "compliance"))
        if abs(s - 1) > 0.02:
            warns.append(f"prioritization weights sum to {s:.2f} (expected 1.0)")
        ids = [i["id"] for i in pr["items"]]
        if len(ids) != len(set(ids)):
            errors.append("prioritization: duplicate item ids")
        for i in pr["items"]:
            if i["decision"] != "include" and not i.get("reason"):
                warns.append(f"prioritization item {i['id']}: no reason recorded for '{i['decision']}'")

    ap = cur["approval"]
    if ap["status"] == "approved" and not (ap.get("by") and ap.get("at")):
        warns.append("approval.status=approved but by/at missing")

    langs = cur["course"]["languages"]
    if langs["primary"].startswith("ar") and not any(
            m.get("title_ar") for m in cur["modules"]) and not cur["course"].get("title_ar"):
        warns.append("Arabic primary language but no title_ar fields — run tcs-localize or add titles")

    if sources:
        known = {s["id"] for s in sources.get("sources", [])}
        for o in cur["objectives"]:
            for sid in o.get("source_ids", []):
                if sid.split("#")[0] not in known:
                    errors.append(f"{o['id']}: unknown source {sid}")
        for m in cur["modules"]:
            for les in m["lessons"]:
                for sid in les.get("source_ids", []):
                    if sid.split("#")[0] not in known:
                        errors.append(f"{les['id']}: unknown source {sid}")
    return errors, warns


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("curriculum")
    ap.add_argument("--sources")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args(argv)
    cur = yaml.safe_load(Path(a.curriculum).read_text())
    src = yaml.safe_load(Path(a.sources).read_text()) if a.sources else None
    errors, warns = validate(cur, src)
    ok = not errors and not (a.strict and warns)
    if a.json:
        print(json.dumps({"ok": ok, "errors": errors, "warnings": warns}, indent=1, ensure_ascii=False))
    else:
        for e in errors:
            print(f"ERROR  {e}")
        for w in warns:
            print(f"WARN   {w}")
        print(f"{'OK' if ok else 'FAIL'}: {len(errors)} error(s), {len(warns)} warning(s)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
