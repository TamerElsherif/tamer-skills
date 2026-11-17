"""Run: .venv/bin/python -m unittest discover -s skills/tcs-scriptwriter/tests"""
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "scripts"))

import script_md  # noqa: E402
from speakable import speakable  # noqa: E402

FIX = HERE / "fixtures" / "M1L1.script.md"
SCHEMA = json.loads((ROOT / "schemas/storyboard.schema.json").read_text())


class SpeakableTests(unittest.TestCase):
    def test_english(self):
        self.assertEqual(speakable("over $25 within 30 days", "en-US"), "over twenty-five dollars within thirty days")
        self.assertEqual(speakable("18% of claims", "en-US"), "eighteen percent of claims")
        self.assertEqual(speakable("up to $1,000", "en-US"), "up to one thousand dollars")
        self.assertEqual(speakable("In 2025", "en-US"), "In twenty twenty-five")
        self.assertEqual(speakable("paper A4", "en-US"), "paper A4")

    def test_arabic(self):
        self.assertEqual(speakable("25 دولار", "ar-EG"), "خمسة وعشرين دولار")
        self.assertIn("في المية", speakable("18%", "ar-EG"))
        self.assertIn("بالمائة", speakable("18%", "ar-MSA"))
        self.assertEqual(speakable("و2025", "ar-EG"), "وألفين وخمسة وعشرين")


class ScriptTests(unittest.TestCase):
    def test_budget(self):
        en = script_md.budget(3, "beginner", "en-US")
        ar = script_md.budget(3, "beginner", "ar-EG")
        self.assertEqual(en["wpm"], 130)
        self.assertEqual(ar["wpm"], 117)
        self.assertLess(ar["words_total"], en["words_total"])
        self.assertEqual(script_md.budget(3, "advanced", "en-US")["wpm"], 155)

    def test_fixture_checks_clean(self):
        doc = script_md.parse(FIX.read_text())
        errs, warns, stats = script_md.check(doc)
        self.assertEqual(errs, [])
        self.assertEqual(warns, [])
        self.assertEqual(stats["cues"], 14)
        self.assertEqual(doc["scenes"][4]["narration"][0]["instr"], "casual, a bit too pleased")

    def test_to_storyboard_valid(self):
        sb = script_md.to_storyboard(script_md.parse(FIX.read_text()))
        Draft202012Validator(SCHEMA).validate(sb)
        self.assertEqual(sb["voices"]["narrator"]["voice"], "marin")
        self.assertIn("rookie", sb["voices"])
        self.assertTrue(all(s["notes"].startswith("script-stage") for s in sb["scenes"]))
        self.assertTrue(all(s["claims"] for s in sb["scenes"]))

    def test_errors(self):
        bad = FIX.read_text().replace("[S01#c1]\n\n## s03", "\n\n## s03").replace("rookie: The", "ghost: The")
        errs, _, _ = script_md.check(script_md.parse(bad))
        self.assertTrue(any("without [S..]" in e for e in errs))
        self.assertTrue(any("ghost" in e for e in errs))

    def test_branching_and_arabic(self):
        txt = """---
course_id: northwind-expenses
lesson_id: M2L1
title: قرار سريع
language: ar-EG
formats: [branching]
level: beginner
cast: [learner, customer]
---
## s01_decide | decision | O1
narrator: العميل طلب عشا غالي. تعمل إيه؟
choice: تستأذن مديرك الأول -> s02_good (correct)
choice: تدفع وخلاص -> s03_bad
claim: Client entertainment must be approved in advance. [S01#c1]
## s02_good | consequence | O1
narrator: ^ برافو. الموافقة المسبقة بتخلي المصروف يترد كامل.
claim: Pre-approved client entertainment is reimbursed. [S01#c1]
## s03_bad | consequence | O1
narrator: ^ للأسف، الكحول مش بيترد من غير موافقة مسبقة.
claim: Alcohol is not reimbursable without pre-approval. [S01#c1]
"""
        doc = script_md.parse(txt)
        errs, warns, stats = script_md.check(doc)
        self.assertEqual(errs, [])
        self.assertEqual(stats["wpm"], 117)
        sb = script_md.to_storyboard(doc)
        Draft202012Validator(SCHEMA).validate(sb)
        self.assertEqual(sb["direction"], "rtl")
        self.assertEqual(sb["scenes"][0]["template"], "decision")
        self.assertTrue(sb["scenes"][0]["props"]["choices"][0]["correct"])
        self.assertIn("Egyptian", sb["voices"]["narrator"]["instructions"])


if __name__ == "__main__":
    unittest.main()
