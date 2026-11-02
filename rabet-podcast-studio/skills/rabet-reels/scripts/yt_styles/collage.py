"""Collage (Ep1/Ep3 reference): big cut-outs in front of two pinned photos on blue smoke, huge white l1 + orange l2 bar."""
from ._common import CUT, cut

NAME = "collage"
LOOK = "big cut-outs in front of two pinned topic photos on blue smoke, huge white l1 + orange l2 bar, episode label top right"
GUESTS = (3, 3)
TEXT = "l1, l2, ep, pins [2 photos]"
POS = [[-60, 60, 520], [380, 90, 560], [800, 40, 560]]   # left, centre, right guest: left, top, width
CSS = CUT + """
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
"""


def render(s):
    pins = "".join(f'<div class="abs ph" id="p{i}"><img src="{p}" alt="" /><div class="pin" style="left: 125px; top: -22px"></div></div>'
                   for i, p in enumerate(s["pin_files"][:2]))
    return CSS, f"""
      <img class="abs bg" src="assets/bg/smoke.jpg" alt="" /><div class="abs tint"></div>{pins}
      {cut(s, 1, POS)}{cut(s, 0, POS)}{cut(s, 2, POS)}
      <div class="abs t1 ar">{s["l1"]}</div><div class="abs t2 ar">{s["l2"]}</div>
      <img class="logo" src="assets/logo.png" alt="" /><div class="abs ep ar">{s["ep"]}</div>"""
