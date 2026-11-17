#!/usr/bin/env python3
"""Render a simple Markdown file to a paginated PDF (test fixtures, golden-run sources).

Usage: md_to_pdf.py <in.md> <out.pdf> [--title T]
Supports #/##/### headings, -/1. lists, **bold**, paragraphs. Uses PyMuPDF Story (no network, no fonts needed).
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

import pymupdf


def md_to_html(md: str) -> str:
    out, in_ul, in_ol = [], False, False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def inline(t: str) -> str:
        t = html.escape(t)
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)

    for line in md.splitlines():
        s = line.strip()
        if not s:
            close_lists()
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            close_lists()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue
        m = re.match(r"^[-*]\s+(.*)$", s)
        if m:
            if not in_ul:
                close_lists()
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        m = re.match(r"^\d+[.)]\s+(.*)$", s)
        if m:
            if not in_ol:
                close_lists()
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        close_lists()
        out.append(f"<p>{inline(s)}</p>")
    close_lists()
    return "\n".join(out)


CSS = "body{font-family:sans-serif;font-size:11pt;} h1{font-size:18pt;} h2{font-size:14pt;margin-top:10pt;} li{margin-bottom:3pt;}"


def render(md_path: Path, pdf_path: Path, title: str | None = None) -> Path:
    body = md_to_html(md_path.read_text(encoding="utf-8"))
    story = pymupdf.Story(html=body, user_css=CSS)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    writer = pymupdf.DocumentWriter(str(pdf_path))
    mediabox = pymupdf.paper_rect("a4")
    where = mediabox + (54, 54, -54, -54)
    more = True
    while more:
        dev = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
    writer.close()
    doc = pymupdf.open(str(pdf_path))
    first = md_path.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
    doc.set_metadata({"title": title or first, "author": "Northwind Co. (fictional)"})
    doc.saveIncr()
    doc.close()
    return pdf_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("pdf")
    ap.add_argument("--title")
    a = ap.parse_args()
    print(render(Path(a.md), Path(a.pdf), a.title))
