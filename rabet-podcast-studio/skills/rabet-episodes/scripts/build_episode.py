"""Render a mini / sub-episode (16:9, master resolution, no captions) from a spec (references/spec.md).

Structure: cold-open hook montage (hard cuts) -> intro logo -> body pieces -> outro logo.
Body joins: "cut" (hard), "jump" (same conversation, something skipped: punch-in when both sides keep the same
framing, so the jump reads as deliberate), "swipe" (0.4 s slide + soft whoosh: the piece comes from elsewhere).
Audio is cut exactly at each edge (every edge sits in a pause: pauses.py, check_edges.py) with 25 ms fades; swipe
joints get 0.2 s video handles so the slide overlaps them and picture stays in sync with sound.
Name cards: "auto" = each speaker's first long solo shot in the body (shots.json "who"), or a list, or "none".
Follow & subscribe pop-up (cta): rendered once by render_cta.py, overlaid bottom-right at the requested moments,
never across a joint, a name card or a burned-in card. ASK the user whether they want it (SKILL.md rule 1).

usage: python build_episode.py <spec.json> [--dry-run]   -> <out_dir>/<prefix> - <title> (src ...) [mmMss].mp4
                                                           + <spec>.render.json (used by qa_episode / brief_episode)
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

from ep import WHOOSH, jload, jsave, load_spec, mm, probe_len, render_meta_path, safe
from render_cta import DURATION as CTA_LEN, render as render_cta

D = 0.4            # swipe length (s); the audio joint sits in its middle
CARD = 6.0         # name card length (s)
SAME = 12.0        # proxy frame difference below this = same framing
SFX_GAIN = 0.6     # house SFX level (rabet-reels rule 11)


class Pictures:
    def __init__(self, ep):
        self.P = np.fromfile(ep["proxy"], np.uint8).reshape(-1, 36, 64, 3).astype(np.float32)
        self.shots = jload(ep["shots"])
        self.split = set(ep.get("split", []))

    def frame(self, t):
        return self.P[min(len(self.P) - 1, int(round(t * 2)))]

    def same(self, t1, t2):
        return np.abs(self.frame(t1) - self.frame(t2)).mean() < SAME

    def next_change(self, a, b):
        """seconds from a to the master's next camera change (proxy jump > 20), capped at the piece end"""
        i = int(round(a * 2)) + 1
        while i < min(len(self.P), int(b * 2)):
            if np.abs(self.P[i] - self.P[i - 1]).mean() > 20:
                return i / 2 - a - 0.25
            i += 1
        return b - a

    def in_split(self, t):
        return any((k in self.split or w == "split") for k, (s, e, w) in enumerate(self.shots) if s <= t < e)


def plan(spec):
    """segments, joins, punch-ins, cards, CTA times: everything except the ffmpeg graph"""
    ep, assets = spec["_episode"], spec["_assets"]
    pics = Pictures(ep)
    segs = [("hook", (h["in"], h["out"]), "cut") for h in spec.get("hook", [])]
    segs.append(("logo", assets["intro"], "cut"))
    segs += [("body", (b["in"], b["out"]), "cut" if i == 0 else b.get("join", "cut"))
             for i, b in enumerate(spec["body"])]
    segs.append(("logo", assets["outro"], "cut"))
    alen = [probe_len(x) if k == "logo" else x[1] - x[0] for k, x, _ in segs]
    swipe = [segs[i + 1][2] == "swipe" for i in range(len(segs) - 1)]
    zoom = spec.get("punch_in", 1.12)
    punch = {}
    for i in range(1, len(segs)):
        if zoom and segs[i][2] == "jump":
            pb, (a, b) = segs[i - 1][1][1], segs[i][1]
            prev_zoomed = i - 1 in punch and punch[i - 1] >= alen[i - 1] - 0.05
            # after a piece that ends punched in, the jump is the zoom back out
            if pics.same(pb - 0.3, a + 0.3) and not pics.in_split(a + 0.3) and not prev_zoomed:
                punch[i] = pics.next_change(a, b)
    starts = list(np.cumsum([0.0] + alen[:-1]))
    total = sum(alen)
    body_idx = [i for i, s in enumerate(segs) if s[0] == "body"]

    def to_out(s0, s1):          # source window -> output windows
        out = []
        for i in body_idx:
            a, b = segs[i][1]
            lo, hi = max(a, s0), min(b, s1)
            if hi > lo:
                out.append((starts[i] + lo - a, starts[i] + hi - a))
        return out

    cards = []
    cs = spec.get("cards", "auto")
    if cs == "auto":
        seen = set()
        for i in body_idx:
            a, b = segs[i][1]
            for k, (s, e, who) in enumerate(pics.shots):
                if who not in assets.get("name_cards", {}) or who in seen or k in pics.split:
                    continue
                s2, e2 = max(s, a + 0.6), min(e, b - 0.6)
                if e2 - s2 >= CARD + 0.8:
                    seen.add(who)
                    cards.append((who, starts[i] + (s2 - a) + 0.4))
    elif isinstance(cs, list):
        cards = [(c["who"], w[0]) for c in cs for w in to_out(c["src"], c["src"] + CARD)[:1]]
    cards.sort(key=lambda c: c[1])

    ctas = []
    cta = spec.get("cta")
    if cta:
        busy = [(tc, tc + CARD) for _, tc in cards]
        for s0, s1 in spec.get("burned_in", []):
            busy += to_out(s0, s1)
        joints = [starts[i] for i in range(1, len(segs))]
        body0, body_end = starts[body_idx[0]], starts[body_idx[-1]] + alen[body_idx[-1]]

        def ok(t):
            if t < body0 + 1.0 or t + CTA_LEN > body_end - 1.0:
                return False
            if any(t - 1.0 < j < t + CTA_LEN + 1.0 for j in joints):
                return False
            return not any(t < e + 1.0 and s - 1.0 < t + CTA_LEN for s, e in busy)

        for at in cta.get("at", ["after_intro", "middle", "end"]):
            target = {"after_intro": body0 + cta.get("after_intro_delay", 20.0), "middle": total / 2,
                      "end": body_end - cta.get("end_lead", 25.0)}.get(at, at)
            for step in range(0, 361):      # +-90 s in 0.5 s steps, nearest first
                t = float(target) + (step + 1) // 2 * 0.5 * (1 if step % 2 else -1)
                if ok(t):
                    ctas.append(round(t, 2))
                    busy.append((t, t + CTA_LEN))
                    break
            else:
                print(f"WARNING: no free 6 s window for the CTA near {target:.1f} s")
    return {"segs": segs, "alen": alen, "swipe": swipe, "punch": punch, "zoom": zoom, "starts": starts,
            "total": total, "cards": cards, "ctas": sorted(ctas)}


def graph(spec, p):
    ep, assets = spec["_episode"], spec["_assets"]
    W, H, fps = ep["width"], ep["height"], ep["fps"]
    segs, alen, swipe, punch = p["segs"], p["alen"], p["swipe"], p["punch"]
    inputs, vf, af = [], [], []
    for i, (kind, x, _) in enumerate(segs):
        if kind == "logo":
            inputs += ["-i", str(x)]
            vf.append(f"[{i}:v]scale={W}:{H}:flags=lanczos,fps={fps},setsar=1,format=yuv420p,setpts=PTS-STARTPTS,"
                      f"settb=1/{fps}[v{i}]")
            af.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
            continue
        a, b = x
        ha = D / 2 if i > 0 and swipe[i - 1] else 0.0
        hb = D / 2 if i < len(swipe) and swipe[i] else 0.0
        inputs += ["-ss", f"{a - ha:.3f}", "-t", f"{b - a + ha + hb:.3f}", "-i", ep["master"]]
        base = f"[{i}:v]fps={fps},setsar=1,format=yuv420p,setpts=PTS-STARTPTS,settb=1/{fps}"
        if i in punch:
            T, Z = punch[i] + ha, p["zoom"]
            z = (f"crop=trunc(iw/{Z}/2)*2:trunc(ih/{Z}/2)*2:(iw-ow)/2:(ih-oh)*0.35,"
                 f"scale={W}:{H}:flags=lanczos,setsar=1")
            vf.append(f"{base},split[p{i}][q{i}]")
            vf.append(f"[p{i}]trim=0:{T:.3f},setpts=PTS-STARTPTS,{z}[pz{i}]")
            vf.append(f"[q{i}]trim={T:.3f},setpts=PTS-STARTPTS[qn{i}]")
            vf.append(f"[pz{i}][qn{i}]concat=n=2:v=1:a=0,settb=1/{fps}[v{i}]")
        else:
            vf.append(f"{base}[v{i}]")
        af.append(f"[{i}:a]atrim={ha:.3f}:{ha + b - a:.3f},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.025,afade=t=out:st={b - a - 0.025:.3f}:d=0.025[a{i}]")
    # video chain: concat for hard/jump joints, xfade (slide) for swipes; offsets follow the audio clock
    cur, curlen, chain = "v0", alen[0] + (D / 2 if swipe[0] else 0), []
    for i in range(1, len(segs)):
        tail = D / 2 if i < len(swipe) and swipe[i] else 0
        if swipe[i - 1]:
            chain.append(f"[{cur}][v{i}]xfade=transition=slideleft:duration={D}:offset={curlen - D:.3f}[x{i}]")
            curlen += alen[i] + tail - D / 2
        else:
            chain.append(f"[{cur}][v{i}]concat=n=2:v=1:a=0,settb=1/{fps}[x{i}]")
            curlen += alen[i] + tail
        cur = f"x{i}"
    n = len(segs)
    for k, (who, tc) in enumerate(p["cards"]):
        inputs += ["-i", assets["name_cards"][who]]
        chain.append(f"[{n}:v]scale=-2:{H},setpts=PTS-STARTPTS+{tc:.3f}/TB[c{k}]")
        chain.append(f"[{cur}][c{k}]overlay=eof_action=pass:format=auto[o{k}]")
        cur, n = f"o{k}", n + 1
    cta_wav = []
    if p["ctas"]:
        mov, wav = render_cta(spec["cta"].get("lang", "en"))
        for k, tc in enumerate(p["ctas"]):
            inputs += ["-i", str(mov)]
            chain.append(f"[{n}:v]scale=-2:trunc(ih*{H}/2160/2)*2,setpts=PTS-STARTPTS+{tc:.3f}/TB[t{k}]")
            # cta.right_edge (px on a 1920-wide frame) moves the card left of a burned-in logo (EP1: 1650)
            re_ = spec["cta"].get("right_edge")
            x = f"{round(re_ * W / 1920)}-w" if re_ else "W-w"
            chain.append(f"[{cur}][t{k}]overlay=x={x}:y=H-h-{round(60 * H / 2160)}:eof_action=pass:format=auto[u{k}]")
            cur, n = f"u{k}", n + 1
            inputs += ["-i", str(wav)]
            cta_wav.append((n, tc))
            n += 1
    # audio: concat + whoosh at swipes + CTA SFX, all at the house SFX gain
    joints, t = [], 0.0
    for i in range(len(segs) - 1):
        t += alen[i]
        if swipe[i]:
            joints.append(t)
    achain = ["".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[ab]"]
    mix = []
    if joints:
        inputs += ["-i", str(WHOOSH)]
        achain.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={SFX_GAIN},asplit={len(joints)}"
                      + "".join(f"[w{j}]" for j in range(len(joints))))
        for j, tj in enumerate(joints):
            ms = int(max(0.0, tj - 0.3) * 1000)
            achain.append(f"[w{j}]adelay={ms}|{ms}[wd{j}]")
            mix.append(f"[wd{j}]")
        n += 1
    for k, (idx, tc) in enumerate(cta_wav):
        ms = int(tc * 1000)
        achain.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={SFX_GAIN},"
                      f"adelay={ms}|{ms}[cs{k}]")
        mix.append(f"[cs{k}]")
    achain.append(f"[ab]{''.join(mix)}amix=inputs={len(mix) + 1}:normalize=0:duration=first[aout]" if mix
                  else "[ab]anull[aout]")
    return inputs, ";".join(vf + af + chain + achain), cur, joints


def src_hint(body):
    """'src 00m40-28m10 + 64m04-64m48': body source ranges merged when < 5 min apart"""
    spans = []
    for a, b in sorted((x["in"], x["out"]) for x in body):
        if spans and a - spans[-1][1] < 300:
            spans[-1][1] = max(spans[-1][1], b)
        else:
            spans.append([a, b])
    return "src " + " + ".join(f"{mm(a)}-{mm(b)}" for a, b in spans)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    spec = load_spec(a.spec)
    p = plan(spec)
    inputs, g, cur, joints = graph(spec, p) if not a.dry_run else ([], "", "", [])
    name = f"{spec['prefix']} - {safe(spec['title'])} ({src_hint(spec['body'])}) [{mm(p['total'])}].mp4"
    out = Path(spec["_assets"]["out_dir"])
    meta = {"file": name, "out_dir": str(out), "total": p["total"],
            "segments": [(k, str(x) if k == "logo" else x, j) for k, x, j in p["segs"]], "alen": p["alen"],
            "swipes_at": [sum(p["alen"][:i + 1]) for i, s in enumerate(p["swipe"]) if s],
            "punch_in": {str(k): round(v, 2) for k, v in p["punch"].items()}, "cards": p["cards"], "cta": p["ctas"]}
    print(json.dumps({k: v for k, v in meta.items() if k != "segments"}, ensure_ascii=False), flush=True)
    if a.dry_run:
        return
    out.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", *inputs, "-filter_complex", g, "-map", f"[{cur}]", "-map", "[aout]",
           "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "21", "-b:v", "16M", "-maxrate", "28M",
           "-bufsize", "40M", "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
           "-movflags", "+faststart", "-t", f"{p['total']:.3f}", str(out / name)]
    subprocess.run(cmd, check=True)
    jsave(meta, render_meta_path(spec))
    print("wrote", out / name)


if __name__ == "__main__":
    main()
