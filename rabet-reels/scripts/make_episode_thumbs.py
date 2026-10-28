"""YouTube episode thumbnails (1280x720), 3 variants in the approved Ep2/Ep3 style, for 2 or 3 guests.
  A: navy grid, cut-outs left, l1 + orange l2 + kicker      B: cream + navy slanted block, outlined number, chips
  C: navy, l1 + big aqua English word + orange l2 + kicker
usage: python make_episode_thumbs.py spec.json
spec: {"out": "<dir>", "prefix": "Ep3_YouTube_Thumbnail_1280x720", "ep": "الحلقة الثالثة", "num": "03",
       "guests": [{"id": "haitham", "img": "<cut-out png>", "name": "هيثم فؤاد", "left": -190, "top": 14, "width": 540}, ...],
       "a": {"l1": "...", "l2": "...", "k": "..."}, "b": {"l1": "...", "l2": "...", "chips": ["AI AGENTS", "PLP"]},
       "c": {"l1": "في عصر الـ", "sw": "AI", "l2": "...", "k": "..."}}
Guests are drawn back to front in list order (put the front speaker last); name chips read right to left in reverse order.
Cut-outs: `npx hyperframes@0.8.163 remove-background frame.png -o cut.png` on a 4K frame; mics/table remnants at the bottom
are hidden by the name chips, the right edge fades out. Keep l1 short (≤ ~18 chars at 84 px) or it runs into the front head.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SNAP = "npx --yes hyperframes@0.8.163 snapshot --at 0.5 --no-end --describe false --no-proxy -o snap"
NAME_CLASSES = ["c", "a", "b"]

BASE = """
      @font-face { font-family: "LalezarLocal"; src: url("assets/fonts/Lalezar-Regular.ttf") format("truetype"); font-weight: 400; font-display: block; }
      @font-face { font-family: "AlexandriaFull"; src: url("assets/fonts/Alexandria.ttf") format("truetype"); font-weight: 100 900; font-display: block; }
      :root { --navy: #10335a; --deep: #0b2340; --aqua: #07c3be; --teal-ink: #0e7487; --orange: #ff6600; --cream: #fdf9f5; --ink: #0b0d10; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      #root { position: relative; width: 1280px; height: 720px; overflow: hidden; }
      .clip { position: absolute; inset: 0; overflow: hidden; }
      .ppl { position: absolute; inset: 0; }
      .who { position: absolute; object-fit: contain; -webkit-mask-image: linear-gradient(to left, transparent 0, #000 14%); mask-image: linear-gradient(to left, transparent 0, #000 14%); }
      .names { position: absolute; left: 24px; bottom: 24px; display: flex; gap: 12px; direction: rtl; }
      .nm { font-family: "AlexandriaFull"; font-weight: 900; font-size: 25px; padding: 4px 14px 10px; white-space: nowrap; box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.35); }
      .nm.a { background: var(--cream); color: var(--ink); } .nm.b { background: var(--ink); color: var(--cream); } .nm.c { background: var(--aqua); color: var(--ink); }
      .ep { position: absolute; right: 168px; top: 52px; font-family: "AlexandriaFull"; font-weight: 900; font-size: 30px; color: var(--ink); background: var(--aqua); padding: 4px 20px 10px; direction: rtl; box-shadow: 8px 8px 0 rgba(0, 0, 0, 0.3); }
      .txt { position: absolute; right: 40px; top: 150px; width: 560px; direction: rtl; display: flex; flex-direction: column; align-items: flex-start; gap: 10px; }
      .l1 { font-family: "LalezarLocal"; font-size: 84px; line-height: 1; white-space: nowrap; }
      .l2 { margin-top: 26px; font-family: "LalezarLocal"; font-size: 90px; line-height: 1.05; color: var(--cream); background: var(--orange); padding: 0 26px 16px; transform: rotate(-2deg); white-space: nowrap; box-shadow: 10px 10px 0 rgba(0, 0, 0, 0.3); }
"""
NAVY = """
      html, body { width: 1280px; height: 720px; overflow: hidden; background: var(--deep); }
      .bg { position: absolute; inset: 0; background-color: var(--navy);
        background-image: repeating-linear-gradient(0deg, rgba(7, 195, 190, 0.2) 0 2px, transparent 2px 48px), repeating-linear-gradient(90deg, rgba(7, 195, 190, 0.2) 0 2px, transparent 2px 48px); }
      .shade { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(11, 35, 64, 0) 0%, rgba(11, 35, 64, 0) 50%, rgba(11, 35, 64, 0.85) 60%, rgba(11, 35, 64, 0.96) 100%); }
      .who { filter: drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 24px 30px rgba(0, 0, 0, 0.5)); }
      .logo { position: absolute; right: 36px; top: 26px; width: 118px; height: 118px; object-fit: contain; }
      .l1 { color: var(--cream); text-shadow: 0 6px 0 rgba(0, 0, 0, 0.35); }
      .sw { font-family: "Archivo Black", sans-serif; direction: ltr; font-size: 150px; line-height: 0.9; letter-spacing: -0.03em; color: var(--aqua); text-shadow: 0 6px 0 rgba(0, 0, 0, 0.35); }
      .k { margin-top: 18px; font-family: "AlexandriaFull"; font-weight: 800; font-size: 29px; color: var(--cream); background: rgba(16, 51, 90, 0.95); border-right: 8px solid var(--aqua); padding: 8px 18px 14px; white-space: nowrap; }
"""
CREAM = """
      html, body { width: 1280px; height: 720px; overflow: hidden; background: var(--cream); }
      .bg { position: absolute; inset: 0; background-color: var(--cream);
        background-image: repeating-linear-gradient(0deg, rgba(16, 51, 90, 0.07) 0 2px, transparent 2px 48px), repeating-linear-gradient(90deg, rgba(16, 51, 90, 0.07) 0 2px, transparent 2px 48px); }
      .block { position: absolute; left: 0; top: 0; width: 790px; height: 720px; background: var(--navy); clip-path: polygon(0 0, 100% 0, 86% 100%, 0 100%); }
      .ppl { clip-path: polygon(0 0, 790px 0, 679px 720px, 0 720px); }
      .num { position: absolute; left: 6px; top: 6px; font-family: "Archivo Black", sans-serif; font-size: 400px; line-height: 0.8; letter-spacing: -0.06em; color: transparent; -webkit-text-stroke: 4px rgba(7, 195, 190, 0.55); direction: ltr; }
      .who { filter: drop-shadow(5px 0 0 var(--cream)) drop-shadow(-5px 0 0 var(--cream)) drop-shadow(0 5px 0 var(--cream)) drop-shadow(0 -5px 0 var(--cream)) drop-shadow(0 20px 26px rgba(0, 0, 0, 0.45)); }
      .badge { position: absolute; right: 40px; top: 34px; width: 120px; height: 120px; background: var(--navy); border-radius: 20px; display: flex; align-items: center; justify-content: center; }
      .badge img { width: 96px; height: 96px; object-fit: contain; }
      .ep { right: 182px; top: 64px; box-shadow: none; }
      .txt { top: 200px; width: 470px; gap: 6px; }
      .l1 { color: var(--navy); font-size: 86px; }
      .l2 { font-size: 84px; box-shadow: 10px 10px 0 var(--navy); }
      .k { margin-top: 28px; display: flex; gap: 8px; direction: ltr; align-self: flex-end; }
      .k span { font-family: "Archivo Black", sans-serif; font-size: 19px; color: var(--teal-ink); border: 3px solid var(--teal-ink); padding: 5px 12px 7px; white-space: nowrap; }
      .nm { box-shadow: none; }
"""


def page(css, body):
    return f"""<!doctype html>
<html lang="ar">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1280, height=720" />
    <title>Rabet YouTube Thumbnail</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{BASE}{css}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1280" data-height="720" data-duration="1">
      <section class="clip" data-start="0" data-duration="1" data-track-index="0">{body}
      </section>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def build(spec):
    g = spec["guests"]
    css_g = "".join(f'\n      #{x["id"]} {{ left: {x["left"]}px; top: {x["top"]}px; width: {x["width"]}px; }}' for x in g)
    people = '\n        <div class="ppl">' + "".join(
        f'<img id="{x["id"]}" class="who" src="assets/{x["id"]}.png" alt="" />' for x in g) + "</div>"
    names = '\n        <div class="names">' + "".join(
        f'<div class="nm {NAME_CLASSES[i]}">{x["name"]}</div>' for i, x in enumerate(reversed(g))) + "</div>"
    head = f'\n        <div class="shade"></div>\n        <img class="logo" src="assets/logo-mark.png" alt="" />\n        <div class="ep">{spec["ep"]}</div>'
    a, b, c = spec["a"], spec["b"], spec["c"]
    return {
        "": page(NAVY + css_g, f"""
        <div class="bg"></div>{people}{head}
        <div class="txt"><div class="l1">{a["l1"]}</div><div class="l2">{a["l2"]}</div><div class="k">{a["k"]}</div></div>{names}"""),
        "_B": page(CREAM + css_g, f"""
        <div class="bg"></div><div class="block"></div><div class="num">{spec.get("num", "")}</div>{people}
        <div class="badge"><img src="assets/logo-mark.png" alt="" /></div>
        <div class="ep">رابط بودكاست · {spec["ep"]}</div>
        <div class="txt"><div class="l1">{b["l1"]}</div><div class="l2">{b["l2"]}</div>
          <div class="k">{"".join(f"<span>{t}</span>" for t in b["chips"])}</div></div>{names}"""),
        "_C": page(NAVY + css_g, f"""
        <div class="bg"></div>{people}{head}
        <div class="txt"><div class="l1">{c["l1"]}</div><div class="sw">{c["sw"]}</div><div class="l2">{c["l2"]}</div><div class="k">{c["k"]}</div></div>{names}"""),
    }


def main(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    out = Path(spec["out"])
    work = out / "_episode_thumb"
    out.mkdir(parents=True, exist_ok=True)
    for suffix, html in build(spec).items():
        d = work / (suffix.strip("_") or "A")
        (d / "assets").mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL / "assets/fonts", d / "assets/fonts", dirs_exist_ok=True)
        shutil.copy(SKILL / "assets/logo-mark.png", d / "assets/logo-mark.png")
        for x in spec["guests"]:
            shutil.copy(x["img"], d / "assets" / f'{x["id"]}.png')
        for f in ("hyperframes.json", "meta.json", "package.json"):
            shutil.copy(SKILL / "templates/thumbs" / f, d / f)
        (d / "index.html").write_text(html, encoding="utf-8")
        shutil.rmtree(d / "snap", ignore_errors=True)
        subprocess.run(SNAP, cwd=d, shell=True, check=True)
        png = next((d / "snap").glob("frame-00*.png"))
        dst = out / f'{spec.get("prefix", "YouTube_Thumbnail_1280x720")}{suffix}'
        shutil.copy(png, f"{dst}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "2", f"{dst}.jpg"], check=True)
        print("wrote", f"{dst}.jpg")


if __name__ == "__main__":
    main(sys.argv[1])
