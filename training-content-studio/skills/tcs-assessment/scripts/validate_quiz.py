#!/usr/bin/env python3
"""Validate <lesson>.quiz.json: JSON Schema + assessment lint.

Usage: validate_quiz.py <quiz.json> [--curriculum curriculum.yaml | --storyboard <L>.storyboard.json | --objectives O1,O2]
                        [--sources sources.yaml] [--strict] [--json]
Errors: schema; duplicate item/option ids; mcq/true_false/scenario not exactly one correct; multi < 1 correct or < 3 options;
        ordering without unique 1..n `order`; matching option without `match`; flashcard without `back`;
        objective not covered (when objectives known); item objective unknown; unknown source ids.
Warnings: options without feedback; "all/none of the above"; correct option much longer than distractors;
        bloom missing; ar-* quiz without Arabic stems; < 2 items per objective in post-tests.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "schemas" / "quiz.schema.json").read_text())
ONE_CORRECT = {"mcq", "true_false", "scenario"}


def objectives_from(curriculum: dict | None, lesson_id: str | None, storyboard: dict | None, explicit: str) -> list[str]:
    if explicit:
        return [o for o in explicit.split(",") if o]
    if curriculum and lesson_id:
        for m in curriculum.get("modules", []):
            for l in m.get("lessons", []):
                if l["id"] == lesson_id:
                    return l["objective_ids"]
    if storyboard:
        return storyboard.get("objective_ids", [])
    return []


def lint(q: dict, objectives: list[str] | None = None, sources: dict | None = None) -> tuple[list[str], list[str], dict]:
    errs, warns = [], []
    for e in Draft202012Validator(SCHEMA).iter_errors(q):
        errs.append(f"schema: {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message[:180]}")
    if errs:
        return errs, warns, {}
    src_ids = {s["id"]: {c["id"] for c in s.get("chunks", [])} for s in (sources or {}).get("sources", [])}
    ids, per_obj = set(), {}
    for it in q["items"]:
        iid, t, opts = it["id"], it["type"], it.get("options", [])
        if iid in ids:
            errs.append(f"duplicate item id {iid}")
        ids.add(iid)
        per_obj[it["objective_id"]] = per_obj.get(it["objective_id"], 0) + 1
        oids = [o["id"] for o in opts]
        if len(oids) != len(set(oids)):
            errs.append(f"{iid}: duplicate option ids")
        correct = [o for o in opts if o.get("correct")]
        if t in ONE_CORRECT:
            if len(correct) != 1:
                errs.append(f"{iid}: {t} needs exactly one correct option (has {len(correct)})")
            if t == "true_false" and len(opts) != 2:
                errs.append(f"{iid}: true_false needs 2 options")
            if t in ("mcq", "scenario") and not 3 <= len(opts) <= 5:
                (errs if len(opts) < 2 else warns).append(f"{iid}: {t} has {len(opts)} options (3–5 recommended)")
        if t == "multi" and (len(correct) < 1 or len(opts) < 3):
            errs.append(f"{iid}: multi needs ≥ 3 options and ≥ 1 correct")
        if t == "ordering":
            orders = [o.get("order") for o in opts]
            if None in orders or sorted(orders) != list(range(1, len(opts) + 1)):
                errs.append(f"{iid}: ordering options need unique order 1..{len(opts)}")
        if t == "matching" and any(not o.get("match") for o in opts):
            errs.append(f"{iid}: matching options need `match`")
        if t == "flashcard" and not it.get("back"):
            errs.append(f"{iid}: flashcard needs `back`")
        if t == "scenario" and not it.get("scenario"):
            warns.append(f"{iid}: scenario item without `scenario` text")
        if t in ONE_CORRECT | {"multi"}:
            if any(not o.get("feedback") for o in opts):
                warns.append(f"{iid}: options without feedback (give per-option feedback)")
            for o in opts:
                if re.search(r"\b(all|none) of the above\b|كل ما سبق|لا شيء مما سبق", o["text"], re.I):
                    warns.append(f"{iid}: avoid '{o['text']}'")
            if correct and len(opts) > 2:
                lc = max(len(o["text"]) for o in correct)
                ld = [len(o["text"]) for o in opts if not o.get("correct")]
                if ld and lc > 1.6 * max(ld):
                    warns.append(f"{iid}: correct option is much longer than distractors (cue to the answer)")
        if not it.get("bloom"):
            warns.append(f"{iid}: no bloom level")
        if objectives and it["objective_id"] not in objectives:
            errs.append(f"{iid}: objective {it['objective_id']} is not an objective of this lesson")
        for sid in it.get("source_ids", []):
            s, _, c = sid.partition("#")
            if sources is not None and (s not in src_ids or (c and c not in src_ids[s])):
                errs.append(f"{iid}: unknown source {sid}")
        if q["language"].startswith("ar") and not re.search(r"[؀-ۿ]", it["stem"] + it.get("stem_ar", "")):
            warns.append(f"{iid}: {q['language']} quiz but stem has no Arabic")
    for o in objectives or []:
        if o not in per_obj:
            errs.append(f"objective {o} not covered by any item")
        elif q.get("kind") == "post-test" and per_obj[o] < 2:
            warns.append(f"objective {o}: only 1 item in a post-test (2+ recommended)")
    stats = {"items": len(q["items"]), "per_objective": per_obj,
             "types": {t: sum(1 for i in q["items"] if i["type"] == t) for t in {i["type"] for i in q["items"]}}}
    return errs, warns, stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quiz")
    ap.add_argument("--curriculum")
    ap.add_argument("--storyboard")
    ap.add_argument("--objectives", default="")
    ap.add_argument("--sources")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    q = json.loads(Path(a.quiz).read_text(encoding="utf-8"))
    cur = yaml.safe_load(Path(a.curriculum).read_text(encoding="utf-8")) if a.curriculum else None
    sb = json.loads(Path(a.storyboard).read_text(encoding="utf-8")) if a.storyboard else None
    src = yaml.safe_load(Path(a.sources).read_text(encoding="utf-8")) if a.sources else None
    objs = objectives_from(cur, q.get("lesson_id"), sb, a.objectives)
    errs, warns, stats = lint(q, objs, src)
    if a.json:
        print(json.dumps({"errors": errs, "warnings": warns, "stats": stats}, ensure_ascii=False, indent=1))
    else:
        for e in errs:
            print("ERROR", e)
        for w in warns:
            print("WARN ", w)
        print(f"{'FAIL' if errs or (a.strict and warns) else 'OK'}: {stats}")
    return 1 if errs or (a.strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
