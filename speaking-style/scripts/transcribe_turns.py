"""Transcribe every diarized turn on its own (Whisper large-v3, GPU float16): words, times and confidence per speaker.

Turn by turn, not the whole file: long-file word times drift (Ep 3 by ~1:35), and a turn's own transcript can't
borrow words from the other speaker. Turns are padded 0.25 s; words whose middle falls outside the turn are dropped.

usage: python transcribe_turns.py <work_dir> [--only Tamer,Hossam] [--lang ar] [--prompt "..."] [--redo]
       [--fixes .claude/skills/rabet-reels/scripts/glossary.json]
writes <work_dir>/words.json (resumable: turns already done are kept unless --redo).
"""
import argparse
from pathlib import Path

from common import REPO, SR, jload, jsave, load_audio


def unloop(words):
    """drop Whisper repetition loops: a 2-3 word unit repeated >= 3 times, or one word >= 4 times, keeps one copy
    (a real «أبسط أبسط أبسط» for emphasis survives)"""
    out = list(words)
    for n, k in ((3, 3), (2, 3), (1, 4)):
        i = 0
        while i + n * k <= len(out):
            unit = [w["w"] for w in out[i:i + n]]
            j = i + n
            while j + n <= len(out) and [w["w"] for w in out[j:j + n]] == unit:
                j += n
            if (j - i) // n >= k:
                del out[i + n:j]
            i += 1
    return out


def model():
    import ctranslate2
    from faster_whisper import WhisperModel
    if ctranslate2.get_cuda_device_count() > 0:
        try:
            return WhisperModel("large-v3", device="cuda", compute_type="float16")
        except Exception as e:                    # cuBLAS DLLs missing: see rabet-reels §5
            print(f"WARNING: GPU failed ({e}); CPU int8 is ~10x slower")
    return WhisperModel("large-v3", device="cpu", compute_type="int8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--only")
    ap.add_argument("--lang", default="ar")
    ap.add_argument("--prompt", help="initial prompt (off by default: Whisper repeats it into short turns)")
    ap.add_argument("--fixes", default=str(REPO / ".claude/skills/rabet-reels/scripts/glossary.json"))
    ap.add_argument("--redo", action="store_true", help="ignore words.json and transcribe every turn again")
    a = ap.parse_args()
    work = Path(a.work)
    T = jload(work / "turns.json")
    x = load_audio(T["source"], work)
    only = set(a.only.split(",")) if a.only else None
    fixes = jload(a.fixes).get("fixes", {}) if a.fixes and Path(a.fixes).exists() else {}
    out_p = work / "words.json"
    done = {(t["s"], t["who"]): t for t in jload(out_p)["turns"]} if out_p.exists() and not a.redo else {}
    todo = [t for t in T["turns"] if t[2] != "?" and (only is None or t[2] in only)]
    m = model()
    res = []
    for i, (s, e, who, mg) in enumerate(todo):
        if (s, who) in done:
            res.append(done[(s, who)])
            continue
        a0 = max(0.0, s - 0.25)
        clip = x[int(a0 * SR): int((e + 0.25) * SR)]
        segs, _ = m.transcribe(clip, language=a.lang, word_timestamps=True, beam_size=5, vad_filter=False,
                               condition_on_previous_text=False, initial_prompt=a.prompt)
        words = []
        for sg in segs:
            for w in sg.words or []:
                ws, we = a0 + w.start, a0 + w.end
                if s <= (ws + we) / 2 <= e:
                    t = w.word.strip()
                    t = fixes.get(t, t)
                    if t:
                        words.append({"w": t, "s": round(ws, 2), "e": round(we, 2), "p": round(w.probability, 2)})
        res.append({"s": s, "e": e, "who": who, "margin": mg, "words": unloop(words)})
        if i % 25 == 0:
            print(f"{i}/{len(todo)}", flush=True)
            jsave({"turns": res}, out_p)
    jsave({"turns": res}, out_p)
    n = sum(len(t["words"]) for t in res)
    print(f"wrote {out_p}: {len(res)} turns, {n} words")


if __name__ == "__main__":
    main()
