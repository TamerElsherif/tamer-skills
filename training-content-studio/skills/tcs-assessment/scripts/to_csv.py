#!/usr/bin/env python3
"""Export quiz.json to a flat CSV for LMS/spreadsheet import (UTF-8 with BOM so Excel shows Arabic).

Usage: to_csv.py <quiz.json> [--out quiz.csv] [--lang ar]
Columns: id,type,objective_id,bloom,difficulty,points,scenario,stem,option_a..option_f,correct (letters, ';'-joined),
         feedback_a..feedback_f,back,explanation,source_ids,general_knowledge
Ordering: correct = letters in the right order; matching: option_x = "text => match".
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

LET = "abcdef"


def rows(q: dict, ar: bool = False) -> list[dict]:
    out = []
    for it in q["items"]:
        opts = it.get("options", [])[:6]
        r = {"id": it["id"], "type": it["type"], "objective_id": it["objective_id"], "bloom": it.get("bloom", ""),
             "difficulty": it.get("difficulty", ""), "points": it.get("points", 1), "scenario": it.get("scenario", ""),
             "stem": it.get("stem_ar") if ar and it.get("stem_ar") else it["stem"], "back": it.get("back", ""),
             "explanation": it.get("explanation", ""), "source_ids": ";".join(it.get("source_ids", [])),
             "general_knowledge": "yes" if it.get("general_knowledge") else ""}
        for i, L in enumerate(LET):
            o = opts[i] if i < len(opts) else None
            text = (o.get("text_ar") if ar and o and o.get("text_ar") else (o or {}).get("text", ""))
            if o and it["type"] == "matching":
                text = f"{text} => {o.get('match', '')}"
            r[f"option_{L}"] = text
            r[f"feedback_{L}"] = (o or {}).get("feedback", "")
        if it["type"] == "ordering":
            r["correct"] = ";".join(LET[i] for i, _ in sorted(enumerate(opts), key=lambda x: x[1].get("order", 0)))
        else:
            r["correct"] = ";".join(LET[i] for i, o in enumerate(opts) if o.get("correct"))
        out.append(r)
    return out


FIELDS = (["id", "type", "objective_id", "bloom", "difficulty", "points", "scenario", "stem"]
          + [f"option_{L}" for L in LET] + ["correct"] + [f"feedback_{L}" for L in LET]
          + ["back", "explanation", "source_ids", "general_knowledge"])


def to_csv(q: dict, ar: bool = False) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows(q, ar))
    return buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("quiz")
    ap.add_argument("--out")
    ap.add_argument("--lang", choices=["src", "ar"], default="src")
    a = ap.parse_args(argv)
    q = json.loads(Path(a.quiz).read_text(encoding="utf-8"))
    out = Path(a.out) if a.out else Path(a.quiz).with_suffix(".csv")
    out.write_text(to_csv(q, a.lang == "ar"), encoding="utf-8-sig")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
