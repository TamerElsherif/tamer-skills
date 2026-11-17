#!/usr/bin/env python3
"""Tests for prioritize.py + validate_curriculum.py.

Always: a small synthetic catalogue (filters, dedupe via alternatives, quotas, family cap, given scores, label scoring).
Optional regression on a real catalogue: set TCS_TEST_CATALOG=<catalogue.xlsx> and TCS_TEST_TRACKER=<tracker.json with
rows[{n, tier}]> (the worked example) — asserts >= 15 of the tracker's "Top 20" are reproduced with --pack security-awareness.

Usage: .venv/bin/python skills/tcs-curriculum/scripts/test_prioritize.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prioritize  # noqa: E402
import validate_curriculum  # noqa: E402

CANDIDATES = {"candidates": [
    {"id": 1, "title": "Phishing", "topic": "Email", "audience": "All staff", "label": "Core (annual)", "format": "cartoon", "media_count": 1},
    {"id": 2, "title": "Preventing Phishing Attacks", "audience": "All staff", "label": "Core", "format": "explainer", "media_count": 1,
     "alternatives": "Phishing"},
    {"id": 3, "title": "Fire Awareness", "topic": "Workplace Health & Safety", "audience": "All staff", "label": "Optional"},
    {"id": 4, "title": "Board Cyber Briefing", "audience": "Executive / Top management", "label": "Role-specific", "media_count": 1},
    {"id": 5, "title": "Least Privilege", "audience": "IT & Security", "label": "Role-specific", "media_count": 1,
     "scores": {"impact": 5, "frequency": 3, "gap": 5, "urgency": 2, "compliance": 4}},
    {"id": 6, "title": "Retired Course", "audience": "All staff", "label": "Retired (dated)"},
    {"id": 7, "title": "Smishing", "audience": "All staff", "label": "Recommended", "prerequisite": "Phishing", "media_count": 1},
    {"id": 8, "title": "Password Managers", "audience": "All staff", "label": "Optional", "media_count": 1},
]}
PROFILE = {"quotas": {"standard": 2, "it": 1, "executives": 1},
           "segments": [{"id": "executives", "match": ["executive / top"]}, {"id": "it", "match": ["it & security"]},
                        {"id": "standard", "default": True, "match": ["all staff"]}],
           "filters": {"exclude_topics": ["health & safety"], "exclude_labels": ["retired"]}}


def test_synthetic():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "c.yaml").write_text(yaml.safe_dump(CANDIDATES))
        (t / "p.yaml").write_text(yaml.safe_dump(PROFILE))
        assert prioritize.main([str(t / "c.yaml"), "--config", str(t / "p.yaml"), "--out", str(t / "cur.yaml")]) == 0
        cur = yaml.safe_load((t / "cur.yaml").read_text())
        dec = {i["id"]: i for i in cur["prioritization"]["items"]}
        assert dec["2"]["decision"] == "deprioritised-duplicate", dec["2"]   # richer cartoon original kept
        assert dec["1"]["decision"] == "include"
        assert dec["3"]["decision"] == "out-of-scope" and dec["6"]["decision"] == "out-of-scope"
        assert dec["4"]["decision"] == "include" and dec["4"]["audience"] == "executives"
        assert dec["5"]["decision"] == "include" and dec["5"]["scores"]["impact"] == 5  # given scores used
        assert dec["8"]["scores"]["compliance"] == 1                                     # optional label < default
        assert sum(1 for i in dec.values() if i["decision"] == "include") == 4
        assert all(i.get("reason") for i in dec.values())
        errors, _ = validate_curriculum.validate(cur)
        assert not errors, errors


def test_catalogue_regression():
    cat, trk = os.environ.get("TCS_TEST_CATALOG"), os.environ.get("TCS_TEST_TRACKER")
    if not (cat and trk and Path(cat).exists() and Path(trk).exists()):
        print("skip: catalogue regression (set TCS_TEST_CATALOG and TCS_TEST_TRACKER)")
        return
    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "cur.yaml"
        prioritize.main([cat, "--pack", "security-awareness", "--out", str(out)])
        cur = yaml.safe_load(out.read_text())
    ours = {str(i["id"]) for i in cur["prioritization"]["items"] if i["decision"] == "include"}
    top = {str(r["n"]) for r in json.loads(Path(trk).read_text())["rows"] if r.get("tier") == "Top 20"}
    hit = len(ours & top)
    print(f"catalogue regression: {hit}/{len(top)} of the reference picks reproduced")
    assert hit >= 15, (sorted(ours - top), sorted(top - ours))
    errors, _ = validate_curriculum.validate(cur)
    assert not errors, errors


if __name__ == "__main__":
    import contextlib
    import io
    for fn in (test_synthetic, test_catalogue_regression):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            fn()
        msg = [ln for ln in buf.getvalue().splitlines() if ln.startswith(("skip", "catalogue"))]
        print(f"PASS  {fn.__name__}" + (f"  ({msg[-1]})" if msg else ""))
    print("OK")
