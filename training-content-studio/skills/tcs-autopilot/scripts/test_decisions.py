#!/usr/bin/env python3
"""Golden-run tests for decide.py. Runs every case in tests/golden_runs.yaml and asserts the decisions.

Also checks, per case: decisions.json validates against schemas/decisions.schema.json, curriculum.draft.yaml has no
validation errors (tcs-curriculum/scripts/validate_curriculum.py), and a second run is byte-identical (determinism).

Usage: .venv/bin/python skills/tcs-autopilot/scripts/test_decisions.py [-k <id-substring>] [-v]
Works under pytest too (test_golden).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
ROOT = SKILL.parents[1]
sys.path.insert(0, str(HERE))
import decide  # noqa: E402

spec = importlib.util.spec_from_file_location("validate_curriculum", ROOT / "skills/tcs-curriculum/scripts/validate_curriculum.py")
vc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vc)


def get(d, path):
    for part in path.split("."):
        if isinstance(d, list):
            d = d[int(part)]
        else:
            d = d.get(part) if isinstance(d, dict) else None
    return d


def check(actual, exp) -> str | None:
    if isinstance(exp, dict):
        if "contains_all" in exp:
            missing = [x for x in exp["contains_all"] if x not in (actual or [])]
            return f"missing {missing}" if missing else None
        if "not_contains" in exp:
            bad = [x for x in exp["not_contains"] if x in (actual or [])]
            return f"unexpected {bad}" if bad else None
        if "len" in exp:
            return None if len(actual or []) == exp["len"] else f"len {len(actual or [])} != {exp['len']}"
        if "in" in exp:
            return None if actual in exp["in"] else f"{actual!r} not in {exp['in']}"
        if "min" in exp:
            v = len(actual) if isinstance(actual, list) else actual
            return None if v is not None and v >= exp["min"] else f"{v!r} < {exp['min']}"
        if "max" in exp:
            v = len(actual) if isinstance(actual, list) else actual
            return None if v is not None and v <= exp["max"] else f"{v!r} > {exp['max']}"
    return None if actual == exp else f"{actual!r} != {exp!r}"


def run_case(case: dict, tmp: Path) -> list[str]:
    os.environ.pop("OPENMONTAGE_ROOT", None)
    fails = []
    outs = []
    for n in (1, 2):
        out = tmp / f"{case['id']}-{n}" / case["id"]
        res = decide.run([case["request"], *case.get("args", []), "--out", str(out)])
        outs.append(out)
    for path, exp in case["expect"].items():
        err = check(get(res, path), exp)
        if err:
            fails.append(f"{path}: {err}")
    schema = json.loads((ROOT / "schemas/decisions.schema.json").read_text())
    try:
        import jsonschema
        jsonschema.validate(res, schema)
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001
        fails.append(f"decisions.json schema: {str(e).splitlines()[0]}")
    cur = yaml.safe_load((outs[0] / "curriculum.draft.yaml").read_text())
    errors, _ = vc.validate(cur)
    fails += [f"curriculum.draft.yaml: {e}" for e in errors]
    for f in ("decisions.json", "decisions.md", "curriculum.draft.yaml"):
        if (outs[0] / f).read_bytes() != (outs[1] / f).read_bytes():
            fails.append(f"non-deterministic output: {f}")
    return fails


def cases():
    return yaml.safe_load((SKILL / "tests/golden_runs.yaml").read_text())


def test_golden():  # pytest entry point
    with tempfile.TemporaryDirectory() as t:
        bad = {c["id"]: f for c in cases() for f in [run_case(c, Path(t))] if f}
    assert not bad, bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-k")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    failed = 0
    with tempfile.TemporaryDirectory() as t:
        for c in cases():
            if a.k and a.k not in c["id"]:
                continue
            fails = run_case(c, Path(t))
            print(f"{'PASS' if not fails else 'FAIL'}  {c['id']}")
            for f in fails:
                print(f"      - {f}")
            failed += bool(fails)
    print(f"\n{'OK' if not failed else 'FAILED'}: {failed} failing case(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
