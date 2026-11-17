#!/usr/bin/env python3
"""Validate sources.yaml against schemas/sources.schema.json plus lint rules.

Usage: validate_sources.py <run>/sources.yaml [--strict] [--json]
Errors (exit 1): schema violations, duplicate ids, fact -> unknown source/chunk, conflict -> unknown fact,
                 missing cached chunk files.
Warnings (exit 0 unless --strict): [auto] summaries left, auto-candidate facts left, sources without facts,
                 unresolved conflicts, outdated? tags, non-ISO dates, low-confidence facts.
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
SCHEMA = ROOT / "schemas" / "sources.schema.json"


def lint(data: dict, run_dir: Path) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    v = Draft202012Validator(json.loads(SCHEMA.read_text()))
    for e in sorted(v.iter_errors(data), key=lambda e: list(e.path)):
        errs.append(f"schema: {'/'.join(map(str, e.path)) or '<root>'}: {e.message[:200]}")
    if errs:
        return errs, warns
    sids, chunks = set(), {}
    for s in data["sources"]:
        if s["id"] in sids:
            errs.append(f"duplicate source id {s['id']}")
        sids.add(s["id"])
        chunks[s["id"]] = {}
        for c in s.get("chunks", []):
            if c["id"] in chunks[s["id"]]:
                errs.append(f"{s['id']}: duplicate chunk id {c['id']}")
            chunks[s["id"]][c["id"]] = c
            if c.get("path") and not (run_dir / c["path"]).exists():
                errs.append(f"{s['id']}#{c['id']}: cached chunk file missing: {c['path']}")
            if c["summary"].startswith("[auto]"):
                warns.append(f"{s['id']}#{c['id']}: summary still [auto] (run the LLM chunk pass)")
        if s.get("date") and not re.match(r"^\d{4}(-\d{2}(-\d{2})?)?", s["date"]):
            warns.append(f"{s['id']}: date not ISO 8601: {s['date']}")
    fids, per_source = set(), {sid: 0 for sid in sids}
    autos = 0
    for f in data["facts"]:
        if f["id"] in fids:
            errs.append(f"duplicate fact id {f['id']}")
        fids.add(f["id"])
        if f["source_id"] not in sids:
            errs.append(f"{f['id']}: unknown source {f['source_id']}")
            continue
        per_source[f["source_id"]] += 1
        if f.get("chunk_id") and f["chunk_id"] not in chunks[f["source_id"]]:
            errs.append(f"{f['id']}: unknown chunk {f['source_id']}#{f['chunk_id']}")
        tags = f.get("tags", [])
        if "auto-candidate" in tags:
            autos += 1
        if "outdated?" in tags:
            pass
        if f.get("confidence") is not None and f["confidence"] < 0.3:
            warns.append(f"{f['id']}: confidence {f['confidence']} < 0.3")
    if autos:
        warns.append(f"{autos} facts are still auto-candidates (review in the LLM pass, then merge_facts.py)")
    for sid, n in per_source.items():
        if n == 0:
            warns.append(f"{sid}: no facts extracted")
    outd = sorted({f["source_id"] for f in data["facts"] if "outdated?" in f.get("tags", [])})
    if outd:
        warns.append(f"possibly outdated sources: {', '.join(outd)} (confirm with owner or prefer newer source)")
    for c in data.get("conflicts", []):
        for fid in c["fact_ids"]:
            if fid not in fids:
                errs.append(f"conflict references unknown fact {fid}")
        if c.get("chosen_fact") and c["chosen_fact"] not in fids:
            errs.append(f"conflict chosen_fact unknown: {c['chosen_fact']}")
        if c.get("resolution") in (None, "", "unresolved") and not c.get("chosen_fact"):
            warns.append(f"unresolved conflict {c['fact_ids']}: {c['note'][:120]}")
    for g in data.get("glossary", []):
        if g.get("source_id") and g["source_id"] not in sids:
            errs.append(f"glossary term {g['term']}: unknown source {g['source_id']}")
    return errs, warns


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    p = Path(a.path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    errs, warns = lint(data, p.parent)
    if a.json:
        print(json.dumps({"errors": errs, "warnings": warns}, indent=1))
    else:
        for e in errs:
            print("ERROR", e)
        for w in warns:
            print("WARN ", w)
        print(f"{'FAIL' if errs or (a.strict and warns) else 'OK'}: {len(errs)} errors, {len(warns)} warnings")
    return 1 if errs or (a.strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
