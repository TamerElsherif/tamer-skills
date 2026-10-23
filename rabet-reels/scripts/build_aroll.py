"""Build tightened A-rolls for every style of one reel from a reel spec (JSON).

Speech islands are found automatically (ffmpeg silencedetect inside spec.range),
tiny islands and filler-only islands are dropped, near islands are merged, each
island is padded, then the hook ranges (if any) are prepended. Every cut edge is then
moved into a real word gap (cutsafe.py: never inside a word, never on a whole second from
the sheet), and put on whichever neighbouring frame is quieter, with 12 ms fades per join.

usage: python build_aroll.py <reel_spec.json> [style ...]
writes <out_dir>/aroll_<style>.mp4 + aroll_<style>.segments.json
"""
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_CROPS = {
    "vertical": "crop=1216:2160:1700:0",
    "split": "crop=2430:2160:1180:0,scale=1216:1080",
}


def silences(src, a, b, noise_db, dmin):
    cmd = ["ffmpeg", "-hide_banner", "-ss", f"{a}", "-t", f"{b - a}", "-i", src, "-vn",
           "-af", f"silencedetect=noise={noise_db}dB:d={dmin}", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore").stderr
    starts = [float(x) + a for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) + a for x in re.findall(r"silence_end: ([\d.]+)", err)]
    if len(ends) < len(starts):
        ends.append(b)
    return list(zip(starts, ends))


def islands(a, b, sil):
    out, cur = [], a
    for s, e in sorted(sil):
        if s > cur:
            out.append([cur, s])
        cur = max(cur, e)
    if cur < b:
        out.append([cur, b])
    return out


def load_words(spec):
    p = spec.get("words_json")
    if not p:
        return []
    d = json.load(open(p, encoding="utf-8"))
    off = spec.get("words_offset", 0)
    if "words" in d:  # compact transcribe_words.py format
        return [(w["w"].strip(), w["s"] + off, w["e"] + off) for w in d["words"]]
    ws = d.get("word_timestamps") or [w for s in d.get("segments", []) for w in s.get("words", [])]
    return [(w["word"].strip(), w["start"] + off, w["end"] + off) for w in ws]


def body_segments(spec):
    out = []
    for a, b in spec.get("ranges") or [spec["range"]]:  # several sheet ranges are joined in order
        out += _body_range(spec, a, b)
    return out


def _body_range(spec, a, b):
    sil = silences(spec["source"], a, b, spec.get("noise_db", -32), spec.get("min_silence", 0.12))
    isl = [i for i in islands(a, b, sil) if i[1] - i[0] >= spec.get("min_island", 0.12)]
    words = load_words(spec)
    drop = set(spec.get("drop_words", []))
    if words and drop:
        keep = []
        for s, e in isl:
            inside = [w for w, ws, we in words if ws < e and we > s]
            if inside and all(w in drop for w in inside):
                continue
            keep.append([s, e])
        isl = keep
    for ds, de in spec.get("drop_ranges", []):  # manual fixes: breaths, fillers Whisper mis-timed
        isl = [i for i in isl if not (i[0] >= ds - 0.05 and i[1] <= de + 0.05)]
    pre, post, gap = spec.get("pad_pre", 0.06), spec.get("pad_post", 0.10), spec.get("merge_gap", 0.22)
    merged = []
    for s, e in isl:
        s, e = max(a, s - pre), min(b, e + post)
        if merged and s - merged[-1][1] < gap:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    from cutsafe import Env                      # surgical edges: sheet ranges are whole seconds
    env = Env(spec["source"])
    return [[env.safe_in(s), env.safe_out(e)] for s, e in merged]


def snap(t, fps):
    return round(round(t * fps) / fps, 3)


AUTO = {  # auto-framing: crop width in source px, face position inside the crop, output scale
    "auto-vertical": {"w": 1216, "face": 0.60, "scale": None},
    "auto-split": {"w": 2430, "face": 0.55, "scale": "1216:1080"},
}


def shot_map(spec, segs):
    """Cached [(start, end, face_x)] covering every segment — multi-camera masters."""
    cache = Path(spec["out_dir"]) / "shots.json"
    if cache.exists():
        return [tuple(x) for x in json.loads(cache.read_text())]
    from shots import shots
    out = []
    for a, b, _ in sorted(segs):
        if out and a < out[-1][1]:
            continue
        out += shots(spec["source"], a, b, spec.get("src_width", 3840))
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out))
    return out


def pieces(segs, smap):
    """Split segments at camera cuts; each piece carries the face x of its shot."""
    out = []
    for a, b, kind in segs:
        cuts = sorted({s for s, e, _ in smap if a < s < b})
        bounds = [a] + cuts + [b]
        for s, e in zip(bounds[:-1], bounds[1:]):
            if e - s < 0.12 and out and abs(out[-1][1] - s) < 1e-6:  # sliver: absorb into the contiguous previous piece
                out[-1] = (out[-1][0], e, out[-1][2], out[-1][3])
                continue
            if e - s < 0.04:
                continue
            m = (s + e) / 2
            fx = next((x for ss, ee, x in smap if ss <= m < ee), None)
            if fx is None:
                fx = min(smap, key=lambda t: abs((t[0] + t[1]) / 2 - m))[2]
            out.append((s, e, kind, fx))
    return out


def build(spec, style, body):
    st = spec["styles"][style]
    fps = spec.get("fps", 25)
    from cutsafe import Env
    env = Env(spec["source"])
    hooks = [(env.safe_in(h[0]), env.safe_out(h[1])) for h in st.get("hook", [])]
    segs = [(a, b, "hook") for a, b in hooks] + [(s, e, "body") for s, e in body]
    auto = AUTO.get(st["crop"])
    items = pieces(segs, shot_map(spec, segs)) if auto else [(a, b, k, None) for a, b, k in segs]
    base = max(0.0, math.floor((min(s for s, *_ in items) - 1.0) * fps) / fps)   # on the frame grid
    span = max(e for _, e, *_ in items) - base + 1.0
    parts, labels, meta, cursor = [], [], [], 0.0
    for i, (a, b, kind, fx) in enumerate(items):
        ra, rb = round(env.on_grid(a, fps) - base, 3), round(env.on_grid(b, fps) - base, 3)
        d = round(rb - ra, 3)
        vf = ""
        if auto:
            W = auto["w"]
            x = int(min(max(fx - auto["face"] * W, 0), spec.get("src_width", 3840) - W)) // 2 * 2
            vf = f",crop={W}:2160:{x}:0" + (f",scale={auto['scale']}" if auto["scale"] else "")
        parts.append(f"[0:v]trim=start={ra}:end={rb},setpts=PTS-STARTPTS{vf}[v{i}];"
                     f"[0:a]atrim=start={ra}:end={rb},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.012,afade=t=out:st={d - 0.012:.3f}:d=0.012[a{i}];")
        labels.append(f"[v{i}][a{i}]")
        meta.append({"kind": kind, "src_start": round(ra + base, 3), "src_end": round(rb + base, 3),
                     "start": round(cursor, 3), "end": round(cursor + d, 3)})
        cursor += d
    if auto:
        graph = "".join(parts) + "".join(labels) + f"concat=n={len(items)}:v=1:a=1[outv][ca]"
    else:
        crop = spec.get("crops", {}).get(st["crop"], DEFAULT_CROPS[st["crop"]])
        graph = "".join(parts) + "".join(labels) + f"concat=n={len(items)}:v=1:a=1[cv][ca];[cv]{crop}[outv]"
    out_dir = Path(spec["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"aroll_{style}.mp4"
    gfile = out_dir / f"graph_{style}.txt"  # long multi-shot graphs exceed the Windows command line
    gfile.write_text(graph, encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{base}", "-t", f"{span}", "-i", spec["source"],
                    "-/filter_complex", str(gfile), "-map", "[outv]", "-map", "[ca]",
                    "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-g", "12", "-pix_fmt", "yuv420p",
                    "-r", str(fps), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)], check=True)
    (out_dir / f"aroll_{style}.segments.json").write_text(
        json.dumps({"duration": round(cursor, 3), "segments": meta}, indent=1), encoding="utf-8")
    print(f"{out.name}: {cursor:.2f}s, {len(items)} pieces")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    body = body_segments(spec)
    for style in sys.argv[2:] or list(spec["styles"]):
        build(spec, style, body)
