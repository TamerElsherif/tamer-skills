"""Shared layout of the classic Ep2/Ep3 styles (grid, board, word): 2-3 cut-outs on the left with a white outline,
text block on the right, name chips bottom left. Guests are placed by their own "left"/"top"/"width" in the spec
(or spec "pos"), drawn back to front in list order (front speaker last); name chips read right to left."""
from ._common import place

NAME_CLASSES = ["c", "a", "b"]
CSS = """
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
NAVY = CSS + """
      .bg { position: absolute; inset: 0; background-color: var(--navy);
        background-image: repeating-linear-gradient(0deg, rgba(7, 195, 190, 0.2) 0 2px, transparent 2px 48px), repeating-linear-gradient(90deg, rgba(7, 195, 190, 0.2) 0 2px, transparent 2px 48px); }
      .shade { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(11, 35, 64, 0) 0%, rgba(11, 35, 64, 0) 50%, rgba(11, 35, 64, 0.85) 60%, rgba(11, 35, 64, 0.96) 100%); }
      .who { filter: drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 24px 30px rgba(0, 0, 0, 0.5)); }
      .logo { position: absolute; right: 36px; top: 26px; width: 118px; height: 118px; object-fit: contain; }
      .l1 { color: var(--cream); text-shadow: 0 6px 0 rgba(0, 0, 0, 0.35); }
      .sw { font-family: "Archivo Black", sans-serif; direction: ltr; font-size: 150px; line-height: 0.9; letter-spacing: -0.03em; color: var(--aqua); text-shadow: 0 6px 0 rgba(0, 0, 0, 0.35); }
      .k { margin-top: 18px; font-family: "AlexandriaFull"; font-weight: 800; font-size: 29px; color: var(--cream); background: rgba(16, 51, 90, 0.95); border-right: 8px solid var(--aqua); padding: 8px 18px 14px; white-space: nowrap; }
"""


def guests_css(s):
    rows = []
    for i, g in enumerate(s["guests"]):
        left, top, width = place(s, i, g, [[g["left"], g["top"], g["width"]]] * len(s["guests"]))
        rows.append(f'\n      #g{i} {{ left: {left}px; top: {top}px; width: {width}px; }}')
    return "".join(rows)


def people(s):
    return '\n      <div class="ppl">' + "".join(
        f'<img id="g{i}" class="who" src="assets/cut/{g["id"]}.png" alt="" />' for i, g in enumerate(s["guests"])) + "</div>"


def names(s):
    return '\n      <div class="names">' + "".join(
        f'<div class="nm {NAME_CLASSES[i]}">{g["name"]}</div>' for i, g in enumerate(reversed(s["guests"]))) + "</div>"


def navy_head(s):
    return f'\n      <div class="shade"></div>\n      <img class="logo" src="assets/logo-mark.png" alt="" />\n      <div class="ep">{s["ep"]}</div>'
