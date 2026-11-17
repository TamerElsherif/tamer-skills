#!/usr/bin/env python3
"""SRT + WebVTT subtitles from storyboard narration (real timing if available, else wpm estimate).

Usage: subtitles.py <L>.<lang>.storyboard.json [--timing timing.json] [--field text|text_ar] [--out-dir DIR]
                    [--max-chars 42] [--max-lines 2] [--max-dur 7]
timing.json (from the renderer): {"lines": [{"scene_id": "s01_title", "idx": 0, "start": 0.35, "end": 4.10}, ...]}
(idx = narration line index within the scene; times in seconds from video start).
Without timing: scenes play back-to-back, line = lead/pause/hold defaults + words / wpm.
Writes <lesson>.<lang>.srt and .vtt (Arabic lines get U+200F RLM so punctuation sits correctly).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "tcs-storyboard" / "scripts"))
import sbtools as T  # noqa: E402

RLM = "‏"


def line_times(sb: dict, timing: dict | None) -> list[tuple[float, float, str, str]]:
    """[(start, end, text, scene_id)]"""
    out = []
    if timing:
        tmap = {(t["scene_id"], t["idx"]): t for t in timing.get("lines", [])}
    wpm = T.default_wpm(sb)
    clock = 0.0
    for sc in sb["scenes"]:
        t = clock + sc.get("lead", T.LEAD)
        for i, n in enumerate(sc["narration"]):
            words = len(T.strip_cues(n["text"]).split())
            dur = words * 60 / wpm
            t += n.get("pre", 0)
            if timing and (sc["id"], i) in tmap:
                tt = tmap[(sc["id"], i)]
                out.append((tt["start"], tt["end"], n, sc["id"]))
            else:
                out.append((t, t + dur, n, sc["id"]))
            t += dur + n.get("pause", T.PAUSE)
        clock = max(t - T.PAUSE + sc.get("hold", T.HOLD), clock + (sc.get("min_s") or 0))
    return out


def split_text(text: str, max_chars: int, max_lines: int) -> list[str]:
    """Split into cue blocks of ≤ max_lines lines of ≤ max_chars, preferring sentence/clause breaks."""
    words, blocks, cur = text.split(), [], ""
    limit = max_chars * max_lines - 4
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            blocks.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
            if re.search(r"[.!?؟]$", w) and len(cur) > limit * 0.5:
                blocks.append(cur)
                cur = ""
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        if len(b) <= max_chars:
            out.append(b)
            continue
        ws = b.split()
        splits = [(" ".join(ws[:i]), " ".join(ws[i:])) for i in range(1, len(ws))]
        ok = [x for x in splits if len(x[0]) <= max_chars and len(x[1]) <= max_chars]
        a, c = min(ok, key=lambda x: abs(len(x[0]) - len(x[1]))) if ok else splits[0] if splits else (b, "")
        out.append(f"{a}\n{c}" if c else a)
    return out


def cues(sb: dict, timing: dict | None, field: str, max_chars: int, max_lines: int, max_dur: float):
    ar = sb["language"].startswith("ar") or field == "text_ar"
    res = []
    for start, end, n, _sid in line_times(sb, timing):
        text = T.strip_cues(n.get(field) or n["text"])
        if not text:
            continue
        blocks = split_text(text, max_chars, max_lines)
        total = sum(len(b) for b in blocks) or 1
        t = start
        for b in blocks:
            d = (end - start) * len(b) / total
            d = min(d, max_dur) if d > max_dur and len(blocks) > 1 else d
            body = "\n".join(RLM + ln for ln in b.split("\n")) if ar else b
            res.append((t, t + d, body))
            t += d
    return res


def ts(sec: float, sep: str) -> str:
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d}{sep}{ms % 1000:03d}"


def to_srt(cs) -> str:
    return "\n".join(f"{i}\n{ts(a, ',')} --> {ts(b, ',')}\n{t}\n" for i, (a, b, t) in enumerate(cs, 1))


def to_vtt(cs) -> str:
    return "WEBVTT\n\n" + "\n".join(f"{ts(a, '.')} --> {ts(b, '.')}\n{t}\n" for a, b, t in cs)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard")
    ap.add_argument("--timing")
    ap.add_argument("--field", default="text", choices=["text", "text_ar"])
    ap.add_argument("--out-dir")
    ap.add_argument("--max-chars", type=int, default=42)
    ap.add_argument("--max-lines", type=int, default=2)
    ap.add_argument("--max-dur", type=float, default=7.0)
    a = ap.parse_args(argv)
    p = Path(a.storyboard)
    sb = json.loads(p.read_text(encoding="utf-8"))
    timing = json.loads(Path(a.timing).read_text()) if a.timing else None
    cs = cues(sb, timing, a.field, a.max_chars, a.max_lines, a.max_dur)
    lang = "ar-EG" if a.field == "text_ar" and not sb["language"].startswith("ar") else sb["language"]
    out = Path(a.out_dir) if a.out_dir else p.parent
    base = out / f"{sb['lesson_id']}.{lang}"
    Path(str(base) + ".srt").write_text(to_srt(cs), encoding="utf-8")
    Path(str(base) + ".vtt").write_text(to_vtt(cs), encoding="utf-8")
    print(f"wrote {base}.srt/.vtt ({len(cs)} cues, {'real' if timing else 'estimated'} timing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
