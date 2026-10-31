"""Build a teaser / promo / cold open from a list of moments: hard cuts, optional name cards, optional music bed,
optional end card (logo sting or "full episode on YouTube" outro). Works on any source: a full episode, a mini
episode or a reel (16:9 or 9:16).

usage: python make_teaser.py teaser.json [--dry-run] [--no-snap]
teaser.json:
{
  "source": "<episode or clip>.mp4",
  "out": "<folder>/Ep4_Teaser.mp4",
  "pieces": [
    {"in": 1810.2, "out": 1817.9, "who": "Tamer", "first": "Nokia كانت", "last": "وفجأة", "card": "Tamer"},
    {"in": 4067.5, "out": 4072.0, "who": "Hossam", "first": "اكتر من 50 %", "last": "مكتوب بAI"}
  ],
  "music": {"file": "<bed>.wav", "under_db": 15, "duck_db": 6},   (optional; bed sits under the voice, ducks on speech)
  "end": "intro" | "outro" | "<path>.mp4" | null                     (logo sting from ~/.rabet-reels.json episodes)
}
Times are SOURCE seconds and only need to be close (within ~0.4 s): each in/out is moved into the nearest real word
gap with rabet-reels cutsafe (rule 13: never cut inside a word). CutError = the speech runs on: pick another
phrase end. After rendering, check every edge with rabet-reels edge_check.py (this script prints the command).
Name cards ("card": key of episodes.name_cards) start 0.25 s into that piece; give each speaker one card, on a solo
shot. Writes <out> + <out>.cuts.json (snapped times, for edge_check and for reuse as a cold open in a spec "hook").
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REELS = HERE.parent.parent / "rabet-reels"
sys.path.insert(0, str(REELS / "scripts"))
from config import load  # noqa: E402
from cutsafe import CutError, Env  # noqa: E402

FADE = 0.025


def probe(path):
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                      "stream=codec_type,width,height,r_frame_rate", "-of", "json", path],
                                     capture_output=True, text=True, check=True).stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    n, d = v["r_frame_rate"].split("/")
    return v["width"], v["height"], round(int(n) / int(d), 3)


def snap(spec, enabled):
    pieces = spec["pieces"]
    if not enabled:
        return [(p["in"], p["out"]) for p in pieces]
    env, out = Env(spec["source"]), []
    for k, p in enumerate(pieces, 1):
        try:
            a, b = env.safe_in(p["in"]), env.safe_out(p["out"])
        except CutError as e:
            sys.exit(f"piece {k} ({p.get('first', '')} … {p.get('last', '')}): {e} -> end it at another phrase break")
        out.append((round(a, 3), round(b, 3)))
        print(f"piece {k}: {p['in']:.2f}-{p['out']:.2f} -> {a:.3f}-{b:.3f}  {p.get('who', '')}: "
              f"{p.get('first', '')} … {p.get('last', '')}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-snap", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    eps = load().get("episodes", {})
    src, out = spec["source"], spec["out"]
    W, H, fps = probe(src)
    cuts = snap(spec, not a.no_snap)
    total = sum(b - x for x, b in cuts)
    print(f"teaser body {total:.2f} s from {len(cuts)} pieces")
    json.dump([{"beat": f"piece {k} {p.get('who', '')}", "parts": [list(c)]}
               for k, (p, c) in enumerate(zip(spec["pieces"], cuts), 1)],
              open(out + ".cuts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if a.dry_run:
        return
    args, fc, t, cards = [], [], 0.0, []
    for i, (p, (x, b)) in enumerate(zip(spec["pieces"], cuts)):
        d = b - x
        args += ["-ss", f"{x:.3f}", "-t", f"{d:.3f}", "-i", src]
        fc.append(f"[{i}:v]fps={fps},scale={W}:{H},setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d={FADE},afade=t=out:st={d - FADE:.3f}:d={FADE}[a{i}]")
        if p.get("card"):
            cards.append((p["card"], t + 0.25))
        t += d
    n = len(cuts)
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[tv][ta]")
    cur, k = "tv", n
    for j, (who, st) in enumerate(cards):
        args += ["-i", eps["name_cards"][who]]
        fc.append(f"[{k}:v]scale={W}:{H}:flags=lanczos,setpts=PTS-STARTPTS+{st:.3f}/TB[c{j}]")
        fc.append(f"[{cur}][c{j}]overlay=0:0:eof_action=pass:format=auto[o{j}]")
        cur, k = f"o{j}", k + 1
    acur = "ta"
    m = spec.get("music")
    if m:
        args += ["-stream_loop", "-1", "-i", m["file"]]
        fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},"
                  f"volume=-{m.get('under_db', 15)}dB,afade=t=in:d=1,afade=t=out:st={max(0, total - 1.2):.3f}:d=1.2[bed]")
        fc.append("[ta]asplit[tv1][sc]")
        fc.append(f"[bed][sc]sidechaincompress=threshold=0.03:ratio={1 + m.get('duck_db', 6)}:attack=20:release=350[bd]")
        fc.append("[tv1][bd]amix=inputs=2:normalize=0:duration=first[tm]")
        acur, k = "tm", k + 1
    end = spec.get("end")
    end = eps.get(end, end) if end in ("intro", "outro") else end
    if end:
        args += ["-i", end]
        fc.append(f"[{k}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
                  f"fps={fps},setsar=1,format=yuv420p[ev]")
        fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo[ea]")
        fc.append(f"[{cur}][{acur}][ev][ea]concat=n=2:v=1:a=1[ov][oa]")
        cur, acur = "ov", "oa"
    fpath = out + ".filter.txt"
    open(fpath, "w", encoding="utf-8").write(";\n".join(fc))
    base = ["ffmpeg", "-v", "error", "-stats", "-y", *args, "-/filter_complex", fpath, "-map", f"[{cur}]",
            "-map", f"[{acur}]", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart"]
    nv = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "20", "-b:v", "16M", "-maxrate", "28M"]
    try:
        if subprocess.run(base + nv + [out]).returncode != 0:
            subprocess.run(base + ["-c:v", "libx264", "-crf", "18", out], check=True)
    finally:
        os.remove(fpath)
    print("wrote", out)
    print("check every edge (whole first/last words):\n  python",
          REELS / "scripts/edge_check.py", f'"{src}"', f'"{out}.cuts.json"')


if __name__ == "__main__":
    main()
