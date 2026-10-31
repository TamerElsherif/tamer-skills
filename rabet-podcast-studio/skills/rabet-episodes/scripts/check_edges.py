"""Before rendering: transcribe every hook/body piece on its own (rabet-reels edge_check.py, 1 s of silence around
each) and print its first and last words.  A clipped or stray word at an edge means the edge is wrong: move it to
another pause from pauses.py.  Only the first/last ~3 s of each piece are checked, so it stays fast on long pieces.

usage: python check_edges.py <spec.json> [--only 3,5,7]     (indexes as printed: H0.. hooks, B0.. body)
"""
import argparse
import subprocess
import sys
from pathlib import Path

from ep import UTF8, REELS, jsave, load_spec

EDGE = 3.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    spec = load_spec(a.spec)
    pieces = [(f"H{i}", h) for i, h in enumerate(spec.get("hook", []))] + \
             [(f"B{i}", b) for i, b in enumerate(spec["body"])]
    only = set(a.only.split(",")) - {""}
    cuts = []
    for lab, x in pieces:
        if only and lab not in only:
            continue
        s, e = x["in"], x["out"]
        if e - s <= 2 * EDGE + 1:
            cuts.append({"beat": f"{lab} whole", "parts": [[s, e]]})
        else:
            cuts += [{"beat": f"{lab} START", "parts": [[s, s + EDGE]]}, {"beat": f"{lab} END", "parts": [[e - EDGE, e]]}]
    work = Path(spec["_path"]).with_suffix("") / "edges"
    work.mkdir(parents=True, exist_ok=True)
    jsave(cuts, work / "cuts.json")
    subprocess.run([sys.executable, str(REELS / "scripts/edge_check.py"), spec["_episode"]["master"],
                    str(work / "cuts.json"), str(work)], check=True, cwd=REELS.parents[2], env=UTF8)
    print("\nexpected words: see each piece's first/last in the spec; START must begin on 'first', END finish on 'last'")


if __name__ == "__main__":
    main()
