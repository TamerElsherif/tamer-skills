"""Shared helpers: audio loading, JSON, time formats, the work-folder layout.

Work folder (one per recording, e.g. projects/speaking-style/work/ep3/):
  audio.wav     16 kHz mono copy of the source
  turns.json    {"source", "speakers", "turns": [[start, end, who, margin], ...]}   (diarize.py)
  words.json    {"turns": [{"s", "e", "who", "words": [{"w", "s", "e", "p"}]}]}     (transcribe_turns.py)
Profiles (one per speaker, across recordings): projects/speaking-style/<speaker>/
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")      # Arabic output piped on Windows
HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parents[1]
CACHE = Path(os.path.expanduser("~/.cache/speaking-style"))
SR = 16000


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def jsave(obj, p):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def mmss(t):
    t = int(t)
    return f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def load_audio(src, work):
    """16 kHz mono float32 array; caches work/audio.wav (a 16 kHz mono wav source is used as is)"""
    import soundfile as sf
    src = Path(src)
    if src.suffix.lower() == ".wav":
        info = sf.info(str(src))
        if info.samplerate == SR and info.channels == 1:
            return sf.read(str(src), dtype="float32")[0]
    wav = Path(work) / "audio.wav"
    if not wav.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", str(SR), str(wav)],
                       check=True)
    return sf.read(str(wav), dtype="float32")[0]


def speech_mask(x, hop=0.01):
    """per-10 ms speech flag from frame level: above the noise floor and within 30 dB of the loud speech (reels with music beds: p20 is already speech)"""
    n = int(SR * hop)
    fr = x[: len(x) // n * n].reshape(-1, n)
    db = 10 * np.log10((fr ** 2).mean(1) + 1e-10)
    thr = max(np.percentile(db, 3) + 8, np.percentile(db, 95) - 30)
    return db > thr, db
