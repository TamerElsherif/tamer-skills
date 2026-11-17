"""Run: .venv/bin/python -m unittest discover -s skills/tcs-localize/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(ROOT / "skills/tcs-storyboard/scripts"))
import localize as L  # noqa: E402
import rtl_lint  # noqa: E402
import subtitles  # noqa: E402
import validate_storyboard as V  # noqa: E402

SRC = json.loads((ROOT / "skills/tcs-storyboard/tests/fixtures/M1L1.storyboard.json").read_text())
FAKE_AR = "ده نص تجريبي عشان نتأكد إن الترجمة مش ناقصة"


def fill(work):
    for w in work:
        caret = " ".join(["^ " + FAKE_AR] * w["cues"])
        w["tr"] = f"{FAKE_AR} {caret}".strip() if w["cues"] else FAKE_AR
    return work


class LocalizeTests(unittest.TestCase):
    def setUp(self):
        self.gl = L.load_glossary(None)

    def test_skeleton_marks_everything(self):
        loc, work = L.skeleton(SRC, "ar-EG", self.gl)
        self.assertEqual(loc["direction"], "rtl")
        self.assertEqual(loc["theme"]["fonts"]["arabic"], "Cairo")
        self.assertIn("Egyptian", loc["voices"]["narrator"]["instructions"])
        self.assertTrue(loc["voices"]["rookie"]["instructions"].startswith("Speak natural Egyptian"))
        self.assertIn("en-US", loc["subtitle_languages"])
        self.assertTrue(loc["scenes"][2]["narration"][0]["text"].startswith("«TR»"))
        self.assertEqual(loc["scenes"][2]["claims"], SRC["scenes"][2]["claims"])  # claims untouched
        self.assertTrue(any("receipt → الإيصال" in w.get("hints", []) for w in work))
        self.assertFalse(any("Next → التالي" in w.get("hints", []) for w in work))
        errs, _ = rtl_lint.lint(loc, SRC)
        self.assertTrue(any("«TR»" in e for e in errs))

    def test_apply_then_lint_and_validate(self):
        loc, work = L.skeleton(SRC, "ar-EG", self.gl)
        done, errs = L.apply(loc, fill(work))
        self.assertEqual(errs, [])
        errs, warns = rtl_lint.lint(done, SRC)
        self.assertEqual(errs, [])
        verrs, _, stats = V.lint(done)
        self.assertEqual(verrs, [])
        self.assertEqual(stats["wpm"], 117)

    def test_cue_mismatch_detected(self):
        loc, work = L.skeleton(SRC, "ar-EG", self.gl)
        work = fill(work)
        w = next(x for x in work if x["cues"] == 3)
        w["tr"] = FAKE_AR
        _, errs = L.apply(loc, work)
        self.assertTrue(any("'^' markers" in e for e in errs))

    def test_lint_bidi_digits_register(self):
        loc, work = L.skeleton(SRC, "ar-MSA", self.gl)
        done, _ = L.apply(loc, fill(work))
        done["scenes"][2]["props"]["title"] = "زوروا northwind.example/help لمعرفة المزيد?"
        done["scenes"][3]["props"]["title"] = "٤ خطوات"
        done["scenes"][3]["on_screen_text"] = None
        done["scenes"][2]["on_screen_text"] = None
        _, warns = rtl_lint.lint(done)
        j = "\n".join(warns)
        self.assertIn("isolate", j)
        self.assertIn("Latin punctuation", j)
        self.assertIn("mixed digits", j)
        self.assertIn("Egyptian colloquial markers", j)

    def test_subtitles(self):
        cs = subtitles.cues(SRC, None, "text", 42, 2, 7)
        self.assertGreater(len(cs), 7)
        self.assertTrue(all(b > a for a, b, _ in cs))
        self.assertTrue(all("^" not in t for _, _, t in cs))
        self.assertTrue(all(len(line) <= 42 for _, _, t in cs for line in t.split("\n")))
        srt = subtitles.to_srt(cs)
        self.assertTrue(srt.startswith("1\n00:00:00,350 --> "))
        timing = {"lines": [{"scene_id": "s01_title", "idx": 0, "start": 1.0, "end": 5.0}]}
        self.assertEqual(subtitles.cues(SRC, timing, "text", 42, 2, 7)[0][0], 1.0)
        ar = copy.deepcopy(SRC)
        ar["language"] = "ar-EG"
        self.assertTrue(subtitles.cues(ar, None, "text", 42, 2, 7)[0][2].startswith("‏"))


if __name__ == "__main__":
    unittest.main()
