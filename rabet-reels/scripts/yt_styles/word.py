"""Classic C (Ep2/Ep3): like grid with a huge aqua English word (sw) between l1 and l2."""
from . import _classic as c

NAME = "word"
LOOK = "classic C: grid layout with a huge aqua English word between l1 and the orange l2 box, kicker"
GUESTS = (2, 3)
TEXT = "l1, sw (English word), l2, k (guests need left/top/width)"
LEGACY = "c"


def render(s):
    return c.NAVY + c.guests_css(s), f"""
      <section class="clip"><div class="bg"></div>{c.people(s)}{c.navy_head(s)}
      <div class="txt"><div class="l1">{s["l1"]}</div><div class="sw">{s["sw"]}</div><div class="l2">{s["l2"]}</div><div class="k">{s["k"]}</div></div>{c.names(s)}</section>"""
