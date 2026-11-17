#!/usr/bin/env python3
"""QA helper: screenshot every scene of a rendered lesson (or deck) with headless Chrome.

Usage: .venv/bin/python skills/tcs-render-lesson/tests/shoot.py <dir>/index.html --out <png dir>
        [--size 1280,900] [--scenes a,b] [--page deck.html]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _common import chrome  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--size", default="1280,900")
    ap.add_argument("--scenes", default="")
    ap.add_argument("--query", default="", help="e.g. reveal=1 to reveal all progressive elements")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    html = a.html.resolve()
    text = html.read_text(encoding="utf-8")
    ids = a.scenes.split(",") if a.scenes else re.findall(r'data-scene="([^"]+)"', text)
    if not ids:
        ids = [m for m in re.findall(r'id="slide-(\d+)"', text)]
    for sid in ids:
        png = a.out / f"{sid}.png"
        frag = f"#s-{sid}" if "data-scene" in text else f"#{sid}"
        r = chrome([f"--window-size={a.size}", "--virtual-time-budget=4000", f"--screenshot={png}", html.as_uri() + (f"?{a.query}" if a.query else "") + frag])
        if r is None:
            sys.exit("Chrome not found")
        print(png, "ok" if png.exists() else r.stderr[-300:])


if __name__ == "__main__":
    main()
