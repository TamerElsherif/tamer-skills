#!/usr/bin/env python3
"""Render a printable job aid (PDF, 1–2 pages, A4 or Letter, RTL-aware) from a storyboard or a jobaid.yaml.

Usage:
  .venv/bin/python skills/tcs-render-lesson/scripts/jobaid.py <storyboard.json | jobaid.yaml | run dir> [--out <pdf|dir>]
        [--paper A4|Letter] [--pages 1|2] [--lesson M1L1] [--lang ar-EG] [--no-strict]

From a storyboard, blocks are taken from scenes of type checklist, steps, do_dont, table (+ bullets, definition,
comparison, icon_grid, statement); the title scene is the header, the outro is the footer. jobaid.yaml shape:
references/jobaid-yaml.md (schema: templates/jobaid.schema.json). HTML → PDF via headless Chrome; without Chrome the
HTML is kept and RENDER_PENDING.md explains the command. Writes <name>.pdf, <name>.html, <name>.png (page-1 preview).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import icons  # noqa: E402
from _common import (GOOGLE_FONTS, TEMPLATES, chrome, css_vars, esc, find_chrome, html_lang, is_rtl,  # noqa: E402
                     lesson_inputs, load_data, render_pending, theme, ui, validate)

BLOCK_TEMPLATES = ("checklist", "steps", "do_dont", "table", "bullets", "definition", "comparison", "icon_grid", "statement")


def from_storyboard(doc: dict) -> dict:
    ja = {"title": doc["title"], "language": doc["language"], "direction": doc.get("direction"), "theme": doc.get("theme"),
          "blocks": [], "footer": (doc.get("theme") or {}).get("evidence_line")}
    for s in doc["scenes"]:
        p = s.get("props") or {}
        if s["template"] == "title":
            ja["title"] = p.get("title") or ja["title"]
            ja["kicker"], ja["subtitle"] = p.get("kicker"), p.get("sub")
        elif s["template"] == "outro":
            ja["blocks"].append({"type": "note", "title": p.get("title"), "text": p.get("line"), "items": p.get("tips", [])})
            ja["footer"] = p.get("evidence_line") or ja["footer"]
        elif s["template"] in BLOCK_TEMPLATES:
            ja["blocks"].append({"type": s["template"], **p})
    return ja


def block_html(b: dict, t: dict) -> str:
    typ = b["type"]
    h = f'<h2>{esc(b["title"])}</h2>' if b.get("title") else ""
    if typ == "checklist":
        body = "<ul class='ck'>" + "".join(f"<li><span class='box'></span>{esc(x)}</li>" for x in b.get("items", [])) + "</ul>"
    elif typ == "steps":
        body = f"<ol class='st{' danger' if b.get('danger') else ''}'>" + "".join(
            f"<li><span class='n'>{i}</span><span><b>{esc(x['label'])}</b>{('<br><small>' + esc(x['sub']) + '</small>') if x.get('sub') else ''}</span></li>"
            for i, x in enumerate(b.get("steps", []), 1)) + "</ol>"
    elif typ == "do_dont":
        col = lambda head, items, cls, ic: (f"<div class='{cls}'><h3>{icons.svg(ic, 16)} {esc(head)}</h3><ul>" +
                                            "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul></div>")
        body = "<div class='dd'>" + col(b.get("dont_head") or t["dont"], b.get("dont", []), "dont", "x-circle") + \
               col(b.get("do_head") or t["do"], b.get("do", []), "do", "check-circle") + "</div>"
    elif typ == "comparison":
        col = lambda c: f"<div><h3>{esc(c['head'])}</h3><ul>" + "".join(f"<li>{esc(x)}</li>" for x in c.get("items", [])) + "</ul></div>"
        body = "<div class='dd cmp'>" + col(b["left"]) + col(b["right"]) + "</div>"
    elif typ == "table":
        body = ("<table><thead><tr>" + "".join(f"<th>{esc(c)}</th>" for c in b.get("columns", [])) + "</tr></thead><tbody>" +
                "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in b.get("rows", [])) + "</tbody></table>")
    elif typ in ("bullets", "icon_grid"):
        body = "<ul class='bl'>" + "".join(
            f"<li>{icons.svg(x.get('icon') or 'dot', 14)}<span><b>{esc(x.get('text') or x.get('label'))}</b>"
            f"{(' — ' + esc(x['sub'])) if x.get('sub') else ''}</span></li>" for x in b.get("items", [])) + "</ul>"
    elif typ == "definition":
        h = f"<h2>{esc(b['term'])}</h2>"
        body = f"<p>{esc(b['def'])}</p>" + (f"<p class='mut'>{esc(b['note'])}</p>" if b.get("note") else "")
    else:  # statement / note
        body = (f"<p class='big'>{esc(b.get('text', ''))}</p>" +
                ("<ul class='bl'>" + "".join(f"<li>{icons.svg('check', 14)}<span>{esc(x)}</span></li>" for x in b.get("items", [])) + "</ul>"
                 if b.get("items") else ""))
    wide = " wide" if typ in ("table",) and len(b.get("columns", [])) > 2 else ""
    return f"<section class='blk t-{typ}{wide}'>{h}{body}</section>"


def page_html(ja: dict, paper: str, scale: float) -> str:
    rtl = is_rtl(ja)
    t = ui(ja)
    th = theme(ja)
    size = "A4" if paper.upper() == "A4" else "Letter"
    css = (TEMPLATES / "jobaid.css").read_text(encoding="utf-8")
    kick = f"<p class='kick'>{esc(ja['kicker'])}</p>" if ja.get("kicker") else ""
    sub = f"<p class='sub'>{esc(ja['subtitle'])}</p>" if ja.get("subtitle") else ""
    foot = f"<footer>{esc(ja['footer'])}</footer>" if ja.get("footer") else ""
    blocks = "".join(block_html(b, t) for b in ja.get("blocks", []))
    return f"""<!doctype html><html lang="{html_lang(ja.get('language', 'en-US'))}" dir="{'rtl' if rtl else 'ltr'}"><head><meta charset="utf-8">
<title>{esc(ja['title'])}</title><link rel="stylesheet" href="{GOOGLE_FONTS}">
<style>{css_vars(th, rtl)} @page{{size:{size};margin:11mm}} :root{{--scale:{scale}}} {css}</style></head>
<body><header class="hd">{kick}<h1>{esc(ja['title'])}</h1>{sub}</header><main class="cols">{blocks}</main>{foot}</body></html>"""


def render(ja: dict, out_pdf: Path, paper: str, max_pages: int) -> Path:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    html_p = out_pdf.with_suffix(".html")
    if not find_chrome():
        html_p.write_text(page_html(ja, paper, 1.0), encoding="utf-8")
        render_pending(out_pdf.parent, "Google Chrome / Chromium not found (needed for HTML → PDF)",
                       [f'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer '
                        f'--print-to-pdf="{out_pdf}" "{html_p.resolve().as_uri()}"',
                        "or open the .html in any browser and Print → Save as PDF (A4/Letter, no headers/footers)"])
        return html_p
    import pymupdf
    pages = 0
    for scale in (1.0, 0.92, 0.85, 0.78, 0.72, 0.66):
        html_p.write_text(page_html(ja, paper, scale), encoding="utf-8")
        if out_pdf.exists():
            out_pdf.unlink()
        chrome(["--no-pdf-header-footer", "--virtual-time-budget=5000", f"--print-to-pdf={out_pdf}", html_p.resolve().as_uri()])
        if not out_pdf.exists():
            render_pending(out_pdf.parent, "Chrome ran but produced no PDF", [f"open {html_p} and print to PDF"])
            return html_p
        with pymupdf.open(out_pdf) as d:
            pages = d.page_count
            if pages <= max_pages or scale == 0.66:
                d[0].get_pixmap(dpi=80).save(str(out_pdf.with_suffix(".png")))
                break
    if (out_pdf.parent / "RENDER_PENDING.md").exists():
        (out_pdf.parent / "RENDER_PENDING.md").unlink()
    print(f"jobaid: {out_pdf}  pages={pages} paper={paper} scale={scale}" + ("  WARNING: over page budget" if pages > max_pages else ""))
    return out_pdf


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, help=".pdf path or folder (default: runs/<id>/renders/<L>/jobaid/)")
    ap.add_argument("--paper", choices=["A4", "Letter"])
    ap.add_argument("--pages", type=int, choices=[1, 2])
    ap.add_argument("--lesson")
    ap.add_argument("--lang")
    ap.add_argument("--no-strict", action="store_true")
    a = ap.parse_args()
    jobs = []
    if a.input.is_file() and a.input.suffix.lower() in (".yaml", ".yml"):
        ja = load_data(a.input)
        errs = validate(ja, "jobaid", a.input.name, TEMPLATES / "jobaid.schema.json")
        if errs and not a.no_strict:
            sys.exit("\n".join(errs))
        jobs.append((ja, a.input.stem, None))
    else:
        for it in lesson_inputs(a.input, a.lesson, a.lang):
            sb = it["storyboard"]
            alt = sb.with_name(f"{it['lesson_id']}-jobaid.storyboard.json")
            if a.input.is_dir() and alt.exists():
                sb = alt
            doc = load_data(sb)
            errs = validate(doc, "storyboard", sb.name)
            if errs and not a.no_strict:
                sys.exit("\n".join(errs[:20]))
            ja = from_storyboard(doc)
            if not ja["blocks"]:
                print(f"skip {sb.name}: no checklist/steps/do_dont/table scenes")
                continue
            out_dir = (Path(it["run_dir"]) / "renders" / it["lesson_id"] / "jobaid") if it.get("run_dir") else None
            jobs.append((ja, doc["lesson_id"], out_dir))
    for ja, name, out_dir in jobs:
        if a.out and a.out.suffix.lower() == ".pdf" and len(jobs) == 1:
            pdf = a.out
        elif a.out:
            pdf = a.out / f"{name}.pdf"
        elif out_dir:
            pdf = out_dir / f"{name}.pdf"
        else:
            sys.exit("--out is required outside a run folder")
        paper = a.paper or ja.get("paper") or "A4"
        render(ja, pdf, paper, a.pages or int(ja.get("pages") or 1))


if __name__ == "__main__":
    main()
