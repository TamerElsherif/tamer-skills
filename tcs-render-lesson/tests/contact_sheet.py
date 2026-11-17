#!/usr/bin/env python3
"""QA helper: tile PNGs into contact sheets (2 columns) using PyMuPDF.

Usage: .venv/bin/python skills/tcs-render-lesson/tests/contact_sheet.py <png dir> --out sheet.png [--per 4] [--cols 2]
Writes sheet-1.png, sheet-2.png ... when there are more than --per images.
"""
import argparse
from pathlib import Path

import pymupdf as fitz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--per", type=int, default=4)
    ap.add_argument("--cols", type=int, default=2)
    a = ap.parse_args()
    pngs = sorted(p for p in a.dir.glob("*.png"))
    pngs.sort(key=lambda p: p.stat().st_mtime)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    W, cw = 1600, 1600 // a.cols
    for k in range(0, len(pngs), a.per):
        chunk = pngs[k:k + a.per]
        rows = (len(chunk) + a.cols - 1) // a.cols
        ch = None
        doc = fitz.open()
        imgs = [fitz.Pixmap(str(p)) for p in chunk]
        ch = max(int(cw * im.height / im.width) for im in imgs) + 24
        page = doc.new_page(width=W, height=rows * ch)
        for i, (p, im) in enumerate(zip(chunk, imgs)):
            x, y = (i % a.cols) * cw, (i // a.cols) * ch
            page.insert_text((x + 6, y + 16), p.stem, fontsize=14)
            page.insert_image(fitz.Rect(x + 4, y + 20, x + cw - 4, y + ch - 4), filename=str(p), keep_proportion=True)
        out = a.out.with_name(f"{a.out.stem}-{k // a.per + 1}.png")
        page.get_pixmap(dpi=72).save(str(out))
        print(out)


if __name__ == "__main__":
    main()
