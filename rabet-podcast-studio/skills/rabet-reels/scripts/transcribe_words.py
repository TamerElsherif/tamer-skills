"""Word-level transcript of a (cut) A-roll in output time — Whisper large-v3, Arabic, GPU (float16).

Runs on the RTX 5050 via CTranslate2. That needs cublas64_12.dll / cublasLt64_12.dll copied from
.venv/Lib/site-packages/nvidia/cublas/bin into .venv/Lib/site-packages/ctranslate2/ (redo after any
ctranslate2 / faster-whisper reinstall). Run from the OpenMontage repo root with
.venv/Scripts/python.exe.

usage: python transcribe_words.py <video_or_audio> <out.words.json> [language]
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
from tools.analysis.transcriber import Transcriber  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else "ar"
r = Transcriber().execute({"input_path": src, "model_size": "large-v3", "language": lang,
                           "output_dir": os.path.dirname(os.path.abspath(out))})
if not r.success:
    sys.exit(f"transcription failed: {r.error}")
json.dump({"words": [{"w": w["word"].strip(), "s": w["start"], "e": w["end"]} for w in r.data["word_timestamps"]]},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{out}: {len(r.data['word_timestamps'])} words on {r.data['device']} ({r.data['compute_type']})")
if r.data.get("gpu_fallback_reason"):
    print(f"WARNING: GPU failed, ran on CPU: {r.data['gpu_fallback_reason']}")
