"""Tests for tcs-source-ingest. Run: .venv/bin/python -m unittest discover -s skills/tcs-source-ingest/tests"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
ROOT = SKILL.parents[1]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

import ingest  # noqa: E402
import merge_facts  # noqa: E402
import validate_sources  # noqa: E402

SOP_MD = ROOT / "examples/_shared/sop/expenses.md"
SOP_PDF = ROOT / "examples/_shared/sop/expenses.pdf"
POLICIES = ROOT / "examples/_shared/policies"


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "sources.yaml"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_ingest(self, *args):
        return ingest.main([*map(str, args), "--out", str(self.out), "--today", "2026-11-17"])

    def load(self):
        return yaml.safe_load(self.out.read_text())

    def test_pdf_and_folder_schema_valid(self):
        if not SOP_PDF.exists():
            subprocess.run([sys.executable, str(SCRIPTS / "md_to_pdf.py"), str(SOP_MD), str(SOP_PDF)], check=True)
        rc = self.run_ingest(SOP_PDF, POLICIES, "--course-id", "northwind-expenses")
        self.assertEqual(rc, 0)
        d = self.load()
        errs, _ = validate_sources.lint(d, self.tmp)
        self.assertEqual(errs, [])
        self.assertEqual([s["id"] for s in d["sources"]], ["S01", "S02"])
        s1 = d["sources"][0]
        self.assertEqual(s1["type"], "pdf")
        self.assertEqual(s1["date"], "2026-03-01")
        self.assertEqual(s1["owner"], "Finance Department")
        self.assertTrue((self.tmp / s1["chunks"][0]["path"]).exists())
        steps = [f for f in d["facts"] if f["kind"] == "step" and f["source_id"] == "S01"]
        self.assertEqual([f["procedure_order"] for f in steps], [1, 2, 3, 4, 5, 6])
        # wrapped PDF lines are re-joined
        self.assertTrue(any("necessary to do Northwind Co. work" in f["text"] for f in d["facts"]))

    def test_conflict_and_outdated(self):
        self.run_ingest(SOP_MD, POLICIES)
        d = self.load()
        self.assertTrue(d.get("conflicts"), "7-year vs 6-year retention conflict expected")
        texts = {f["id"]: f["text"] for f in d["facts"]}
        c = d["conflicts"][0]
        joined = " ".join(texts[i] for i in c["fact_ids"])
        self.assertIn("7 years", joined)
        self.assertIn("6 years", joined)
        old = [f for f in d["facts"] if "outdated?" in f.get("tags", [])]
        self.assertTrue(old and all(f["source_id"] == "S02" for f in old))

    def test_chunking_large_text(self):
        big = self.tmp / "big.md"
        big.write_text("# Big\n\n" + "\n\n".join(f"## Section {i}\n\n" + ("Employees must follow rule number %d. " % i) * 60
                                                for i in range(1, 15)))
        self.run_ingest(big)
        d = self.load()
        chunks = d["sources"][0]["chunks"]
        self.assertGreater(len(chunks), 3)
        for c in chunks[:-1]:
            self.assertLessEqual(c["tokens"], 1300)
            self.assertGreaterEqual(c["tokens"], 400)
        self.assertTrue(chunks[0]["loc"].startswith("§"))

    def test_pasted_append_and_dedupe(self):
        self.run_ingest(SOP_MD)
        rc = ingest.main(["--text", "Visitors must wear a badge at all times. Never lend your badge.", "--title", "Badge note",
                          "--append", "--out", str(self.out)])
        self.assertEqual(rc, 0)
        rc = ingest.main([str(SOP_MD), "--append", "--out", str(self.out)])  # duplicate content
        d = self.load()
        self.assertEqual([s["type"] for s in d["sources"]], ["markdown", "pasted"])
        ids = [f["id"] for f in d["facts"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_remote_is_instructions_only(self):
        self.run_ingest(SOP_MD)
        rc = ingest.main(["gdrive:Training/Expenses", "--append", "--out", str(self.out)])
        self.assertEqual(rc, 3)
        rep = (self.tmp / "cache/ingest_report.md").read_text()
        self.assertIn("rclone copy gdrive:Training/Expenses", rep)

    def test_vtt_and_arabic(self):
        cues = ingest.parse_vtt("WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nhello there\n\n00:01:05.000 --> 00:01:08.000\nnext part\n")
        segs = ingest.timed_segments(cues)
        self.assertEqual(segs[0].loc, "00:00:01-00:01:08")
        self.assertEqual(ingest.detect_lang("ده مثال بسيط عشان نفهم إزاي الموضوع ماشي كده مش أكتر"), "ar-EG")
        self.assertEqual(ingest.detect_lang("يجب على جميع الموظفين الالتزام بسياسة المصروفات المعتمدة"), "ar-MSA")

    def test_merge_batch(self):
        self.run_ingest(SOP_MD, POLICIES)
        batch = yaml.safe_load((SKILL / "templates/facts_batch.example.yaml").read_text())
        d = merge_facts.apply_batch(self.load(), batch)
        s01 = [f for f in d["facts"] if f["source_id"] == "S01"]
        self.assertFalse(any("auto-candidate" in f.get("tags", []) for f in s01))
        self.assertFalse(d["sources"][0]["chunks"][0]["summary"].startswith("[auto]"))
        self.assertTrue(any(g["term"] == "Per diem" for g in d["glossary"]))
        self.assertTrue(d.get("conflicts"), "conflict re-detected against LLM fact")
        errs, warns = validate_sources.lint(d, self.tmp)
        self.assertEqual(errs, [])


if __name__ == "__main__":
    unittest.main()
