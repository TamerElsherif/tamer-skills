"""Where can I cut near T?  Real pauses (cutsafe, audio level) around each time with the words on both sides, plus
a level strip so continuous speech is obvious.  Pick piece edges from these pauses, never from word times.

  level strip, 80 ms per char:  ' ' silence (< -30 dB under speech)  '.' quiet  ':' low  '#' speech
  "quietest" = the quietest 10 ms in the window: use it when two voices overlap and there is no real pause.

usage: python pauses.py <episode.json> <T> [<T> ...] [--win 4] [--min 0.12]      (T in seconds or m:ss)
"""
import argparse

import numpy as np

from ep import jload, load_episode, mmss
from cutsafe import Env
from tx import sec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("times", nargs="+")
    ap.add_argument("--win", type=float, default=4.0)
    ap.add_argument("--min", type=float, default=0.12, help="shortest pause to list (s)")
    a = ap.parse_args()
    ep = load_episode(a.episode)
    W = jload(ep["words"])["words"]
    env = Env(ep["wav"])
    for t in map(sec, a.times):
        lo, hi = t - a.win, t + a.win
        print(f"\n== ~{t:.2f} ({mmss(t)})")
        print("   words: " + " ".join(f"{w['w'].strip()}[{w['s']:.1f}]" for w in W if lo <= w["s"] <= hi))
        t0, level, speech, i0, i1 = env._range(lo, hi)
        seg = level[i0:i1] - speech
        k = int(np.argmin(np.convolve(seg, np.ones(2) / 2, "same")))
        strip = "".join(" " if b < -30 else "." if b < -20 else ":" if b < -12 else "#"
                        for b in (seg[j:j + 16].min() for j in range(0, len(seg), 16)))
        print(f"   level {lo:.1f} |{strip}| {hi:.1f}   quietest {t0 + (i0 + k) / 200:.3f} ({seg[k]:.0f} dB)")
        for ps, pe in env.pauses(lo, hi, a.min):
            mid = (ps + pe) / 2
            prev = [w["w"].strip() for w in W if (w["s"] + w["e"]) / 2 < mid and w["s"] > mid - 6][-3:]
            nxt = [w["w"].strip() for w in W if (w["s"] + w["e"]) / 2 >= mid][:3]
            print(f"   pause {ps:9.3f}-{pe:9.3f} ({pe - ps:.2f}s)  «{' '.join(prev)}» | «{' '.join(nxt)}»")


if __name__ == "__main__":
    main()
