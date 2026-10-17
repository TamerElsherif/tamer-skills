"""Speaker matte with clean head edges.

remove-background (u2net_human_seg) runs at a fixed 320 px input, so a full 1216x2160 frame
gets coarse, haloed head edges. This matts a top crop (head + shoulders) at ~1.8x finer
detail, optionally merges it over a full-frame matte for the body, chokes the alpha 1 px
and feathers it, then re-attaches the ORIGINAL A-roll RGB (no colour drift from re-encoding).

usage:
  python refine_matte.py <aroll.mp4> <out.webm> --head-rows 1400            # head/upper body only
  python refine_matte.py <aroll.mp4> <out.webm> --head-rows 1216 --full     # full body, refined head
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print(">", " ".join(str(c) for c in cmd)[:180])
    subprocess.run(cmd, check=True, shell=False)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True).stdout.strip())


def matte(src, out):
    """Gray speaker mask (.mkv). GPU via gpu_matte.py; HyperFrames on CPU only as a fallback."""
    if Path(out).exists() and Path(out).stat().st_size > 0:  # reuse: matting is the slow step
        print("reuse", out)
        return
    gpu = subprocess.run([sys.executable, str(Path(__file__).with_name("gpu_matte.py")), str(src), str(out)])
    if gpu.returncode == 0:
        return
    print("gpu_matte failed -> falling back to hyperframes remove-background (CPU, ~10x slower)")
    tmp = Path(out).with_suffix(".hf.webm")
    # npx resolves through the shell on Windows
    run(["npx.cmd" if Path("C:/").exists() else "npx", "-y", "hyperframes", "remove-background", str(src),
         "-o", str(tmp), "--quality", "best"])
    run(["ffmpeg", "-y", "-loglevel", "error", "-c:v", "libvpx-vp9", "-i", tmp, "-vf", "alphaextract,format=gray",
         "-c:v", "ffv1", out])


ap = argparse.ArgumentParser()
ap.add_argument("aroll")
ap.add_argument("out")
ap.add_argument("--head-rows", type=int, default=1400)
ap.add_argument("--full", action="store_true")
ap.add_argument("--fade", type=int, default=160, help="rows of blend at the bottom of the head crop")
a = ap.parse_args()

aroll, out = Path(a.aroll), Path(a.out)
work = out.parent / (out.stem + "_work")
work.mkdir(parents=True, exist_ok=True)
W, H = probe(aroll)
D = duration(aroll)
hr = min(a.head_rows, H)

head_src = work / "head_src.mp4"
run(["ffmpeg", "-y", "-loglevel", "error", "-i", aroll, "-vf", f"crop={W}:{hr}:0:0", "-an",
     "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", head_src])
head_m = work / "head_mask.mkv"
matte(head_src, head_m)
full_m = None
if a.full:
    full_m = work / "full_mask.mkv"
    matte(aroll, full_m)

# alpha planes -> merge -> choke/feather -> re-attach original RGB
fade_top = hr - a.fade
mask_png = work / "mask.png"
run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}", "-frames:v", "1",
     "-vf", f"format=gray,geq=lum='if(lt(Y,{fade_top}),255,if(lt(Y,{hr}),255*({hr}-Y)/{a.fade},0))'", mask_png])
inputs = ["-i", aroll, "-i", head_m, "-loop", "1", "-framerate", "25", "-t", f"{D}", "-i", mask_png]
if full_m:
    inputs += ["-i", full_m]
    base = "[3:v]format=gray[fa];"
else:
    base = f"color=c=black:s={W}x{H}:r=25:d={D},format=gray[fa];"
graph = (f"[1:v]format=gray,pad={W}:{H}:0:0:black[ha];[2:v]format=gray[mask];" + base +
         "[fa][ha][mask]maskedmerge[al];"
         "[al]erosion,erosion,gblur=sigma=1.0,format=gray[alc];"
         "[0:v]format=yuva420p[rgb];[rgb][alc]alphamerge,format=yuva420p[v]")
run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[v]", "-t", f"{D}",
     "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "16", "-b:v", "0", "-auto-alt-ref", "0",
     "-deadline", "good", "-cpu-used", "4", "-row-mt", "1", "-metadata:s:v:0", "alpha_mode=1", "-r", "25", out])
print("wrote", out)
