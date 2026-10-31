"""Render a Rabet name card (lower third, bottom-left): transparent ProRes 4444 MOV, full frame, 25 fps.

Look (Ep 3 cards): aqua bar grows, a white block sweeps right and reveals the Arabic name (Alexandria 800) and the
English title in capitals, shrinks to a cursor; at the end it sweeps back and hides them. White text with a soft
shadow, no background box, so it reads on any shot. Full-frame canvas: overlay at 0,0, no positioning needed.

usage: python make_namecard.py --name "هيثم فؤاد" --title "Founder - prodXeed" --key haitham [options]
  --out-dir DIR     default: episodes.name_cards folder from ~/.rabet-reels.json, else ./name_cards
  --res 4k|1080     canvas (default 4k = 3840x2160, matches the episode masters; 1080 renders ~4x faster)
  --speed F         1.0 = 6 s card (default), 1.4 = 4.3 s "fast" card
  --force           render again even if the file exists
-> <out-dir>/NameCard_<key>.mov  (+ NameCard_<key>_preview.jpg, a frame at full reveal)
Add the new card to ~/.rabet-reels.json episodes.name_cards {"<Key>": "<path>"} so rabet-episodes can place it.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REELS = SKILL.parent / "rabet-reels"
sys.path.insert(0, str(REELS / "scripts"))
from config import load  # noqa: E402


def default_dir():
    cards = load().get("episodes", {}).get("name_cards") or {}
    first = next(iter(cards.values()), None)
    return Path(first).parent if first else Path("name_cards")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--key", required=True, help="file key, e.g. haitham or tamer_IT-AI")
    ap.add_argument("--out-dir")
    ap.add_argument("--res", default="4k", choices=["4k", "1080"])
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    out = Path(a.out_dir) if a.out_dir else default_dir()
    out.mkdir(parents=True, exist_ok=True)
    mov = (out / f"NameCard_{a.key}.mov").resolve()
    if mov.exists() and not a.force:
        sys.exit(f"exists: {mov} (use --force)")
    work = out / f"_work_{a.key}"
    shutil.rmtree(work, ignore_errors=True)
    (work / "assets/fonts").mkdir(parents=True)
    shutil.copy(REELS / "assets/fonts/Alexandria.ttf", work / "assets/fonts/Alexandria.ttf")
    for f in ("hyperframes.json", "meta.json", "package.json"):
        shutil.copy(REELS / "templates/thumbs" / f, work / f)
    dur = round(6.0 / a.speed, 3)
    html = (SKILL / "templates/namecard.html").read_text(encoding="utf-8")
    for k, v in {"NAME": a.name, "TITLE": a.title, "DURATION": str(dur), "SPEED": str(a.speed)}.items():
        html = html.replace("{{" + k + "}}", v)
    (work / "index.html").write_text(html, encoding="utf-8")
    res = "--resolution landscape-4k" if a.res == "4k" else ""
    subprocess.run(f'npx --yes hyperframes@0.8.163 render --fps 25 --format mov {res} -o "{mov}"', cwd=work,
                   shell=True, check=True, stdin=subprocess.DEVNULL)
    prev = mov.with_name(f"NameCard_{a.key}_preview.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x40505a:s=1920x1080",
                    "-ss", f"{min(2.0, dur / 2):.2f}", "-i", str(mov), "-filter_complex",
                    "[1:v]scale=1920:1080[c];[0:v][c]overlay=format=auto", "-frames:v", "1", str(prev)], check=True)
    shutil.rmtree(work, ignore_errors=True)
    print("wrote", mov, "\npreview", prev)


if __name__ == "__main__":
    main()
