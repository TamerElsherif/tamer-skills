"""Add the Rabet follow & subscribe pop-up (white card, Subscribe click, bell ring, sound) to any video.

usage:
  python add_subscribe.py <video> <time> [<time> ...] [options]
    times: 4:30   1:01:50   270.5   (pop-up starts there and stays 6 s)

options:
  -o, --out FILE      output file (default: "<video name> - Subscribe.mp4" next to the video)
  --lang en|ar        button text: SUBSCRIBE / اشترك (default en)
  --pos br|bl|tr|tl|bc|tc  bottom-right (default), bottom-left, top-right, top-left, bottom-centre, top-centre
  --clear-logo        bottom-right but shifted left so the card clears the burned-in Rabet logo (EP1 masters)
  --x N --y N         exact top-left position in pixels (overrides --pos)
  --size F            card height as a fraction of the video height (default 0.204 = 220 px on 1080p)
  --sfx F             sound-effect volume (default 0.6, sits under the voice; 0 = silent)
  --test              render only 16 s around each time (<out>_testN.mp4) to check placement fast

examples:
  python add_subscribe.py "Ep 4 Final.mp4" 4:30 32:03 1:01:50 1:18:59
  python add_subscribe.py "Ep 1 Final.mp4" 4:30 --clear-logo --test
  python add_subscribe.py "Reel.mp4" 0:20 --pos tc --size 0.12

Works for any size (16:9, 9:16, 4K). The card never gets wider than 92 % of the frame.
Encodes with NVIDIA NVENC when available (fast), otherwise libx264. Audio: AAC 256k.
Pop-up source: Rabet_Subscribe_<LANG>_4K.mov next to this script or in $RABET_SUBSCRIBE_DIR; otherwise it is rendered
once with ../../rabet-episodes/scripts/render_cta.py (HyperFrames) and cached.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 6.0
CARD_W, CARD_H = 2000, 440            # source pixels of the pop-up MOV


def secs(t):
    parts = [float(p) for p in str(t).split(":")]
    s = 0.0
    for p in parts:
        s = s * 60 + p
    return s


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    return v["width"], v["height"], float(info["format"]["duration"]), has_audio


def placement(a, W, H):
    h = round(H * a.size)
    w = round(h * CARD_W / CARD_H)
    if w > W * 0.92:                                   # vertical videos: limit by width
        w = round(W * 0.92)
        h = round(w * CARD_H / CARD_W)
    w -= w % 2
    h -= h % 2
    m = round(H * 30 / 1080)                           # margin, 30 px at 1080p
    if a.x is not None and a.y is not None:
        return w, h, a.x, a.y
    if a.clear_logo:                                   # right edge at x≈1650 of 1920 (left of the logo bug)
        return w, h, round(W * 1650 / 1920) - w, H - h - m
    pos = {"br": (W - w - m, H - h - m), "bl": (m, H - h - m), "tr": (W - w - m, m), "tl": (m, m),
           "bc": ((W - w) // 2, H - h - m), "tc": ((W - w) // 2, m)}
    return (w, h, *pos[a.pos])


def popup_files(lang):
    """(mov, wav): wav is None when the MOV carries the sound.
    1. Rabet_Subscribe_<LANG>_4K.mov next to this script or in $RABET_SUBSCRIBE_DIR (exported, sound inside)
    2. otherwise the rabet-episodes cache, rendered on first use by render_cta.py (MOV + separate WAV)"""
    name = f"Rabet_Subscribe_{lang.upper()}_4K.mov"
    for d in (os.environ.get("RABET_SUBSCRIBE_DIR"), HERE):
        if d and os.path.exists(os.path.join(d, name)):
            return os.path.join(d, name), None
    sys.path.insert(0, os.path.join(HERE, "..", "..", "rabet-episodes", "scripts"))
    from render_cta import render                     # noqa: E402 (HyperFrames render, ~1 min, then cached)
    mov, wav = render(lang)
    return str(mov), str(wav)


def build(a, video, times, out, W, H, has_audio, window=None):
    mov, wav = popup_files(a.lang)
    w, h, x, y = placement(a, W, H)
    t0 = window[0] if window else 0.0
    inputs = (["-ss", f"{window[0]:.3f}", "-t", f"{window[1] - window[0]:.3f}"] if window else []) + ["-i", video]
    fc, vlast, alabels, n = [], "0:v", [], 1
    for i, t in enumerate(times):
        t -= t0
        inputs += ["-i", mov] + (["-i", wav] if wav else [])
        fc.append(f"[{n}:v]scale={w}:{h}:flags=lanczos,setpts=PTS-STARTPTS+{t:.3f}/TB[c{i}]")
        fc.append(f"[{vlast}][c{i}]overlay=x={x}:y={y}:eof_action=pass:format=auto[v{i}]")
        vlast = f"v{i}"
        if a.sfx > 0:
            ms = max(0, int(round(t * 1000)))
            src = n + 1 if wav else n
            fc.append(f"[{src}:a]aresample=48000,aformat=channel_layouts=stereo,volume={a.sfx},adelay={ms}|{ms}[s{i}]")
            alabels.append(f"[s{i}]")
        n += 2 if wav else 1
    amap = []
    if has_audio:
        fc.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[main]")
        if alabels:
            fc.append(f"[main]{''.join(alabels)}amix=inputs={len(alabels) + 1}:normalize=0:duration=first[aout]")
            amap = ["-map", "[aout]"]
        else:
            amap = ["-map", "[main]"]
    elif alabels:
        fc.append(f"{''.join(alabels)}amix=inputs={len(alabels)}:normalize=0[aout]")
        amap = ["-map", "[aout]"]
    fpath = os.path.splitext(out)[0] + ".filter.txt"
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(";\n".join(fc))
    base = ["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-/filter_complex", fpath, "-map", f"[{vlast}]", *amap]
    tail = ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out]
    nvenc = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "21", "-b:v", "16M", "-maxrate", "28M",
             "-bufsize", "32M", "-profile:v", "high"]
    x264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "18"]
    try:
        if subprocess.run(base + nvenc + tail).returncode != 0:
            print("NVENC not available, encoding with libx264 (slower)")
            subprocess.run(base + x264 + tail, check=True)
    finally:
        os.remove(fpath)
    print("wrote", out, f"(card {w}x{h} at x={x}, y={y})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("times", nargs="+")
    ap.add_argument("-o", "--out")
    ap.add_argument("--lang", default="en", choices=["en", "ar"])
    ap.add_argument("--pos", default="br", choices=["br", "bl", "tr", "tl", "bc", "tc"])
    ap.add_argument("--clear-logo", action="store_true")
    ap.add_argument("--x", type=int)
    ap.add_argument("--y", type=int)
    ap.add_argument("--size", type=float, default=220 / 1080)
    ap.add_argument("--sfx", type=float, default=0.6)
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()

    W, H, dur, has_audio = probe(a.video)
    times = sorted(secs(t) for t in a.times)
    for t in times:
        if t + DUR > dur + 0.01:
            sys.exit(f"pop-up at {t:.1f}s would run past the end of the video ({dur:.1f}s)")
    for p, q in zip(times, times[1:]):
        if q - p < DUR:
            sys.exit(f"pop-ups at {p:.1f}s and {q:.1f}s overlap (each lasts {DUR:.0f}s)")
    out = a.out or os.path.splitext(a.video)[0] + " - Subscribe.mp4"
    if os.path.abspath(out) == os.path.abspath(a.video):
        sys.exit("output would overwrite the input; pass a different -o")
    if a.test:
        stem, ext = os.path.splitext(out)
        for k, t in enumerate(times, 1):
            win = (max(0.0, t - 4), min(dur, t + 12))
            build(a, a.video, [t], f"{stem}_test{k}{ext}", W, H, has_audio, window=win)
    else:
        build(a, a.video, times, out, W, H, has_audio)


if __name__ == "__main__":
    main()
