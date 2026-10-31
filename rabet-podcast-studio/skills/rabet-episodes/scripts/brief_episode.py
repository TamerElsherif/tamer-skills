"""Brief (.docx) for a rendered mini / sub-episode, from its spec + <spec>.render.json: main idea, storyline,
audience, editing notes, cut list (episode time, source time, join, who, first/last words, what happens), YouTube
chapters, CTA times, B-roll ideas for the next pass and a suggested Arabic description.

usage: python brief_episode.py <spec.json>   -> <out_dir>/<prefix with _>_Brief.docx
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from ep import dur, jload, load_spec, mmss, render_meta_path


def rtl(p):
    p._p.get_or_add_pPr().append(OxmlElement("w:bidi"))
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in p.runs:
        r._r.get_or_add_rPr().append(OxmlElement("w:rtl"))
    return p


def run_font(r, size, bold=False):
    r.bold, r.font.size, r.font.name = bold, Pt(size), "Arial"
    r._r.get_or_add_rPr().get_or_add_rFonts().set(qn("w:cs"), "Arial")
    r.font.size_cs = Pt(size)


def ar(doc, text, size=12, bold=False):
    p = doc.add_paragraph()
    run_font(p.add_run(text), size, bold)
    return rtl(p)


def heading(doc, text, level):
    h = doc.add_heading(text, level)
    for r in h.runs:
        r.font.color.rgb = RGBColor(0x10, 0x33, 0x5A)


def table(doc, head, rows, arabic_cols=()):
    t = doc.add_table(rows=1, cols=len(head))
    t.style = "Light Grid Accent 1"
    for i, row in enumerate([head] + rows):
        cells = t.rows[0].cells if i == 0 else t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = ""
            p = cells[j].paragraphs[0]
            run_font(p.add_run(str(v)), 9.5, bold=i == 0)
            if i and j in arabic_cols:
                rtl(p)


def main():
    spec = load_spec(sys.argv[1])
    meta = jload(render_meta_path(spec))
    b = spec.get("brief", {})
    off = spec["_episode"].get("teaser_offset", 0)
    pieces = spec.get("hook", []) + spec["body"]
    rows, first, t, k, logos = [], {}, 0.0, 0, iter(("intro logo", "outro logo"))
    for (kind, x, join), L in zip(meta["segments"], meta["alen"]):
        if kind == "logo":
            rows.append(["", mmss(t), dur(L), "", "", next(logos), "", ""])
        else:
            p = pieces[k]
            sec = p.get("sec", "hook")
            first.setdefault(sec, t)
            rows.append([sec, mmss(t), dur(L), f"{mmss(p['in'])} – {mmss(p['out'])}", join, p.get("who", ""),
                         f"«{p.get('first', '')}…» / «…{p.get('last', '')}»", p.get("what", "")])
            k += 1
        t += L
    doc = Document()
    s = doc.sections[0]
    s.orientation, s.page_width, s.page_height = WD_ORIENT.LANDSCAPE, s.page_height, s.page_width
    s.left_margin = s.right_margin = Cm(1.8)
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    if b.get("kicker"):
        ar(doc, b["kicker"], 10)
    ar(doc, spec["title"], 20, bold=True)
    heading(doc, b.get("headline_en", spec["prefix"]), 1)
    n_cta = len(meta.get("cta", []))
    doc.add_paragraph(
        f"File: {meta['file']}\nLength {dur(meta['total'])} ({'cold open, ' if spec.get('hook') else ''}intro logo, "
        f"{len(spec['body'])} pieces from the episode, outro logo). Speakers: {b.get('speakers', '')}. No captions. "
        + (f"Follow & subscribe pop-up at {', '.join(mmss(x) for x in meta['cta'])}." if n_cta else
           "No follow & subscribe pop-up."))
    for key, title in (("main_idea", "Main idea"), ("audience", "Target audience")):
        if b.get(key):
            heading(doc, title, 2)
            doc.add_paragraph(b[key])
    if b.get("storyline"):
        heading(doc, "Storyline", 2)
        for line in b["storyline"]:
            doc.add_paragraph(line, style="List Number")
    heading(doc, "Editing", 2)
    for line in ["Swipe (0.4 s slide + soft whoosh) where a piece comes from a different place in the episode.",
                 f"Jump cuts inside the same conversation; where both sides keep the same framing the incoming piece "
                 f"punches in {spec.get('punch_in', 1.12)}× until the next camera change (the next jump zooms back "
                 "out), so the jump reads as deliberate.",
                 "Every edge sits in a pause, checked by transcribing both sides on their own, and every join was "
                 "transcribed again after rendering."] + b.get("editing_notes", []):
        doc.add_paragraph(line, style="List Bullet")
    heading(doc, "Cut list", 2)
    doc.add_paragraph("Episode time = where the piece starts in this video; source time = in the full-episode master"
                      + (f" (add {off:g} s for the uploaded version with the teaser)." if off else "."))
    table(doc, ["Section", "Episode", "Length", "Source in – out", "Join", "Who", "Starts / ends with", "What happens"],
          rows, arabic_cols=(6,))
    if b.get("chapters"):
        heading(doc, "YouTube chapters", 2)
        for sec, name in b["chapters"].items():
            if sec in first:
                ar(doc, f"{dur(first[sec])} {name}", 11)
    if b.get("broll"):
        heading(doc, "B-roll explainers for the next pass", 2)
        table(doc, ["Section", "Idea"], b["broll"])
    if b.get("description_ar"):
        heading(doc, "Suggested description (Arabic)", 2)
        ar(doc, b["description_ar"])
    path = Path(meta["out_dir"]) / f"{spec['prefix'].replace(' ', '_')}_Brief.docx"
    doc.save(path)
    print("wrote", path)


if __name__ == "__main__":
    main()
