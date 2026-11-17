"""QA contact sheets for a prepared run_dir (before rendering) or a finished MP4 (after).

usage:
  stills.py <run_dir> [--aspect A] [--at 3.5,12,40.2] [--scale 0.5]
      default: one still per scene, taken just after the scene's last cue (or mid-scene)
      → <run_dir>/qa/stills_<tag>/sheet.jpg (+ per-frame PNGs). LOOK at the sheet.
  stills.py --video <file.mp4> [--n 12]
      → evenly spaced frame grid next to the video: <file>.grid.jpg
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import aspect_tag, contact_sheet, ensure_kit, need, probe_duration  # noqa: E402
from render import props_for  # noqa: E402


def scene_frames(tl: dict) -> list[tuple[int, str]]:
    fps = tl["fps"]
    out = []
    for s in tl["scenes"]:
        dur = s["frames"] / fps
        last = max(s["cues"]) + 0.9 if s["cues"] else dur * 0.55
        t = min(dur - 0.4, max(dur * 0.3, last))
        out.append((s["from"] + int(t * fps), s["id"]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", nargs="?")
    ap.add_argument("--aspect")
    ap.add_argument("--at", help="comma-separated seconds")
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--video")
    ap.add_argument("--n", type=int, default=12)
    a = ap.parse_args()
    need("ffmpeg")
    if a.video:
        v = Path(a.video).resolve()
        d = probe_duration(v)
        tmp = v.parent / f".{v.stem}_grid"
        tmp.mkdir(exist_ok=True)
        imgs = []
        for i in range(a.n):
            t = d * (i + 0.5) / a.n
            f = tmp / f"g{i:02d}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(v), "-frames:v", "1", "-vf", "scale=640:-2", str(f)], check=True)
            imgs.append(f)
        portrait = "1920" in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=height", "-of", "csv=p=0", str(v)], capture_output=True, text=True).stdout
        out = contact_sheet(imgs, v.with_suffix(".grid.jpg"), cols=6 if portrait else 4, tile=(270, 480) if portrait else (480, 270))
        print(out)
        return
    if not a.run_dir:
        sys.exit("run_dir or --video required")
    run_dir = Path(a.run_dir).resolve()
    kit = ensure_kit()
    props, tl = props_for(run_dir, a.aspect)
    fps = tl["fps"]
    if a.at:
        frames = [(int(float(s) * fps), f"{s}s") for s in a.at.split(",")]
    else:
        frames = scene_frames(tl)
    out_dir = run_dir / "qa" / f"stills_{aspect_tag(tl.get('aspect', '16:9'))}"
    r = subprocess.run(["node", "scripts/stills.mjs", str(props), str(run_dir / "public"), str(out_dir), str(a.scale), *[str(f) for f, _ in frames]], cwd=kit)
    if r.returncode:
        sys.exit("still rendering failed")
    imgs = [out_dir / f"f{f:06d}.png" for f, _ in frames]
    portrait = tl["height"] > tl["width"] * 1.1
    square = not portrait and tl["width"] < tl["height"] * 1.2
    tile = (270, 480) if portrait else (400, 400) if square else (560, 315)
    sheet = contact_sheet(imgs, out_dir / "sheet.jpg", cols=6 if portrait else 4, tile=tile)
    (out_dir / "sheet.txt").write_text("\n".join(f"{i + 1}. {lab} (frame {f})" for i, (f, lab) in enumerate(frames)) + "\n")
    print(sheet)


if __name__ == "__main__":
    main()
