"""Stage (Ep3 reference): navy curtain + teal spotlight, aqua frame, stacked centre title with l2 between cream rules."""
from ._common import CUT, cut, tags

NAME = "stage"
LOOK = "navy curtain + teal spotlight, aqua frame, stacked centre title with orange l2 between cream rules, episode chip"
GUESTS = (3, 3)
TEXT = "l1, mid (optional middle line), l2, ep"
POS = [[-60, 150, 470], [700, 290, 470], [890, 70, 400]]
CSS = CUT + """
      .bg { inset: 0; background: repeating-linear-gradient(90deg, #0b2340 0 26px, #143e6b 26px 44px, #0d2a4a 44px 70px), var(--deep); }
      .bg::after { content: ""; position: absolute; inset: 0; background: radial-gradient(ellipse 520px 420px at 50% 0%, rgba(26, 170, 193, 0.55), transparent 70%), linear-gradient(180deg, rgba(11, 35, 64, 0) 40%, rgba(11, 35, 64, 0.95) 100%); }
      .frame { inset: 18px; border: 5px solid var(--aqua); box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.25); }
      .txt { left: 300px; width: 600px; top: 120px; display: flex; flex-direction: column; align-items: center; text-align: center; }
      .s1 { font-family: "LalezarLocal"; font-size: 70px; line-height: 1.05; color: var(--cream); text-shadow: 0 4px 0 rgba(0, 0, 0, 0.5); }
      .s2 { font-family: "LalezarLocal"; font-size: 70px; line-height: 1; color: #fff; margin-top: 4px; text-shadow: 0 4px 0 rgba(0, 0, 0, 0.5); }
      .s3 { margin-top: 18px; font-family: "LalezarLocal"; font-size: 122px; line-height: 1; color: var(--orange); padding: 8px 34px 26px; border-top: 5px solid var(--cream); border-bottom: 5px solid var(--cream); background: rgba(11, 35, 64, 0.82); text-shadow: 0 5px 0 rgba(0, 0, 0, 0.55); }
      .chip { left: 50%; transform: translateX(-50%); bottom: 40px; font-family: "AlexandriaFull"; font-weight: 800; font-size: 24px; color: var(--ink); background: var(--aqua); padding: 4px 22px 9px; box-shadow: 5px 5px 0 rgba(0, 0, 0, 0.35); }
      .logo { left: 38px; top: 34px; }
"""


def render(s):
    mid = f'<div class="s2">{s["mid"]}</div>' if s.get("mid") else ""
    return CSS, f"""
      <div class="abs bg"></div>
      {cut(s, 0, POS)}{cut(s, 2, POS)}{cut(s, 1, POS)}
      <div class="abs txt ar"><div class="s1">{s["l1"]}</div>{mid}<div class="s3">{s["l2"]}</div></div>
      {tags(s, ["left: 60px; bottom: 110px", "left: 780px; bottom: 90px", "right: 60px; bottom: 150px"])}
      <div class="abs chip ar">{s["ep"]}</div><div class="abs frame"></div><img class="logo" src="assets/logo.png" alt="" />"""
