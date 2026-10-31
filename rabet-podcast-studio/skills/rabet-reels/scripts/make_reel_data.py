"""Turn an A-roll's words + segments + a style's beats file into reel-data.js for a template.

Everything a template animates is resolved here, so a new reel = new data, not new code:
  * caption chunks (2-3 words, split on pauses / segment joins / length), English terms
    normalized to Latin via glossary.json, emphasis words flagged;
  * camera joins (segment starts) for punch-in alternation;
  * beat anchors: {"word": "Sales", "n": 1, "in": "body", "offset": 0.0} -> output seconds.
    "in": "hook"|"body"|"any". Or {"time": 3.2}. Or {"after": "<other anchor>", "offset": 0.4}.

usage: python make_reel_data.py <aroll_X.words.json> <aroll_X.segments.json> <beats.json> <out reel-data.js>
"""
import json
import os
import re
import sys
from pathlib import Path

GLOSSARY = json.load(open(Path(__file__).with_name("glossary.json"), encoding="utf-8"))
LATIN = re.compile(r"[A-Za-z]")


def norm(t):
    t = t.strip().strip("،,.!؟?")
    return t.lower() if LATIN.search(t) else t


def tokens_from(words, extra_fixes=None):
    fixes = {**GLOSSARY["fixes"], **(extra_fixes or {})}
    toks = []
    for w in words:
        t = w["w"].strip()
        if not t:
            continue
        if t.startswith("-") and LATIN.search(t):  # wide transcripts write "ال -development", "ن -implement"
            t = t.lstrip("-")
            if toks and toks[-1]["t"] in ("ال", "وال", "بال", "فال", "لل") and not toks[-1].get("en"):
                toks[-1]["t"] += "ـ"  # "ال" -> "الـ" so it reads «الـ Development»
            t = t[:1].upper() + t[1:]
        t = fixes.get(t, t)
        if not t:  # fix mapped to "" = drop the token (mis-heard filler)
            continue
        parts = t.split(" ")
        if len(parts) == 2 and LATIN.search(parts[1]) and not LATIN.search(parts[0]):  # "بالـ Marketing"
            toks.append({"t": parts[0], "s": w["s"], "e": w["s"] + 0.05, "en": False})
            toks.append({"t": parts[1], "s": w["s"] + 0.05, "e": w["e"], "en": True})
        else:  # e.g. "يا إما" stays one unbreakable token
            toks.append({"t": t, "s": w["s"], "e": w["e"], "en": False})
    # phrases -> one English run
    out, i = [], 0
    phrases = sorted(GLOSSARY["phrases"], key=lambda p: -len(p["ar"]))
    while i < len(toks):
        hit = None
        for p in phrases:
            n = len(p["ar"])
            if [norm(x["t"]) for x in toks[i:i + n]] == [norm(x) for x in p["ar"]]:
                hit = p
                break
        if hit:
            n = len(hit["ar"])
            if hit.get("prefix"):
                out.append({"t": hit["prefix"], "s": toks[i]["s"], "e": toks[i]["s"] + 0.05, "en": False})
            out.append({"t": hit["en"], "s": toks[i]["s"], "e": toks[i + n - 1]["e"], "en": True})
            i += n
        else:
            tk = toks[i]
            if LATIN.search(tk["t"]):
                tk["en"] = True
            out.append(tk)
            i += 1
    return out


def chunk(toks, segs, max_words=3, max_chars=20, gap=0.45, merge_words=3, bias=0.1, stretched=0.85):
    """Phrase-aware captions: split at pauses (cut joins / word gaps), merge tiny phrases,
    then balance long phrases into <= max_words chunks. English runs count as one word."""
    def seg_of(tk):  # by midpoint: Whisper word starts often run early
        m = (tk["s"] + tk["e"]) / 2 + bias
        return next((i for i, sg in enumerate(segs) if m < sg["end"]), len(segs) - 1)

    hook_end = max([sg["end"] for sg in segs if sg.get("kind") == "hook"] or [0.0])
    phrases, cur = [], []
    for tk in toks:
        if cur:
            prev = cur[-1]
            pause = (tk["s"] - prev["e"] > gap or seg_of(tk) != seg_of(prev)
                     or (not prev["en"] and prev["e"] - prev["s"] > stretched)  # Whisper stretches a word over a pause
                     or prev["s"] < hook_end <= tk["s"] + bias)  # the hook never shares a chunk with the body
            marker = norm(tk["t"]) in GLOSSARY.get("break_before", []) or norm(prev["t"]) in GLOSSARY.get("break_after", [])
            if pause or marker or prev["t"].endswith(("؟", "?", "!")):
                phrases.append(cur)
                cur = []
        cur.append(tk)
    if cur:
        phrases.append(cur)
    merged = []
    for ph in phrases:
        if merged and merged[-1][-1]["t"].endswith("ـ"):  # a phrase ending on a prefix "فـ"/"الـ" glues forward
            merged[-1] = merged[-1] + ph
            continue
        if merged:
            last = merged[-1]
            chars = sum(len(x["t"]) for x in last + ph)
            if (len(last) <= 2 and len(last) + len(ph) <= merge_words and chars <= max_chars
                    and not last[-1]["t"].endswith(("؟", "?", "!"))
                    and not last[-1]["s"] < hook_end <= ph[0]["s"] + bias
                    and norm(ph[0]["t"]) not in GLOSSARY.get("break_before", [])
                    and norm(last[-1]["t"]) not in GLOSSARY.get("break_after", [])):
                merged[-1] = last + ph
                continue
        merged.append(ph)
    out = []
    for ph in merged:
        n = len(ph)
        k = max(1, -(-n // max_words))  # ceil
        while k < n and any(sum(len(x["t"]) for x in ph[i * n // k:(i + 1) * n // k]) > max_chars for i in range(k)):
            k += 1
        parts = [ph[i * n // k:(i + 1) * n // k] for i in range(k)]
        if k >= n > 2:  # one long token (e.g. «Product Knowledge») made every even split too wide: pack greedily instead
            parts, cur = [], []
            for x in ph:
                if cur and (len(cur) >= max_words or sum(len(y["t"]) for y in cur + [x]) > max_chars):
                    parts.append(cur)
                    cur = []
                cur.append(x)
            parts.append(cur)
        parts = [p for p in parts if p]
        for i in range(len(parts) - 1):  # never end a chunk on a function word
            while len(parts[i]) > 1 and (norm(parts[i][-1]["t"]) in GLOSSARY.get("no_end", []) or parts[i][-1]["t"].endswith("ـ")):
                parts[i + 1].insert(0, parts[i].pop())
        out.extend(parts)
    return out


def resolve(anchors, toks, segs):
    hook_end = max([s["end"] for s in segs if s["kind"] == "hook"] or [0.0])
    times = {}

    def find(a):
        if "time" in a:
            return a["time"] + a.get("offset", 0)
        if "after" in a:
            return times[a["after"]] + a.get("offset", 0)
        where = a.get("in", "body")
        want = norm(a["word"])
        hits = [tk for tk in toks if (want == norm(tk["t"]) or (a.get("contains") and want in norm(tk["t"])))
                and (where == "any" or (where == "hook") == (tk["s"] < hook_end - 0.12))]
        n = a.get("n", 1)
        if len(hits) < n:
            if os.environ.get("RABET_DEBUG_TOKENS"):  # show what the caption tokens actually are
                print(" | ".join(f"{t['t']}@{t['s']:.1f}" for t in toks))
            raise SystemExit(f"anchor not found: {a}  (have {len(hits)} hits)")
        return round(hits[n - 1]["s"] + a.get("offset", 0), 3)

    for k, a in anchors.items():
        times[k] = find(a)
    return times, hook_end


def main(words_p, segs_p, beats_p, out_p):
    words = json.load(open(words_p, encoding="utf-8"))["words"]
    segd = json.load(open(segs_p, encoding="utf-8"))
    beats = json.load(open(beats_p, encoding="utf-8"))
    segs = segd["segments"]
    # optional: take ALL words from the wide (source) transcript mapped through the cut — use when the
    # cut A-roll's own transcript is poor. {"file": path, "offset": source seconds of the wide file's t=0}
    if beats.get("wide_words"):
        ww = json.load(open(beats["wide_words"]["file"], encoding="utf-8"))["words"]
        off = beats["wide_words"]["offset"]
        words = []
        for w in ww:
            src = w["s"] + off
            hits = []
            for kind in {g.get("kind") for g in segs}:  # hook and body are separate copies of the source
                ks = [g for g in segs if g.get("kind") == kind]
                ws_, we_ = w["s"] + off, w["e"] + off
                # a word belongs to a piece only if most of it is inside (a word straddling a cut edge is mostly cut away)
                inside = [g for g in ks if min(we_, g["src_end"]) - max(ws_, g["src_start"]) >= min(0.4 * max(we_ - ws_, 0.05), 0.3)]
                if not inside:  # wide timings run a little early: a word starting in a cut gap belongs to the next piece
                    # ...but only if most of the word lies inside that piece (not a previous word's tail)
                    inside = [g for g in ks if 0 < g["src_start"] - src <= 0.45
                              and (w["e"] + off - g["src_start"]) > 0.5 * (w["e"] - w["s"])][:1]
                hits += inside[:1]  # one copy per kind, even when a word straddles a cut
            for sg in hits:
                src = max(w["s"] + off, sg["src_start"])
                t = round(sg["start"] + src - sg["src_start"], 3)
                words.append({"w": w["w"], "s": max(t, sg["start"]), "e": round(min(sg["end"], t + (w["e"] - w["s"])), 3)})
    # words Whisper dropped on the cut A-roll, recovered from the wide transcript in SOURCE time
    for xw in beats.get("extra_words", []):  # into EVERY segment containing it (hooks repeat body audio)
        for sg in (g for g in segs if g["src_start"] - 0.02 <= xw["src"] <= g["src_end"]):
            t = round(sg["start"] + xw["src"] - sg["src_start"], 3)
            if not any(abs(w["s"] - t) < 0.15 and w["w"] == xw["w"] for w in words):
                words.append({"w": xw["w"], "s": t, "e": round(t + xw.get("dur", 0.4), 3)})
    words.sort(key=lambda w: w["s"])
    toks = tokens_from(words, beats.get("fixes"))
    emph = set(beats.get("emphasis", []))
    joins = [s["start"] for s in segs[1:]]
    # adjacent English words become one caption token: separate LTR spans in an RTL line display reversed
    # («Pain Point» -> «Point Pain») and a chunk break between them splits the term. Anchors keep the single words.
    ctoks = []
    for tk in toks:
        if (ctoks and tk["en"] and ctoks[-1]["en"] and tk["s"] - ctoks[-1]["e"] < 0.6
                and not any(ctoks[-1]["s"] < j <= tk["s"] + 0.1 for j in joins)):  # never across a cut
            ctoks[-1] = {**ctoks[-1], "t": ctoks[-1]["t"] + " " + tk["t"], "e": tk["e"]}
        else:
            ctoks.append(dict(tk))
    groups = chunk(ctoks, segs, **beats.get("chunking", {}))
    # a cut inside a hesitated «ال… Market» leaves «الـ» alone in a chunk: it always travels with the next word
    for gi in range(len(groups) - 2, -1, -1):
        if all(x["t"].endswith("ـ") for x in groups[gi]):
            groups[gi + 1] = groups[gi] + groups[gi + 1]
            del groups[gi]
    caps = []
    for gi, g in enumerate(groups):
        nxt = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else segd["duration"]
        caps.append({"s": round(g[0]["s"], 3), "e": round(min(nxt, g[-1]["e"] + 0.6), 3),
                     "w": [[x["t"], 1 if x["en"] else 0, round(x["s"], 3)] for x in g],
                     "hl": [i for i, x in enumerate(g) if x["en"] or norm(x["t"]) in emph]})
    t, hook_end = resolve(beats.get("anchors", {}), toks, segs)
    data = {"duration": segd["duration"], "ctaDur": beats.get("cta_duration", 2.2), "hookEnd": hook_end,
            "joins": joins, "segments": segs, "caps": caps, "t": t, "content": beats.get("content", {})}
    Path(out_p).write_text("window.REEL = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"{out_p}: {len(caps)} caption chunks, {len(t)} anchors, {segd['duration']}s + CTA")


if __name__ == "__main__":
    main(*sys.argv[1:5])
