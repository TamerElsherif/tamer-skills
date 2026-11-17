"""Run: .venv/bin/python -m unittest discover -s skills/tcs-grounding-check/tests"""
import copy
import datetime as dt
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(ROOT / "skills/tcs-source-ingest/scripts"))
import apply_verdicts  # noqa: E402
import check  # noqa: E402
import ingest  # noqa: E402

SB = json.loads((ROOT / "skills/tcs-storyboard/tests/fixtures/M1L1.storyboard.json").read_text())
QUIZ = json.loads((ROOT / "skills/tcs-assessment/templates/quiz.example.json").read_text())
SCHEMA = json.loads((ROOT / "schemas/grounding_report.schema.json").read_text())


def mini(claims, ost=None, sid="s01"):
    sc = {"id": sid, "template": "statement", "props": {"text": "x"}, "narration": [], "claims": claims}
    if ost is not None:
        sc["on_screen_text"] = ost
    return {"lesson_id": "T", "scenes": [sc]}


class GroundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        ingest.main([str(ROOT / "examples/_shared/sop/expenses.md"), str(ROOT / "examples/_shared/policies"),
                     "--out", str(cls.tmp / "sources.yaml"), "--today", "2026-11-17"])
        cls.S = check.Sources(cls.tmp / "sources.yaml", dt.date(2026, 11, 17), 3)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def status(self, claims, ost=None):
        return [c["status"] for c in check.run(self.S, mini(claims, ost), None, "T", [])["claims"]]

    def test_golden_lesson_passes(self):
        rep = check.run(self.S, SB, QUIZ, "M1L1", ["O1", "O2", "O3"])
        Draft202012Validator(SCHEMA).validate(rep)
        s = rep["summary"]
        self.assertEqual(s["unsupported"] + s["partial"] + s["conflicting"], 0, check.markdown(rep))
        self.assertEqual(s["general_knowledge"], 2)
        self.assertIn("quiz:Q1", rep["coverage"]["O1"])

    def test_wrong_number_conflicts(self):
        st = self.status([{"text": "A receipt is required for every expense over $50.", "source_ids": ["S01"]}])
        self.assertEqual(st, ["conflicting"])

    def test_unknown_source_and_unsupported(self):
        st = self.status([{"text": "Receipts are required.", "source_ids": ["S09"]},
                          {"text": "Employees may fly business class on all trips.", "source_ids": ["S01"]}])
        self.assertEqual(st[0], "unsupported")
        self.assertIn(st[1], ("unsupported", "partial"))

    def test_source_conflict_and_outdated(self):
        st = self.status([{"text": "Expense receipts are retained for 6 years.", "source_ids": ["S02"]},
                          {"text": "Routine email is retained for 2 years.", "source_ids": ["S02"]}])
        self.assertEqual(st, ["conflicting", "outdated"])

    def test_uncited_onscreen_number_and_gk(self):
        st = self.status([{"text": "Expenses need care.", "general_knowledge": True}], ost=["Save $500 a year", "Step 3"])
        self.assertEqual(st, ["general-knowledge", "unsupported"])

    def test_apply_verdicts(self):
        rep = check.run(self.S, mini([{"text": "Employees may fly business class on all trips.", "source_ids": ["S01"]}]),
                        None, "T", [])
        rep, missing = apply_verdicts.apply(copy.deepcopy(rep), [{"scene_id": "s01", "text": "Employees may fly",
                                                                 "status": "conflicting", "note": "economy under 6 h"}])
        self.assertEqual(missing, [])
        self.assertEqual(rep["summary"]["conflicting"], 1)
        self.assertTrue(rep["claims"][0]["note"].startswith("llm:"))


if __name__ == "__main__":
    unittest.main()
