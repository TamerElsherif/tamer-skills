"""One-time prep of a full episode master for cutting mini / sub-episodes.

Writes into <work_dir>:
  episode.wav              16 kHz mono (cutsafe + edge checks)
  episode.words.json       Whisper large-v3 word timings (GPU), via rabet-reels transcribe_words.py
  episode_2fps_64x36.rgb   tiny picture proxy: camera changes + "same framing?" tests for jump-cut punch-ins
  shots.json               [[start, end, "?"], ...] camera shots (proxy frame jump > 20)
  shots_sheetN.jpg         one labelled frame per shot >= 6 s: fill in who is on screen ("Tamer", "split", ...)
  transcript.txt           readable transcript, a stamp at each pause > 0.6 s
  episode.json             pointers + fps/size/duration (load with ep.load_episode)

Word times drift on long files (Ep 3: unreliable after ~1:35). Use them to find the words, never as cut points:
cut points come from pauses.py (audio level) and are verified with check_edges.py.

usage: python prep_episode.py <master.mp4> <work_dir> [--teaser-offset S] [--skip-words]
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

from ep import FONT, REELS, jload, jsave, mmss, probe_len


def shots_from_proxy(proxy, min_len=1.0):
    P = np.fromfile(proxy, np.uint8).reshape(-1, 36, 64, 3).astype(np.float32)
    d = np.abs(P[1:] - P[:-1]).mean(axis=(1, 2, 3))
    cuts = [0.0] + [(i + 1) / 2 for i in np.where(d > 20)[0]] + [len(P) / 2]
    out = []
    for a, b in zip(cuts, cuts[1:]):
        if out and b - a < min_len:          # flashes / swipes: fold into the previous shot
            out[-1][1] = float(b)
        else:
            out.append([float(a), float(b), "?"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("master")
    ap.add_argument("work")
    ap.add_argument("--teaser-offset", type=float, default=0.0)
    ap.add_argument("--skip-words", action="store_true")
    a = ap.parse_args()
    work = Path(a.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    master = Path(a.master).resolve()
    wav, words, proxy = work / "episode.wav", work / "episode.words.json", work / "episode_2fps_64x36.rgb"
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(master)],
                          capture_output=True, text=True).stdout.strip().split(",")
    w, h, (fn, fd) = int(info[0]), int(info[1]), info[2].split("/")
    if not wav.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-vn", "-ac", "1", "-ar", "16000", str(wav)],
                       check=True)
    if not proxy.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-vf", "fps=2,scale=64:36:flags=area",
                        "-pix_fmt", "rgb24", "-f", "rawvideo", str(proxy)], check=True)
    shots_p = work / "shots.json"
    shots = jload(shots_p) if shots_p.exists() else shots_from_proxy(proxy)
    jsave(shots, shots_p)
    long = [(k, s, e) for k, (s, e, _) in enumerate(shots) if e - s >= 6]
    tiles = []
    for k, s, e in long:
        p = work / f"_shot{k}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(s + e) / 2:.2f}", "-i", str(master), "-frames:v", "1",
                        "-vf", f"scale=320:-2,drawtext={FONT}:text='{k} {mmss(s).replace(':', chr(92) + ':')}':x=6:y=6:fontsize=22:fontcolor=white:"
                        "box=1:boxcolor=black@0.6", str(p)], check=True)
        tiles.append(p)
    for i in range(0, len(tiles), 48):     # sheets of 8x6
        chunk = tiles[i:i + 48]
        args = sum([["-i", str(p)] for p in chunk], [])
        lay = "|".join(f"{(j % 8) * 320}_{(j // 8) * 180}" for j in range(len(chunk)))
        f = f"xstack=inputs={len(chunk)}:layout={lay}:fill=black" if len(chunk) > 1 else "null"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", f,
                        str(work / f"shots_sheet{i // 48 + 1}.jpg")], check=True)
    for p in tiles:
        p.unlink()
    if not words.exists() and not a.skip_words:
        subprocess.run([sys.executable, str(REELS / "scripts/transcribe_words.py"), str(wav), str(words)], check=True)
    if words.exists():
        lines, cur, prev = [], [], None
        for x in jload(words)["words"]:
            if prev is None or x["s"] - prev > 0.6 or len(cur) >= 14:
                if cur:
                    lines.append(" ".join(cur))
                cur = [f"[{x['s']:.1f} {mmss(x['s'])}]"]
            cur.append(x["w"].strip())
            prev = x["e"]
        lines.append(" ".join(cur))
        (work / "transcript.txt").write_text("\n".join(lines), encoding="utf-8")
    ep = {"master": str(master), "wav": wav.name, "words": words.name, "proxy": proxy.name, "shots": shots_p.name,
          "split": [], "fps": round(int(fn) / int(fd), 3), "width": w, "height": h, "duration": probe_len(master),
          "teaser_offset": a.teaser_offset}
    old = work / "episode.json"
    if old.exists():                         # keep hand edits (split list, teaser offset)
        ep.update({k: v for k, v in jload(old).items() if k in ("split", "teaser_offset")})
    jsave(ep, old)
    print(f"wrote {old}  ({len(shots)} shots, {len(long)} on the sheet{'s' if len(tiles) > 48 else ''})")
    print("next: label shots.json 'who' from the sheet (speaker name, or 'split' for multi-person frames) and put the "
          "split-screen shot indexes in episode.json 'split'")


if __name__ == "__main__":
    main()
