"""Stamp a style template with one reel's data -> a renderable HyperFrames project.

HyperFrames reads root duration and <audio> tags from static HTML, so they can't be created
by script at runtime. This fills the template placeholders:
  {{DURATION}}  total (A-roll + CTA)      {{AROLL_DUR}}  A-roll length
  <!--SFX-->    one <audio> per content.sfx cue  ({"at": "<anchor id>" | seconds, "file", "vol", "offset"})
and copies media (aroll, cutout, dialogue WAV) + shared assets into the project.

usage: python assemble.py <template_dir> <project_dir> <reel-data.js> <aroll.mp4> [cutout.webm]
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

tpl, proj, data_js, aroll = map(Path, sys.argv[1:5])
cutout = Path(sys.argv[5]) if len(sys.argv) > 5 else None
proj.mkdir(parents=True, exist_ok=True)
assets = proj / "assets"
if (tpl / "assets").exists():
    shutil.copytree(tpl / "assets", assets, dirs_exist_ok=True)
assets.mkdir(exist_ok=True)
shared = Path(__file__).resolve().parent.parent / "assets"
if shared.exists():
    shutil.copytree(shared, assets, dirs_exist_ok=True)

reel = json.loads(data_js.read_text(encoding="utf-8").split("=", 1)[1].rstrip().rstrip(";"))
shutil.copy(data_js, proj / "reel-data.js")
shutil.copy(aroll, assets / "aroll.mp4")
if cutout:
    shutil.copy(cutout, assets / "cutout.webm")
# dialogue as audio-only WAV: an .mp4 used only by <audio> was drawn as a picture layer on long renders
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aroll), "-vn", "-c:a", "pcm_s16le", "-ar", "48000",
                str(assets / "vo.wav")], check=True)

dur = reel["duration"]
total = round(dur + reel["ctaDur"], 3)
lanes, tags = {}, []
# SFX sit under the voice: every cue's volume x sfxGain (house default 0.6 — user asked for quieter effects)
gain = float(os.environ.get("RABET_SFX_GAIN", reel["content"].get("sfxGain", 0.6)))
for i, c in enumerate(reel["content"].get("sfx", [])):
    at = c["at"]
    special = {"@hookEnd": reel["hookEnd"], "@cta": dur}
    t = (special[at] if at in special else reel["t"][at] if isinstance(at, str) else at) + c.get("offset", 0)
    t = max(0.0, round(t, 3))
    d = c.get("dur", 1.2)
    lane = 11
    while any(not (t >= e or t + d <= s) for s, e in lanes.get(lane, [])):
        lane += 1
    lanes.setdefault(lane, []).append((t, t + d))
    tags.append(f'      <audio id="sfx-{i}" src="assets/{c["file"]}.mp3" data-start="{t}" data-duration="{d}" '
                f'data-track-index="{lane}" data-volume="{round(c.get("vol", 0.45) * gain, 3)}"></audio>')

html = (tpl / "index.html").read_text(encoding="utf-8")
extra = data_js.parent / "extra"  # reel-specific files (e.g. SDR-converted B-roll) -> assets/
if extra.exists():
    shutil.copytree(extra, assets, dirs_exist_ok=True)
pol = reel["content"].get("polaroid")
if pol:
    b0 = reel["t"][pol["at"]] if isinstance(pol["at"], str) else pol["at"]
    b1 = reel["t"][pol["out"]] if isinstance(pol.get("out"), str) else b0 + 2.5
    html = html.replace("{{BROLL_START}}", str(round(b0, 3))).replace("{{BROLL_DUR}}", str(round(b1 - b0 + 0.35, 3)))
    html = html.replace('src="assets/broll.mp4"', f'src="assets/{pol.get("file", "broll.mp4")}"')
else:
    import re
    html = re.sub(r'\s*<video id="broll"[^>]*></video>', "", html)
html = html.replace("{{DURATION}}", str(total)).replace("{{AROLL_DUR}}", str(dur))
html = html.replace("<!--SFX-->", "\n".join(tags))
(proj / "index.html").write_text(html, encoding="utf-8")
for f in ("hyperframes.json", "package.json", "meta.json"):
    if (tpl / f).exists() and not (proj / f).exists():
        shutil.copy(tpl / f, proj / f)
print(f"{proj}: {total}s, {len(tags)} sfx cues")
