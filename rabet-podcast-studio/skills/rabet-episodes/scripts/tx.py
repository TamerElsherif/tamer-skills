"""Compact transcript windows for picking pieces: a stamp at each pause > 0.4 s, every 8 words and at each
speaker (shot) change.  Times are source seconds; word times drift, so treat them as +-1 s.

usage: python tx.py <episode.json> <start> <end> [<start> <end> ...]     (seconds or m:ss)
"""
import sys

from ep import jload, load_episode


def sec(x):
    if ":" in x:
        p = [float(v) for v in x.split(":")]
        return sum(v * 60 ** (len(p) - 1 - i) for i, v in enumerate(p))
    return float(x)


def main():
    ep = load_episode(sys.argv[1])
    words = jload(ep["words"])["words"]
    shots = jload(ep["shots"])

    def who(t):
        return next((w for a, b, w in shots if a <= t < b), "?")

    a_ = [sec(x) for x in sys.argv[2:]]
    for a, b in zip(a_[::2], a_[1::2]):
        out, n, prev, ps = [], 0, None, None
        for x in words:
            if not a <= x["s"] <= b:
                continue
            sp = who(x["s"])
            if prev is None or x["s"] - prev > 0.4 or n >= 8 or sp != ps:
                out.append(f"\n[{x['s']:.2f}{' ' + sp[:3] if sp != ps else ''}]")
                n = 0
            out.append(x["w"].strip())
            n += 1
            prev, ps = x["e"], sp
        print(f"== {a}-{b}", " ".join(out), f"[end {prev or b:.2f}]\n")


if __name__ == "__main__":
    main()
