"""Does the reel end where the idea ends? Check a planned end (or start) BEFORE building the A-roll.

Partner review of Ep 3 (2026-10-28): five reels stopped mid-thought («…المتخصصة» before «علشان تقدر تاخد القرار»,
«…كويسة» before «لكن ده مش معناه…») or inside the last word («كا-» of «كاش», run straight into the next speaker).
The sheet's whole seconds and the episode transcript (which drops words) were trusted; nobody listened past the end.

What it does:
  1. Whisper large-v3 on the source from <end - before> to <end + after> (its own pass, not the episode transcript)
     and prints the words with SOURCE times, marking the planned end with ||.
  2. Lists acoustic gaps (cutsafe) after the planned end and the first real gap after each of the next words,
     so a new end can be read straight off: "after «القرار» -> 359.88".
  3. With --cut T: isolated edge check of [T-5, T] and [T, T+1.5]. The first must end on the whole last word,
     the second must start on the next word (nothing of it before T). Put a verified T in the spec as an exact end.

usage (repo root, .venv python):
  python tail_check.py <source.mp4> <end_s> [--after 15] [--before 6] [--cut T]...
  python tail_check.py <source.mp4> <start_s> --start      (same, for an in point: reads 15 s BEFORE it)
Read the words after the mark. Keep extending while they continue the thought: «علشان / عشان / لكن / بس / ف… /
على مستوى…», the second half of «X ولا Y», or a parallel «طب بالنسبة لـ…» that answers the same question. Stop at a
speaker change, a new question, or a new topic.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cutsafe import Env  # noqa: E402


def arg(name, default, cast=float):
    if name in sys.argv:
        return cast(sys.argv[sys.argv.index(name) + 1])
    return default


def transcribe(src, a, dur, work):
    wav, js = os.path.join(work, "win.wav"), os.path.join(work, "win.words.json")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(dur), "-i", src, "-vn", "-ac", "1",
                    "-ar", "16000", wav], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, "transcribe_words.py"), wav, js], check=True,
                   stdout=subprocess.DEVNULL)
    return [dict(w, s=w["s"] + a, e=w["e"] + a) for w in json.load(open(js, encoding="utf-8"))["words"]]


def main():
    src, t = sys.argv[1], float(sys.argv[2])
    start = "--start" in sys.argv
    after, before = arg("--after", 15.0), arg("--before", 6.0)
    a, b = (t - after, t + before) if start else (t - before, t + after)
    work = tempfile.mkdtemp(prefix="tailcheck_")
    words = transcribe(src, max(0.0, a), b - max(0.0, a), work)
    out, marked = [], False
    for w in words:
        if not marked and w["s"] >= t:
            out.append("||")
            marked = True
        out.append(f"{w['w']}[{w['s']:.2f}]")
    print(f"== {'start' if start else 'end'} {t:.2f}  (Whisper word edges drift 50-300 ms; use the gaps below)")
    print(" ".join(out), flush=True)
    env = Env(src)
    lo, hi = (max(0.0, a) + 0.3, t + 2) if start else (t - 2, b - 0.3)
    print("\nreal pauses (cutsafe) with the words around them -> candidate cuts (middle of the pause):", flush=True)
    for ps, pe in env.pauses(lo, hi, 0.04):
        m = (ps + pe) / 2
        mid = lambda w: (w["s"] + w["e"]) / 2  # Whisper starts drift; midpoints place words around a pause better
        prev = [w["w"] for w in words if mid(w) < m][-2:]
        nxt = [w["w"] for w in words if mid(w) >= m][:2]
        print(f"  {ps:.3f}-{pe:.3f}  cut {m:.3f}   «{' '.join(prev)}» | «{' '.join(nxt)}»", flush=True)
    print("  Labels are approximate. A cut is verified only by --cut (isolated transcription of both sides).")
    print("  No pause between two words = they run together: end at another break.", flush=True)
    cuts = [float(sys.argv[i + 1]) for i, x in enumerate(sys.argv) if x == "--cut"]
    if cuts:
        parts = []
        for c in cuts:
            parts += [{"beat": f"{c:.3f} before", "parts": [[round(c - 5, 3), c]]},
                      {"beat": f"{c:.3f} after", "parts": [[c, round(c + 1.5, 3)]]}]
        cj = os.path.join(work, "cuts.json")
        json.dump(parts, open(cj, "w"))
        print("\nisolated edge check (before must end on the whole word, after must start on the next one):", flush=True)
        subprocess.run([sys.executable, os.path.join(HERE, "edge_check.py"), src, cj, os.path.join(work, "edge")])


if __name__ == "__main__":
    main()
