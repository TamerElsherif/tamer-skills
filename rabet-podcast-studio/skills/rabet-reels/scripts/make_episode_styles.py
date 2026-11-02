"""YouTube episode thumbnails (1280x720) in four reference styles (Ep1/Ep3, 2026-11-02), Rabet colours, 3 guests:
  collage  - big cut-outs in front of two pinned photos on blue smoke, huge white l1 + orange l2 bar, «الحلقة …» top right
  dark     - dark close-up, small aqua kicker + l1 with orange l2, tilted, low centre, "#<num>" top right
  giant    - bright blurred office, huge orange word behind the speakers, small navy line, name tags, navy bottom bar
  stage    - navy curtain + teal spotlight, aqua frame, stacked centre title with l2 orange between cream rules
usage: python make_episode_styles.py spec.json [collage dark giant stage]
       python make_episode_styles.py stock "<pexels query>" <out_dir> [n]   (free Pexels photos for the collage pins;
                                                                           PEXELS_API_KEY from env or ./.env)
spec: {"out": "<dir>", "prefix": "Ep1_YouTube_Thumbnail_A", "ep": "الحلقة الأولى", "num": "1",
       "l1": "ليه المنتجات", "l2": "بتفشل؟", "k": "من الـ Product Manager لحد الـ AI",       (k optional: dark kicker)
       "mid": "وإنت",                                     (optional: stage line between l1 and l2)
       "giant": "بتفشل؟", "small": "ليه المنتجات…",        (optional: giant word / small line, default l2 / l1 + "…")
       "guests": [{"id": "haitham", "img": "<cut-out png>", "name": "هيثم فؤاد", "fade_right": true},   left
                  {"id": "tamer", "img": "...", "name": "تامر الشريف", "host": true},                   centre
                  {"id": "hossam", "img": "...", "name": "حسام عزت"}],                                  right
       "pins": ["<photo 1>", "<photo 2>"],                (collage; default: none -> no pinned photos)
       "styles": ["collage", "dark", "giant"],            (default: all four)
       "pos": {"collage": {"haitham": [left, top, width]}}}   (optional per-style position overrides, px)
Defaults fit trimmed 1080p cut-outs (aspect ~0.75-0.9, face toward the centre). fade_right fades a guest's right edge
(mic clips, cropped shoulders). Output: <out>/<prefix>_<style>.png/.jpg.
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SNAP = "npx --yes hyperframes@0.8.163 snapshot --at 0.5 --no-end --describe false --no-proxy -o snap"
POS = {   # left, centre, right guest: [left, top, width]
    "collage": [[-60, 60, 520], [380, 90, 560], [800, 40, 560]],
    "dark": [[-130, 40, 640], [340, 90, 600], [760, 20, 680]],
    "giant": [[-40, 250, 500], [370, 236, 560], [790, 230, 540]],
    "stage": [[-60, 150, 470], [700, 290, 470], [890, 70, 400]],
}

BASE = """
      @font-face { font-family: "LalezarLocal"; src: url("assets/fonts/Lalezar-Regular.ttf") format("truetype"); font-display: block; }
      @font-face { font-family: "AlexandriaFull"; src: url("assets/fonts/Alexandria.ttf") format("truetype"); font-weight: 100 900; font-display: block; }
      :root { --navy: #10335a; --deep: #0b2340; --teal: #1aaac1; --aqua: #07c3be; --orange: #ff6600; --cream: #fdf9f5; --ink: #0b0d10; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1280px; height: 720px; overflow: hidden; background: var(--deep); }
      #root { position: relative; width: 1280px; height: 720px; overflow: hidden; }
      .abs { position: absolute; }
      .cut { position: absolute; --vm: linear-gradient(180deg, #000 58%, transparent 90%); -webkit-mask-image: var(--vm); mask-image: var(--vm); }
      .cut.fr { -webkit-mask-image: linear-gradient(90deg, #000 74%, transparent 88%), var(--vm); mask-image: linear-gradient(90deg, #000 74%, transparent 88%), var(--vm); -webkit-mask-composite: source-in; mask-composite: intersect; }
      .logo { position: absolute; width: 96px; height: 96px; object-fit: contain; }
      .ar { direction: rtl; white-space: nowrap; }
      .nm { position: absolute; font-family: "AlexandriaFull"; font-weight: 800; font-size: 20px; padding: 3px 12px 7px; direction: rtl; white-space: nowrap; box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.35); background: var(--cream); color: var(--ink); }
      .nm.t { background: var(--aqua); }
"""

CSS = {
    "collage": """
      .bg { inset: 0; width: 1280px; height: 720px; object-fit: cover; filter: saturate(1.2) brightness(0.75); }
      .tint { inset: 0; background: radial-gradient(ellipse 700px 420px at 50% 35%, rgba(16, 51, 90, 0.2), rgba(11, 35, 64, 0.85)), linear-gradient(180deg, rgba(11, 35, 64, 0) 45%, rgba(11, 35, 64, 0.97) 82%); }
      .ph { background: #fff; padding: 10px 10px 30px; box-shadow: 0 14px 30px rgba(0, 0, 0, 0.6); }
      .ph img { display: block; width: 100%; height: 100%; object-fit: cover; }
      .pin { position: absolute; width: 38px; height: 38px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #ffb27a, var(--orange) 45%, #a83f00); box-shadow: 0 6px 8px rgba(0, 0, 0, 0.5); }
      .pin::after { content: ""; position: absolute; left: 17px; top: 34px; width: 4px; height: 18px; background: #c9c9c9; border-radius: 2px; }
      #p0 { left: 320px; top: 34px; width: 300px; height: 210px; transform: rotate(-7deg); }
      #p1 { left: 700px; top: 40px; width: 290px; height: 200px; transform: rotate(6deg); }
      .t1 { left: 0; right: 0; top: 440px; text-align: center; font-family: "LalezarLocal"; font-size: 120px; line-height: 1; color: #fff; background: linear-gradient(180deg, #ffffff 40%, #c9e9ee); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 6px 0 rgba(0, 0, 0, 0.55)); }
      .t2 { left: 50%; transform: translateX(-50%) rotate(-2deg); top: 572px; font-family: "LalezarLocal"; font-size: 100px; line-height: 1; color: #fff; background: var(--orange); padding: 0 40px 18px; border-radius: 6px; box-shadow: 0 8px 0 rgba(0, 0, 0, 0.4); }
      .logo { left: 24px; top: 20px; }
      .ep { right: 28px; top: 22px; font-family: "LalezarLocal"; font-size: 48px; color: var(--aqua); text-shadow: 0 3px 0 rgba(0, 0, 0, 0.6); }
    """,
    "dark": """
      .bg { inset: 0; background: radial-gradient(ellipse 900px 520px at 50% 40%, #12304f, #070b12 75%); }
      .rim { inset: 0; background: radial-gradient(circle 260px at 20% 30%, rgba(26, 170, 193, 0.22), transparent 70%), radial-gradient(circle 260px at 80% 30%, rgba(26, 170, 193, 0.22), transparent 70%); }
      .cut { --vm: linear-gradient(180deg, #000 55%, transparent 88%); filter: brightness(0.92) contrast(1.05); }
      .cut.c { filter: brightness(0.8); }
      .vig { inset: 0; background: radial-gradient(ellipse 760px 470px at 50% 42%, transparent 55%, rgba(0, 0, 0, 0.7)), linear-gradient(180deg, transparent 55%, rgba(5, 8, 14, 0.92) 92%); }
      .q { left: 0; right: 0; top: 490px; display: flex; flex-direction: column; align-items: center; transform: rotate(-3deg); }
      .q1 { font-family: "AlexandriaFull"; font-weight: 800; font-size: 32px; color: var(--aqua); }
      .q2 { font-family: "LalezarLocal"; font-size: 104px; line-height: 1.05; color: var(--cream); text-shadow: 0 5px 0 rgba(0, 0, 0, 0.7); }
      .q2 span { color: var(--orange); }
      .num { right: 34px; top: 20px; font-family: "LalezarLocal"; font-size: 72px; color: var(--cream); transform: skewX(-8deg); text-shadow: 0 4px 0 rgba(0, 0, 0, 0.6); }
      .num span { color: var(--orange); }
      .logo { left: 26px; top: 20px; width: 84px; height: 84px; opacity: 0.95; }
    """,
    "giant": """
      .bg { inset: 0; width: 1280px; height: 720px; object-fit: cover; filter: blur(6px) brightness(1.15) saturate(0.6); transform: scale(1.05); }
      .wash { inset: 0; background: linear-gradient(180deg, rgba(253, 249, 245, 0.72), rgba(253, 249, 245, 0.45) 60%, rgba(16, 51, 90, 0.35)); }
      .small { right: 54px; top: 26px; font-family: "AlexandriaFull"; font-weight: 800; font-size: 46px; color: var(--navy); }
      .giant { left: 0; right: 0; top: 64px; text-align: center; font-family: "LalezarLocal"; line-height: 1; color: var(--orange); }
      .curve { left: 0; top: 0; }
      .cut { --vm: linear-gradient(180deg, #000 70%, transparent 98%); }
      .bar { left: 0; right: 0; bottom: 0; height: 64px; background: var(--navy); }
      .logo { left: 22px; top: 16px; width: 88px; height: 88px; }
      .ep { right: 50%; transform: translateX(50%); bottom: 11px; font-family: "LalezarLocal"; font-size: 38px; color: var(--cream); }
    """,
    "stage": """
      .bg { inset: 0; background: repeating-linear-gradient(90deg, #0b2340 0 26px, #143e6b 26px 44px, #0d2a4a 44px 70px), var(--deep); }
      .bg::after { content: ""; position: absolute; inset: 0; background: radial-gradient(ellipse 520px 420px at 50% 0%, rgba(26, 170, 193, 0.55), transparent 70%), linear-gradient(180deg, rgba(11, 35, 64, 0) 40%, rgba(11, 35, 64, 0.95) 100%); }
      .frame { inset: 18px; border: 5px solid var(--aqua); box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.25); }
      .txt { left: 300px; width: 600px; top: 120px; display: flex; flex-direction: column; align-items: center; text-align: center; }
      .s1 { font-family: "LalezarLocal"; font-size: 70px; line-height: 1.05; color: var(--cream); text-shadow: 0 4px 0 rgba(0, 0, 0, 0.5); }
      .s2 { font-family: "LalezarLocal"; font-size: 70px; line-height: 1; color: #fff; margin-top: 4px; text-shadow: 0 4px 0 rgba(0, 0, 0, 0.5); }
      .s3 { margin-top: 18px; font-family: "LalezarLocal"; font-size: 122px; line-height: 1; color: var(--orange); padding: 8px 34px 26px; border-top: 5px solid var(--cream); border-bottom: 5px solid var(--cream); background: rgba(11, 35, 64, 0.82); text-shadow: 0 5px 0 rgba(0, 0, 0, 0.55); }
      .chip { left: 50%; transform: translateX(-50%); bottom: 40px; font-family: "AlexandriaFull"; font-weight: 800; font-size: 24px; color: var(--ink); background: var(--aqua); padding: 4px 22px 9px; box-shadow: 5px 5px 0 rgba(0, 0, 0, 0.35); }
      .logo { left: 38px; top: 34px; }
    """,
}


def cut(g, cls, style, spec, i):
    left, top, width = spec.get("pos", {}).get(style, {}).get(g["id"], POS[style][i])
    fr = " fr" if g.get("fade_right") else ""
    return (f'<img class="cut {cls}{fr}" src="assets/cut/{g["id"]}.png" alt="" '
            f'style="left: {left}px; top: {top}px; width: {width}px" />')


def names(spec, places):
    return "".join(f'<div class="nm{" t" if g.get("host") else ""}" style="{p}">{g["name"]}</div>'
                   for g, p in zip(spec["guests"], places))


def body(style, spec):
    L, C, R = spec["guests"]
    l1, l2, ep = spec["l1"], spec["l2"], spec["ep"]
    ppl = {"l": cut(L, "l", style, spec, 0), "c": cut(C, "c", style, spec, 1), "r": cut(R, "r", style, spec, 2)}
    if style == "collage":
        pins = "".join(f'<div class="abs ph" id="p{i}"><img src="assets/pins/{i}{Path(p).suffix}" alt="" />'
                       f'<div class="pin" style="left: 125px; top: -22px"></div></div>' for i, p in enumerate(spec.get("pins", [])[:2]))
        return f"""
      <img class="abs bg" src="assets/bg/smoke.jpg" alt="" /><div class="abs tint"></div>{pins}
      {ppl["c"]}{ppl["l"]}{ppl["r"]}
      <div class="abs t1 ar">{l1}</div><div class="abs t2 ar">{l2}</div>
      <img class="logo" src="assets/logo.png" alt="" /><div class="abs ep ar">{ep}</div>"""
    if style == "dark":
        k = f'<div class="q1">{spec["k"]}</div>' if spec.get("k") else ""
        return f"""
      <div class="abs bg"></div><div class="abs rim"></div>
      {ppl["c"]}{ppl["l"]}{ppl["r"]}
      <div class="abs vig"></div>
      <div class="abs q ar">{k}<div class="q2">{l1} <span>{l2}</span></div></div>
      <div class="abs num"><span>#</span>{spec["num"]}</div><img class="logo" src="assets/logo.png" alt="" />"""
    if style == "giant":
        word = spec.get("giant", l2)
        px = min(300, 3200 // max(len(word), 1))
        return f"""
      <img class="abs bg" src="assets/bg/office.jpg" alt="" /><div class="abs wash"></div>
      <div class="abs giant ar" style="font-size: {px}px">{word}</div>
      <svg class="abs curve" width="1280" height="720" viewBox="0 0 1280 720"><path d="M-20 520 C 180 300, 330 330, 430 430 S 760 600, 900 420 S 1180 250, 1300 380" fill="none" stroke="#10335a" stroke-width="5" /></svg>
      {ppl["l"]}{ppl["r"]}{ppl["c"]}
      <div class="abs small ar">{spec.get("small", l1 + "…")}</div><div class="abs bar"></div>
      {names(spec, ["left: 70px; bottom: 82px", "left: 560px; bottom: 82px", "right: 70px; bottom: 82px"])}
      <div class="abs ep ar">رابط بودكاست · {ep}</div><img class="logo" src="assets/logo.png" alt="" />"""
    mid = f'<div class="s2">{spec["mid"]}</div>' if spec.get("mid") else ""
    return f"""
      <div class="abs bg"></div>
      {ppl["l"]}{ppl["r"]}{ppl["c"]}
      <div class="abs txt ar"><div class="s1">{l1}</div>{mid}<div class="s3">{l2}</div></div>
      {names(spec, ["left: 60px; bottom: 110px", "left: 780px; bottom: 90px", "right: 60px; bottom: 150px"])}
      <div class="abs chip ar">{ep}</div><div class="abs frame"></div><img class="logo" src="assets/logo.png" alt="" />"""


def page(style, spec):
    return f"""<!doctype html>
<html lang="ar">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1280, height=720" />
    <title>Rabet Thumbnail {style}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{BASE}{CSS[style]}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1280" data-height="720" data-duration="1">{body(style, spec)}
    </div>
    <script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""


def render(spec_path, styles):
    spec = json.load(open(spec_path, encoding="utf-8"))
    assert len(spec["guests"]) == 3, "guests: exactly 3 (left, centre, right)"
    out = Path(spec["out"])
    work = out / "_styles"
    for style in styles or spec.get("styles") or list(CSS):
        d = work / style
        for sub in ("cut", "pins", "bg"):
            (d / "assets" / sub).mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL / "assets/fonts", d / "assets/fonts", dirs_exist_ok=True)
        shutil.copy(SKILL / "assets/logo.png", d / "assets/logo.png")
        for f in ("smoke.jpg", "office.jpg"):
            shutil.copy(SKILL / "assets/thumb_bg" / f, d / "assets/bg" / f)
        for g in spec["guests"]:
            shutil.copy(g["img"], d / "assets/cut" / f'{g["id"]}.png')
        for i, p in enumerate(spec.get("pins", [])[:2]):
            shutil.copy(p, d / "assets/pins" / f"{i}{Path(p).suffix}")
        for f in ("hyperframes.json", "meta.json", "package.json"):
            shutil.copy(SKILL / "templates/thumbs" / f, d / f)
        (d / "index.html").write_text(page(style, spec), encoding="utf-8")
        shutil.rmtree(d / "snap", ignore_errors=True)
        if subprocess.run(SNAP, cwd=d, shell=True, capture_output=True).returncode:   # first snapshot sometimes fails
            subprocess.run(SNAP, cwd=d, shell=True, check=True, capture_output=True)
        png = next((d / "snap").glob("frame-00*.png"))
        dst = out / f'{spec["prefix"]}_{style}'
        shutil.copy(png, f"{dst}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "2", f"{dst}.jpg"], check=True)
        print("wrote", f"{dst}.png")


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
    if sys.argv[1] == "stock":
        stock(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 4)
    else:
        render(sys.argv[1], sys.argv[2:])
