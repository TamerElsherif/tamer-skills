#!/usr/bin/env python3
"""Render a storyboard.json into a narrated deck: <lesson>.pptx (python-pptx, editable native shapes, speaker
notes = narration, RTL for Arabic, 16:9 / 9:16 / 1:1) and deck.html (keyboard slides + notes view).

Usage:
  .venv/bin/python skills/tcs-render-lesson/scripts/deck.py <storyboard.json> --out <dir> [--audio <dir>]
        [--quiz quiz.json] [--no-strict] [--no-html]

Audio: if <audio dir>/<scene_id>.mp3|m4a|wav exists it is embedded on that slide (PowerPoint plays it on click).
For a narrated MP4 use the video render skills (tcs-render-remotion / tcs-render-openmontage) instead.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402

from _common import (GOOGLE_FONTS, TEMPLATES, css_vars, default_out, display_name, esc, find_scene_audio,  # noqa: E402
                     html_lang, is_rtl, lesson_inputs, line_text, load_validated, theme, ui)
from figures import palette  # noqa: E402
from render_html import Ctx, flow_layers, mindmap_layout, scene_body  # noqa: E402

SIZES = {"16:9": (13.333, 7.5), "9:16": (7.5, 13.333), "1:1": (7.5, 7.5)}


def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class Deck:
    def __init__(self, doc, base: Path, audio_dir: Path | None, quiz: dict | None):
        self.doc, self.base, self.audio_dir = doc, base, audio_dir
        self.rtl = is_rtl(doc)
        self.th = theme(doc)
        self.c = {k: rgb(v) for k, v in self.th["colors"].items()}
        self.t = ui(doc)
        self.items = {i["id"]: i for i in (quiz or {}).get("items", [])}
        self.prs = Presentation()
        w, h = SIZES[doc.get("aspect", "16:9")]
        self.prs.slide_width, self.prs.slide_height = Inches(w), Inches(h)
        self.W, self.H = w, h
        self.portrait = h > w
        self.font = self.th["fonts"]["arabic"] if self.rtl else self.th["fonts"]["body"]
        self.hfont = self.th["fonts"]["arabic"] if self.rtl else self.th["fonts"]["latin"]
        self.lang = doc["language"]
        self.m = 0.6  # margin inches
        self.embedded_audio = 0

    # ------------------------------------------------------------- primitives
    def para_fmt(self, p, size, bold=False, color=None, align=None, font=None):
        p.alignment = align if align is not None else (PP_ALIGN.RIGHT if self.rtl else PP_ALIGN.LEFT)
        if self.rtl:
            p._p.get_or_add_pPr().set("rtl", "1")
        for r in p.runs:
            f = r.font
            f.size, f.bold = Pt(size), bold
            f.name = font or self.font
            f.color.rgb = color or self.c["ink"]
            rPr = r._r.get_or_add_rPr()
            rPr.set("lang", self.lang)
            if self.rtl:
                cs = rPr.find(qn("a:cs"))
                if cs is None:
                    cs = rPr.makeelement(qn("a:cs"), {})
                    rPr.append(cs)
                cs.set("typeface", font or self.font)

    def text(self, slide, x, y, w, h, lines, size=18, bold=False, color=None, align=None, font=None,
             anchor=MSO_ANCHOR.TOP, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, bullets=None, autofit=True):
        """lines: str or list of str | (str, dict(size,bold,color)). Returns shape."""
        if fill is not None or line is not None or shape != MSO_SHAPE.RECTANGLE:
            sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
            if fill is not None:
                sh.fill.solid()
                sh.fill.fore_color.rgb = fill
            else:
                sh.fill.background()
            if line is not None:
                sh.line.color.rgb = line
                sh.line.width = Pt(1.5)
            else:
                sh.line.fill.background()
            sh.shadow.inherit = False
        else:
            sh = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = sh.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        for attr in ("margin_left", "margin_right"):
            setattr(tf, attr, Inches(0.12))
        if isinstance(lines, str):
            lines = [lines]
        for i, ln in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            opts = {}
            if isinstance(ln, tuple):
                ln, opts = ln
            prefix = (bullets + " ") if bullets else ""
            p.text = prefix + (ln or "")
            p.space_after = Pt(6)
            self.para_fmt(p, opts.get("size", size), opts.get("bold", bold), opts.get("color", color),
                          opts.get("align", align), opts.get("font", font))
        return sh

    def box(self, slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
        sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
        if line is None:
            sh.line.fill.background()
        else:
            sh.line.color.rgb = line
            sh.line.width = Pt(1.5)
        sh.shadow.inherit = False
        return sh

    def connect(self, slide, x1, y1, x2, y2, color=None, width=2):
        c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        c.line.color.rgb = color or self.c["muted"]
        c.line.width = Pt(width)
        return c

    def X(self, x, w):
        """Mirror horizontal placement for RTL slides."""
        return self.W - x - w if self.rtl else x

    def title(self, slide, s, y=None, size=None):
        if not s:
            return self.m
        y = self.m if y is None else y
        self.text(slide, self.m, y, self.W - 2 * self.m, 1.0, s, size=size or (30 if not self.portrait else 28),
                  bold=True, font=self.hfont, color=self.c["navy"], anchor=MSO_ANCHOR.BOTTOM)
        return y + 1.15

    def kicker(self, slide, k, y):
        if k:
            self.text(slide, self.m, y - 0.35, self.W - 2 * self.m, 0.4, k.upper() if not self.rtl else k, size=13,
                      bold=True, color=self.c["blue"])

    def bg(self, slide, color):
        f = slide.background.fill
        f.solid()
        f.fore_color.rgb = color

    def cols(self, n, y, h, gap=0.3):
        """Return n column rects (x, y, w, h) across the content width; stacked rows in portrait."""
        cw = self.W - 2 * self.m
        if self.portrait and n == 2:
            rh = (h - gap) / 2
            rects = [(self.m, y + i * (rh + gap), cw, rh) for i in range(n)]
        else:
            w = (cw - gap * (n - 1)) / n
            rects = [(self.m + i * (w + gap), y, w, h) for i in range(n)]
        if self.rtl and not (self.portrait and n == 2):
            rects = [(self.W - x - w, yy, w, hh) for (x, yy, w, hh) in rects]
        return rects

    # ------------------------------------------------------------- templates
    def s_hero(self, sl, p, s):
        tpl = s["template"]
        cx, w = self.m, self.W - 2 * self.m
        if tpl in ("title", "section"):
            self.bg(sl, self.c["navy"])
            band = self.box(sl, 0, self.H - 0.25, self.W, 0.25, self.c["cyan"], shape=MSO_SHAPE.RECTANGLE)
            lines = []
            if p.get("kicker"):
                lines.append((p["kicker"], {"size": 16, "bold": True, "color": self.c["cyan"], "align": PP_ALIGN.CENTER}))
            if p.get("n") not in (None, ""):
                lines.append((str(p["n"]), {"size": 54, "bold": True, "color": self.c["cyan"], "align": PP_ALIGN.CENTER, "font": self.hfont}))
            lines.append((p["title"], {"size": 44 if tpl == "title" else 38, "bold": True, "color": RGBColor(255, 255, 255), "align": PP_ALIGN.CENTER, "font": self.hfont}))
            if p.get("sub"):
                lines.append((p["sub"], {"size": 20, "color": RGBColor(0xDD, 0xE6, 0xF5), "align": PP_ALIGN.CENTER}))
            if p.get("part"):
                lines.append((p["part"], {"size": 16, "color": self.c["cyan"], "align": PP_ALIGN.CENTER}))
            self.text(sl, cx, self.H * 0.18, w, self.H * 0.64, lines, anchor=MSO_ANCHOR.MIDDLE)
            return band
        if tpl == "stat":
            v = p.get("value", 0)
            num = f'{p.get("prefix", "")}{v:,}{p.get("suffix", "")}' if float(v).is_integer() else f'{p.get("prefix", "")}{v}{p.get("suffix", "")}'
            lines = [(num, {"size": 88, "bold": True, "color": self.c["blue"], "align": PP_ALIGN.CENTER, "font": self.hfont}),
                     (p["label"], {"size": 28, "bold": True, "color": self.c["navy"], "align": PP_ALIGN.CENTER, "font": self.hfont})]
            if p.get("source"):
                lines.append((p["source"], {"size": 14, "color": self.c["muted"], "align": PP_ALIGN.CENTER}))
        elif tpl == "definition":
            lines = [(p["term"], {"size": 40, "bold": True, "color": self.c["blue"], "font": self.hfont}), (p["def"], {"size": 24})]
            if p.get("note"):
                lines.append((p["note"], {"size": 16, "color": self.c["muted"]}))
            self.box(sl, cx, self.H * 0.22, w, self.H * 0.56, self.c["bg"])
            self.text(sl, cx + 0.3, self.H * 0.22, w - 0.6, self.H * 0.56, lines, anchor=MSO_ANCHOR.MIDDLE)
            return
        elif tpl == "statement":
            lines = [(p["text"], {"size": 36, "bold": True, "color": self.c["navy"], "align": PP_ALIGN.CENTER, "font": self.hfont})]
            if p.get("sub"):
                lines.append((p["sub"], {"size": 20, "color": self.c["muted"], "align": PP_ALIGN.CENTER}))
        else:  # outro
            self.bg(sl, self.c["bg"])
            lines = []
            if p.get("title"):
                lines.append((p["title"], {"size": 22, "bold": True, "color": self.c["blue"], "align": PP_ALIGN.CENTER}))
            lines.append((p["line"], {"size": 36, "bold": True, "color": self.c["navy"], "align": PP_ALIGN.CENTER, "font": self.hfont}))
            for tip in p.get("tips", []):
                lines.append(("✓ " + tip, {"size": 20, "align": PP_ALIGN.CENTER}))
            ev = p.get("evidence_line") or self.th.get("evidence_line")
            if ev:
                self.text(sl, cx, self.H - 0.9, w, 0.5, ev, size=12, color=self.c["muted"], align=PP_ALIGN.CENTER)
        self.text(sl, cx, self.H * 0.15, w, self.H * 0.7, lines, anchor=MSO_ANCHOR.MIDDLE)

    def s_list(self, sl, p, s):
        tpl = s["template"]
        y = self.title(sl, p.get("title"))
        self.kicker(sl, p.get("kicker"), self.m + 0.45)
        if tpl == "checklist":
            items = [(x, None) for x in p.get("items", [])]
            glyph = "☐"
        elif tpl == "flashcard":
            self.box(sl, self.m, y, self.W - 2 * self.m, (self.H - y - self.m) / 2 - 0.1, self.c["navy"])
            self.text(sl, self.m, y, self.W - 2 * self.m, (self.H - y - self.m) / 2 - 0.1, p["front"], size=32, bold=True,
                      color=RGBColor(255, 255, 255), align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            y2 = y + (self.H - y - self.m) / 2 + 0.1
            self.box(sl, self.m, y2, self.W - 2 * self.m, (self.H - y - self.m) / 2 - 0.1, self.c["bg"], line=self.c["blue"])
            self.text(sl, self.m, y2, self.W - 2 * self.m, (self.H - y - self.m) / 2 - 0.1, p["back"], size=24,
                      align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            return
        else:
            items = [(it["text"] + (f" — {it['sub']}" if it.get("sub") else ""), it.get("tone")) for it in p.get("items", [])]
            glyph = None
        avail = self.H - y - self.m
        rh = min(0.85, avail / max(1, len(items)))
        w = self.W - 2 * self.m
        if tpl == "broll_panel" and not self.portrait:
            w = w * 0.55
            img_x = self.X(self.m + w + 0.3, self.W - 2 * self.m - w - 0.3)
            self.media(sl, p.get("shot"), None, img_x, y, self.W - 2 * self.m - w - 0.3, avail * 0.8, s)
        if tpl == "bullets" and p.get("side_broll") and not self.portrait:
            w = w * 0.58
            self.media(sl, p["side_broll"], None, self.X(self.m + w + 0.3, self.W - 2 * self.m - w - 0.3), y,
                       self.W - 2 * self.m - w - 0.3, avail * 0.8, s)
        for i, (txt, tone) in enumerate(items):
            yy = y + i * rh
            col = self.c["attention"] if tone == "warn" else self.c["safe"] if tone == "safe" else self.c["blue"]
            self.box(sl, self.X(self.m, w), yy, w, rh - 0.12, self.c["bg"])
            dot = self.box(sl, self.X(self.m + 0.15, 0.22), yy + (rh - 0.12) / 2 - 0.11, 0.22, 0.22, col, shape=MSO_SHAPE.OVAL)
            if glyph:
                dot.fill.background()
                dot.line.color.rgb = self.c["navy"]
                dot.line.width = Pt(1.5)
            self.text(sl, self.X(self.m + 0.5, w - 0.6), yy, w - 0.6, rh - 0.12, txt, size=20 if rh > 0.7 else 17,
                      anchor=MSO_ANCHOR.MIDDLE)

    def s_grid(self, sl, p, s):
        y = self.title(sl, p.get("title"))
        items = p.get("items", [])
        cols = int(p.get("cols") or (2 if self.portrait else 3))
        rows = (len(items) + cols - 1) // cols
        cw = (self.W - 2 * self.m - 0.3 * (cols - 1)) / cols
        rh = min(2.2, (self.H - y - self.m - 0.3 * (rows - 1)) / max(1, rows))
        for i, it in enumerate(items):
            x = self.X(self.m + (i % cols) * (cw + 0.3), cw)
            yy = y + (i // cols) * (rh + 0.3)
            tone = it.get("tone")
            col = self.c["attention"] if tone == "warn" else self.c["safe"] if tone == "safe" else self.c["blue"]
            self.box(sl, x, yy, cw, rh, self.c["bg"])
            self.box(sl, x + 0.2 if not self.rtl else x + cw - 0.75, yy + 0.2, 0.55, 0.55, col, shape=MSO_SHAPE.OVAL)
            lines = [(it["label"], {"size": 20, "bold": True})] + ([(it["sub"], {"size": 15, "color": self.c["muted"]})] if it.get("sub") else [])
            self.text(sl, x + 0.1, yy + 0.85, cw - 0.2, rh - 0.9, lines)

    def s_steps(self, sl, p, s):
        y = self.title(sl, p.get("title"))
        steps = p.get("steps", [])
        n = max(1, len(steps))
        col = self.c["attention"] if p.get("danger") else self.c["blue"]
        if self.portrait:
            rh = min(1.4, (self.H - y - self.m) / n)
            for i, st in enumerate(steps):
                yy = y + i * rh
                self.box(sl, self.X(self.m, 0.7), yy, 0.7, 0.7, col, shape=MSO_SHAPE.OVAL)
                self.text(sl, self.X(self.m, 0.7), yy, 0.7, 0.7, str(i + 1), size=22, bold=True, color=RGBColor(255, 255, 255), align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
                self.text(sl, self.X(self.m + 0.9, self.W - 2 * self.m - 0.9), yy - 0.05, self.W - 2 * self.m - 0.9, rh,
                          [(st["label"], {"size": 20, "bold": True})] + ([(st["sub"], {"size": 15, "color": self.c["muted"]})] if st.get("sub") else []))
            return
        cw = (self.W - 2 * self.m) / n
        cy = y + 0.6
        self.connect(sl, self.m + cw / 2, cy + 0.4, self.W - self.m - cw / 2, cy + 0.4, self.c["cyan"], 3)
        for i, st in enumerate(steps):
            x = self.X(self.m + i * cw, cw)
            self.box(sl, x + cw / 2 - 0.4, cy, 0.8, 0.8, col, shape=MSO_SHAPE.OVAL)
            self.text(sl, x + cw / 2 - 0.4, cy, 0.8, 0.8, str(i + 1), size=24, bold=True, color=RGBColor(255, 255, 255), align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            self.text(sl, x + 0.05, cy + 1.0, cw - 0.1, 2.4, [(st["label"], {"size": 19, "bold": True, "align": PP_ALIGN.CENTER})] +
                      ([(st["sub"], {"size": 15, "color": self.c["muted"], "align": PP_ALIGN.CENTER})] if st.get("sub") else []))

    def s_timeline(self, sl, p, s):
        y = self.title(sl, p.get("title"))
        ev = p.get("events", [])
        n = max(1, len(ev))
        if self.portrait:
            rh = (self.H - y - self.m) / n
            self.connect(sl, self.X(self.m + 0.15, 0), y, self.X(self.m + 0.15, 0), self.H - self.m, self.c["blue"], 3)
            for i, e in enumerate(ev):
                yy = y + i * rh
                self.box(sl, self.X(self.m, 0.3), yy + 0.05, 0.3, 0.3, self.c["blue"], shape=MSO_SHAPE.OVAL)
                self.text(sl, self.X(self.m + 0.5, self.W - 2 * self.m - 0.5), yy - 0.05, self.W - 2 * self.m - 0.5, rh,
                          ([(e["when"], {"size": 14, "bold": True, "color": self.c["blue"]})] if e.get("when") else []) + [(e["label"], {"size": 19, "bold": True})] + ([(e["sub"], {"size": 14, "color": self.c["muted"]})] if e.get("sub") else []))
            return
        cw = (self.W - 2 * self.m) / n
        ly = y + 0.5
        self.connect(sl, self.m, ly, self.W - self.m, ly, self.c["blue"], 3)
        for i, e in enumerate(ev):
            x = self.X(self.m + i * cw, cw)
            self.box(sl, x, ly - 0.15, 0.3, 0.3, self.c["blue"], shape=MSO_SHAPE.OVAL)
            self.text(sl, x, ly + 0.3, cw - 0.15, 2.5, ([(e["when"], {"size": 14, "bold": True, "color": self.c["blue"]})] if e.get("when") else [])
                      + [(e["label"], {"size": 19, "bold": True})] + ([(e["sub"], {"size": 14, "color": self.c["muted"]})] if e.get("sub") else []))

    def two_col(self, sl, p, heads, lists, fills, glyphs, y):
        rects = self.cols(2, y, self.H - y - self.m)
        for (x, yy, w, h), head, items, fill, g in zip(rects, heads, lists, fills, glyphs):
            self.box(sl, x, yy, w, h, fill)
            lines = [(head, {"size": 22, "bold": True, "color": g[1]})] + [((g[0] + " " if g[0] else "• ") + it, {"size": 18}) for it in items]
            self.text(sl, x + 0.15, yy + 0.15, w - 0.3, h - 0.3, lines)

    def s_do_dont(self, sl, p, s):
        y = self.title(sl, p.get("title"))
        tint = lambda c, a: RGBColor(*[int(255 - (255 - v) * a) for v in c])
        self.two_col(sl, p, [p.get("dont_head") or self.t["dont"], p.get("do_head") or self.t["do"]], [p.get("dont", []), p.get("do", [])],
                     [tint(self.c["attention"], .1), tint(self.c["safe"], .1)], [("✕", self.c["attention_text"]), ("✓", self.c["safe"])], y)

    def s_comparison(self, sl, p, s):
        y = self.title(sl, p.get("title"))
        tint = lambda c, a: RGBColor(*[int(255 - (255 - v) * a) for v in c])
        self.two_col(sl, p, [p["left"]["head"], p["right"]["head"]], [p["left"].get("items", []), p["right"].get("items", [])],
                     [self.c["bg"], tint(self.c["cyan"], .2)], [("", self.c["navy"]), ("", self.c["navy"])], y)

    def s_table(self, sl, p, s):
        y = self.title(sl, p.get("title"))
        cols, rows = p.get("columns", []), p.get("rows", [])
        if not cols:
            return
        h = min(self.H - y - self.m, 0.55 * (len(rows) + 1))
        gt = sl.shapes.add_table(len(rows) + 1, len(cols), Inches(self.m), Inches(y), Inches(self.W - 2 * self.m), Inches(h))
        tbl = gt.table
        if self.rtl:
            tbl._tbl.get_or_add_tblPr().set("rtl", "1")
        for j, c in enumerate(cols):
            cell = tbl.cell(0, j)
            cell.text = c
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.c["navy"]
            for para in cell.text_frame.paragraphs:
                self.para_fmt(para, 16, True, RGBColor(255, 255, 255))
        for i, r in enumerate(rows, 1):
            for j in range(len(cols)):
                cell = tbl.cell(i, j)
                cell.text = r[j] if j < len(r) else ""
                cell.fill.solid()
                cell.fill.fore_color.rgb = self.c["bg"] if i % 2 == 0 else RGBColor(255, 255, 255)
                for para in cell.text_frame.paragraphs:
                    self.para_fmt(para, 15, j == 0)

    def s_quiz(self, sl, p, s):
        it = self.items.get(p.get("quiz_item"))
        if it:
            stem = it.get("stem_ar") if self.rtl and it.get("stem_ar") else it["stem"]
            opts = [(o.get("text_ar") if self.rtl and o.get("text_ar") else o["text"]) for o in it.get("options", [])]
        else:
            stem, opts = p.get("q", ""), p.get("options", [])
        y = self.title(sl, stem, size=26)
        self.kicker(sl, self.t["final_check"], self.m + 0.45)
        rh = min(0.85, (self.H - y - self.m) / max(1, len(opts)))
        for i, o in enumerate(opts):
            self.text(sl, self.m, y + i * rh, self.W - 2 * self.m, rh - 0.12, f"{chr(65 + i)}.  {o}", size=19,
                      fill=RGBColor(255, 255, 255), line=self.c["line"], shape=MSO_SHAPE.ROUNDED_RECTANGLE, anchor=MSO_ANCHOR.MIDDLE)

    def s_decision(self, sl, p, s):
        y = self.title(sl, p["prompt"], size=26)
        self.kicker(sl, self.t["choose"], self.m + 0.45)
        ch = p.get("choices", [])
        rh = min(0.95, (self.H - y - self.m) / max(1, len(ch)))
        for i, c in enumerate(ch):
            self.text(sl, self.m, y + i * rh, self.W - 2 * self.m, rh - 0.15, c["label"], size=20, bold=True,
                      fill=RGBColor(255, 255, 255), line=self.c["blue"], shape=MSO_SHAPE.ROUNDED_RECTANGLE, anchor=MSO_ANCHOR.MIDDLE)

    def s_flow(self, sl, p, s):
        y = self.title(sl, p.get("title"))
        nodes, edges = p.get("nodes", []), p.get("edges", [])
        depth = flow_layers(nodes, edges)
        ncol = max(depth.values(), default=0) + 1
        byd = {}
        for n in nodes:
            byd.setdefault(depth[n["id"]], []).append(n)
        avail_w, avail_h = self.W - 2 * self.m, self.H - y - self.m
        pos = {}
        if self.portrait:
            ncol, rows = max(len(v) for v in byd.values()), len(byd)
            bw, bh = min(2.6, avail_w / ncol - 0.3), min(0.8, avail_h / rows - 0.4)
            for d, ns in byd.items():
                for k, n in enumerate(ns):
                    x = self.m + (avail_w - len(ns) * (bw + 0.3)) / 2 + k * (bw + 0.3)
                    pos[n["id"]] = (x, y + d * (avail_h / rows), bw, bh)
        else:
            bw = min(2.6, avail_w / ncol - 0.45)
            for d, ns in byd.items():
                bh = min(0.9, avail_h / len(ns) - 0.4)
                for k, n in enumerate(ns):
                    x = self.X(self.m + d * (avail_w / ncol), bw)
                    pos[n["id"]] = (x, y + k * (avail_h / max(len(v) for v in byd.values())), bw, bh)
        for e in edges:
            if e["from"] in pos and e["to"] in pos:
                a, b = pos[e["from"]], pos[e["to"]]
                c = self.connect(sl, a[0] + a[2] / 2, a[1] + a[3] / 2, b[0] + b[2] / 2, b[1] + b[3] / 2)
                c.line._get_or_add_ln().append(c.line._ln.makeelement(qn("a:tailEnd"), {"type": "triangle"}))
                if e.get("label"):
                    self.text(sl, (a[0] + b[0] + a[2]) / 2 - 0.4 + b[2] / 2 - a[2] / 2, (a[1] + b[1]) / 2 + 0.05, 0.8, 0.35, e["label"],
                              size=12, color=self.c["muted"], align=PP_ALIGN.CENTER)
        for n in nodes:
            x, yy, w, h = pos[n["id"]]
            kind = n.get("kind", "step")
            fill = self.c["navy"] if kind in ("start", "end") else RGBColor(255, 255, 255)
            shape = MSO_SHAPE.DIAMOND if kind == "decision" else MSO_SHAPE.ROUNDED_RECTANGLE
            self.text(sl, x, yy, w, h, n["label"], size=15, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                      color=RGBColor(255, 255, 255) if kind in ("start", "end") else self.c["ink"], fill=fill,
                      line=self.c["attention"] if kind == "decision" else self.c["blue"], shape=shape)

    def s_mindmap(self, sl, p, s):
        nodes = p.get("nodes", [])
        pos = mindmap_layout(p["root"], nodes)
        ids = {n["id"] for n in nodes}
        top = self.m
        aw, ah = self.W - 2 * self.m, self.H - 2 * self.m
        P = lambda xy: (self.m + ((100 - xy[0]) if self.rtl else xy[0]) / 100 * aw, top + xy[1] / 100 * ah)
        for n in nodes:
            par = n.get("parent") if n.get("parent") in ids else "root"
            (x1, y1), (x2, y2) = P(pos[par]), P(pos[n["id"]])
            self.connect(sl, x1, y1, x2, y2, self.c["cyan"], 2.5)
        rx, ry = P((50, 50))
        self.text(sl, rx - 1.4, ry - 0.45, 2.8, 0.9, p["root"], size=20, bold=True, color=RGBColor(255, 255, 255), align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.MIDDLE, fill=self.c["navy"], shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        for n in nodes:
            x, y = P(pos[n["id"]])
            tone = n.get("tone")
            col = self.c["attention"] if tone == "warn" else self.c["safe"] if tone == "safe" else self.c["blue"]
            self.text(sl, x - 1.1, y - 0.3, 2.2, 0.6, n["label"], size=14, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                      fill=RGBColor(255, 255, 255), line=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE)

    def mock_frame(self, sl, x, y, w, h, bar_text=""):
        self.box(sl, x, y, w, h, RGBColor(255, 255, 255), line=self.c["line"], shape=MSO_SHAPE.RECTANGLE)
        self.box(sl, x, y, w, 0.4, RGBColor(0xEE, 0xF2, 0xF8), shape=MSO_SHAPE.RECTANGLE)
        if bar_text:
            self.text(sl, x + 0.6, y, w - 0.7, 0.4, bar_text, size=13, color=self.c["muted"], anchor=MSO_ANCHOR.MIDDLE, font="IBM Plex Mono", align=PP_ALIGN.LEFT)
        for i in range(3):
            self.box(sl, x + 0.12 + i * 0.16, y + 0.14, 0.11, 0.11, RGBColor(0xC9, 0xD2, 0xE0), shape=MSO_SHAPE.OVAL)

    def callouts(self, sl, callouts, x, y, w):
        for i, c in enumerate(sorted(callouts or [], key=lambda c: c.get("cue", 0))):
            yy = y + i * 0.7
            self.box(sl, self.X(x, 0.4), yy + 0.08, 0.4, 0.4, self.c["attention"], shape=MSO_SHAPE.OVAL)
            self.text(sl, self.X(x, 0.4), yy + 0.08, 0.4, 0.4, str(i + 1), size=13, bold=True, color=self.c["ink_strong"], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            self.text(sl, self.X(x + 0.5, w - 0.5), yy, w - 0.5, 0.6, c["label"], size=15, anchor=MSO_ANCHOR.MIDDLE)

    def s_mock(self, sl, p, s):
        tpl = s["template"]
        side = 0 if self.portrait or not (p.get("callouts") or p.get("highlight") or p.get("actions")) else 3.6
        mw = self.W - 2 * self.m - side - (0.3 if side else 0)
        mx, my = self.X(self.m, mw), self.m + (0.9 if p.get("title") and tpl in ("code_mock",) else 0)
        if tpl == "code_mock" and p.get("title"):
            self.title(sl, p["title"], y=self.m - 0.3)
            my = self.m + 0.9
        mh = self.H - my - self.m - (2.2 if self.portrait and side == 0 and (p.get("callouts")) else 0)
        if tpl == "email_mock":
            e = p["email"]
            self.mock_frame(sl, mx, my, mw, mh)
            lines = [(e["subject"], {"size": 22, "bold": True}),
                     (f'{e["from"]}  <{e.get("from_addr", "")}>' if e.get("from_addr") else e["from"], {"size": 15, "color": self.c["muted"]})]
            if e.get("to"):
                lines.append((e["to"], {"size": 13, "color": self.c["muted"]}))
            lines += [(b, {"size": 16}) for b in e.get("body", [])]
            if e.get("attachment"):
                lines.append(("📎 " + e["attachment"], {"size": 15}))
            lines += [(x, {"size": 13, "color": self.c["muted"]}) for x in e.get("signature", [])]
            self.text(sl, mx + 0.2, my + 0.5, mw - 0.4, mh - 1.3, lines)
            if e.get("button"):
                self.text(sl, mx + 0.3 if not self.rtl else mx + mw - 2.8, my + mh - 0.75, 2.5, 0.5, e["button"], size=15, bold=True,
                          color=RGBColor(255, 255, 255), fill=self.c["blue"], shape=MSO_SHAPE.ROUNDED_RECTANGLE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        elif tpl == "chat_mock":
            self.box(sl, mx, my, mw, mh, RGBColor(0xF2, 0xF5, 0xFA), shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            if p.get("title"):
                self.text(sl, mx + 0.2, my + 0.1, mw - 0.4, 0.5, p["title"], size=17, bold=True)
            y = my + 0.7
            for m in p.get("messages", []):
                bw = mw * 0.68
                me = m.get("me")
                x = mx + mw - bw - 0.2 if me != self.rtl else mx + 0.2
                self.text(sl, x, y, bw, 0.7, m["text"], size=15, fill=self.c["blue"] if me else RGBColor(255, 255, 255),
                          color=RGBColor(255, 255, 255) if me else self.c["ink"], line=self.c["attention"] if m.get("warn") else None,
                          shape=MSO_SHAPE.ROUNDED_RECTANGLE, anchor=MSO_ANCHOR.MIDDLE)
                y += 0.85
        elif tpl == "browser_mock":
            self.mock_frame(sl, mx, my, mw, mh, ("⚠ " if p.get("bad") else "🔒 ") + p["url"])
            lines = ([(p["brand"], {"size": 20, "bold": True, "color": self.c["navy"], "align": PP_ALIGN.CENTER})] if p.get("brand") else []) + \
                    ([(p["heading"], {"size": 22, "bold": True, "align": PP_ALIGN.CENTER})] if p.get("heading") else []) + \
                    [(x, {"size": 16, "align": PP_ALIGN.CENTER}) for x in p.get("lines", [])]
            self.text(sl, mx + 0.3, my + 0.7, mw - 0.6, mh - 1.0, lines)
            if p.get("page") in ("login", "checkout"):
                for k in range(3):
                    f = self.box(sl, mx + mw / 2 - 1.6, my + 2.0 + k * 0.6, 3.2, 0.45, self.c["blue"] if k == 2 else RGBColor(255, 255, 255),
                                 line=self.c["line"], shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        elif tpl == "popup":
            self.box(sl, self.m, self.m, self.W - 2 * self.m, self.H - 2 * self.m, RGBColor(0x4A, 0x50, 0x70), shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            pw, ph = min(6, self.W - 2 * self.m - 0.6), 3.2
            px, py = (self.W - pw) / 2, (self.H - ph) / 2
            self.box(sl, px, py, pw, ph, RGBColor(255, 255, 255))
            lines = [("⚠", {"size": 30, "color": self.c["attention_text"], "align": PP_ALIGN.CENTER}), (p["title"], {"size": 22, "bold": True, "align": PP_ALIGN.CENTER}),
                     (p["body"], {"size": 16, "align": PP_ALIGN.CENTER})]
            if p.get("cta"):
                lines.append(("[ " + p["cta"] + " ]", {"size": 16, "bold": True, "color": self.c["attention_text"], "align": PP_ALIGN.CENTER}))
            self.text(sl, px + 0.2, py + 0.1, pw - 0.4, ph - 0.2, lines, anchor=MSO_ANCHOR.MIDDLE)
        elif tpl == "mfa_prompt":
            pw = min(3.6, mw)
            px = (self.W - pw) / 2
            self.box(sl, px, self.m, pw, self.H - 2 * self.m - 0.6, self.c["ink"])
            n = min(int(p.get("count_to") or 1), 4)
            for k in range(n):
                self.text(sl, px + 0.2, self.m + 0.3 + k * 1.15, pw - 0.4, 1.0, [(p.get("app", ""), {"size": 15, "bold": True}), (p.get("place", ""), {"size": 12, "color": self.c["muted"]})],
                          fill=RGBColor(255, 255, 255), shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            if p.get("count_to", 1) > 1:
                self.text(sl, px + pw - 0.4, self.m - 0.2, 0.7, 0.7, str(p["count_to"]), size=18, bold=True, color=self.c["ink_strong"],
                          fill=self.c["attention"], shape=MSO_SHAPE.OVAL, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            if p.get("caption"):
                self.text(sl, self.m, self.H - self.m - 0.5, self.W - 2 * self.m, 0.5, p["caption"], size=16, align=PP_ALIGN.CENTER)
        elif tpl == "code_mock":
            self.box(sl, mx, my, mw, mh, self.c["ink"], shape=MSO_SHAPE.RECTANGLE)
            hl = {h["line"]: h for h in p.get("highlight", [])}
            lines = []
            for i, ln in enumerate(p.get("lines", []), 1):
                lines.append((f"{i:>2}  {ln}" + (f"    ◀ {hl[i]['label']}" if i in hl and hl[i].get("label") else ""),
                              {"size": 15, "color": self.c["attention"] if i in hl else RGBColor(0xE4, 0xE9, 0xF5), "font": "IBM Plex Mono", "align": PP_ALIGN.LEFT}))
            self.text(sl, mx + 0.2, my + 0.2, mw - 0.4, mh - 0.4, lines)
        elif tpl == "screencast":
            app = p["app"]
            self.mock_frame(sl, mx, my, mw, mh, app.get("title", ""))
            y = my + 0.6
            for f in app.get("fields", []):
                if f.get("kind") == "button":
                    self.text(sl, mx + 0.3, y, 2.6, 0.5, f["label"], size=15, bold=True, color=RGBColor(255, 255, 255), fill=self.c["blue"],
                              shape=MSO_SHAPE.ROUNDED_RECTANGLE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
                    y += 0.7
                else:
                    self.text(sl, mx + 0.3, y, mw - 0.6, 0.35, f["label"], size=13, color=self.c["muted"])
                    self.text(sl, mx + 0.3, y + 0.35, mw - 0.6, 0.45, f.get("value", ""), size=14, fill=RGBColor(255, 255, 255), line=self.c["line"],
                              shape=MSO_SHAPE.ROUNDED_RECTANGLE, anchor=MSO_ANCHOR.MIDDLE)
                    y += 0.95
            acts = [{"label": a.get("label") or a.get("value") or a["do"], "cue": a.get("cue", 0)} for a in p.get("actions", [])]
            if side:
                self.callouts(sl, acts, self.W - self.m - side if not self.rtl else self.m, self.m, side)
            return
        if side:
            self.callouts(sl, p.get("callouts") or p.get("highlight"), self.W - self.m - side if not self.rtl else self.m, self.m + 0.3, side)
        elif p.get("callouts"):
            self.callouts(sl, p["callouts"], self.m, self.H - self.m - 2.1, self.W - 2 * self.m)

    def figure(self, sl, cast, x, y, h, flip=False):
        """Simple native-shape persona placeholder (head + body) in the persona colours."""
        skin, hair, shirt = palette(cast)
        w = h * 0.45
        self.box(sl, x + w * 0.1, y + h * 0.36, w * 0.8, h * 0.64, rgb(shirt), shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        self.box(sl, x + w * 0.2, y, w * 0.6, w * 0.6, rgb(skin), shape=MSO_SHAPE.OVAL)

    def s_scene_art(self, sl, p, s):
        tpl = s["template"]
        panels = p.get("panels") if tpl == "comic" else [p]
        n = len(panels)
        cols = 1 if self.portrait else min(3, n) if n != 4 else 2
        rows = (n + cols - 1) // cols
        aw, ah = self.W - 2 * self.m, self.H - 2 * self.m
        if tpl == "whiteboard":
            self.bg(sl, RGBColor(255, 255, 255))
            y0 = self.title(sl, p.get("title")) if p.get("title") else self.m
            for it in sorted(p.get("items", []), key=lambda i: i.get("cue", 0)):
                fx = lambda v, full: (v if v <= 1 else v / 100 if v <= 100 else v / full)
                x = self.m + fx(it.get("x", .5), 1920) * aw
                y = y0 + fx(it.get("y", .5), 1080) * (self.H - y0 - self.m)
                col = {"attention": self.c["attention"], "safe": self.c["safe"]}.get(it.get("color"), self.c["ink"])
                tcol = self.c["attention_text"] if it.get("color") == "attention" else col
                if self.rtl:
                    x = self.W - x
                k = it["kind"]
                if k == "arrow":
                    to = it.get("to") or {}
                    tx = self.m + fx(to.get("x", .6), 1920) * aw
                    c = self.connect(sl, x, y, self.W - tx if self.rtl else tx, y0 + fx(to.get("y", .5), 1080) * (self.H - y0 - self.m), col, 3)
                    c.line._get_or_add_ln().append(c.line._ln.makeelement(qn("a:tailEnd"), {"type": "triangle"}))
                elif k == "person":
                    self.figure(sl, it.get("cast", "host"), x - 0.4, y - 0.9, 1.8)
                elif k in ("circle", "box"):
                    w, h = fx(it.get("w", .15), 1920) * aw, fx(it.get("h", .12), 1080) * (self.H - y0 - self.m)
                    b = sl.shapes.add_shape(MSO_SHAPE.OVAL if k == "circle" else MSO_SHAPE.RECTANGLE, Inches(x - w / 2), Inches(y - h / 2), Inches(w), Inches(h))
                    b.fill.background()
                    b.line.color.rgb = col
                    b.line.width = Pt(3)
                elif it.get("text") or k in ("check", "cross", "icon", "note"):
                    glyph = {"check": "✓", "cross": "✕"}.get(k, "")
                    self.text(sl, x - 1.3, y - 0.35, 2.6, 0.7, glyph + (" " if glyph and it.get("text") else "") + (it.get("text") or ""), size=24, bold=True,
                              color=tcol, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, font=self.th["fonts"]["hand"] if not self.rtl else None)
            return
        pw, ph = (aw - 0.3 * (cols - 1)) / cols, (ah - 0.3 * (rows - 1)) / rows
        for i, pn in enumerate(panels):
            x = self.X(self.m + (i % cols) * (pw + 0.3), pw)
            y = self.m + (i // cols) * (ph + 0.3)
            art_h = ph * (0.62 if (pn.get("bubbles") or pn.get("caption")) else 1)
            self.box(sl, x, y, pw, art_h, self.c["bg"], line=self.c["ink"] if tpl == "comic" else None, shape=MSO_SHAPE.RECTANGLE)
            ppl = pn.get("people", [])
            for k, pp in enumerate(ppl):
                fx = pp.get("x")
                fx = (fx if fx is not None and fx <= 1 else (fx / 1920 if fx else (k + 1) / (len(ppl) + 1)))
                fh = art_h * 0.7
                self.figure(sl, pp["cast"], x + fx * pw - fh * 0.22, y + art_h - fh - 0.05, fh)
            lines = [(f'{display_name(b["who"], self.rtl)}: {b["text"]}', {"size": 14 if tpl == "comic" else 17}) for b in sorted(pn.get("bubbles", []), key=lambda b: b.get("cue", 0))]
            if pn.get("caption"):
                lines.append((pn["caption"], {"size": 13, "bold": True, "color": self.c["navy"]}))
            if lines:
                self.text(sl, x, y + art_h + 0.05, pw, ph - art_h - 0.05, lines)

    def media(self, sl, shot_id, image_id, x, y, w, h, s):
        path = None
        if shot_id:
            path = next((b.get("path") for b in self.doc.get("broll_shots", []) if b["id"] == shot_id), None)
        if image_id:
            path = next((g.get("path") for g in self.doc.get("generated_images", []) if g["id"] == image_id), None)
        full = (self.base / path) if path and not Path(path).is_absolute() else (Path(path) if path else None)
        if full and full.exists() and full.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
            sl.shapes.add_picture(str(full), Inches(x), Inches(y), Inches(w), Inches(h))
        else:
            self.text(sl, x, y, w, h, s.get("visual", "") or "", size=16, color=RGBColor(255, 255, 255), fill=self.c["navy"],
                      shape=MSO_SHAPE.ROUNDED_RECTANGLE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    def s_media(self, sl, p, s):
        tpl = s["template"]
        cap_h = 0.6 if p.get("caption") else 0
        self.media(sl, p.get("shot"), p.get("image"), self.m, self.m, self.W - 2 * self.m, self.H - 2 * self.m - cap_h, s)
        for i, c in enumerate(p.get("chips", [])):
            self.text(sl, self.X(self.m + 0.3 + i * 2.6, 2.4), self.H - self.m - cap_h - 0.8, 2.4, 0.5, c, size=15, bold=True,
                      fill=RGBColor(255, 255, 255), shape=MSO_SHAPE.ROUNDED_RECTANGLE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        if cap_h:
            self.text(sl, self.m, self.H - self.m - 0.5, self.W - 2 * self.m, 0.5, p["caption"], size=16, color=self.c["muted"], align=PP_ALIGN.CENTER)

    DISPATCH = {
        "title": "s_hero", "section": "s_hero", "stat": "s_hero", "definition": "s_hero", "statement": "s_hero", "outro": "s_hero",
        "bullets": "s_list", "checklist": "s_list", "broll_panel": "s_list", "flashcard": "s_list",
        "icon_grid": "s_grid", "steps": "s_steps", "timeline": "s_timeline", "do_dont": "s_do_dont", "comparison": "s_comparison",
        "table": "s_table", "quiz": "s_quiz", "decision": "s_decision", "process_flow": "s_flow", "mindmap": "s_mindmap",
        "email_mock": "s_mock", "chat_mock": "s_mock", "browser_mock": "s_mock", "popup": "s_mock", "mfa_prompt": "s_mock",
        "code_mock": "s_mock", "screencast": "s_mock", "cartoon": "s_scene_art", "comic": "s_scene_art", "whiteboard": "s_scene_art",
        "broll": "s_media", "image": "s_media",
    }

    def notes(self, s) -> str:
        out = []
        for l in s.get("narration", []):
            out.append(f'{display_name(l.get("who", ""), self.rtl)}: {line_text(l, self.rtl)}')
        p = s.get("props") or {}
        if s["template"] == "quiz":
            it = self.items.get(p.get("quiz_item"))
            if it:
                ans = [o["text"] for o in it.get("options", []) if o.get("correct")]
                out.append(f'[{self.t["correct"]}] ' + "; ".join(ans) + (f' — {it.get("explanation")}' if it.get("explanation") else ""))
            elif p.get("options") and p.get("answer") is not None:
                out.append(f'[{self.t["correct"]}] {p["options"][p["answer"]]}' + (f' — {p.get("why")}' if p.get("why") else ""))
        if s["template"] == "decision":
            for c in p.get("choices", []):
                out.append(f'→ {c["label"]} ⇒ {c["next"]}' + (" ✓" if c.get("correct") else ""))
        if s["template"] == "flashcard":
            out.append(p.get("back", ""))
        if s.get("notes"):  # presenter-only notes (narrated-deck format)
            out.append(("ملاحظات المقدّم: " if self.rtl else "Presenter: ") + s["notes"])
        return "\n".join(out)

    def build(self) -> Presentation:
        blank = self.prs.slide_layouts[6]
        for s in self.doc["scenes"]:
            sl = self.prs.slides.add_slide(blank)
            self.bg(sl, RGBColor(255, 255, 255))
            getattr(self, self.DISPATCH.get(s["template"], "s_list"))(sl, s.get("props") or {}, s)
            nt = sl.notes_slide.notes_text_frame
            nt.text = self.notes(s)
            if self.rtl:
                for para in nt.paragraphs:
                    para._p.get_or_add_pPr().set("rtl", "1")
            a = find_scene_audio(self.audio_dir, s["id"])
            if a:
                mime = {".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".wav": "audio/wav", ".ogg": "audio/ogg"}[a.suffix.lower()]
                sl.shapes.add_movie(str(a), Inches(self.W - 0.75), Inches(self.H - 0.75), Inches(0.5), Inches(0.5), mime_type=mime)
                self.embedded_audio += 1
        return self.prs


DECK_JS = r"""(function(){var s=[].slice.call(document.querySelectorAll('.slide')),i=0,rtl=document.dir==='rtl',
cnt=document.getElementById('cnt'),nb=document.getElementById('notes-btn');
function fit(){var st=document.querySelector('.deck');var W=st.dataset.w,H=st.dataset.h;var k=Math.min(innerWidth/W,(innerHeight-56)/H);
s.forEach(function(e){e.style.transform='scale('+k+')';e.parentNode.style.width=W*k+'px';e.parentNode.style.height=H*k+'px';});}
function go(n){i=Math.max(0,Math.min(s.length-1,n));s.forEach(function(e,k){e.parentNode.hidden=k!==i;});cnt.textContent=(i+1)+' / '+s.length;
location.hash='slide-'+(i+1);flows(s[i]);var h=s[i].querySelector('.scene-title');if(h)h.focus({preventScroll:true});}
function flows(sc){[].slice.call(sc.querySelectorAll('.flow')).forEach(function(fl){var svg=fl.querySelector('.flow-svg'),E=JSON.parse(fl.dataset.edges||'[]'),
k=fl.getBoundingClientRect().width/fl.offsetWidth||1,fr=fl.getBoundingClientRect(),o='<defs><marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#5B6385"/></marker></defs>';
E.forEach(function(e,j){var a=fl.querySelector('[data-node="'+e.from+'"]'),b=fl.querySelector('[data-node="'+e.to+'"]');if(!a||!b)return;
var ra=a.getBoundingClientRect(),rb=b.getBoundingClientRect(),ax=(ra.left+ra.width/2-fr.left)/k,ay=(ra.top+ra.height/2-fr.top)/k,bx=(rb.left+rb.width/2-fr.left)/k,by=(rb.top+rb.height/2-fr.top)/k;
function c(x,y,tx,ty,r){var dx=tx-x,dy=ty-y,sx=Math.abs(dx)?(r.width/k/2+2)/Math.abs(dx):1e9,sy=Math.abs(dy)?(r.height/k/2+2)/Math.abs(dy):1e9,q=Math.min(sx,sy);return[x+dx*q,y+dy*q];}
var p1=c(ax,ay,bx,by,ra),p2=c(bx,by,ax,ay,rb);o+='<line x1="'+p1[0]+'" y1="'+p1[1]+'" x2="'+p2[0]+'" y2="'+p2[1]+'" stroke="#5B6385" stroke-width="2" marker-end="url(#fa)"/>';
var l=fl.querySelector('.elabel[data-e="'+j+'"]');if(l){l.style.left=(p1[0]+p2[0])/2+'px';l.style.top=(p1[1]+p2[1])/2+'px';}});svg.innerHTML=o;});}
document.addEventListener('keydown',function(e){var f=rtl?'ArrowLeft':'ArrowRight',b=rtl?'ArrowRight':'ArrowLeft';
if(e.key===f||e.key===' '||e.key==='PageDown'){e.preventDefault();go(i+1);}if(e.key===b||e.key==='PageUp'){e.preventDefault();go(i-1);}
if(e.key==='Home')go(0);if(e.key==='End')go(s.length-1);if(e.key==='n'||e.key==='N'||e.key==='s'||e.key==='S')toggle();});
function toggle(){var on=document.body.classList.toggle('show-notes');nb.setAttribute('aria-pressed',String(on));fit();}
nb.addEventListener('click',toggle);document.getElementById('prev').addEventListener('click',function(){go(i-1);});
document.getElementById('next').addEventListener('click',function(){go(i+1);});
window.addEventListener('resize',fit);window.addEventListener('beforeprint',function(){s.forEach(function(e){e.parentNode.hidden=false;e.style.transform='none';e.parentNode.style.width='';e.parentNode.style.height='';flows(e);});});
window.addEventListener('afterprint',function(){fit();go(i);});
if(/[?&]notes=1/.test(location.search))document.body.classList.add('show-notes');
var m=/slide-(\d+)/.exec(location.hash);fit();go(m?+m[1]-1:0);})();"""


def deck_html(doc, base: Path, out: Path, quiz) -> Path:
    rtl = is_rtl(doc)
    ctx = Ctx(doc, base, out, quiz, interactive=False)
    t = ctx.t
    W, H = {"16:9": (1600, 900), "9:16": (900, 1600), "1:1": (1100, 1100)}[doc.get("aspect", "16:9")]
    slides = []
    for i, s in enumerate(doc["scenes"], 1):
        notes = "".join(f"<p><b>{esc(display_name(l.get('who', ''), rtl))}</b> {esc(line_text(l, rtl))}</p>" for l in s.get("narration", []))
        if s.get("notes"):
            notes += f"<p><i>{esc(s['notes'])}</i></p>"
        slides.append(f'<div class="frame" id="slide-{i}"><section class="slide scene active t-{s["template"]}" aria-roledescription="slide" '
                      f'aria-label="{i} / {len(doc["scenes"])}"><div class="stage">{scene_body(s, ctx)}</div></section>'
                      f'<aside class="notes" aria-label="{esc(t["notes"])}"><h2>{esc(t["notes"])}</h2>{notes}</aside></div>')
    css = (TEMPLATES / "lesson.css").read_text(encoding="utf-8") + (TEMPLATES / "deck.css").read_text(encoding="utf-8")
    page = f"""<!doctype html><html lang="{html_lang(doc['language'])}" dir="{'rtl' if rtl else 'ltr'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(doc['title'])}</title>
<link rel="stylesheet" href="{GOOGLE_FONTS}"><style>{css_vars(theme(doc), rtl)}{css}
@page{{size:{W}px {H}px;margin:0}} .slide{{width:{W}px;height:{H}px}}</style></head>
<body class="deckbody"><main class="deck" data-w="{W}" data-h="{H}">{''.join(slides)}</main>
<nav class="deck-nav"><button class="btn ghost" id="prev">{esc(t['back'])}</button><span id="cnt" aria-live="polite"></span>
<button class="btn ghost" id="notes-btn" aria-pressed="false">{esc(t['notes'])} (N)</button><button class="btn primary" id="next">{esc(t['next'])}</button></nav>
<script>{DECK_JS}</script></body></html>"""
    p = out / "deck.html"
    p.write_text(page, encoding="utf-8")
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard", type=Path, help="<L>.storyboard.json or a run folder runs/<id>/")
    ap.add_argument("--out", type=Path, help="default: runs/<id>/renders/<L>/deck/")
    ap.add_argument("--audio", type=Path)
    ap.add_argument("--quiz", type=Path, help="default: sibling <L>.quiz.json")
    ap.add_argument("--lesson")
    ap.add_argument("--lang")
    ap.add_argument("--no-strict", action="store_true")
    ap.add_argument("--no-html", action="store_true")
    a = ap.parse_args()
    items = lesson_inputs(a.storyboard, a.lesson, a.lang, a.quiz)
    for it in items:
        out = default_out(it, "deck", a.out, a.lang, multi=len(items) > 1)
        doc = load_validated(it["storyboard"], "storyboard", strict=not a.no_strict)
        quiz = load_validated(it["quiz"], "quiz", strict=not a.no_strict) if it["quiz"] else None
        out.mkdir(parents=True, exist_ok=True)
        d = Deck(doc, it["storyboard"].parent, a.audio or (it["storyboard"].parent / "audio"), quiz)
        prs = d.build()
        pptx = out / f"{doc['lesson_id']}.pptx"
        prs.save(pptx)
        print(f"deck: {pptx}  slides={len(prs.slides)} aspect={doc.get('aspect')} audio_embedded={d.embedded_audio}")
        if not a.no_html:
            print(f"deck html: {deck_html(doc, it['storyboard'].parent, out, quiz)}")


if __name__ == "__main__":
    main()
