#!/usr/bin/env python3
"""Render a storyboard.json (+ optional quiz.json) into a self-contained, accessible HTML lesson.

Usage:
  .venv/bin/python skills/tcs-render-lesson/scripts/html_lesson.py <storyboard.json> [--quiz quiz.json]
        --out <dir> [--audio <dir>] [--no-strict]

Output: <dir>/index.html (CSS+JS inlined), <dir>/media/* (copied images/clips/audio/captions), <dir>/lesson.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import icons  # noqa: E402
from _common import (GOOGLE_FONTS, TEMPLATES, audio_duration, css_vars, esc, find_scene_audio, html_lang,  # noqa: E402
                     is_rtl, line_text, load_validated, theme)
from render_html import SIM_MODES, Ctx, quiz_item_html, scene_body, sim_id, transcript_html  # noqa: E402
from _common import default_out, lesson_inputs  # noqa: E402

LMS_MARKER = "<!--TCS_LMS-->"


def scene_label(s: dict) -> str:
    p = s.get("props") or {}
    for k in ("title", "prompt", "term", "root", "label", "q", "front", "line", "text", "heading"):
        if isinstance(p.get(k), str) and p[k].strip():
            return p[k].strip()
    if isinstance(p.get("email"), dict):
        return p["email"].get("subject", s["id"])
    if isinstance(p.get("app"), dict) and p["app"].get("title"):
        return p["app"]["title"]
    return s.get("visual") or s["id"].replace("_", " ")


def check_refs(doc, quiz):
    errs = []
    ids = {s["id"] for s in doc["scenes"]}
    qids = {i["id"] for i in (quiz or {}).get("items", [])}
    br = doc.get("branching")
    nodes = {n["id"] for n in br["nodes"]} if br else set()
    if br:
        if br["start"] not in nodes:
            errs.append(f"branching.start '{br['start']}' is not a node id")
        for n in br["nodes"]:
            for sid in n["scenes"]:
                if sid not in ids:
                    errs.append(f"branching node {n['id']}: unknown scene '{sid}'")
    for s in doc["scenes"]:
        p = s.get("props") or {}
        if s["template"] == "decision":
            for c in p.get("choices", []):
                if c["next"] not in ids and c["next"] not in nodes:
                    errs.append(f"scene {s['id']}: choice '{c['id']}' next '{c['next']}' is neither a scene nor a node")
        if s["template"] == "quiz" and quiz and p.get("quiz_item") not in qids:
            errs.append(f"scene {s['id']}: quiz_item '{p.get('quiz_item')}' not found in quiz.json")
        if s["template"] == "quiz" and not quiz and not p.get("q"):
            errs.append(f"scene {s['id']}: quiz scene needs quiz.json or inline props q/options/answer")
    return errs


def make_vtt(scene, rtl, dur: float, path: Path):
    lines = [line_text(l, rtl) for l in scene.get("narration", []) if line_text(l, rtl)]
    words = [max(1, len(l.split())) for l in lines]
    tot = sum(words) or 1
    t, cues = 0.0, ["WEBVTT", ""]
    fmt = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}"
    for l, w in zip(lines, words):
        d = dur * w / tot
        cues += [f"{fmt(t)} --> {fmt(t + d)}", l, ""]
        t += d
    path.write_text("\n".join(cues), encoding="utf-8")


def build(storyboard: Path, quiz_path: Path | None, out: Path, audio_dir: Path | None, strict=True) -> dict:
    doc = load_validated(storyboard, "storyboard", strict=strict)
    quiz = load_validated(quiz_path, "quiz", strict=strict) if quiz_path else None
    errs = check_refs(doc, quiz)
    for e in errs:
        print("REF ERROR", e, file=sys.stderr)
    if errs and strict:
        sys.exit(f"{len(errs)} reference error(s)")
    out.mkdir(parents=True, exist_ok=True)
    rtl = is_rtl(doc)
    ctx = Ctx(doc, storyboard.parent, out, quiz, interactive=True)
    t = ctx.t
    th = theme(doc)
    audio_dir = audio_dir or (storyboard.parent / "audio")

    embedded = {(s.get("props") or {}).get("quiz_item") for s in doc["scenes"] if s["template"] == "quiz"}
    sims = [sim_id(s) for s in doc["scenes"] if s["template"] == "screencast"
            and ((s.get("props") or {}).get("sim") or {}).get("mode") == "assess"]
    embedded |= set(sims)
    final_items = [i for i in (quiz or {}).get("items", []) if i["id"] not in embedded and i["type"] != "flashcard"]
    scored = [i for i in (quiz or {}).get("items", []) if i["type"] != "flashcard"]
    if not quiz:  # inline quiz scenes still score
        scored = [{"id": (s["props"].get("quiz_item") or s["id"]), "points": 1} for s in doc["scenes"] if s["template"] == "quiz"]
    have = {i["id"] for i in scored}
    scored += [{"id": i, "points": 1} for i in sims if i not in have]

    order = [s["id"] for s in doc["scenes"]]
    if final_items:
        order.append("__check")
    order.append("__end")
    n_total = len(order)
    sections = []
    for i, s in enumerate(doc["scenes"]):
        label = f'{t["scene"]} {i + 1} {t["of"]} {n_total}: {scene_label(s)}'
        narr = ""
        a = find_scene_audio(audio_dir, s["id"])
        if a:
            url = ctx.media(str(a))
            track = ""
            dur = audio_duration(a)
            if dur:
                vtt = out / "media" / f"{s['id']}.vtt"
                make_vtt(s, rtl, dur, vtt)
                track = f'<track kind="captions" src="media/{vtt.name}" srclang="{html_lang(doc["language"])[:2]}" label="{esc(t["transcript"])}" default>'
            narr += f'<audio controls preload="none" src="{esc(url)}" aria-label="{esc(t["audio"])}">{track}</audio>'
        narr += transcript_html(s, ctx)
        sections.append(
            f'<section class="scene t-{s["template"]}" id="s-{s["id"]}" data-scene="{s["id"]}" data-template="{s["template"]}" '
            f'aria-label="{esc(label)}"><div class="stage">{scene_body(s, ctx)}</div><div class="narr">{narr}</div></section>')
    if doc.get("branching"):
        sections.append(
            f'<section class="scene" id="s-__outcome" data-scene="__outcome" aria-label="{esc(t["outcome"])}"><div class="stage">'
            f'<div class="outcome" role="status"><p class="oc-ico" aria-hidden="true"></p><h2 class="scene-title" tabindex="-1">{esc(t["outcome"])}</h2>'
            f'<p class="oc-fb"></p><p class="oc-score"></p>'
            f'<button class="btn ghost" data-branch-replay>{icons.svg("refresh", 16)} {esc(t["branch_restart"])}</button></div></div></section>')
    if final_items:
        forms = "".join(f'<div class="card">{quiz_item_html(i, ctx, "final")}</div>' for i in final_items)
        sections.append(
            f'<section class="scene" id="s-__check" data-scene="__check" aria-label="{esc(t["final_check"])}"><div class="stage">'
            f'<h2 class="scene-title" tabindex="-1">{esc(t["final_check"])}</h2><div class="final-items" style="display:grid;gap:16px">{forms}</div>'
            f'<p><button class="btn primary" data-submit-all>{icons.svg("check", 16)} {esc(t["results"])}</button></p></div></section>')
    retry = f'<button class="btn ghost" data-retry>{icons.svg("refresh", 16)} {esc(t["try_again"])}</button>' if scored else ""
    sections.append(
        f'<section class="scene" id="s-__end" data-scene="__end" aria-label="{esc(t["complete"])}"><div class="stage"><div class="results">'
        f'<div class="hero-ico">{icons.svg("check-circle", 56)}</div><h2 class="scene-title" tabindex="-1">{esc(t["complete"])}</h2>'
        f'<h3>{esc(doc["title"])}</h3><div id="end-score" role="status"></div>{retry}</div></div></section>')

    menu = "".join(f'<li><button data-jump="{s["id"]}">{esc(scene_label(s))}</button></li>' for s in doc["scenes"])
    data = {
        "lesson_id": doc["lesson_id"], "course_id": doc["course_id"], "title": doc["title"], "lang": html_lang(doc["language"]),
        "rtl": rtl, "order": order, "branching": doc.get("branching"), "ui": t,
        "hasQuiz": bool(scored), "passMark": (quiz or {}).get("pass_mark", 80),
        "quiz": [{"id": i["id"], "points": int(i.get("points", 1))} for i in scored],
    }
    css = (TEMPLATES / "lesson.css").read_text(encoding="utf-8")
    js = (TEMPLATES / "lesson.js").read_text(encoding="utf-8")
    page = f"""<!doctype html>
<html lang="{html_lang(doc['language'])}" dir="{'rtl' if rtl else 'ltr'}" class="no-js">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(doc['title'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{GOOGLE_FONTS}">
<style>{css_vars(th, rtl)}
{css}</style>
{LMS_MARKER}
</head>
<body>
<a class="skip" href="#main">{esc(t['skip'])}</a>
<header class="topbar"><button class="btn" id="menu-btn" aria-expanded="false" aria-controls="menu">{icons.svg('menu', 18)}<span class="sr-only">{esc(t['menu'])}</span></button>
<h1>{esc(doc['title'])}</h1><div class="progress" role="presentation"><i></i></div></header>
<nav id="menu" class="menu" hidden aria-label="{esc(t['menu'])}"><h2>{esc(t['menu'])}</h2><ol>{menu}</ol></nav>
<main id="main" tabindex="-1">
{''.join(sections)}
</main>
<nav class="navbar" aria-label="{esc(t['progress'])}">
<button class="btn ghost" id="nav-back">{icons.svg('arrow-left', 18, 'ico flip-rtl')} {esc(t['back'])}</button>
<span class="pos" id="nav-pos" aria-hidden="true"></span>
<button class="btn primary" id="nav-next">{esc(t['next'])} {icons.svg('arrow-right', 18, 'ico flip-rtl')}</button>
</nav>
<div id="live" class="sr-only" aria-live="polite"></div>
<script type="application/json" id="tcs-data">{json.dumps(data, ensure_ascii=False).replace('</', '<\\/')}</script>
<script>{js}</script>
</body></html>"""
    (out / "index.html").write_text(page, encoding="utf-8")
    files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file() and p.name != "lesson.json")
    manifest = {
        "lesson_id": doc["lesson_id"], "course_id": doc["course_id"], "title": doc["title"], "language": doc["language"],
        "direction": "rtl" if rtl else "ltr", "entry": "index.html", "scenes": len(doc["scenes"]),
        "has_quiz": bool(scored), "pass_mark": data["passMark"], "quiz_items": len(scored),
        "branching": bool(doc.get("branching")), "files": files, "missing_media": sorted(set(ctx.missing)),
    }
    (out / "lesson.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard", type=Path, help="<L>.storyboard.json or a run folder runs/<id>/")
    ap.add_argument("--quiz", type=Path, help="default: sibling <L>.quiz.json")
    ap.add_argument("--out", type=Path, help="default: runs/<id>/renders/<L>/lesson/")
    ap.add_argument("--lesson", help="run folder: only this lesson id")
    ap.add_argument("--lang", help="run folder: render <L>.<lang>.storyboard.json")
    ap.add_argument("--audio", type=Path, help="dir with <scene_id>.mp3|m4a|wav (default: <storyboard dir>/audio)")
    ap.add_argument("--no-strict", action="store_true", help="warn instead of failing on schema/reference errors")
    a = ap.parse_args()
    items = lesson_inputs(a.storyboard, a.lesson, a.lang, a.quiz)
    for it in items:
        out = default_out(it, "lesson", a.out, a.lang, multi=len(items) > 1)
        m = build(it["storyboard"], it["quiz"], out, a.audio, strict=not a.no_strict)
        print(f"lesson: {out / 'index.html'}  scenes={m['scenes']} quiz_items={m['quiz_items']} branching={m['branching']}")
        if m["missing_media"]:
            print("missing media (placeholders used):", ", ".join(m["missing_media"]))


if __name__ == "__main__":
    main()
