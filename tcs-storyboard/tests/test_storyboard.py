"""Run: .venv/bin/python -m unittest discover -s skills/tcs-storyboard/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import preview  # noqa: E402
import sbtools as T  # noqa: E402
import validate_storyboard as V  # noqa: E402

FIX = json.loads((HERE / "fixtures/M1L1.storyboard.json").read_text())
SKEL = json.loads((HERE.parent / "templates/storyboard.skeleton.json").read_text())


def scene(sb, sid):
    return next(s for s in sb["scenes"] if s["id"] == sid)


class StoryboardTests(unittest.TestCase):
    def test_fixture_and_skeleton_clean(self):
        for sb in (FIX, SKEL):
            errs, warns, stats = V.lint(sb)
            self.assertEqual(errs, [], errs)
        self.assertEqual(V.lint(FIX)[2]["cues"], 14)

    def test_cue_mismatch(self):
        sb = copy.deepcopy(SKEL)
        scene(sb, "s03_email")["props"]["callouts"].append({"cue": 2, "target": "button", "label": "Fake button"})
        errs, _, _ = V.lint(sb)
        self.assertTrue(any("reference cue 2" in e for e in errs))

    def test_too_many_bullets_and_missing_claims(self):
        sb = copy.deepcopy(FIX)
        scene(sb, "s03_rules")["props"]["items"] = [{"text": f"r{i}"} for i in range(7)]
        scene(sb, "s07_recap")["claims"] = []
        errs, _, _ = V.lint(sb)
        self.assertTrue(any("schema" in e and "items" in e for e in errs) or any("max 6" in e for e in errs))
        sb2 = copy.deepcopy(FIX)
        scene(sb2, "s07_recap")["claims"] = []
        errs2, _, _ = V.lint(sb2)
        self.assertTrue(any("no claims" in e for e in errs2))

    def test_image_prompt_clause_and_personas(self):
        sb = copy.deepcopy(SKEL)
        sb["generated_images"][0]["prompt"] = "A laptop with a sign that says PAY NOW"
        scene(sb, "s02_story")["props"]["people"][0]["cast"] = "sam"
        errs, _, _ = V.lint(sb)
        self.assertTrue(any("must end with" in e for e in errs))
        self.assertTrue(any("unknown persona id 'sam'" in e for e in errs))
        self.assertIn("vex", T.known_personas())  # domain pack persona discovered (if pack present)

    def test_voice_rtl_stage(self):
        sb = copy.deepcopy(FIX)
        sb["language"] = "ar-EG"
        del sb["voices"]["rookie"]
        scene(sb, "s01_title")["notes"] = "script-stage: template TBD"
        errs, _, _ = V.lint(sb, stage="final")
        joined = "\n".join(errs)
        self.assertIn("direction: rtl", joined)
        self.assertIn("no entry in voices", joined)
        self.assertIn("script-stage", joined)
        errs_s, warns_s, _ = V.lint(copy.deepcopy(FIX) | {"scenes": [dict(scene(FIX, "s01_title"), notes="script-stage: x")]},
                                    stage="script")
        self.assertEqual(errs_s, [])

    def test_quiz_ref(self):
        errs, _, _ = V.lint(FIX, quiz={"items": [{"id": "Q9"}]})
        self.assertTrue(any("Q1 not in quiz.json" in e for e in errs))

    def test_derive_text(self):
        st = T.derive_on_screen_text(scene(FIX, "s02_hook"))
        self.assertEqual(st[0], "18%")
        em = T.derive_on_screen_text(scene(SKEL, "s03_email"))
        self.assertIn("billing@northwind-co.example", em)
        self.assertIn("Look-alike domain", em)
        self.assertNotIn("addr", em)
        cart = T.derive_on_screen_text(scene(SKEL, "s02_story"))
        self.assertEqual(cart, ["Overdue invoice? I'll just pay it.", "Check the sender first!"])
        sc = {"template": "screencast", "props": {"app": {"kind": "form", "title": "New Claim",
              "fields": [{"id": "amt", "label": "Amount", "kind": "amount"}]},
              "actions": [{"cue": 0, "do": "type", "target": "amt", "value": "$140"}]}}
        self.assertEqual(T.derive_on_screen_text(sc), ["New Claim", "Amount", "$140"])

    def test_preview(self):
        md = preview.render(FIX)
        self.assertIn("| 3 | s03_rules | bullets |", md)
        self.assertIn("▸", md)
        self.assertIn("Approve", md)


if __name__ == "__main__":
    unittest.main()
