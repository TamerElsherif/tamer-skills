"""Speaker alpha mask on the NVIDIA GPU — drop-in for `hyperframes remove-background`'s mask.

HyperFrames' remove-background uses onnxruntime-node, whose Windows build has no CUDA backend, so it
silently runs on CPU (~350 ms/frame here). This runs the SAME model (u2net_human_seg, cached by
HyperFrames) with the SAME pre/post-processing (lanczos3 to 320x320, max-pixel + ImageNet
normalisation, min/max mask stretch, lanczos3 back up) through onnxruntime-gpu (~10x faster).

Output is a grayscale mask video (white = speaker) — refine_matte.py only ever used the alpha.
Falls back to CPU if CUDA is unavailable and says so.

usage: python gpu_matte.py <video.mp4> <out_mask.mkv>
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL = Path.home() / ".cache/hyperframes/background-removal/models/u2net_human_seg.onnx"
SIZE = 320
MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    return s["width"], s["height"], s["r_frame_rate"]


def session():
    if not MODEL.exists():
        sys.exit(f"model missing: {MODEL} (run `npx hyperframes remove-background --info` once to fetch it)")
    try:
        ort.preload_dlls()  # CUDA 12 / cuDNN 9 DLLs from the nvidia-* pip packages
    except Exception:
        pass
    s = ort.InferenceSession(str(MODEL), providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    return s, s.get_providers()[0]


def mask_of(sess, name, rgb, w, h):
    small = np.asarray(Image.fromarray(rgb).resize((SIZE, SIZE), Image.LANCZOS), np.float32)
    small = (small / max(small.max(), 1.0) - MEAN) / STD
    raw = sess.run(None, {name: small.transpose(2, 0, 1)[None]})[0].reshape(SIZE, SIZE)
    lo, hi = raw.min(), raw.max()
    m = np.clip(np.rint((raw - lo) / ((hi - lo) or 1) * 255), 0, 255).astype(np.uint8)
    return np.asarray(Image.fromarray(m).resize((w, h), Image.LANCZOS))


def main(src, out):
    w, h, fps = probe(src)
    sess, provider = session()
    name = sess.get_inputs()[0].name
    print(f"gpu_matte: {Path(src).name} {w}x{h} on {provider}")
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(src), "-an", "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    # lossless gray so refine_matte gets exactly what the model produced
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "gray",
                            "-s", f"{w}x{h}", "-r", fps, "-i", "-", "-c:v", "ffv1", "-pix_fmt", "gray",
                            str(out)], stdin=subprocess.PIPE)
    n, t0, frame = 0, time.time(), w * h * 3
    while True:
        buf = dec.stdout.read(frame)
        if len(buf) < frame:
            break
        enc.stdin.write(mask_of(sess, name, np.frombuffer(buf, np.uint8).reshape(h, w, 3), w, h).tobytes())
        n += 1
    enc.stdin.close()
    if dec.wait() or enc.wait():
        sys.exit("gpu_matte: ffmpeg failed")
    dt = time.time() - t0
    print(f"gpu_matte: {n} frames in {dt:.1f}s ({n / dt:.1f} fps, {provider}) -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
