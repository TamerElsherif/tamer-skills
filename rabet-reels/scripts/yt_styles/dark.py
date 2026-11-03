"""Dark (Ep1/Ep3 reference): dark close-up, small aqua kicker + l1 with orange l2, tilted, low centre, «#N» top right."""
from ._common import CUT, cut

NAME = "dark"
LOOK = "dark close-up of the three speakers, small aqua kicker + l1 with orange l2 tilted low centre, «#N» top right"
GUESTS = (3, 3)
TEXT = "l1, l2, k (optional kicker), num"
POS = [[-130, 40, 640], [340, 90, 600], [760, 20, 680]]
CSS = CUT + """
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
"""


def render(s):
    k = f'<div class="q1">{s["k"]}</div>' if s.get("k") else ""
    return CSS, f"""
      <div class="abs bg"></div><div class="abs rim"></div>
      {cut(s, 1, POS, "c")}{cut(s, 0, POS)}{cut(s, 2, POS)}
      <div class="abs vig"></div>
      <div class="abs q ar">{k}<div class="q2">{s["l1"]} <span>{s["l2"]}</span></div></div>
      <div class="abs num"><span>#</span>{s["num"]}</div><img class="logo" src="assets/logo.png" alt="" />"""
