"""Prepare a storyboard for rendering: validate → TTS + word timing → cue times → assets → timeline.

usage: .venv/bin/python skills/tcs-render-remotion/scripts/prepare.py <lesson>.storyboard.json --out <run_dir>
         [--quiz <lesson>.quiz.json] [--aspect 16:9|9:16|1:1] [--placeholder-voice] [--force-tts]
         [--music-dir DIR] [--sfx-dir DIR] [--no-broll]

Writes <run_dir>/: timeline.json, timeline.ts, public/ (audio, broll, images, music, sfx),
missing_assets.json, prepare_report.json, qa/broll_sheet.jpg (+ broll_sheet.txt).
Never blocks on missing keys or assets: uses placeholders and lists them in missing_assets.json.
Keys: OPENAI_API_KEY, PEXELS_API_KEY (optional PIXABAY_API_KEY) from env or the file in TCS_ENV_FILE.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import difflib
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from array import array
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (ASPECTS, PLUGIN_ROOT, SCHEMA_DIR, cache_dir, comp_id, contact_sheet, key, need,  # noqa: E402
                     probe_duration, write_json)

FPS_DEFAULT = 30
GAP = 0.28
OPENAI = "https://api.openai.com/v1"
AR_INSTR = {
    "ar-EG": "Speak natural, warm Egyptian Arabic (Masri) as used in a modern Cairo office; clear, friendly, unhurried, about 10% slower than normal conversation.",
    "ar-MSA": "Speak clear Modern Standard Arabic (Fusha) with a neutral, professional tone; unhurried, about 10% slower than normal conversation.",
}
MISSING: list[dict] = []


def miss(kind: str, ident: str, reason: str) -> None:
    MISSING.append({"kind": kind, "id": ident, "reason": reason, "placeholder": True})
    print(f"  ! {kind} {ident}: {reason}", flush=True)


# ------------------------------------------------------------------ validation
def validate(sb: dict) -> list[str]:
    import jsonschema
    schema = json.loads((SCHEMA_DIR / "storyboard.schema.json").read_text())
    v = jsonschema.Draft202012Validator(schema)
    errs = [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message[:300]}" for e in sorted(v.iter_errors(sb), key=lambda e: list(e.absolute_path))]
    return errs


def semantic_warnings(sb: dict) -> list[str]:
    w = []
    shots = {b["id"] for b in sb.get("broll_shots", [])}
    imgs = {g["id"] for g in sb.get("generated_images", [])}
    ids = set()
    for sc in sb["scenes"]:
        if sc["id"] in ids:
            w.append(f"duplicate scene id {sc['id']}")
        ids.add(sc["id"])
        p = sc["props"]
        for k in ("shot", "side_broll"):
            if p.get(k) and p[k] not in shots:
                w.append(f"{sc['id']}: {k} '{p[k]}' not in broll_shots (placeholder)")
        if sc["template"] == "image" and p.get("image") not in imgs:
            w.append(f"{sc['id']}: image '{p.get('image')}' not in generated_images (placeholder)")
        n_cues = sum(line["text"].count("^") for line in sc["narration"])
        need_n = {"bullets": len(p.get("items", [])), "icon_grid": len(p.get("items", [])), "steps": len(p.get("steps", [])),
                  "checklist": len(p.get("items", [])), "broll_panel": len(p.get("items", [])), "timeline": len(p.get("events", [])),
                  "do_dont": len(p.get("dont", [])) + len(p.get("do", [])), "process_flow": len(p.get("nodes", []))}.get(sc["template"])
        if need_n and n_cues and n_cues < need_n:
            w.append(f"{sc['id']}: {n_cues} cues for {need_n} items (rest spread evenly)")
    return w


# ------------------------------------------------------------------ audio helpers
def amp_env(f: Path, fps: int) -> str:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "12000", "-f", "s16le", "-"], capture_output=True).stdout
    a = array("h")
    a.frombytes(raw[: len(raw) // 2 * 2])
    hop = 12000 // fps
    n = len(a) // hop
    if n == 0:
        return ""
    rms = []
    for i in range(n):
        seg = a[i * hop:(i + 1) * hop]
        rms.append(math.sqrt(sum(x * x for x in seg) / hop) / 32768)
    ref = sorted(rms)[int(len(rms) * 0.95)] + 1e-6
    out = []
    for r in rms:
        v = min(1.0, r / ref) ** 0.7
        out.append("0" if r < ref * 0.12 else str(int(round(v * 9))))
    return "".join(out)


def fake_amp(dur: float, fps: int, seed: str) -> str:
    h = int(hashlib.sha1(seed.encode()).hexdigest()[:8], 16)
    return "".join(str((3 + ((i * 7 + h) % 11) // 2) if (i // 6 + h) % 5 else 0) for i in range(int(dur * fps)))


def words_of(text: str) -> list[str]:
    return [w for w in re.sub(r"\s+", " ", text.replace("^", " ")).strip().split(" ") if w]


def norm(w: str) -> str:
    w = re.sub(r"[ً-ْـ]", "", w.lower())  # Arabic diacritics/tatweel
    return re.sub(r"[^\w؀-ۿ]", "", w)


def cue_word_idx(text: str) -> list[int]:
    out, k = [], 0
    for chunk in text.split("^")[:-1]:
        k += len(chunk.split())
        out.append(k)
    return out


def align_cues(text: str, wstarts: list[tuple[str, float]], dur: float) -> list[float]:
    """Cue time = start of the first word after each '^' (whisper word timestamps; proportional fallback)."""
    tw = words_of(text)
    idxs = cue_word_idx(text)
    if not idxs:
        return []
    if not wstarts:
        chars = [len(w) + 1 for w in tw]
        total = sum(chars) or 1
        return [round(max(0.0, dur * sum(chars[:k]) / total - 0.1), 3) for k in idxs]
    ww = [norm(w) for w, _ in wstarts]
    sm = difflib.SequenceMatcher(a=[norm(w) for w in tw], b=ww, autojunk=False)
    amap: dict[int, int] = {}
    for blk in sm.get_matching_blocks():
        for j in range(blk.size):
            amap[blk.a + j] = blk.b + j
    out = []
    ns, nt = len(tw), len(wstarts)
    for k in idxs:
        if k >= ns:
            out.append(round(max(0.0, wstarts[-1][1]), 3))
            continue
        if k in amap:
            j = amap[k]
        else:  # nearest matched neighbours, else proportional
            left = max([a for a in amap if a < k], default=None)
            right = min([a for a in amap if a > k], default=None)
            if left is not None and right is not None and right > left:
                j = round(amap[left] + (amap[right] - amap[left]) * (k - left) / (right - left))
            else:
                j = round(k * nt / max(ns, 1))
        j = min(max(j, 0), nt - 1)
        out.append(round(max(0.0, wstarts[j][1] - 0.12), 3))
    return out


# ------------------------------------------------------------------ TTS
def voice_cfg(sb: dict, who: str) -> dict:
    v = dict(sb["voices"].get(who) or sb["voices"]["narrator"])
    lang = v.get("lang") or sb["language"]
    instr = v.get("instructions", "")
    if lang.startswith("ar"):
        extra = AR_INSTR.get(lang, AR_INSTR["ar-MSA"])
        instr = f"{instr} {extra}".strip() if extra.split(";")[0] not in instr else instr
        v.setdefault("speed", 0.9)
    v["instructions"] = instr
    v["lang"] = lang
    return v


def openai_tts(text: str, v: dict, out: Path, api_key: str) -> None:
    body = {"model": v.get("model") or "gpt-4o-mini-tts", "voice": v["voice"], "input": text, "response_format": "mp3"}
    if v.get("instructions"):
        body["instructions"] = v["instructions"]
    for attempt in range(4):
        r = requests.post(f"{OPENAI}/audio/speech", headers={"Authorization": f"Bearer {api_key}"}, json=body, timeout=120)
        if r.status_code == 200 and r.content:
            out.write_bytes(r.content)
            return
        if r.status_code in (429, 500, 502, 503) and attempt < 3:
            time.sleep(2 + attempt * 3)
            continue
        raise RuntimeError(f"OpenAI TTS {r.status_code}: {r.text[:200]}")


def whisper_words(f: Path, lang: str, api_key: str) -> list[tuple[str, float]]:
    with open(f, "rb") as fh:
        r = requests.post(f"{OPENAI}/audio/transcriptions", headers={"Authorization": f"Bearer {api_key}"},
                          files={"file": (f.name, fh, "audio/mpeg")},
                          data={"model": "whisper-1", "response_format": "verbose_json", "timestamp_granularities[]": "word",
                                "language": "ar" if lang.startswith("ar") else "en"}, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"whisper {r.status_code}: {r.text[:200]}")
    return [(w["word"], float(w["start"])) for w in r.json().get("words", [])]


def wpm_ok(words: int, dur: float, lang: str) -> bool:
    if words < 4:
        return True
    wpm = words / max(dur, 0.1) * 60
    lo, hi = (65, 200) if lang.startswith("ar") else (95, 230)
    if words < 12:  # short acted lines carry natural pauses
        lo -= 20
    return lo <= wpm <= hi


def synth_line(text: str, who: str, v: dict, run_dir: Path, fps: int, force: bool, placeholder: bool, wpm: int) -> dict:
    clean = " ".join(words_of(text))
    speed = float(v.get("speed", 1.0) or 1.0)
    provider = v.get("provider", "openai")
    api_key = key("OPENAI_API_KEY")
    h = hashlib.sha1(f"{provider}|{v.get('model')}|{v['voice']}|{v.get('instructions')}|{speed}|{clean}".encode()).hexdigest()[:14]
    rel = f"audio/{who}-{h}.mp3"
    dst = run_dir / "public" / rel
    use_real = provider == "openai" and api_key and not placeholder
    if not use_real:
        n = len(clean.split())
        dur = round(max(1.2, n / (wpm / 60.0)), 3)
        return {"src": "", "dur": dur, "amp": fake_amp(dur, fps, clean), "starts": [], "placeholder": True,
                "reason": "placeholder voice requested" if placeholder else (f"provider '{provider}' not supported by prepare.py" if provider != "openai" else "OPENAI_API_KEY missing")}
    cdir = cache_dir("tts")
    cmp3, cmeta = cdir / f"{h}.mp3", cdir / f"{h}.json"
    if cmp3.exists() and cmeta.exists() and not force:
        info = json.loads(cmeta.read_text())
    else:
        best = None
        for attempt in range(3):
            raw = cdir / f"{h}.raw.mp3"
            openai_tts(clean, v, raw, api_key)
            if abs(speed - 1.0) > 0.01:
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-filter:a", f"atempo={min(2.0, max(0.5, speed))}", "-b:a", "128k", str(cmp3)], check=True)
                raw.unlink()
            else:
                raw.replace(cmp3)
            d = probe_duration(cmp3)
            ok = wpm_ok(len(clean.split()), d, v["lang"])
            best = d
            if ok:
                break
            print(f"  retry {who}-{h}: {len(clean.split()) / max(d, .1) * 60:.0f} wpm (truncated/garbled TTS?)", flush=True)
        try:
            starts = whisper_words(cmp3, v["lang"], api_key)
        except Exception as e:  # never block
            print(f"  whisper failed ({e}); proportional cue timing", flush=True)
            starts = []
        info = {"dur": round(best or probe_duration(cmp3), 3), "starts": starts, "amp": amp_env(cmp3, 30), "text": clean}
        cmeta.write_text(json.dumps(info, ensure_ascii=False))
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(cmp3, dst)
    info = dict(info)
    if fps != 30:  # cache stores 30 fps envelopes
        info["amp"] = amp_env(dst, fps)
    info["src"] = rel
    return info


# ------------------------------------------------------------------ b-roll
def pexels_pick(query: str, orient: str, min_s: float, pick: int, used: set) -> dict | None:
    k = key("PEXELS_API_KEY")
    if not k:
        return None
    r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization": k},
                     params={"query": query, "per_page": 20, "orientation": orient, "size": "medium"}, timeout=60)
    if r.status_code != 200:
        print(f"  pexels {r.status_code}: {r.text[:120]}")
        return None
    cands = []
    for vid in r.json().get("videos", []):
        if vid["duration"] < min_s or vid["id"] in used:
            continue
        files = [f for f in vid.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("width") and f.get("height")]
        long_side = lambda f: max(f["width"], f["height"])  # noqa: E731
        good = sorted([f for f in files if long_side(f) >= 1280], key=lambda f: abs(long_side(f) - 1920))
        if good:
            cands.append({"id": vid["id"], "url": good[0]["link"], "user": vid.get("user", {}).get("name", ""), "page": vid.get("url", ""), "duration": vid["duration"]})
    if not cands:
        return None
    return cands[min(max(pick, 1), len(cands)) - 1]


def pixabay_pick(query: str, min_s: float, pick: int, used: set) -> dict | None:
    k = key("PIXABAY_API_KEY")
    if not k:
        return None
    r = requests.get("https://pixabay.com/api/videos/", params={"key": k, "q": query, "per_page": 20}, timeout=60)
    if r.status_code != 200:
        return None
    cands = [{"id": f"px{h['id']}", "url": (h["videos"].get("large") or h["videos"]["medium"])["url"], "user": h.get("user", ""), "page": h.get("pageURL", ""), "duration": h["duration"]}
             for h in r.json().get("hits", []) if h["duration"] >= min_s and f"px{h['id']}" not in used and (h["videos"].get("large", {}).get("url") or h["videos"].get("medium", {}).get("url"))]
    return cands[min(max(pick, 1), len(cands)) - 1] if cands else None


def fetch_broll(sb: dict, run_dir: Path, W: int, H: int, scene_len: dict, sb_dir: Path, skip: bool) -> dict:
    out: dict = {}
    credits = []
    thumbs, labels = [], []
    used: set = set()
    orient = "portrait" if H > W * 1.1 else "square" if W < H * 1.2 else "landscape"
    bdir = run_dir / "public" / "broll"
    bdir.mkdir(parents=True, exist_ok=True)
    for b in sb.get("broll_shots", []):
        sid = b["id"]
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", sid)
        dst = bdir / f"{safe}.mp4"
        need_s = max(12.0, scene_len.get(sid, 0) * 0.65)
        tgt_len = min(25.0, max(need_s, 14.0))
        if dst.exists() and dst.stat().st_size > 0:
            out[sid] = {"src": f"broll/{safe}.mp4", "len": round(probe_duration(dst), 2)}
        else:
            src_file, meta = None, None
            prov = b.get("provider", "pexels")
            if b.get("path"):
                p = Path(b["path"]).expanduser()
                p = p if p.is_absolute() else (sb_dir / p)
                if p.exists():
                    src_file, meta = p, {"id": p.name, "user": "", "page": str(p), "license": b.get("license", "local")}
                else:
                    miss("broll", sid, f"local path not found: {b['path']}")
            elif not skip and prov in ("pexels", "pixabay"):
                cand = (pexels_pick if prov == "pexels" else lambda q, o, m, pk, u: pixabay_pick(q, m, pk, u))(b["query"], orient, float(b.get("min_s", 8)), int(b.get("pick", 1)), used)
                if cand:
                    used.add(cand["id"])
                    cpath = cache_dir("broll") / f"{cand['id']}.mp4"
                    if not cpath.exists():
                        with requests.get(cand["url"], stream=True, timeout=180) as r:
                            r.raise_for_status()
                            with open(cpath, "wb") as fh:
                                for chunk in r.iter_content(1 << 20):
                                    fh.write(chunk)
                    src_file, meta = cpath, {**cand, "license": f"{prov.capitalize()} License"}
                else:
                    miss("broll", sid, f"no {prov} result / {prov.upper()}_API_KEY missing for query '{b['query']}'")
            elif skip:
                miss("broll", sid, "b-roll fetch skipped (--no-broll)")
            if src_file:
                vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,format=yuv420p"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(b.get("ss", 0)), "-i", str(src_file), "-t", str(tgt_len), "-an",
                                "-vf", vf, "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", str(dst)], check=True)
                out[sid] = {"src": f"broll/{safe}.mp4", "len": round(probe_duration(dst), 2)}
                credits.append({"shot": sid, "query": b.get("query"), "provider": prov if not b.get("path") else "local", **{k: meta.get(k) for k in ("id", "user", "page", "license")}})
            else:
                out[sid] = {"src": "", "len": 0, "placeholder": True}
        if not out[sid].get("placeholder"):
            j = run_dir / "qa" / "broll" / f"{safe}.jpg"
            j.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(min(3, out[sid]["len"] / 2)), "-i", str(dst), "-frames:v", "1", "-vf", "scale=640:-2", str(j)])
            thumbs.append(j)
            labels.append(sid)
    if credits:
        write_json(run_dir / "public" / "broll" / "credits.json", credits)
    if thumbs:
        tile = (360, 640) if H > W * 1.1 else (480, 480) if W < H * 1.2 else (640, 360)
        cols = 5 if tile[0] < 400 else 3
        sheet = contact_sheet(thumbs, run_dir / "qa" / "broll_sheet.jpg", cols=cols, tile=tile)
        (run_dir / "qa" / "broll_sheet.txt").write_text("\n".join(f"{i + 1}. row {i // cols + 1} col {i % cols + 1}: {s}" for i, s in enumerate(labels)) + "\n")
        print(f"  b-roll contact sheet: {sheet}")
    return out


# ------------------------------------------------------------------ images / music / sfx
def find_media(name: str, dirs: list[Path], exts: tuple) -> Path | None:
    p = Path(name).expanduser()
    if p.suffix and p.exists():
        return p
    for d in dirs:
        if not d or not d.exists():
            continue
        for e in exts:
            c = d / f"{name}{e}"
            if c.exists():
                return c
    return None


def copy_public(src: Path, run_dir: Path, sub: str, name: str) -> str:
    dst = run_dir / "public" / sub / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', name)}{src.suffix.lower()}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        shutil.copy2(src, dst)
    return str(dst.relative_to(run_dir / "public"))


def resolve_quiz(sc: dict, quiz: dict | None, lang: str) -> None:
    p = sc["props"]
    if p.get("q") and p.get("options"):
        return
    if not quiz:
        miss("quiz", p.get("quiz_item", sc["id"]), "quiz.json not found and scene props lack q/options")
        return
    item = next((i for i in quiz.get("items", []) if i["id"] == p.get("quiz_item")), None)
    if not item:
        miss("quiz", p.get("quiz_item", sc["id"]), "quiz_item id not in quiz.json")
        return
    ar = lang.startswith("ar")
    p.setdefault("q", (item.get("stem_ar") if ar else None) or item["stem"])
    opts = item.get("options", [])
    p.setdefault("options", [((o.get("text_ar") if ar else None) or o["text"]) for o in opts])
    if "answer" not in p:
        p["answer"] = next((i for i, o in enumerate(opts) if o.get("correct")), -1)
    if item.get("explanation"):
        p.setdefault("why", item["explanation"])


def linear_path(sb: dict) -> list[dict]:
    """Branching storyboards: the linear video follows start → decision `video_choice` (else the `correct: true` choice)."""
    br = sb.get("branching")
    if not br:
        return sb["scenes"]
    by_id = {s["id"]: s for s in sb["scenes"]}
    nodes = {n["id"]: n for n in br["nodes"]}
    out, seen, cur = [], set(), br["start"]
    while cur and cur not in seen:
        seen.add(cur)
        node = nodes.get(cur)
        ids = node["scenes"] if node else ([cur] if cur in by_id else [])
        nxt = None
        for sid in ids:
            sc = by_id.get(sid)
            if not sc:
                continue
            out.append(sc)
            if sc["template"] == "decision":
                ch = sc["props"]["choices"]
                pick = next((c for c in ch if c["id"] == sc["props"].get("video_choice")), None) or next((c for c in ch if c.get("correct")), ch[0])
                nxt = pick["next"]
                break
        if nxt is None:
            break
        if nxt in by_id and nxt not in nodes:  # choice points straight at a scene: continue from that scene's position
            idx = [s["id"] for s in sb["scenes"]].index(nxt)
            out.extend(s for s in sb["scenes"][idx:] if s not in out)
            break
        cur = nxt
    if not out:
        return sb["scenes"]
    # Scenes outside every branching node (title before the scenario; rule/quiz/outro after it) stay in the video at
    # their storyboard position, matching the HTML player ("resumes linear order after the last branch scene").
    in_nodes = {sid for n in br["nodes"] for sid in n.get("scenes", [])}
    order = [s["id"] for s in sb["scenes"]]
    br_idx = [i for i, sid in enumerate(order) if sid in in_nodes]
    if br_idx:
        pre = [s for s in sb["scenes"][:br_idx[0]] if s["id"] not in in_nodes and s not in out]
        post = [s for s in sb["scenes"][br_idx[-1] + 1:] if s["id"] not in in_nodes and s not in out]
        out = pre + out + post
    return out


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard")
    ap.add_argument("--out", required=True)
    ap.add_argument("--quiz")
    ap.add_argument("--aspect", choices=list(ASPECTS))
    ap.add_argument("--placeholder-voice", action="store_true", help="no TTS calls; silent timing from word counts")
    ap.add_argument("--force-tts", action="store_true")
    ap.add_argument("--music-dir")
    ap.add_argument("--sfx-dir")
    ap.add_argument("--no-broll", action="store_true")
    a = ap.parse_args()
    need("ffmpeg"); need("ffprobe")

    sb_path = Path(a.storyboard).resolve()
    sb = json.loads(sb_path.read_text(encoding="utf-8"))
    errs = validate(sb)
    if errs:
        print("storyboard INVALID:\n  " + "\n  ".join(errs[:40]))
        sys.exit(2)
    warns = semantic_warnings(sb)
    path = linear_path(sb)
    if len(path) != len(sb["scenes"]):
        warns.append(f"branching: linear video follows {len(path)}/{len(sb['scenes'])} scenes")
        sb = {**sb, "scenes": path}
    for w in warns:
        print(f"  warn: {w}")
    run_dir = Path(a.out).resolve()
    (run_dir / "public").mkdir(parents=True, exist_ok=True)
    (run_dir / "storyboard.json").write_text(json.dumps(sb, ensure_ascii=False, indent=1), encoding="utf-8")

    lang = sb["language"]
    rtl = sb.get("direction") == "rtl" or lang.startswith("ar")
    aspect = a.aspect or sb["aspect"]
    W, H = ASPECTS[aspect]
    fps = int(sb.get("fps", FPS_DEFAULT))
    wpm = int(sb.get("wpm") or (120 if lang.startswith("ar") else 150))
    quiz = None
    qp = Path(a.quiz) if a.quiz else sb_path.with_name(f"{sb['lesson_id']}.quiz.json")
    if qp.exists():
        quiz = json.loads(qp.read_text(encoding="utf-8"))

    # ---- TTS (parallel) ----
    jobs = {}
    print(f"prepare {sb['lesson_id']} ({lang}, {aspect}) → {run_dir}", flush=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for si, sc in enumerate(sb["scenes"]):
            for li, ln in enumerate(sc["narration"]):
                text = (ln.get("text_ar") if lang.startswith("ar") and ln.get("text_ar") else ln["text"])
                v = voice_cfg(sb, ln["who"])
                if ln.get("instr"):
                    v["instructions"] = f"{v['instructions']} {ln['instr']}".strip()
                jobs[(si, li)] = (text, ex.submit(synth_line, text, ln["who"], v, run_dir, fps, a.force_tts, a.placeholder_voice, wpm))
        results = {}
        for k, (text, fut) in jobs.items():
            try:
                results[k] = (text, fut.result())
            except Exception as e:
                miss("tts", f"scene{k[0]}-line{k[1]}", f"TTS failed: {e}")
                n = len(words_of(text))
                d = max(1.2, n / (wpm / 60))
                results[k] = (text, {"src": "", "dur": d, "amp": fake_amp(d, fps, text), "starts": [], "placeholder": True})
    ph = [r for _, r in results.values() if r.get("placeholder")]
    if ph:
        miss("tts", f"{len(ph)} line(s)", ph[0].get("reason", "placeholder timing"))

    # ---- scene timing ----
    scenes, frame, sfx_abs, report = [], 0, [], []
    sfx_dirs = [Path(d).expanduser() for d in [a.sfx_dir] if d] + [PLUGIN_ROOT / "assets" / "sfx"]
    if os.environ.get("TCS_SFX_DIR"):
        sfx_dirs.insert(0, Path(os.environ["TCS_SFX_DIR"]).expanduser())
    scene_len: dict = {}
    for si, sc in enumerate(sb["scenes"]):
        if sc["template"] == "quiz":
            resolve_quiz(sc, quiz, lang)
        t = float(sc.get("lead", 0.35 if sc["narration"] else 0.0))
        lines, cues = [], []
        for li, ln in enumerate(sc["narration"]):
            text, info = results[(si, li)]
            t += float(ln.get("pre", 0))
            lines.append({"who": ln["who"], "at": round(t, 3), "dur": info["dur"], "src": info["src"], "amp": info["amp"], "text": " ".join(words_of(text))})
            cues += [round(t + c, 3) for c in align_cues(text, [tuple(x) for x in info.get("starts", [])], info["dur"])]
            default_pause = 2.2 if sc["template"] in ("quiz", "decision") and li == 0 and len(sc["narration"]) > 1 else GAP
            t += info["dur"] + float(ln.get("pause", default_pause))
        if sc["narration"]:
            last_pause = float(sc["narration"][-1].get("pause", GAP))
            t = t - last_pause + float(sc.get("hold", 0.75))
        else:
            t = float(sc.get("duration_hint_s") or sc.get("min_s") or 4.0)
        t = max(t, float(sc.get("min_s", 0) or 0), 1.0)
        frames = int(round(t * fps))
        for s in sc.get("sfx", []) + [{"cue": b["cue"], "name": b["sfx"]} for b in sc["props"].get("beats", []) if isinstance(b, dict) and b.get("sfx")]:
            at = s["at"] if "at" in s else (cues[s["cue"]] if s.get("cue", 0) < len(cues) else 0.3)
            f = find_media(s["name"], sfx_dirs, (".wav", ".mp3", ".m4a", ".ogg"))
            if f:
                sfx_abs.append({"at": round(frame / fps + at, 3), "src": copy_public(f, run_dir, "sfx", s["name"]), "vol": s.get("vol", 0.35)})
            elif not any(m["kind"] == "sfx" and m["id"] == s["name"] for m in MISSING):
                miss("sfx", s["name"], "sfx file not found (assets/sfx or TCS_SFX_DIR)")
        p = sc["props"]
        for k in ("shot", "side_broll"):
            if p.get(k):
                scene_len[p[k]] = max(scene_len.get(p[k], 0), t)
        scenes.append({"id": sc["id"], "template": sc["template"], "props": p, "from": frame, "frames": frames, "cues": cues, "lines": lines, "transition": sc.get("transition", "fade")})
        report.append({"id": sc["id"], "template": sc["template"], "start_s": round(frame / fps, 2), "dur_s": round(t, 2), "cues": [round(c, 2) for c in cues],
                       "n_cue_markers": sum(ln["text"].count("^") for ln in sc["narration"])})
        frame += frames

    # ---- assets ----
    print("assets …", flush=True)
    broll = fetch_broll(sb, run_dir, W, H, scene_len, sb_path.parent, a.no_broll)
    images: dict = {}
    for g in sb.get("generated_images", []):
        p = Path(g["path"]).expanduser() if g.get("path") else None
        if p and not p.is_absolute():
            p = sb_path.parent / p
        if p and p.exists():
            images[g["id"]] = {"src": copy_public(p, run_dir, "images", g["id"])}
        else:
            images[g["id"]] = {"src": "", "placeholder": True}
            miss("image", g["id"], "generated image not rendered yet (no path) — placeholder used")
    for sc in sb["scenes"]:
        if sc["template"] == "screencast":
            ss = sc["props"].get("app", {}).get("screenshot")
            if ss and ss not in images:
                p = Path(ss).expanduser()
                p = p if p.is_absolute() else sb_path.parent / p
                if p.exists():
                    images[ss] = {"src": copy_public(p, run_dir, "images", p.stem)}
                else:
                    images[ss] = {"src": "", "placeholder": True}
                    miss("image", ss, "screencast screenshot not found")
    music = None
    bed = (sb.get("music") or {}).get("bed")
    if bed:
        mdirs = [Path(d).expanduser() for d in [a.music_dir, os.environ.get("TCS_MUSIC_DIR")] if d] + [PLUGIN_ROOT / "assets" / "music"]
        f = find_media(bed, mdirs, (".mp3", ".m4a", ".wav", ".ogg"))
        if f:
            music = {"src": copy_public(f, run_dir, "music", Path(bed).stem), "vol": float(sb["music"].get("volume", 0.12))}
        else:
            miss("music", bed, "music bed not found (assets/music, TCS_MUSIC_DIR or --music-dir); rendering without music")
    theme = dict(sb.get("theme") or {})
    if theme.get("logo"):
        lp = Path(theme["logo"]).expanduser()
        lp = lp if lp.is_absolute() else sb_path.parent / lp
        theme["logo"] = copy_public(lp, run_dir, "brand", "logo") if lp.exists() else None
        if not lp.exists():
            miss("logo", str(lp), "logo file not found; slot left empty")

    # subtitle timing for tcs-localize: absolute start/end per narration line, beside the storyboard
    stem = sb_path.name[: -len(".storyboard.json")] if sb_path.name.endswith(".storyboard.json") else sb_path.stem
    timing = {"lesson_id": sb["lesson_id"], "language": lang, "lines": [
        {"scene_id": s["id"], "idx": i, "start": round(s["from"] / fps + l["at"], 3), "end": round(s["from"] / fps + l["at"] + l["dur"], 3), "who": l["who"], "text": l["text"]}
        for s in scenes for i, l in enumerate(s["lines"])]}
    for tp in {sb_path.with_name(f"{stem}.timing.json"), run_dir / "timing.json"}:
        try:
            write_json(tp, timing)
        except OSError as e:
            print(f"  warn: could not write {tp}: {e}")
    tl = {"lesson_id": sb["lesson_id"], "course_id": sb["course_id"], "title": sb["title"], "comp_id": comp_id(sb["lesson_id"]),
          "fps": fps, "width": W, "height": H, "aspect": aspect, "total": frame, "language": lang, "direction": "rtl" if rtl else "ltr",
          "theme": theme, "scenes": scenes, "music": music, "sfx": sfx_abs, "broll": broll, "images": images}
    write_json(run_dir / "timeline.json", {"tl": tl})
    (run_dir / "timeline.ts").write_text("// AUTO-GENERATED by tcs-render-remotion/scripts/prepare.py — do not edit.\nconst T = "
                                         + json.dumps(tl, ensure_ascii=False) + ";\nexport default T;\n", encoding="utf-8")
    write_json(run_dir / "missing_assets.json", MISSING)
    total_s = round(frame / fps, 2)
    write_json(run_dir / "prepare_report.json", {"lesson_id": sb["lesson_id"], "aspect": aspect, "duration_s": total_s, "scenes": report,
                                                 "warnings": warns, "missing_assets": len(MISSING), "rtl": rtl})
    print(f"\n{sb['lesson_id']}: {total_s}s, {len(scenes)} scenes, {len(MISSING)} missing/placeholder asset(s)")
    for r in report:
        print(f"  {r['id']:<22} {r['template']:<13} @{r['start_s']:>7.2f}s  {r['dur_s']:>6.2f}s  cues {r['cues']}")
    print(f"timeline: {run_dir / 'timeline.json'}")


if __name__ == "__main__":
    main()
