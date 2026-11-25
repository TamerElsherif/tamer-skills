"""Who speaks when, by voice (ECAPA speaker embeddings on the GPU), seeded from known moments of each speaker.

Seeds tell the model what each voice sounds like:
  --shots shots.json      camera labels [[start, end, who], ...] (multicam podcast: solo shots of a speaker).
                          Reaction shots make labels noisy, so seed windows that sound like someone else are
                          dropped (two refinement passes) before the voices are learned.
  --seed "Tamer=8-115,189-222" --seed "Hossam=222.5-276"   hand-picked moments (seconds or m:ss), any recording.
  --voices work/ep3/voices.npz   voices learned in an earlier run (every seeded run saves voices.npz); add
                          --min-sim ~0.35 so unknown voices and music become "?".
Several short clips (reels): join their audio into one work/<rec>/audio.wav with 2 s gaps and write
work/<rec>/parts.json {"parts": [[start, name], ...]} so the corpus cites "Reel 6 0:34" (see SKILL.md).
Then every 1.5 s speech window gets the closest voice; a window too close to two voices (overlap, laughter)
becomes "?". Neighbouring windows vote (5-window majority), same-speaker runs merge across pauses < 1 s.

usage: python diarize.py <video_or_wav> <work_dir> [--shots shots.json] [--seed NAME=a-b,c-d ...]
       [--min-margin 0.08]
writes <work_dir>/turns.json and prints speaking time per speaker + seed purity.
"""
import argparse
from collections import Counter
from pathlib import Path

import numpy as np
import torch

from common import CACHE, SR, jload, jsave, load_audio, mmss, speech_mask

WIN, HOP = 1.5, 0.5


def parse_t(s):
    p = s.split(":")
    return sum(float(v) * 60 ** i for i, v in enumerate(reversed(p)))


def encoder():
    from speechbrain.inference.speaker import EncoderClassifier
    from speechbrain.utils.fetching import LocalStrategy
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    return EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb", savedir=str(CACHE / "ecapa"),
                                          run_opts={"device": dev}, local_strategy=LocalStrategy.COPY), dev


def embed(x, starts, enc, dev, bs=64):
    n = int(WIN * SR)
    out = []
    for i in range(0, len(starts), bs):
        b = np.stack([x[int(s * SR): int(s * SR) + n] for s in starts[i:i + bs]])
        with torch.no_grad():
            e = enc.encode_batch(torch.from_numpy(b).to(dev)).squeeze(1).cpu().numpy()
        out.append(e / np.linalg.norm(e, axis=1, keepdims=True))
    return np.concatenate(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("work")
    ap.add_argument("--shots")
    ap.add_argument("--seed", action="append", default=[])
    ap.add_argument("--voices", help="voices.npz from an earlier diarize run: match these known voices")
    ap.add_argument("--min-margin", type=float, default=0.08)
    ap.add_argument("--min-sim", type=float, default=0.0,
                    help="below this similarity to every known voice = '?' (someone else, music); ~0.35 with --voices")
    ap.add_argument("--ignore", default="Intro,split,?,Outro", help="shot labels that are not a speaker")
    a = ap.parse_args()
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    x = load_audio(a.src, work)
    sp, _ = speech_mask(x)
    starts = np.arange(0, len(x) / SR - WIN, HOP)
    frac = np.array([sp[int(s * 100): int((s + WIN) * 100)].mean() for s in starts])
    keep = frac >= 0.5
    starts = starts[keep]
    print(f"{len(starts)} speech windows of {WIN}s; embedding...", flush=True)
    enc, dev = encoder()
    E = embed(x, starts, enc, dev)

    seeds = []                                    # (start, end, who)
    ignore = set(a.ignore.split(","))
    if a.shots:
        for s, e, who in jload(a.shots):
            if who not in ignore and e - s >= 4:
                seeds.append((s + 1, e - 1, who))
    for arg in a.seed:
        who, spans = arg.split("=", 1)
        for sp_ in spans.split(","):
            s, e = sp_.split("-")
            seeds.append((parse_t(s), parse_t(e), who))
    if a.voices:                                 # known voices from an earlier recording (no seeds needed)
        V = np.load(a.voices)
        names, C = [str(n) for n in V["names"]], V["centroids"]
        sim = E @ C.T
        purity = "known voices from " + a.voices
    else:
        names = sorted({w for _, _, w in seeds})
        mid = starts + WIN / 2
        lab = np.full(len(starts), -1)
        for s, e, who in seeds:
            lab[(mid >= s) & (mid <= e)] = names.index(who)
        use = lab >= 0
        for it in range(3):                      # learn voices, drop seed windows that sound like someone else
            C = np.stack([E[use & (lab == k)].mean(0) for k in range(len(names))])
            C /= np.linalg.norm(C, axis=1, keepdims=True)
            sim = E @ C.T
            if it < 2:
                use = (lab >= 0) & (sim.argmax(1) == lab)
        purity = {n: f"{(use & (lab == k)).sum()}/{(lab == k).sum()}" for k, n in enumerate(names)}
        np.savez(work / "voices.npz", names=np.array(names), centroids=C)

    srt = np.sort(sim, 1)
    margin = srt[:, -1] - srt[:, -2] if len(names) > 1 else srt[:, -1]
    best = np.where((margin >= a.min_margin) & (srt[:, -1] >= a.min_sim), sim.argmax(1), -1)
    print("best-voice similarity p10/p50/p90:", np.round(np.percentile(srt[:, -1], [10, 50, 90]), 2))
    vote = best.copy()
    for i in range(len(best)):                   # 5-window majority (2.5 s)
        c = Counter(best[max(0, i - 2): i + 3])
        v, n = c.most_common(1)[0]
        vote[i] = v if n >= 3 else best[i]

    cuts = [p[0] for p in jload(work / "parts.json")["parts"]] if (work / "parts.json").exists() else []
    part = np.searchsorted(cuts, starts + WIN / 2, side="right")      # joined clips: never merge across one
    turns = []                                   # each window owns its central hop
    for i, s in enumerate(starts):
        a0, b0 = s + (WIN - HOP) / 2, s + (WIN + HOP) / 2
        who = names[vote[i]] if vote[i] >= 0 else "?"
        if turns and turns[-1][2] == who and a0 - turns[-1][1] < 1.0 and part[i] == part[i - 1]:
            turns[-1][1] = b0
            turns[-1][3].append(float(margin[i]))
        else:
            turns.append([a0, b0, who, [float(margin[i])]])
    turns = [[round(s, 2), round(e, 2), w, round(float(np.median(m)), 3)] for s, e, w, m in turns if e - s >= 1.0]
    jsave({"source": str(Path(a.src).resolve()), "speakers": names, "turns": turns}, work / "turns.json")
    tot = Counter()
    for s, e, w, _ in turns:
        tot[w] += e - s
    print("seed windows kept (sound like the labelled speaker):", purity)
    print("speaking time:", {w: mmss(t) for w, t in tot.most_common()})
    print(f"wrote {work / 'turns.json'} ({len(turns)} turns)")


if __name__ == "__main__":
    main()
