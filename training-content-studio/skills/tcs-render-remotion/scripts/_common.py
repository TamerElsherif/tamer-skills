"""Shared helpers for the TCS render scripts (env/keys, paths, ffmpeg, aspect sizes).

Keys are read from the environment or from the file named in TCS_ENV_FILE (KEY=VALUE lines).
Nothing here ever writes a key anywhere.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS.parent
PLUGIN_ROOT = SCRIPTS.parents[2]
KIT_DIR = Path(os.environ.get("TCS_KIT_DIR", PLUGIN_ROOT / "kit")).resolve()
SCHEMA_DIR = PLUGIN_ROOT / "schemas"

ASPECTS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}


def aspect_tag(aspect: str) -> str:
    return aspect.replace(":", "x")


_ENV_CACHE: dict[str, str] | None = None


def _env_file_values() -> dict[str, str]:
    global _ENV_CACHE
    if _ENV_CACHE is not None:
        return _ENV_CACHE
    vals: dict[str, str] = {}
    f = os.environ.get("TCS_ENV_FILE")
    if f and Path(f).expanduser().is_file():
        for line in Path(f).expanduser().read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", line)
            if not m or line.lstrip().startswith("#"):
                continue
            v = m.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
                v = v[1:-1]
            else:
                v = v.split(" #")[0].strip()
            vals[m.group(1)] = v
    _ENV_CACHE = vals
    return vals


def key(name: str) -> str | None:
    """Secret lookup: environment first, then TCS_ENV_FILE. Returns None when unset/empty."""
    v = os.environ.get(name) or _env_file_values().get(name)
    return v or None


def cache_dir(kind: str) -> Path:
    base = Path(os.environ.get("TCS_CACHE_DIR", Path.home() / ".cache" / "training-content-studio")).expanduser()
    d = base / kind
    d.mkdir(parents=True, exist_ok=True)
    return d


def need(tool: str) -> str:
    p = shutil.which(tool)
    if not p:
        sys.exit(f"error: `{tool}` not found on PATH (install ffmpeg / Node.js)")
    return p


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kw)


def probe_duration(f: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def has_audio(f: Path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def comp_id(s: str) -> str:
    """Remotion composition ids allow only [a-zA-Z0-9-]."""
    return re.sub(r"[^a-zA-Z0-9-]+", "-", s).strip("-") or "lesson"


def write_json(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def ensure_kit() -> Path:
    """Make sure kit/node_modules exists (runs kit/setup.sh once)."""
    if not (KIT_DIR / "node_modules" / "remotion").exists():
        print(f"installing render kit deps in {KIT_DIR} …", flush=True)
        run(["bash", str(KIT_DIR / "setup.sh")])
    return KIT_DIR


def contact_sheet(images: list[Path], out: Path, cols: int = 3, tile=(640, 360)) -> Path | None:
    """ffmpeg xstack grid of images (no Pillow needed)."""
    images = [p for p in images if p.exists()]
    if not images:
        return None
    w, h = tile
    args = ["ffmpeg", "-v", "error", "-y"]
    for p in images:
        args += ["-i", str(p)]
    n = len(images)
    scale = ";".join(f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x1E2448[v{i}]" for i in range(n))
    if n == 1:
        flt = f"{scale};[v0]null[out]"
    else:
        layout = "|".join(f"{(i % cols) * w}_{(i // cols) * h}" for i in range(n))
        flt = f"{scale};{''.join(f'[v{i}]' for i in range(n))}xstack=inputs={n}:layout={layout}:fill=0x10142E[out]"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(args + ["-filter_complex", flt, "-map", "[out]", "-frames:v", "1", "-q:v", "3", str(out)], check=True)
    return out
