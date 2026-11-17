#!/usr/bin/env python3
"""Lightweight storyboard preview (Markdown) for the lesson-1 approval gate.

Usage: preview.py <lesson>.storyboard.json [--out preview.md] [--full]
Prints/writes: header (title, language, formats, aspect, est. duration, cast, voices, claims) + one table row per scene:
# | scene | template | ~s | narration (▸ = cue) | on screen | visuals | claims.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sbtools as T  # noqa: E402


def cell(s: str, n: int | None) -> str:
    s = " ".join(str(s).split()).replace("|", "\\|")
    return s if n is None or len(s) <= n else s[: n - 1] + "…"


def visuals(sc: dict, sb: dict) -> str:
    p, bits = sc["props"], []
    if p.get("shot"):
        q = next((b["query"] for b in sb.get("broll_shots", []) if b["id"] == p["shot"]), p["shot"])
        bits.append(f"b-roll: {q}")
    if p.get("side_broll"):
        q = next((b["query"] for b in sb.get("broll_shots", []) if b["id"] == p["side_broll"]), p["side_broll"])
        bits.append(f"side b-roll: {q}")
    if p.get("image"):
        bits.append(f"image: {p['image']}")
    if p.get("set"):
        who = ", ".join(f"{x['cast']}({x.get('pose', 'idle')}/{x.get('expr', 'neutral')})" for x in p.get("people", []))
        bits.append(f"set {p['set']}: {who}")
    if sc.get("visual"):
        bits.append(sc["visual"])
    return "; ".join(bits)


def claims(sc: dict) -> str:
    out = []
    for c in sc["claims"]:
        tag = "GK" if c.get("general_knowledge") else ",".join(c.get("source_ids", []))
        if tag not in out:
            out.append(tag)
    return f"{len(sc['claims'])}: " + " · ".join(out)


def render(sb: dict, full: bool = False) -> str:
    wpm = T.default_wpm(sb)
    secs = [T.scene_seconds(s, wpm) for s in sb["scenes"]]
    total = sum(secs)
    n_claims = sum(len(s["claims"]) for s in sb["scenes"])
    gk = sum(1 for s in sb["scenes"] for c in s["claims"] if c.get("general_knowledge"))
    lines = [f"# Storyboard preview — {sb['lesson_id']}: {sb['title']}", "",
             f"**Language** {sb['language']} ({sb.get('direction', 'ltr')}) · **Formats** {', '.join(sb['formats'])} · "
             f"**Aspect** {sb['aspect']} · **Est.** {int(total // 60)}:{int(total % 60):02d} at {wpm} wpm · "
             f"**Scenes** {len(sb['scenes'])} · **Claims** {n_claims} ({gk} general knowledge)",
             f"**Cast** {', '.join(sb.get('cast', [])) or '—'} · **Voices** " +
             ", ".join(f"{k}={v['provider']}/{v['voice']}" for k, v in sb["voices"].items()),
             "", "| # | scene | template | ~s | narration (▸ = cue) | on screen | visuals | claims |",
             "|---|---|---|---|---|---|---|---|"]
    lim = None if full else 140
    for i, (sc, s) in enumerate(zip(sb["scenes"], secs), 1):
        narr = " / ".join(f"{'' if n['who'] == 'narrator' else n['who'] + ': '}{n['text'].replace('^', '▸')}"
                          for n in sc["narration"])
        ost = sc.get("on_screen_text") or T.derive_on_screen_text(sc)
        lines.append(f"| {i} | {sc['id']} | {sc['template']} | {s:.0f} | {cell(narr, lim)} | "
                     f"{cell(' • '.join(ost), None if full else 90)} | {cell(visuals(sc, sb), None if full else 70)} | "
                     f"{cell(claims(sc), None)} |")
    if sb.get("generated_images"):
        lines += ["", "**Generated images** (no text in images): " +
                  "; ".join(f"{g['id']}: {cell(g['prompt'], 80)}" for g in sb["generated_images"])]
    lines += ["", "Approve, or reply with edits (scene id + change)."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard")
    ap.add_argument("--out")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args(argv)
    sb = json.loads(Path(a.storyboard).read_text(encoding="utf-8"))
    md = render(sb, a.full)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
        print(f"wrote {a.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
