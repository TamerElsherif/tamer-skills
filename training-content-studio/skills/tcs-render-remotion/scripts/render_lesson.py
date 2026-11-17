"""One-shot video render for a lesson (prepare → render → QA grid), following the TCS run-folder contract.

usage:
  render_lesson.py <runs/<id>>            [--lesson M1L1] [--lang ar-EG] [--target video|video-vertical] [--draft]
  render_lesson.py <L>.storyboard.json    [--out DIR] [--target …] [--draft]
  common: [--engine remotion|openmontage] [--placeholder-voice] [--no-broll]

Run dir: reads runs/<id>/lessons/<L>/<L>[.<lang>].storyboard.json, writes runs/<id>/renders/<L>/<target>/
  <L>[.<lang>]_<16x9|9x16>.mp4 (+ .json report, .grid.jpg) and keeps the prepared work dir in work[.<lang>]/.
target video = 16:9 (or the storyboard's 1:1), video-vertical = 9:16.
Never fails the pipeline: if Node/ffmpeg/keys/renderer are unavailable it writes RENDER_PENDING.md (spec +
exact commands) into the target folder and exits 0.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _common import PLUGIN_ROOT, aspect_tag  # noqa: E402

PY = sys.executable
OM_SCRIPT = PLUGIN_ROOT / "skills" / "tcs-render-openmontage" / "scripts" / "om_render.py"


def find_storyboards(run: Path, lesson: str | None, lang: str | None) -> list[Path]:
    out = []
    for d in sorted((run / "lessons").glob("*")):
        if not d.is_dir() or (lesson and d.name != lesson):
            continue
        cand = d / (f"{d.name}.{lang}.storyboard.json" if lang else f"{d.name}.storyboard.json")
        if cand.exists():
            out.append(cand)
    return out


def pending(target_dir: Path, sb: Path, cmds: list[list[str]], reason: str) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    body = "\n".join(" ".join(shlex.quote(c) for c in cmd) for cmd in cmds)
    (target_dir / "RENDER_PENDING.md").write_text(
        f"# Render pending\n\n- storyboard: `{sb}`\n- reason: {reason}\n\n"
        "Requirements: Node.js ≥ 18, ffmpeg, `kit/setup.sh` (npm install). Optional keys (env or TCS_ENV_FILE): OPENAI_API_KEY (voice), PEXELS_API_KEY (b-roll).\n\n"
        f"Run from the plugin root `{PLUGIN_ROOT}`:\n\n```bash\n{body}\n```\n", encoding="utf-8")
    print(f"RENDER_PENDING → {target_dir / 'RENDER_PENDING.md'} ({reason})")


def render_one(sb: Path, target_dir: Path, target: str, a) -> dict | None:
    data = json.loads(sb.read_text(encoding="utf-8"))
    aspect = "9:16" if target == "video-vertical" else ("1:1" if data.get("aspect") == "1:1" else "16:9")
    lang_suffix = sb.name[: -len(".storyboard.json")].split(".", 1)[1] if sb.name.count(".") > 2 else ""
    work = target_dir / (f"work.{lang_suffix}" if lang_suffix else "work")
    stem = f"{data['lesson_id']}{'.' + lang_suffix if lang_suffix else ''}_{aspect_tag(aspect)}{'_draft' if a.draft else ''}"
    prep = [PY, str(HERE / "prepare.py"), str(sb), "--out", str(work), "--aspect", aspect] + (["--placeholder-voice"] if a.placeholder_voice else []) + (["--no-broll"] if a.no_broll else [])
    if a.engine == "openmontage":
        rend = [PY, str(OM_SCRIPT), str(work)] + (["--draft"] if a.draft else [])
    else:
        rend = [PY, str(HERE / "render.py"), str(work)] + (["--draft"] if a.draft else [])
    missing = [t for t in ("ffmpeg", "ffprobe", "node", "npx") if not shutil.which(t)]
    if missing:
        pending(target_dir, sb, [prep, rend], f"missing tools: {', '.join(missing)}")
        return None
    for cmd in (prep, rend):
        print("$", " ".join(shlex.quote(c) for c in cmd), flush=True)
        if subprocess.run(cmd).returncode != 0:
            pending(target_dir, sb, [prep, rend], f"step failed: {Path(cmd[1]).name}")
            return None
    produced = sorted((work / "renders").glob(f"{data['lesson_id']}_*.mp4"), key=lambda p: p.stat().st_mtime)
    if not produced:
        pending(target_dir, sb, [prep, rend], "render produced no mp4")
        return None
    final = target_dir / f"{stem}.mp4"
    shutil.copy2(produced[-1], final)
    rep = produced[-1].with_suffix(".json")
    info = json.loads(rep.read_text()) if rep.exists() else {}
    info.update({"output": str(final), "target": target, "engine": a.engine, "missing_assets": json.loads((work / "missing_assets.json").read_text())})
    (target_dir / f"{stem}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    subprocess.run([PY, str(HERE / "stills.py"), "--video", str(final)])
    (target_dir / "RENDER_PENDING.md").unlink(missing_ok=True)
    print(json.dumps({k: info.get(k) for k in ("output", "duration_s", "target", "engine")}, indent=1))
    return info


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="run dir (runs/<id>) or a storyboard.json")
    ap.add_argument("--lesson")
    ap.add_argument("--lang")
    ap.add_argument("--target", choices=["video", "video-vertical"], action="append")
    ap.add_argument("--out", help="output dir when src is a storyboard (default: <storyboard dir>/renders/<L>)")
    ap.add_argument("--engine", choices=["remotion", "openmontage"], default="remotion")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--placeholder-voice", action="store_true")
    ap.add_argument("--no-broll", action="store_true")
    a = ap.parse_args()
    src = Path(a.src).resolve()
    targets = a.target or ["video"]
    jobs: list[tuple[Path, Path]] = []
    if src.is_dir():
        for sb in find_storyboards(src, a.lesson, a.lang):
            L = sb.parent.name
            jobs += [(sb, src / "renders" / L / t) for t in targets]
        if not jobs:
            sys.exit(f"no storyboards under {src}/lessons/ (lesson={a.lesson}, lang={a.lang})")
    else:
        L = json.loads(src.read_text())["lesson_id"]
        base = Path(a.out).resolve() if a.out else src.parent / "renders" / L
        jobs = [(src, base / t) for t in targets]
    for sb, td in jobs:
        td.mkdir(parents=True, exist_ok=True)
        render_one(sb, td, td.name, a)


if __name__ == "__main__":
    main()
