"""QA the rendered episode: transcribe 3.5 s before and 3 s after every joint (whole words on both sides?), probe the
streams, and build a contact sheet: swipe mid-points, each punch-in (before / after / when it ends), name cards
(+2.5 s) and each CTA pop-up (+1.0 s card in, +2.9 s bell rung).

usage: python qa_episode.py <spec.json>   -> <spec>/qa/joints.txt + sheet.jpg
"""
import subprocess
import sys
from pathlib import Path

from ep import FONT, UTF8, REELS, jload, jsave, load_spec, render_meta_path


def main():
    spec = load_spec(sys.argv[1])
    meta = jload(render_meta_path(spec))
    vid = Path(meta["out_dir"]) / meta["file"]
    qa = Path(spec["_path"]).with_suffix("") / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    t, joints, starts = 0.0, [], [0.0]
    for i, L in enumerate(meta["alen"][:-1]):
        t += L
        starts.append(t)
        s0, s1 = meta["segments"][i], meta["segments"][i + 1]
        joints.append((f"{i}:{s0[0]}->{s1[0]}({s1[2]})", t))
    cuts = []
    for lab, tj in joints:
        cuts += [{"beat": f"{lab} @{tj:.2f} BEFORE", "parts": [[round(tj - 3.5, 3), round(tj, 3)]]},
                 {"beat": f"{lab} @{tj:.2f} AFTER", "parts": [[round(tj, 3), round(tj + 3.0, 3)]]}]
    jsave(cuts, qa / "cuts.json")
    res = subprocess.run([sys.executable, str(REELS / "scripts/edge_check.py"), str(vid), str(qa / "cuts.json"),
                          str(qa / "ec")], cwd=REELS.parents[2], env=UTF8, capture_output=True, text=True,
                         encoding="utf-8").stdout
    lines = [f"{meta['file']}  total {meta['total']:.2f}s"] + [l for l in res.splitlines() if "BEFORE" in l or "AFTER" in l]
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "csv=p=0",
                            str(vid)], capture_output=True, text=True).stdout.split()
    lines.append("streams: " + " ".join(probe))
    (qa / "joints.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    shots = list(meta["swipes_at"])
    for k, T in meta["punch_in"].items():
        s = starts[int(k)]
        shots += [s - 0.3, s + 0.5, s + T + 0.3]
    shots += [tc + 2.5 for _, tc in meta["cards"]]
    shots += [x for tc in meta.get("cta", []) for x in (tc + 1.0, tc + 2.9)]
    tiles = []
    for k, ts in enumerate(shots):
        p = qa / f"f{k}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ts:.3f}", "-i", str(vid), "-frames:v", "1", "-vf",
                        f"scale=640:-1,drawtext={FONT}:text='{ts:.1f}':x=8:y=8:fontsize=24:fontcolor=white:box=1:"
                        "boxcolor=black@0.6", str(p)], check=True)
        tiles.append(p)
    if tiles:
        args = sum([["-i", str(p)] for p in tiles], [])
        lay = "|".join(f"{(i % 3) * 640}_{(i // 3) * 360}" for i in range(len(tiles)))
        f = f"xstack=inputs={len(tiles)}:layout={lay}:fill=black" if len(tiles) > 1 else "null"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", f, str(qa / "sheet.jpg")], check=True)
        for p in tiles:
            p.unlink()
    print("sheet:", qa / "sheet.jpg")


if __name__ == "__main__":
    main()
