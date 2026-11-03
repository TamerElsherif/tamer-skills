"""YouTube thumbnails (1280x720) from an open style catalog: every file in scripts/yt_styles/ (not starting with "_")
is one style; add a style by adding a file (see yt_styles/_common.py for the interface).
usage: python yt_thumbs.py --list                            styles with their look, guest count and text fields
       python yt_thumbs.py spec.json <style> [<style> ...]   or list them in spec "styles"; no style -> the list
       python yt_thumbs.py stock "<pexels query>" <dir> [n]  free Pexels photos (collage pins; PEXELS_API_KEY env/.env)
spec: {"out": "<dir>", "prefix": "Ep1_YouTube_Thumbnail", "ep": "الحلقة الأولى", "num": "1",
       "l1": "ليه المنتجات", "l2": "بتفشل؟", "k": "من الـ Product Manager لحد الـ AI",   shared text, every style
       "text": {"board": {"l1": "مدير المنتج", "l2": "بيعمل إيه؟", "chips": ["AI PM"]}},   per-style text (title pairing)
       "guests": [{"id": "haitham", "img": "<cut-out png>", "name": "هيثم فؤاد", "fade_right": true,
                   "left": -190, "top": 14, "width": 540}, ...],     left, centre (host: "host": true), right;
                                                                     left/top/width = classic (grid/board/word) placement
       "pins": ["<photo>", "<photo>"], "pos": {"<style>": {"<guest id>": [left, top, width]}},
       "names": {"grid": ""}}                                        output suffix per style (default "_<style>")
Old make_episode_thumbs specs (blocks "a"/"b"/"c") still work: grid reads "a", board "b", word "c".
Output: <out>/<prefix><suffix>.png/.jpg, work dirs in <out>/_yt_thumbs/<style>/.
"""
import importlib
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SNAP = "npx --yes hyperframes@0.8.163 snapshot --at 0.5 --no-end --describe false --no-proxy -o snap"
sys.path.insert(0, str(HERE))
from yt_styles._common import page  # noqa: E402


def styles():
    out = {}
    for f in sorted((HERE / "yt_styles").glob("[!_]*.py")):
        m = importlib.import_module(f"yt_styles.{f.stem}")
        out[m.NAME] = m
    return out


def show(cat):
    for name, m in cat.items():
        lo, hi = m.GUESTS
        print(f"{name:10s} {lo}-{hi} guests  {m.LOOK}\n{'':10s} text: {m.TEXT}")


def merge(spec, m):
    s = {**spec, **spec.get(getattr(m, "LEGACY", None) or "", {}), **spec.get("text", {}).get(m.NAME, {})}
    s["style"] = m.NAME
    s["pin_files"] = [f"assets/pins/{i}{Path(p).suffix}" for i, p in enumerate(spec.get("pins", []))]
    return s


def render(spec, names):
    cat = styles()
    unknown = [n for n in names if n not in cat]
    if not names or unknown:
        print(f"unknown style(s): {unknown}\n" if unknown else "no style given; pick one or more:\n")
        show(cat)
        sys.exit(2)
    out = Path(spec["out"])
    out.mkdir(parents=True, exist_ok=True)
    for name in names:
        m = cat[name]
        lo, hi = m.GUESTS
        assert lo <= len(spec["guests"]) <= hi, f"{name}: needs {lo}-{hi} guests, spec has {len(spec['guests'])}"
        s = merge(spec, m)
        css, body = m.render(s)
        d = out / "_yt_thumbs" / name
        for sub in ("cut", "pins", "bg"):
            shutil.rmtree(d / "assets" / sub, ignore_errors=True)
            (d / "assets" / sub).mkdir(parents=True)
        shutil.copytree(SKILL / "assets/fonts", d / "assets/fonts", dirs_exist_ok=True)
        for f in ("logo.png", "logo-mark.png"):
            shutil.copy(SKILL / "assets" / f, d / "assets" / f)
        for f in (SKILL / "assets/thumb_bg").glob("*"):
            shutil.copy(f, d / "assets/bg" / f.name)
        for g in spec["guests"]:
            shutil.copy(g["img"], d / "assets/cut" / f'{g["id"]}.png')
        for i, p in enumerate(spec.get("pins", [])):
            shutil.copy(p, d / "assets/pins" / f"{i}{Path(p).suffix}")
        for f in ("hyperframes.json", "meta.json", "package.json"):
            shutil.copy(SKILL / "templates/thumbs" / f, d / f)
        (d / "index.html").write_text(page(name, css, body), encoding="utf-8")
        shutil.rmtree(d / "snap", ignore_errors=True)
        if subprocess.run(SNAP, cwd=d, shell=True, capture_output=True).returncode:   # first snapshot sometimes fails
            subprocess.run(SNAP, cwd=d, shell=True, check=True, capture_output=True)
        png = next((d / "snap").glob("frame-00*.png"))
        dst = out / f'{spec.get("prefix", "YouTube_Thumbnail_1280x720")}{spec.get("names", {}).get(name, "_" + name)}'
        shutil.copy(png, f"{dst}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "2", f"{dst}.jpg"], check=True)
        print("wrote", f"{dst}.jpg")


def stock(query, out_dir, n=4):
    key = os.environ.get("PEXELS_API_KEY") or next((l.split("=", 1)[1].strip().strip('"') for l in open(".env", encoding="utf-8")
                                                    if l.startswith("PEXELS_API_KEY")), None)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": query, "per_page": n, "orientation": "landscape"})
    photos = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": key, "User-Agent": "Mozilla/5.0"})))["photos"]
    tag = "_".join(query.split()[:2])
    for i, p in enumerate(photos):
        req = urllib.request.Request(p["src"]["large"], headers={"User-Agent": "Mozilla/5.0"})
        (out / f"{tag}_{i}.jpg").write_bytes(urllib.request.urlopen(req).read())
        print(out / f"{tag}_{i}.jpg", "-", p["photographer"])


if __name__ == "__main__":
    if sys.argv[1] == "--list":
        show(styles())
    elif sys.argv[1] == "stock":
        stock(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 4)
    else:
        spec = json.load(open(sys.argv[1], encoding="utf-8"))
        render(spec, sys.argv[2:] or spec.get("styles", []))
