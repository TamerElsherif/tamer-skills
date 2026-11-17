"""Render a prepared run_dir to MP4 with the standalone kit (Remotion), then loudness-normalise to -16 LUFS.

usage: .venv/bin/python skills/tcs-render-remotion/scripts/render.py <run_dir> [--draft] [--aspect 16:9|9:16|1:1]
                                                                    [--concurrency N] [--crf N]
Output: <run_dir>/renders/<lesson_id>_<WxH-tag>.mp4  (draft: *_draft.mp4, half scale, crf 28)
--aspect re-flows the same timeline to another aspect (b-roll is centre-cropped; re-run prepare.py
with --aspect for b-roll searched in that orientation).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ASPECTS, aspect_tag, ensure_kit, has_audio, need, probe_duration, write_json  # noqa: E402


def gl_args() -> list[str]:
    gl = os.environ.get("TCS_REMOTION_GL", "").strip() or ("angle" if sys.platform == "darwin" else "default")
    return [] if gl == "default" else [f"--gl={gl}"]


def props_for(run_dir: Path, aspect: str | None) -> tuple[Path, dict]:
    data = json.loads((run_dir / "timeline.json").read_text(encoding="utf-8"))
    tl = data["tl"]
    if aspect and aspect != tl.get("aspect"):
        tl["width"], tl["height"] = ASPECTS[aspect]
        tl["aspect"] = aspect
        p = run_dir / f"timeline_{aspect_tag(aspect)}.json"
        write_json(p, {"tl": tl})
        return p, tl
    return run_dir / "timeline.json", tl


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--aspect", choices=list(ASPECTS))
    ap.add_argument("--concurrency", type=int, default=max(2, (os.cpu_count() or 4) // 2))
    ap.add_argument("--crf", type=int)
    a = ap.parse_args()
    need("ffmpeg"); need("npx")
    run_dir = Path(a.run_dir).resolve()
    kit = ensure_kit()
    props, tl = props_for(run_dir, a.aspect)
    tag = aspect_tag(tl.get("aspect", "16:9"))
    out_dir = run_dir / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)
    final = out_dir / f"{tl['lesson_id']}_{tag}{'_draft' if a.draft else ''}.mp4"
    raw = final.with_suffix(".raw.mp4")
    cmd = ["npx", "remotion", "render", "src/index.ts", "tcs-lesson", str(raw), f"--props={props}",
           f"--public-dir={run_dir / 'public'}", f"--concurrency={a.concurrency}", f"--crf={a.crf or (28 if a.draft else 19)}",
           "--log=error", *gl_args()]
    if a.draft:
        cmd.append("--scale=0.5")
    t0 = time.time()
    print(" ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=kit)
    if r.returncode != 0 or not raw.exists():
        sys.exit(f"remotion render failed (exit {r.returncode})")
    if has_audio(raw):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                        "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)], check=True)
        raw.unlink()
    else:
        raw.replace(final)
    info = {"lesson_id": tl["lesson_id"], "output": str(final), "aspect": tl.get("aspect"), "duration_s": round(probe_duration(final), 2),
            "audio": has_audio(final), "render_s": round(time.time() - t0), "draft": a.draft}
    write_json(out_dir / f"{final.stem}.json", info)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
