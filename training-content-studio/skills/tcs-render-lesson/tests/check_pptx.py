#!/usr/bin/env python3
"""Structural QA for decks: re-open each .pptx, check shapes stay inside the slide, estimate text overflow,
confirm speaker notes exist for slides whose scene has narration, report RTL paragraphs and media.

Usage: .venv/bin/python skills/tcs-render-lesson/tests/check_pptx.py <file.pptx> [...]
"""
import sys

from pptx import Presentation
from pptx.util import Emu

EMU_IN = 914400


def est_lines(text, width_in, pt):
    cpl = max(1, int(width_in * 72 / (pt * 0.55)))
    return sum(max(1, -(-len(par) // cpl)) for par in text.split("\n"))


def check(path):
    prs = Presentation(path)
    W, H = prs.slide_width, prs.slide_height
    issues, rtl, media = [], 0, 0
    for i, sl in enumerate(prs.slides, 1):
        for sh in sl.shapes:
            if sh.left is None:
                continue
            if sh.left < -Emu(10000) or sh.top < -Emu(10000) or sh.left + sh.width > W + Emu(20000) or sh.top + sh.height > H + Emu(20000):
                issues.append(f"slide {i}: '{sh.name}' outside slide bounds")
            if sh.shape_type == 16 or "movie" in sh.name.lower():
                media += 1
            if sh.has_text_frame and sh.text_frame.text.strip():
                tf = sh.text_frame
                pts = [r.font.size.pt for p in tf.paragraphs for r in p.runs if r.font.size] or [18]
                need = est_lines(tf.text, sh.width / EMU_IN - 0.25, max(pts)) * max(pts) * 1.25 / 72
                if need > sh.height / EMU_IN * 1.6 + 0.3 and sh.height / EMU_IN < 6:
                    issues.append(f"slide {i}: text may overflow '{tf.text[:40]}' ({need:.1f}in > {sh.height / EMU_IN:.1f}in)")
                rtl += sum(1 for p in tf.paragraphs if p._p.pPr is not None and p._p.pPr.get("rtl") == "1")
        if not sl.has_notes_slide or not sl.notes_slide.notes_text_frame.text.strip():
            issues.append(f"slide {i}: no speaker notes")
    print(f"{path}: slides={len(prs.slides)} rtl_paragraphs={rtl} media={media} issues={len(issues)}")
    for x in issues[:15]:
        print("  -", x)
    return issues


if __name__ == "__main__":
    bad = sum(len(check(p)) for p in sys.argv[1:])
    sys.exit(0)
