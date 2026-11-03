"""Classic A (Ep2/Ep3): navy grid, outlined cut-outs left, «الحلقة …» chip + logo, l1 cream + l2 orange tilted box + kicker."""
from . import _classic as c

NAME = "grid"
LOOK = "classic A: navy grid, outlined cut-outs left, episode chip + logo, cream l1 + orange tilted l2 box + kicker"
GUESTS = (2, 3)
TEXT = "l1, l2, k (guests need left/top/width)"
LEGACY = "a"


def render(s):
    return c.NAVY + c.guests_css(s), f"""
      <section class="clip"><div class="bg"></div>{c.people(s)}{c.navy_head(s)}
      <div class="txt"><div class="l1">{s["l1"]}</div><div class="l2">{s["l2"]}</div><div class="k">{s["k"]}</div></div>{c.names(s)}</section>"""
