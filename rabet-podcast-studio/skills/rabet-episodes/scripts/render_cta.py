"""Render the follow & subscribe pop-up once per variant: a transparent ProRes 4444 MOV (2000x440, 4K pixels) +
a matching SFX WAV (pop, two clicks, bell ping), cached and reused by build_episode.py.

Look: white pill card, Rabet logo-mark avatar, channel name + handle, YouTube-red Subscribe button with the YouTube
mark, notification bell. A cursor clicks Subscribe (turns grey "Subscribed"), then the bell (it rings), then the card
pops out. No dark-blue or orange backgrounds (user rule, 2026-10-31).

usage: python render_cta.py [--lang en|ar] [--channel "رابط بودكاست"] [--handle @RabetPodcast] [--force]
       (render again with --force after changing the template or the channel name; the cache is per language)
       -> <cta_dir>/cta_<lang>.mov + .wav   (cta_dir from ~/.rabet-reels.json "episodes.cta_dir", default
          ~/.cache/rabet-episodes/cta)
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REELS = SKILL.parent / "rabet-reels"
sys.path.insert(0, str(REELS / "scripts"))
from config import load  # noqa: E402
from PIL import Image  # noqa: E402

DURATION = 6.0                 # card on screen 0 -> OUT_AT + 0.4
OUT_AT = 5.4
CUES = [("pop.mp3", 0.0, 0.7), ("click-soft.mp3", 1.45, 1.0), ("click-soft.mp3", 2.6, 1.0), ("ping.mp3", 2.65, 0.6),
        ("pop.mp3", OUT_AT, 0.45)]  # (file, time, volume): mirrors T in templates/subscribe-cta/index.html
LABELS = {"en": ("SUBSCRIBE", "SUBSCRIBED"), "ar": ("اشترك", "مشترك")}


def cta_dir():
    d = load().get("episodes", {}).get("cta_dir") or "~/.cache/rabet-episodes/cta"
    return Path(d).expanduser()


def render(lang="en", channel=None, handle=None, force=False):
    cfg = load().get("episodes", {})
    channel, handle = channel or cfg.get("channel", "رابط بودكاست"), handle or cfg.get("handle", "@RabetPodcast")
    out = cta_dir()
    mov, wav = out / f"cta_{lang}.mov", out / f"cta_{lang}.wav"
    if mov.exists() and wav.exists() and not force:
        return mov, wav
    work = out / f"work_{lang}"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(SKILL / "templates/subscribe-cta", work)
    (work / "assets/fonts").mkdir(parents=True)
    shutil.copy(REELS / "assets/fonts/Alexandria.ttf", work / "assets/fonts/Alexandria.ttf")
    logo = Image.open(REELS / "assets/logo.png")           # the triangle mark only (top part of the logo)
    logo.crop(logo.crop((0, 0, logo.width, logo.height // 2)).getbbox()).save(work / "assets/mark.png")
    sub, done = LABELS[lang]
    html = (work / "index.html").read_text(encoding="utf-8")
    for k, v in {"DURATION": f"{DURATION}", "OUT_AT": f"{OUT_AT}", "CHANNEL": channel, "HANDLE": handle,
                 "SUBSCRIBE": sub, "SUBSCRIBED": done}.items():
        html = html.replace("{{" + k + "}}", v)
    (work / "index.html").write_text(html, encoding="utf-8")
    subprocess.run(f'npx --yes hyperframes@0.8.163 render --format mov --fps 25 -o "{mov}"', cwd=work, shell=True,
                   check=True)
    args, mix = [], []
    for i, (f, t, v) in enumerate(CUES):
        args += ["-i", str(REELS / "assets" / f)]
        ms = int(t * 1000)
        mix.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[c{i}]")
    graph = ";".join(mix) + ";" + "".join(f"[c{i}]" for i in range(len(CUES))) + \
        f"amix=inputs={len(CUES)}:normalize=0,apad,atrim=0:{DURATION}[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", graph, "-map", "[a]", "-c:a", "pcm_s16le",
                    str(wav)], check=True)
    return mov, wav


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en", choices=sorted(LABELS))
    ap.add_argument("--channel", help="default: episodes.channel in ~/.rabet-reels.json")
    ap.add_argument("--handle", help="default: episodes.handle")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    print(*render(a.lang, a.channel, a.handle, a.force), sep="\n")
