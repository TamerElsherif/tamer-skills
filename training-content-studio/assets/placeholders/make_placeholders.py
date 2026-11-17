"""Generate word-free placeholder assets (PNG, SVG, WAV) with the standard library only.

Usage: .venv/bin/python assets/placeholders/make_placeholders.py [--out DIR]
Default output: assets/placeholders/generated/
Images carry only the "missing asset" glyph (frame + hills + sun + diagonal slash) — no words, digits or logos.
"""
import argparse
import math
import struct
import wave
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

BG = (0xE6, 0xEB, 0xF3)       # light neutral (not cream)
INK = (0x36, 0x3E, 0x77)      # navy
SOFT = (0xB9, 0xC2, 0xDD)
SLASH = (0xB3, 0x47, 0x00)    # attention_text


def glyph_pixel(x, y, w, h):
    """Return colour for pixel (x, y) of a w×h canvas or None for background."""
    s = min(w, h) * 0.36                      # glyph box size
    cx, cy = w / 2, h / 2
    gx, gy = (x - cx) / s, (y - cy) / s       # glyph coords, box = [-0.5, 0.5]
    t = 0.035                                 # stroke thickness in glyph units
    # diagonal slash (drawn on top)
    if abs(gx + gy) / math.sqrt(2) < t * 0.9 and abs(gx) < 0.62 and abs(gy) < 0.62:
        return SLASH
    inside = abs(gx) <= 0.5 and abs(gy) <= 0.38
    # frame outline
    if (abs(gx) <= 0.5 + t and abs(gy) <= 0.38 + t) and not (abs(gx) <= 0.5 - t and abs(gy) <= 0.38 - t):
        return INK
    if not inside:
        return None
    # sun
    if (gx - 0.22) ** 2 + (gy + 0.16) ** 2 < 0.07 ** 2:
        return INK
    # hills (two triangles)
    if gy > 0.32 - (0.30 - abs(gx + 0.12)) * 1.6 and gy < 0.38 - t:
        return SOFT
    if gy > 0.32 - (0.22 - abs(gx - 0.22)) * 1.6 and gy < 0.38 - t:
        return SOFT
    return None


def png(path, w, h, border=True):
    rows = bytearray()
    dash = max(8, min(w, h) // 60)
    for y in range(h):
        rows.append(0)
        for x in range(w):
            c = glyph_pixel(x, y, w, h)
            if c is None and border:
                on_edge = x < 6 or y < 6 or x >= w - 6 or y >= h - 6
                if on_edge and ((x + y) // dash) % 2 == 0:
                    c = SOFT
            rows.extend(c or BG)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b"")
    path.write_bytes(data)


SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" role="img" aria-label="missing asset">
  <rect width="160" height="160" fill="#E6EBF3"/>
  <rect x="30" y="44" width="100" height="76" rx="4" fill="none" stroke="#363E77" stroke-width="5"/>
  <circle cx="102" cy="66" r="7" fill="#363E77"/>
  <path d="M34 116 L62 82 L84 108 L98 92 L126 116 Z" fill="#B9C2DD"/>
  <line x1="24" y1="136" x2="136" y2="24" stroke="#B34700" stroke-width="6" stroke-linecap="round"/>
</svg>
"""


def wav(path, seconds, freq=0.0, gain_db=-60.0, fade=0.02, sr=48000):
    n = int(seconds * sr)
    amp = 10 ** (gain_db / 20) * 32767 if freq else 0
    frames = bytearray()
    for i in range(n):
        env = min(1.0, i / (fade * sr + 1), (n - i) / (fade * sr + 1))
        v = int(amp * env * math.sin(2 * math.pi * freq * i / sr)) if freq else 0
        frames.extend(struct.pack("<h", v))
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(bytes(frames))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "generated"))
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    for name, (w, h) in {"missing_16x9.png": (1920, 1080), "missing_9x16.png": (1080, 1920),
                         "missing_1x1.png": (1080, 1080), "missing_character.png": (1024, 1024),
                         "missing_thumb.png": (320, 180)}.items():
        png(out / name, w, h)
    (out / "missing.svg").write_text(SVG)
    wav(out / "silence_1s.wav", 1.0)
    wav(out / "music_bed_placeholder.wav", 4.0)                        # silent bed; renderer loops it
    wav(out / "sfx_placeholder.wav", 0.18, freq=880, gain_db=-18)       # soft blip
    wav(out / "narration_placeholder_tone.wav", 1.0, freq=440, gain_db=-24)  # per-line stand-in for provider "placeholder"
    for p in sorted(out.iterdir()):
        print(f"{p.name:34} {p.stat().st_size:>8} bytes")


if __name__ == "__main__":
    main()
