"""Classic Ep2/Ep3 YouTube thumbnails A/B/C in one go (kept for old specs and habits): runs the grid, board and word
styles of yt_thumbs.py and names them <prefix>.png/.jpg, <prefix>_B, <prefix>_C as before.
usage: python make_episode_thumbs.py spec.json
spec: {"out": "<dir>", "prefix": "Ep3_YouTube_Thumbnail_1280x720", "ep": "الحلقة الثالثة", "num": "03",
       "guests": [{"id": "haitham", "img": "<cut-out png>", "name": "هيثم فؤاد", "left": -190, "top": 14, "width": 540}, ...],
       "a": {"l1": "...", "l2": "...", "k": "..."}, "b": {"l1": "...", "l2": "...", "chips": ["AI AGENTS", "PLP"]},
       "c": {"l1": "في عصر الـ", "sw": "AI", "l2": "...", "k": "..."}}
Guests are drawn back to front in list order (put the front speaker last); name chips read right to left in reverse order.
Cut-outs: `npx hyperframes@0.8.163 remove-background frame.png -o cut.png` on a 4K frame; mics/table remnants at the bottom
are hidden by the name chips, the right edge fades out. Keep l1 short (≤ ~18 chars at 84 px) or it runs into the front head.
Any other style (or a single one of these): yt_thumbs.py.
"""
import json
import sys

import yt_thumbs

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    spec.setdefault("names", {"grid": "", "board": "_B", "word": "_C"})
    yt_thumbs.render(spec, ["grid", "board", "word"])
