"""Prepend the thumbnail as a short cover intro (for platforms where Postiz can't set a cover:
Instagram, Facebook, TikTok, LinkedIn). The still gets a gentle push-in, then a whoosh cuts into
the reel's hook. YouTube uses the real thumbnail setting instead — don't use this for YouTube.

usage: python add_cover.py <reel.mp4> <thumb.png> <out.mp4> [seconds=1.2] [whoosh.mp3]
"""
import subprocess
import sys

reel, thumb, out = sys.argv[1:4]
sec = float(sys.argv[4]) if len(sys.argv) > 4 else 1.2
whoosh = sys.argv[5] if len(sys.argv) > 5 else None
frames = int(round(sec * 25))
inputs = ["-loop", "1", "-framerate", "25", "-t", f"{sec}", "-i", thumb, "-i", reel]
amix = f"anullsrc=r=48000:cl=stereo,atrim=0:{sec}[sil];"
if whoosh:
    inputs += ["-i", whoosh]
    amix = (f"anullsrc=r=48000:cl=stereo,atrim=0:{sec}[sil0];[2:a]aresample=48000,volume=0.45,"
            f"atrim=0:{sec},apad=whole_dur={sec}[w];[sil0][w]amix=inputs=2:normalize=0[sil];")
graph = (f"[0:v]scale=1188:2112,zoompan=z='1+0.035*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
         f":d=1:s=1080x1920:fps=25,format=yuv420p,setsar=1[cv];"
         f"[1:v]fps=25,format=yuv420p,setsar=1[rv];[1:a]aresample=48000,aformat=channel_layouts=stereo[ra];"
         + amix + "[cv][sil][rv][ra]concat=n=2:v=1:a=1[v][a]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "25",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print("wrote", out)
