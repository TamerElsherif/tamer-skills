#!/usr/bin/env python3
"""Lint a localized storyboard (Arabic RTL or AR→EN) against RTL, bidi, register and cue rules.

Usage: rtl_lint.py <L>.ar-EG.storyboard.json [--source <L>.storyboard.json] [--json]
Errors: leftover «TR» markers; ar-* without direction rtl; narration not in Arabic; `^` count per scene differs from source;
        scene ids differ from source; voices without the target language.
Warnings: mixed Western/Eastern digits; Latin ?,; in Arabic text; Latin runs (URL/e-mail/code) inside Arabic strings
        without bidi isolation; → arrows in RTL text; register drift (ar-EG reads MSA or vice versa); no Arabic font.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "tcs-storyboard" / "scripts"))
import sbtools as T  # noqa: E402

AR = re.compile(r"[؀-ۿ]")
EG_MARKERS = re.compile(r"(?:^|\s|[،.؟])(?:ده|دي|دول|عشان|إزاي|ازاي|مش|كده|بتاع|إيه|ليه|دلوقتي|هن\w+|بت\w+|متع\w+ش|يلا|خلّي\w*|خلي\w*)(?=\s|$|[،.؟!])")
MSA_MARKERS = re.compile(r"(?:^|\s)(?:هذا|هذه|هؤلاء|لماذا|كيف|ماذا|سوف|لكي|ليس|لن|الآن|إذا|يجب)(?=\s|$|[،.؟!])")
ISOLATES = "⁦⁧⁨⁩‎‏"


def lint(sb: dict, src: dict | None = None) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    lang = sb["language"]
    ar = lang.startswith("ar")
    if ar and sb.get("direction") != "rtl":
        errs.append("direction must be rtl for Arabic")
    if not ar and sb.get("direction") == "rtl":
        errs.append("direction rtl on a non-Arabic storyboard")
    if ar and not (sb.get("theme", {}).get("fonts") or {}).get("arabic"):
        warns.append("theme.fonts.arabic not set (Cairo / IBM Plex Sans Arabic / Noto Kufi Arabic)")
    for k, v in sb["voices"].items():
        if v.get("lang") and v["lang"] != lang:
            errs.append(f"voices.{k}.lang {v['lang']} ≠ {lang}")
        ins = v.get("instructions", "")
        if ar and not re.search(r"arabic|عرب", ins, re.I):
            warns.append(f"voices.{k}.instructions do not mention Arabic/dialect")
    blob = json.dumps(sb, ensure_ascii=False)
    n_tr = blob.count("«TR»")
    if n_tr:
        errs.append(f"{n_tr} untranslated «TR» strings left")
    west = east = 0
    narr_all = []
    for sc in sb["scenes"]:
        sid = sc["id"]
        for n in sc["narration"]:
            narr_all.append(n["text"])
            if ar and not AR.search(n["text"]):
                errs.append(f"{sid}: narration line not Arabic: {n['text'][:50]}")
            if not ar and AR.search(n["text"]):
                errs.append(f"{sid}: Arabic left in {lang} narration")
        texts = sc.get("on_screen_text") or T.derive_on_screen_text(sc)
        for s in texts:
            west += len(re.findall(r"[0-9]", s))
            east += len(re.findall(r"[٠-٩]", s))
            if not ar or not AR.search(s):
                continue
            if re.search(r"[?;]|(?<=[؀-ۿ]),", s):
                warns.append(f"{sid}: Latin punctuation in Arabic text (use ؟ ، ؛): {s[:40]}")
            if re.search(r"(https?://|www\.|[\w.+-]+@[\w-]+\.|\w+\.\w+/|`)", s) and not any(c in s for c in ISOLATES):
                warns.append(f"{sid}: URL/e-mail/code inside Arabic text — isolate with U+2068…U+2069 or put it on its own line: {s[:40]}")
            if "→" in s or "->" in s:
                warns.append(f"{sid}: '→' in RTL text points backwards — use '←'")
    if west and east:
        warns.append(f"mixed digits on screen ({west} Western, {east} Eastern Arabic) — pick one")
    if ar:
        joined = " ".join(narr_all)
        eg, msa = len(EG_MARKERS.findall(joined)), len(MSA_MARKERS.findall(joined))
        words = max(1, len(joined.split()))
        if lang == "ar-EG" and eg == 0 and words > 30:
            warns.append("ar-EG narration has no Egyptian markers (ده/مش/عشان/إزاي…) — reads like MSA")
        if lang == "ar-MSA" and eg > max(2, msa):
            warns.append(f"ar-MSA narration has {eg} Egyptian colloquial markers")
    if src:
        sids = [s["id"] for s in src["scenes"]]
        if sids != [s["id"] for s in sb["scenes"]]:
            errs.append("scene ids/order differ from source storyboard")
        smap = {s["id"]: T.count_cues(s) for s in src["scenes"]}
        for sc in sb["scenes"]:
            if sc["id"] in smap and T.count_cues(sc) != smap[sc["id"]]:
                errs.append(f"{sc['id']}: {T.count_cues(sc)} '^' cues vs {smap[sc['id']]} in source (visual sync breaks)")
    return errs, warns


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard")
    ap.add_argument("--source")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    sb = json.loads(Path(a.storyboard).read_text(encoding="utf-8"))
    src = json.loads(Path(a.source).read_text(encoding="utf-8")) if a.source else None
    errs, warns = lint(sb, src)
    if a.json:
        print(json.dumps({"errors": errs, "warnings": warns}, ensure_ascii=False, indent=1))
    else:
        for e in errs:
            print("ERROR", e)
        for w in warns:
            print("WARN ", w)
        print(f"{'FAIL' if errs else 'OK'}: {len(errs)} errors, {len(warns)} warnings")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
