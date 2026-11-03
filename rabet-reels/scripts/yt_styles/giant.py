"""Giant word (Ep1/Ep3 reference): bright blurred office, huge orange word behind the speakers, small navy line, name tags."""
from ._common import CUT, cut, tags

NAME = "giant"
LOOK = "bright blurred office, huge orange word behind the speakers, small navy line above, name tags, navy bottom bar"
GUESTS = (3, 3)
TEXT = "giant (default l2), small (default l1 + …), ep"
POS = [[-40, 250, 500], [370, 236, 560], [790, 230, 540]]
CSS = CUT + """
      .bg { inset: 0; width: 1280px; height: 720px; object-fit: cover; filter: blur(6px) brightness(1.15) saturate(0.6); transform: scale(1.05); }
      .wash { inset: 0; background: linear-gradient(180deg, rgba(253, 249, 245, 0.72), rgba(253, 249, 245, 0.45) 60%, rgba(16, 51, 90, 0.35)); }
      .small { right: 54px; top: 26px; font-family: "AlexandriaFull"; font-weight: 800; font-size: 46px; color: var(--navy); }
      .giant { left: 0; right: 0; top: 64px; text-align: center; font-family: "LalezarLocal"; line-height: 1; color: var(--orange); }
      .curve { left: 0; top: 0; }
      .cut { --vm: linear-gradient(180deg, #000 70%, transparent 98%); }
      .bar { left: 0; right: 0; bottom: 0; height: 64px; background: var(--navy); }
      .logo { left: 22px; top: 16px; width: 88px; height: 88px; }
      .ep { right: 50%; transform: translateX(50%); bottom: 11px; font-family: "LalezarLocal"; font-size: 38px; color: var(--cream); }
"""


def render(s):
    word = s.get("giant") or s["l2"]
    px = min(300, 3200 // max(len(word), 1))
    return CSS, f"""
      <img class="abs bg" src="assets/bg/office.jpg" alt="" /><div class="abs wash"></div>
      <div class="abs giant ar" style="font-size: {px}px">{word}</div>
      <svg class="abs curve" width="1280" height="720" viewBox="0 0 1280 720"><path d="M-20 520 C 180 300, 330 330, 430 430 S 760 600, 900 420 S 1180 250, 1300 380" fill="none" stroke="#10335a" stroke-width="5" /></svg>
      {cut(s, 0, POS)}{cut(s, 2, POS)}{cut(s, 1, POS)}
      <div class="abs small ar">{s.get("small") or s["l1"] + "…"}</div><div class="abs bar"></div>
      {tags(s, ["left: 70px; bottom: 82px", "left: 560px; bottom: 82px", "right: 70px; bottom: 82px"])}
      <div class="abs ep ar">رابط بودكاست · {s["ep"]}</div><img class="logo" src="assets/logo.png" alt="" />"""
