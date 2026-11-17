#!/usr/bin/env python3
"""Derive scenes[].on_screen_text from template props (every visible string, for translation, a11y, grounding).

Usage: derive_text.py <lesson>.storyboard.json [--write] [--force]
  default: print scene id + strings;  --write: fill missing on_screen_text in place;  --force: overwrite all.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sbtools as T  # noqa: E402


def derive_all(sb: dict, force: bool = False) -> int:
    n = 0
    for sc in sb["scenes"]:
        if force or sc.get("on_screen_text") is None:
            sc["on_screen_text"] = T.derive_on_screen_text(sc)
            n += 1
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    p = Path(a.storyboard)
    sb = json.loads(p.read_text(encoding="utf-8"))
    if a.write or a.force:
        n = derive_all(sb, a.force)
        p.write_text(json.dumps(sb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"on_screen_text set on {n} scene(s)")
    else:
        for sc in sb["scenes"]:
            print(f"{sc['id']}: {json.dumps(T.derive_on_screen_text(sc), ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
