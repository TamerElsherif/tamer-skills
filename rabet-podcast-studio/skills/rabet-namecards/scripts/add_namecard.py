"""Burn one or more name cards into a video (any size; the full-frame card is scaled to the video).

usage: python add_namecard.py <video> <card.mov>@<time> [<card.mov>@<time> ...] [-o out.mp4] [--test]
  time: 0:44  1:58  118.5   (card starts there; it lasts 6 s, or 4.3 s for fast cards)
  example: python add_namecard.py "Ep 4.mp4" NameCard_tamer.mov@0:44 NameCard_haitham.mov@1:58
Rules (rabet-reels / rabet-episodes): put each card on a SOLO shot of that speaker, early, once; never on a split
screen; keep it away from the subscribe pop-up (pop-up is bottom-right, card bottom-left, but not at the same moment
on small screens). Output: "<video> - Cards.mp4". --test renders 12 s around each card.
"""
import argparse
import json
import os
import subprocess
import sys


def secs(t):
    s = 0.0
    for p in str(t).split(":"):
        s = s * 60 + float(p)
    return s


def probe(path, entries):
    return json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "json", path],
                                     capture_output=True, text=True, check=True).stdout)


def build(video, cards, out, W, H, window=None):
    t0 = window[0] if window else 0.0
    inputs = (["-ss", f"{window[0]:.3f}", "-t", f"{window[1] - window[0]:.3f}"] if window else []) + ["-i", video]
    fc, cur = [], "0:v"
    for i, (mov, t) in enumerate(cards, 1):
        inputs += ["-i", mov]
        fc.append(f"[{i}:v]scale={W}:{H}:flags=lanczos,setpts=PTS-STARTPTS+{t - t0:.3f}/TB[c{i}]")
        fc.append(f"[{cur}][c{i}]overlay=0:0:eof_action=pass:format=auto[o{i}]")
        cur = f"o{i}"
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", f"[{cur}]",
           "-map", "0:a?", "-c:a", "copy", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    nvenc = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "21", "-b:v", "16M", "-maxrate", "28M"]
    if subprocess.run(cmd + nvenc + [out]).returncode != 0:
        subprocess.run(cmd + ["-c:v", "libx264", "-crf", "18", out], check=True)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("cards", nargs="+", help="card.mov@time")
    ap.add_argument("-o", "--out")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    info = probe(a.video, "stream=codec_type,width,height:format=duration")
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    W, H, dur = v["width"], v["height"], float(info["format"]["duration"])
    cards = []
    for c in a.cards:
        mov, _, t = c.rpartition("@")
        if not mov or not os.path.exists(mov):
            sys.exit(f"bad card argument (want path.mov@time): {c}")
        cards.append((mov, secs(t)))
    out = a.out or os.path.splitext(a.video)[0] + " - Cards.mp4"
    if a.test:
        stem, ext = os.path.splitext(out)
        for k, (mov, t) in enumerate(cards, 1):
            build(a.video, [(mov, t)], f"{stem}_test{k}{ext}", W, H, (max(0.0, t - 3), min(dur, t + 9)))
    else:
        build(a.video, cards, out, W, H)


if __name__ == "__main__":
    main()
