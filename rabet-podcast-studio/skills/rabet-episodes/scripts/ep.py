"""Shared bits for rabet-episodes: episode/spec loading, time formats, assets from ~/.rabet-reels.json.

episode.json (written by prep_episode.py, one per full episode):
  {"master": <HQ mp4>, "wav": <16 kHz mono>, "words": <words.json>, "proxy": <2 fps 64x36 rgb>,
   "shots": <shots.json [[s, e, who], ...]>, "split": [shot indexes that are multi-person split screens],
   "fps": 25, "width": 3840, "height": 2160, "duration": s, "teaser_offset": 0}
spec.json (one per mini / sub-episode): see references/spec.md.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REELS = SKILL.parent / "rabet-reels"
sys.path.insert(0, str(REELS / "scripts"))
from config import load as load_config  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")   # Arabic titles in output piped on Windows

WHOOSH = REELS / "assets/whoosh-short.mp3"
UTF8 = {**os.environ, "PYTHONIOENCODING": "utf-8"}        # child scripts print Arabic into a pipe
FONT = r"fontfile='C\:/Windows/Fonts/arial.ttf'"         # drawtext (ffmpeg on Windows has no fontconfig)


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def jsave(obj, p):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def resolve(base, p):
    """paths in a spec/episode file are absolute or relative to that file"""
    p = Path(str(p)).expanduser()
    return p if p.is_absolute() else (Path(base).parent / p).resolve()


def load_episode(path):
    ep = jload(path)
    for k in ("master", "wav", "words", "proxy", "shots"):
        if ep.get(k):
            ep[k] = str(resolve(path, ep[k]))
    return ep


def load_spec(path):
    """spec + its episode + assets (spec keys override episodes.* in ~/.rabet-reels.json)"""
    spec = jload(path)
    spec["_path"] = str(Path(path).resolve())
    spec["_episode"] = load_episode(resolve(path, spec["episode"]))
    assets = dict(load_config().get("episodes", {}))
    assets.update(spec.get("assets", {}))
    for k in ("intro", "outro", "out_dir"):
        if spec.get(k):
            assets[k] = spec[k]
        if assets.get(k):
            assets[k] = str(resolve(path, assets[k]))
    assets["name_cards"] = {w: str(resolve(path, p)) for w, p in assets.get("name_cards", {}).items()}
    spec["_assets"] = assets
    return spec


def probe_len(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout.strip())


def mm(t):
    return f"{int(t // 60):02d}m{int(t % 60):02d}"


def mmss(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:04.1f}" if h else f"{int(m)}:{s:04.1f}"


def dur(t):
    return f"{int(t // 60)}:{int(round(t % 60)):02d}"


def safe(s):
    s = s.replace("..", " -").replace("?", "").replace("؟", "")
    return re.sub(r'[\\/:*"<>|]', "", s).strip()


def render_meta_path(spec):
    return Path(spec["_path"]).with_suffix(".render.json")
