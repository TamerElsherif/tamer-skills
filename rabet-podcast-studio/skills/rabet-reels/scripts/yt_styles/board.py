"""Classic B (Ep2/Ep3): cream board, navy slanted block with the outlined episode number, l1 navy + l2 orange + English chips."""
from . import _classic as c

NAME = "board"
LOOK = "classic B: cream board, navy slanted block with the outlined episode number, navy l1 + orange l2 + English chips"
GUESTS = (2, 3)
TEXT = "l1, l2, chips [English], num (guests need left/top/width)"
LEGACY = "b"
CSS = """
      html, body { background: var(--cream); }
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


def render(s):
    chips = "".join(f"<span>{t}</span>" for t in s.get("chips", []))
    return c.CSS + CSS + c.guests_css(s), f"""
      <section class="clip"><div class="bg"></div><div class="block"></div><div class="num">{s.get("num", "")}</div>{c.people(s)}
      <div class="badge"><img src="assets/logo-mark.png" alt="" /></div>
      <div class="ep">رابط بودكاست · {s["ep"]}</div>
      <div class="txt"><div class="l1">{s["l1"]}</div><div class="l2">{s["l2"]}</div><div class="k">{chips}</div></div>{c.names(s)}</section>"""
