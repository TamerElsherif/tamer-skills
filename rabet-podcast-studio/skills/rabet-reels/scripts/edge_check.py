"""Edge check before delivery: is any word clipped at a cut?

Every kept part is exported on its own with 1 s of silence around it, all parts are
transcribed in one Whisper pass, and each part is printed with its words (offsets in
seconds from the part start). A clipped first/last word shows up as a missing or
garbled word at that edge. Words Whisper places in the silent padding far from the part
(e.g. «اشتركوا في القناة») are its usual hallucinations, not audio.

usage (from the OpenMontage repo root, with .venv/Scripts/python.exe):
    python .claude/skills/rabet-reels/scripts/edge_check.py <source.mp4> <cuts.json> [work_dir]
cuts.json: [{"beat": "<label>", "parts": [[start, end], ...]}, ...]   (source seconds)
           or an aroll_<style>.segments.json from build_aroll.py
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

SR = 16000


def load_parts(path):
    d = json.load(open(path, encoding="utf-8"))
    if isinstance(d, dict) and "segments" in d:                       # build_aroll.py output
        return [(s.get("kind", "seg"), s["src_start"], s["src_end"]) for s in d["segments"]]
    return [(c.get("beat", c.get("label", "part")), a, b) for c in d for a, b in c["parts"]]


def main(src, cuts, work):
    os.makedirs(work, exist_ok=True)
    gap = np.zeros(SR, np.float32)
    chunks, spans, t = [gap], [], 1.0
    for label, a, b in load_parts(cuts):
        x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", src,
                                          "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                         capture_output=True).stdout, np.float32)
        chunks += [x, gap]
        spans.append((label, a, b, t, t + len(x) / SR))
        t += len(x) / SR + 1.0
    wav, words_json = os.path.join(work, "edge_check.wav"), os.path.join(work, "edge_check.words.json")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(np.concatenate(chunks), -1, 1) * 32767).astype(np.int16).tobytes())
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, "transcribe_words.py"), os.path.abspath(wav),
                    os.path.abspath(words_json)], check=True)
    words = json.load(open(words_json, encoding="utf-8"))["words"]
    groups = [[] for _ in spans]
    for wd in words:                     # each word goes to the part its midpoint is nearest to
        m = (wd["s"] + wd["e"]) / 2
        k = min(range(len(spans)), key=lambda i: 0 if spans[i][3] <= m <= spans[i][4]
                else min(abs(m - spans[i][3]), abs(m - spans[i][4])))
        groups[k].append(f'{wd["w"].strip()}[{wd["s"] - spans[k][3]:+.2f}]')
    for (label, a, b, s, e), g in zip(spans, groups):
        print(f"{label:17s} {a:9.3f}-{b:9.3f} ({e - s:4.2f}s) | {' '.join(g)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(sys.argv[2])))
