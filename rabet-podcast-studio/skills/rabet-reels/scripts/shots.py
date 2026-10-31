"""Shot boundaries + speaker face position for multi-camera masters (auto-framing).

shots(src, a, b) -> [(start, end, face_cx), ...]  in absolute source seconds; face_cx in source pixels
(None when no face was found — the caller falls back to the previous shot).
Cuts: ffmpeg scene score on a low-res proxy. Faces: OpenCV Haar (frontal, then profile) on 3 frames per shot.
"""
import re
import subprocess

import cv2
import numpy as np

_FRONT = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_PROF = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")


def cuts(src, a, b, thresh=0.25):
    cmd = ["ffmpeg", "-hide_banner", "-ss", f"{a}", "-t", f"{b - a}", "-i", src, "-an",
           "-vf", f"scale=320:-1,select='gt(scene,{thresh})',showinfo", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore").stderr
    return [a + float(t) for t in re.findall(r"pts_time:([\d.]+)", err)]


def frame(src, t, width=960):
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t}", "-i", src, "-frames:v", "1",
                          "-vf", f"scale={width}:-1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True).stdout
    h = len(out) // (width * 3)
    return np.frombuffer(out, np.uint8)[: h * width * 3].reshape(h, width, 3) if h else None


def face_x(src, t, src_w=3840, width=960):
    img = frame(src, t, width)
    if img is None:
        return None
    g = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    found = []
    for cas, flip in ((_FRONT, False), (_PROF, False), (_PROF, True)):
        im = cv2.flip(g, 1) if flip else g
        fs = cas.detectMultiScale(im, scaleFactor=1.1, minNeighbors=6, minSize=(width // 20, width // 20))
        for (x, y, w, h) in fs:
            cx = (width - (x + w / 2)) if flip else (x + w / 2)
            found.append((w * h, cx))
        if found:
            break
    if not found:
        return None
    return max(found)[1] * src_w / width  # largest face = the speaker in a single-person shot


def shots(src, a, b, src_w=3840):
    bounds = [a] + [c for c in cuts(src, a, b) if a + 0.2 < c < b - 0.2] + [b]
    out, last = [], None
    for s, e in zip(bounds[:-1], bounds[1:]):
        xs = [x for x in (face_x(src, s + (e - s) * k, src_w) for k in (0.25, 0.5, 0.75)) if x is not None]
        fx = float(np.median(xs)) if xs else last
        out.append((round(s, 3), round(e, 3), fx))
        last = fx if fx is not None else last
    # back-fill leading shots with no face
    first = next((x for _, _, x in out if x is not None), src_w * 0.62)
    return [(s, e, x if x is not None else first) for s, e, x in out]


if __name__ == "__main__":
    import sys
    for s in shots(sys.argv[1], float(sys.argv[2]), float(sys.argv[3])):
        print(s)
