"""Render one reel thumbnail (1080x1920 PNG) from a JSON spec with the parametric template.

spec keys: type (T1|T2|T3), l1, l2 / l1html (T3), kicker, chip1, chip2, tag, stamp,
           subject (cut-out PNG, T1/T2), subjectBox {left, top, width}, bg (T2 image), frame (T3 still), frameLeft.
usage: python make_thumb.py <thumb.json> <out.png>
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

spec_p, out = Path(sys.argv[1]), Path(sys.argv[2])
spec = json.loads(spec_p.read_text(encoding="utf-8"))
sk = Path(__file__).resolve().parent.parent
proj = spec_p.parent / "hf" / "thumb"
shutil.copytree(sk / "templates" / "thumb", proj, dirs_exist_ok=True)
shutil.copytree(sk / "assets", proj / "assets", dirs_exist_ok=True)
for key, name in (("subject", "subject.png"), ("bg", "bg.jpg"), ("frame", "frame.png")):
    if spec.get(key):
        shutil.copy(spec[key], proj / "assets" / name)
(proj / "thumb-data.js").write_text("window.THUMB = " + json.dumps(spec, ensure_ascii=False) + ";\n", encoding="utf-8")
for f in ("hyperframes.json", "package.json", "meta.json"):
    src = sk / "templates" / "s1-clean" / f
    if not (proj / f).exists():
        shutil.copy(src, proj / f)
snap = proj / "snap"
subprocess.run("npx --yes hyperframes@0.8.163 snapshot --at 0.5 --no-end --describe false --no-proxy -o snap",
               cwd=proj, shell=True, check=True, capture_output=True)
shutil.copy(next(snap.glob("frame-00*.png")), out)
print("wrote", out)
