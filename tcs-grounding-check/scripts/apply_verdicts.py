#!/usr/bin/env python3
"""Merge LLM verification verdicts into grounding_report.json and recompute the summary.

Usage: apply_verdicts.py <L>.grounding_report.json verdicts.yaml
verdicts.yaml: list of {scene_id, text (exact claim text, or a unique prefix), status, note?, fact_ids?, fix?}
status ∈ supported | partial | unsupported | conflicting | outdated | general-knowledge. Notes get prefix "llm: ".
Exit 2 if unsupported/partial/conflicting remain.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

STATUSES = {"supported", "partial", "unsupported", "conflicting", "outdated", "general-knowledge"}


def apply(rep: dict, verdicts: list[dict]) -> tuple[dict, list[str]]:
    missing = []
    for v in verdicts:
        if v["status"] not in STATUSES:
            raise SystemExit(f"bad status {v['status']!r}")
        hits = [c for c in rep["claims"] if c["scene_id"] == v["scene_id"] and c["text"].startswith(v["text"])]
        if len(hits) != 1:
            missing.append(f"{v['scene_id']}: {v['text'][:50]} ({len(hits)} matches)")
            continue
        c = hits[0]
        c["status"] = v["status"]
        if v.get("note"):
            c["note"] = "llm: " + v["note"]
        for k in ("fact_ids", "fix"):
            if v.get(k):
                c[k] = v[k]
        if v["status"] in ("supported", "general-knowledge"):
            c.pop("fix", None)
    s = {k: 0 for k in ("total", "supported", "general_knowledge", "unsupported", "conflicting", "outdated", "partial")}
    for c in rep["claims"]:
        s["total"] += 1
        s[{"general-knowledge": "general_knowledge"}.get(c["status"], c["status"])] += 1
    rep["summary"] = s
    return rep, missing


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    rp, vp = Path(argv[0]), Path(argv[1])
    rep, missing = apply(json.loads(rp.read_text(encoding="utf-8")), yaml.safe_load(vp.read_text(encoding="utf-8")) or [])
    rp.write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check import markdown
    rp.with_suffix(".md").write_text(markdown(rep), encoding="utf-8")
    for m in missing:
        print("UNMATCHED", m)
    print(rep["summary"])
    s = rep["summary"]
    return 2 if s["unsupported"] + s["partial"] + s["conflicting"] else 0


if __name__ == "__main__":
    sys.exit(main())
