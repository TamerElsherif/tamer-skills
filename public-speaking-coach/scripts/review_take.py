"""Measure one rehearsal / talk recording for coaching: voice over time, pauses, fillers, opening and ending
energy, monotone and rushed stretches, time per section, and contact sheets of the body every few seconds.

usage: python review_take.py <video_or_audio> --out <take_dir> [--mode stage|camera|online]
       [--profile <speaker>/metrics.json --speaker Tamer] [--target-min 20]
       [--sections sections.json] [--compare <previous take_dir>/review.json] [--every 3] [--lang ar]
sections.json: [["Opening", 0], ["Point 1", 95.0], ...] (start seconds, e.g. from the clicker or by ear)
writes <take_dir>/: review.md, review.json, words.json, transcript.md, sheet_NN.jpg (if there is video)
Then read review.md + every sheet + transcript.md and write the feedback (references/feedback.md).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
STYLE = HERE.parents[1] / "speaking-style"
sys.path.insert(0, str(STYLE / "scripts"))
from common import SR, jload, jsave, mmss, speech_mask  # noqa: E402

MODES = {"stage": (0.87, 1.4), "camera": (1.0, 1.2), "online": (1.0, 1.3)}   # pace factor, pitch factor vs profile
WIN = 10


def has_video(src):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=codec_type",
                          "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout
    return "video" in out


def sheets(src, out, every):
    font = r"fontfile='C\:/Windows/Fonts/arial.ttf':" if sys.platform == "win32" else ""
    vf = (f"fps=1/{every},scale=320:-2,drawtext={font}text='%{{pts\\:hms}}':x=6:y=6:fontsize=20:fontcolor=yellow:"
          "box=1:boxcolor=black@0.6,tile=6x4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", vf, "-fps_mode", "vfr",
                    str(out / "sheet_%02d.jpg")], check=True)
    return sorted(p.name for p in out.glob("sheet_*.jpg"))


def transcribe(wav, lang):
    from transcribe_turns import model, unloop
    import soundfile as sf
    x = sf.read(str(wav), dtype="float32")[0]
    segs, _ = model().transcribe(x, language=lang, word_timestamps=True, beam_size=5, vad_filter=True,
                                 condition_on_previous_text=False)
    words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)}
             for sg in segs for w in (sg.words or []) if w.word.strip()]
    return unloop(words)


def runs(mask, val, min_len):
    """[(start_frame, length)] of runs where mask == val, length >= min_len frames"""
    out, i = [], 0
    while i < len(mask):
        if mask[i] == val:
            j = i
            while j < len(mask) and mask[j] == val:
                j += 1
            if j - i >= min_len:
                out.append((i, j - i))
            i = j
        else:
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", default="stage", choices=MODES)
    ap.add_argument("--profile")
    ap.add_argument("--speaker")
    ap.add_argument("--target-min", type=float)
    ap.add_argument("--sections")
    ap.add_argument("--compare")
    ap.add_argument("--every", type=float, default=3)
    ap.add_argument("--lang", default="ar")
    a = ap.parse_args()
    import librosa
    import soundfile as sf
    from style_metrics import LATIN, count_markers, norm

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "audio.wav"
    if not wav.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-vn", "-ac", "1", "-ar", str(SR), str(wav)],
                       check=True)
    x = sf.read(str(wav), dtype="float32")[0]
    dur = len(x) / SR
    wp = out / "words.json"
    words = jload(wp)["words"] if wp.exists() else transcribe(wav, a.lang)
    jsave({"words": words}, wp)
    sp, db = speech_mask(x)
    for s0, n in runs(sp, False, 1):            # fill dips < 0.25 s inside words
        if n < 25:
            sp[s0:s0 + n] = True
    f0 = librosa.yin(x, fmin=65, fmax=400, sr=SR, frame_length=1024, hop_length=160)
    n = min(len(f0), len(db), len(sp))
    f0, db, sp = f0[:n], db[:n], sp[:n]
    loud_thr = np.percentile(db[sp], 40) if sp.any() else -40

    def pitch_var(sl):
        v = f0[sl][(db[sl] > loud_thr) & sp[sl]]
        v = v[(v > 70) & (v < 380)]
        return float(np.std(12 * np.log2(v / np.median(v)))) if len(v) > 40 else None

    first, last = (words[0]["s"], words[-1]["e"]) if words else (0, dur)
    a0, b0 = int(first * 100), int(last * 100)
    speech_s = sp[a0:b0].sum() / 100
    gaps = [(s0 + a0, ln) for s0, ln in runs(sp[a0:b0], False, 30)]
    talk_min = max(1e-6, (last - first) / 60)
    toks = [v for v in (norm(w["w"]) for w in words) if v]
    mk = jload(STYLE / "references/markers.json")
    m = count_markers(toks, mk)
    fill = {k: v for c in ("hesitation", "filler") for k, v in m.get(c, {}).items()}
    rep = sum(1 for p, q in zip(toks, toks[1:]) if p == q and len(p) > 1)

    W = []
    for t in np.arange(0, dur, WIN):
        sl = slice(int(t * 100), int(min(dur, t + WIN) * 100))
        ws = [w for w in words if t <= w["s"] < t + WIN]
        spk = sp[sl].sum() / 100
        W.append({"t": round(float(t)), "wpm": round(len(ws) / spk * 60) if spk > 2 else None,
                  "pitch_var": None if (pv := pitch_var(sl)) is None else round(pv, 2),
                  "loud": round(float(np.percentile(db[sl][sp[sl]], 90)), 1) if sp[sl].sum() > 50 else None,
                  "silence": round(1 - float(sp[sl].mean()), 2), "text": " ".join(w["w"] for w in ws)})
    pv = [w["pitch_var"] for w in W if w["pitch_var"] is not None]
    ld = [w["loud"] for w in W if w["loud"] is not None]
    wpm_all = [w["wpm"] for w in W if w["wpm"]]
    med_pv, med_ld = (float(np.median(pv)) if pv else 0), (float(np.median(ld)) if ld else 0)

    base = {}
    if a.profile:
        P = jload(a.profile)
        S = P["speakers"][a.speaker or P["speaker"]]
        base = {"wpm": S["wpm_articulation"], "pitch_var": S.get("prosody", {}).get("pitch_variation_in_turn_st"),
                "fillers_per_1000": None}
        mp = S.get("markers_per_1000", {})
        base["fillers_per_1000"] = round(mp.get("hesitation", 0) + mp.get("filler", 0), 1)
    pf, vf = MODES[a.mode]
    target_wpm = round(base["wpm"] * pf) if base.get("wpm") else None
    target_pv = round(base["pitch_var"] * vf, 2) if base.get("pitch_var") else None
    flat_thr = max(1.8, 0.75 * (target_pv or med_pv))
    flat, cur = [], None
    for w in W:
        if w["pitch_var"] is not None and w["pitch_var"] < flat_thr:
            cur = [w["t"], w["t"] + WIN] if cur is None else [cur[0], w["t"] + WIN]
        else:
            if cur and cur[1] - cur[0] >= 30:
                flat.append(cur)
            cur = None
    if cur and cur[1] - cur[0] >= 30:
        flat.append(cur)
    rushed = [w["t"] for w in W if w["wpm"] and target_wpm and w["wpm"] > target_wpm * 1.25]

    def span(t0, t1, key):
        v = [w[key] for w in W if t0 <= w["t"] < t1 and w[key] is not None]
        return float(np.median(v)) if v else None

    op_ld, op_pv = span(0, 30, "loud"), span(0, 30, "pitch_var")
    en_ld, en_pv = span(dur - 30, dur + 1, "loud"), span(dur - 30, dur + 1, "pitch_var")
    R = {
        "source": str(Path(a.src).resolve()), "mode": a.mode, "duration": mmss(dur), "duration_s": round(dur, 1),
        "words": len(toks), "wpm_articulation": round(len(toks) / max(1, speech_s) * 60),
        "wpm_overall": round(len(toks) / talk_min), "target_wpm": target_wpm,
        "pitch_var_median": round(med_pv, 2), "target_pitch_var": target_pv,
        "pauses_per_min": round(len(gaps) / talk_min, 1),
        "beats_per_min": round(sum(1 for _, ln in gaps if ln >= 100) / talk_min, 2),
        "long_silences": [[mmss(s0 / 100), round(ln / 100, 1)] for s0, ln in gaps if ln >= 300],
        "fillers_per_1000": round(sum(fill.values()) / max(1, len(toks)) * 1000, 1),
        "baseline_fillers_per_1000": base.get("fillers_per_1000"), "fillers": fill,
        "repeats_per_1000": round(rep / max(1, len(toks)) * 1000, 1),
        "english_share": round(sum(1 for v in toks if LATIN.search(v)) / max(1, len(toks)), 3),
        "opening_vs_median": {"loud_db": None if op_ld is None else round(op_ld - med_ld, 1),
                              "pitch_var": None if op_pv is None else round(op_pv - med_pv, 2)},
        "ending_drop_db": None if en_ld is None else round(med_ld - en_ld, 1),
        "ending_pitch_var_change": None if en_pv is None else round(en_pv - med_pv, 2),
        "flat_runs": [[mmss(s), mmss(e)] for s, e in flat], "rushed_windows": [mmss(t) for t in rushed],
        "loudness_range_db": round(float(np.percentile(ld, 90) - np.percentile(ld, 10)), 1) if ld else None,
        "windows": W,
    }
    if a.target_min:
        R["overrun_s"] = round(dur - a.target_min * 60)
    if a.sections:
        secs = jload(a.sections)
        ends = [s for _, s in secs[1:]] + [dur]
        R["sections"] = [[t, mmss(s), round((e - s) / 60, 1),
                          len([w for w in words if s <= w["s"] < e])] for (t, s), e in zip(secs, ends)]
    vid = has_video(a.src)
    R["sheets"] = sheets(a.src, out, a.every) if vid else []
    prev = jload(a.compare) if a.compare else None
    jsave(R, out / "review.json")

    lines = [f"# Take review: {Path(a.src).name} ({a.mode})", "",
             "| measure | this take | target / baseline | previous |", "|---|---|---|---|"]

    def row(label, key, target=""):
        lines.append(f"| {label} | {R.get(key)} | {target} | {prev.get(key) if prev else ''} |")
    row("duration", "duration", f"{a.target_min} min (overrun {R.get('overrun_s')} s)" if a.target_min else "")
    row("articulation wpm", "wpm_articulation", f"{target_wpm} ({a.mode}: profile × {pf})" if target_wpm else "")
    row("pitch movement (semitones, median per 10 s)", "pitch_var_median",
        f"{target_pv} (profile × {vf})" if target_pv else "")
    row("pauses ≥ 0.3 s per min", "pauses_per_min")
    row("beats ≥ 1 s per min", "beats_per_min", "stage: ~2–4 (transitions + punchlines)" if a.mode == "stage" else "")
    row("fillers per 1000 words", "fillers_per_1000", f"profile {base.get('fillers_per_1000')}" if base else "")
    row("restart repeats per 1000", "repeats_per_1000")
    row("loudness range p10–p90 (dB)", "loudness_range_db")
    row("ending drop vs median (dB)", "ending_drop_db", "≤ 2")
    lines += ["", f"- Opening 30 s vs the talk: loudness {R['opening_vs_median']['loud_db']} dB, pitch movement "
              f"{R['opening_vs_median']['pitch_var']} st (≥ 0 wanted)",
              f"- Monotone stretches (≥ 30 s under {flat_thr:.1f} st): {R['flat_runs'] or 'none'}",
              f"- Rushed 10 s windows (> target + 25 %): {R['rushed_windows'] or 'none'}",
              f"- Silences ≥ 3 s (blank? deliberate?): {R['long_silences'] or 'none'}",
              f"- Fillers: {' · '.join(f'{k} {v}' for k, v in sorted(fill.items(), key=lambda x: -x[1]))}"]
    if R.get("sections"):
        lines += ["", "## Sections", "| section | start | minutes | words |", "|---|---|---|---|"]
        lines += [f"| {t} | {s} | {m_} | {w} |" for t, s, m_, w in R["sections"]]
    lines += ["", "## Timeline (10 s windows)", "| t | wpm | pitch st | loud dB | silence | text |", "|---|---|---|---|---|---|"]
    for w in W:
        lines.append(f"| {mmss(w['t'])} | {w['wpm'] or ''} | {w['pitch_var'] or ''} | {w['loud'] or ''} | "
                     f"{int(w['silence'] * 100)}% | {w['text']} |")
    if R["sheets"]:
        lines += ["", f"## Contact sheets (a frame every {a.every:g} s): " + ", ".join(R["sheets"])]
    (out / "review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    tx, cur_t = [], -1
    for w in words:
        if int(w["s"] // 30) != cur_t:
            cur_t = int(w["s"] // 30)
            tx.append(f"\n[{mmss(w['s'])}] ")
        tx.append(w["w"] + " ")
    (out / "transcript.md").write_text("".join(tx).strip() + "\n", encoding="utf-8")
    print(f"wrote {out / 'review.md'} ({R['duration']}, {len(R['sheets'])} contact sheets)")


if __name__ == "__main__":
    main()
