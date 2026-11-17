"""Run: .venv/bin/python -m unittest discover -s skills/tcs-assessment/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import to_csv  # noqa: E402
import to_gift  # noqa: E402
import validate_quiz as V  # noqa: E402

Q = json.loads((HERE.parent / "templates/quiz.example.json").read_text())


class QuizTests(unittest.TestCase):
    def test_example_valid(self):
        errs, warns, stats = V.lint(Q, ["O1", "O2", "O3"])
        self.assertEqual(errs, [])
        self.assertEqual(stats["items"], 5)

    def test_coverage_and_correct_count(self):
        q = copy.deepcopy(Q)
        q["items"][0]["options"][0]["correct"] = True
        errs, _, _ = V.lint(q, ["O1", "O2", "O3", "O4"])
        self.assertTrue(any("exactly one correct" in e for e in errs))
        self.assertTrue(any("O4 not covered" in e for e in errs))

    def test_ordering_and_sources(self):
        q = copy.deepcopy(Q)
        q["items"][2]["options"][0]["order"] = 3
        src = {"sources": [{"id": "S01", "chunks": [{"id": "c2"}]}]}
        errs, _, _ = V.lint(q, None, src)
        self.assertTrue(any("ordering" in e for e in errs))
        self.assertTrue(any("unknown source S01#c1" in e for e in errs))

    def test_objectives_from_curriculum(self):
        cur = {"modules": [{"lessons": [{"id": "M1L1", "objective_ids": ["O1", "O2"]}]}]}
        self.assertEqual(V.objectives_from(cur, "M1L1", None, ""), ["O1", "O2"])

    def test_gift(self):
        g = to_gift.to_gift(Q)
        self.assertIn("::Q1 [O1]::You took a $12 taxi ride", g)
        self.assertIn("=No, receipts are required over $25 #Right.", g)
        self.assertIn("{FALSE", g)
        self.assertIn("-> 2nd", g)
        self.assertIn("\\=", to_gift.esc("a=b"))
        self.assertIn("أيوه", to_gift.to_gift(Q, ar=True))

    def test_csv(self):
        c = to_csv.to_csv(Q)
        lines = c.strip().splitlines()
        self.assertEqual(len(lines), 6)
        self.assertIn("Q3,ordering", c)
        self.assertTrue(lines[3].split(",")[-1] == "" and "a;b;c;d" in lines[3])


if __name__ == "__main__":
    unittest.main()
