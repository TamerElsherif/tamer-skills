"""Measure a speaker's style across one or more recordings, against the other speakers in them.

usage: python style_metrics.py <speaker> <work_dir> [<work_dir> ...] --out <profile_dir> [--no-prosody]
writes <profile_dir>/
  metrics.json   numbers for the speaker and each other speaker (same recordings) as the baseline
  metrics.md     readable comparison table + lists (distinctive phrases, English terms, openers, pause words)
  corpus.md      the speaker's turns in order, «…» = pause >= 0.7 s, «⟨w⟩» = low-confidence word, with the
                 previous speaker's last words as context. Read it to write profile.md (see SKILL.md).
"""
import argparse
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from common import SKILL, SR, jload, jsave, load_audio, mmss, speech_mask

LATIN = re.compile(r"[A-Za-z]")
PUNCT = re.compile(r"[\.,!،؛:\"'()\[\]«»…\-]+")
NUM = re.compile(r"^\d+([.,]\d+)?%?$|^(واحد|اتنين|تلاتة|تلات|أربعة|خمسة|ستة|سبعة|تمانية|تسعة|عشرة|مية|ألف|مليون|مليار)$")


def norm(w):
    w = PUNCT.sub("", w).strip()
    w = re.sub(r"^ال(?=[A-Za-z])|^الـ ?(?=[A-Za-z])", "", w)     # «الـProduct» -> Product
    return w.lower() if LATIN.search(w) else w


def count_markers(tokens, markers):
    out = {}
    for cat, items in markers.items():
        if cat.startswith("_"):
            continue
        c = Counter()
        for it in items:
            seq = [norm(v) for v in it.split()]
            n = len(seq)
            c[it] = sum(1 for i in range(len(tokens) - n + 1) if tokens[i:i + n] == seq)
        out[cat] = {k: v for k, v in c.most_common() if v}
    return out


def logodds(target, other, prior, n_min=4, top=40):
    """Monroe et al. log-odds with an informative Dirichlet prior: phrases that set the speaker apart"""
    nt, no, a0 = sum(target.values()), sum(other.values()), sum(prior.values())
    res = []
    for w, yt in target.items():
        if yt < n_min:
            continue
        yo, aw = other.get(w, 0), prior[w]
        d = math.log((yt + aw) / (nt + a0 - yt - aw)) - math.log((yo + aw) / (no + a0 - yo - aw))
        z = d / math.sqrt(1 / (yt + aw) + 1 / (yo + aw))
        res.append((w, round(z, 2), yt, yo))
    return sorted(res, key=lambda r: -r[1])[:top]


def ngrams(turns, n):
    c = Counter()
    for t in turns:
        tok = [norm(w["w"]) for w in t["words"]]
        tok = [v for v in tok if v]
        c.update(" ".join(tok[i:i + n]) for i in range(len(tok) - n + 1))
    return c


def prosody(turns, work_audio):
    import librosa
    f0s, dbs, per_turn = [], [], []
    for x, ts in work_audio:
        for t in ts:
            seg = x[int(t["s"] * SR): int(t["e"] * SR)]
            if len(seg) < SR:
                continue
            f0 = librosa.yin(seg, fmin=65, fmax=400, sr=SR, frame_length=1024, hop_length=160)
            rms = librosa.feature.rms(y=seg, frame_length=1024, hop_length=160)[0]
            db = 20 * np.log10(rms + 1e-7)
            m = min(len(f0), len(db))
            f0, db = f0[:m], db[:m]
            voiced = db > np.percentile(db, 40)          # loud frames: yin on silence/breath is noise
            v = f0[voiced]
            v = v[(v > 70) & (v < 380)]
            if len(v) > 50:
                f0s.append(v)
                per_turn.append(float(np.std(12 * np.log2(v / np.median(v)))))
            dbs.append(db[db > np.percentile(db, 30)])
    if not f0s:
        return {}
    f = np.concatenate(f0s)
    d = np.concatenate(dbs)
    p10, p50, p90 = np.percentile(f, [10, 50, 90])
    return {"f0_median_hz": round(float(p50), 1), "f0_p10_p90_hz": [round(float(p10)), round(float(p90))],
            "pitch_range_semitones": round(float(12 * math.log2(p90 / p10)), 1),
            "pitch_variation_in_turn_st": round(float(np.median(per_turn)), 2),
            "loudness_range_db": round(float(np.percentile(d, 90) - np.percentile(d, 10)), 1)}


def pauses_in(t, sp):
    """silent runs >= 0.3 s inside a turn (first word to last word), from the audio level: Whisper stretches word
    ends to the next word, so word gaps miss most pauses"""
    if not t["words"]:
        return []
    a0, b0 = int(t["words"][0]["s"] * 100), int(t["words"][-1]["e"] * 100)
    seg = sp[a0:b0]
    out, i = [], 0
    while i < len(seg):
        if not seg[i]:
            j = i
            while j < len(seg) and not seg[j]:
                j += 1
            if j - i >= 30:
                out.append(((a0 + i) / 100, (j - i) / 100))
            i = j
        else:
            i += 1
    return out


def word_before(t, s):
    prev = [w for w in t["words"] if w["s"] < s]
    return norm(prev[-1]["w"]) if prev else ""


def word_after(t, s):
    nxt = [w for w in t["words"] if w["s"] >= s]
    return norm(nxt[0]["w"]) if nxt else ""


def basics(turns):
    words = [w for t in turns for w in t["words"]]
    talk = sum(t["e"] - t["s"] for t in turns)
    gaps, long_before, long_after = [], Counter(), Counter()
    for t in turns:
        for ps, d in t.get("pauses", []):
            gaps.append(d)
            if d >= 0.7:
                long_before[word_before(t, ps)] += 1
                long_after[word_after(t, ps + d - 0.05)] += 1
    pause_t = sum(gaps)
    toks = [norm(w["w"]) for w in words]
    toks = [v for v in toks if v]
    latin = [v for v in toks if LATIN.search(v)]
    rep = sum(1 for a, b in zip(toks, toks[1:]) if a == b and len(a) > 1)
    tw = [len(t["words"]) for t in turns if t["words"]]
    tl = [t["e"] - t["s"] for t in turns]
    return {
        "talk_time": mmss(talk), "talk_s": round(talk), "turns": len(turns), "words": len(toks),
        "wpm_overall": round(len(toks) / talk * 60) if talk else 0,
        "wpm_articulation": round(len(toks) / max(1, talk - pause_t) * 60),
        "turn_s_median": round(float(np.median(tl)), 1) if tl else 0,
        "turn_s_p90": round(float(np.percentile(tl, 90)), 1) if tl else 0,
        "turn_words_median": int(np.median(tw)) if tw else 0,
        "share_turns_over_30s": round(sum(1 for v in tl if v > 30) / max(1, len(tl)), 2),
        "pauses_per_min": round(len(gaps) / talk * 60, 1) if talk else 0,
        "pause_median_s": round(float(np.median(gaps)), 2) if gaps else 0,
        "long_pauses_per_min": round(sum(1 for g in gaps if g >= 0.7) / talk * 60, 2) if talk else 0,
        "english_share": round(len(latin) / max(1, len(toks)), 3),
        "english_terms": Counter(latin).most_common(40),
        "repeats_per_1000": round(rep / max(1, len(toks)) * 1000, 1),
        "numbers_per_1000": round(sum(1 for v in toks if NUM.match(v)) / max(1, len(toks)) * 1000, 1),
        "low_conf_share": round(sum(1 for w in words if w.get("p", 1) < 0.4) / max(1, len(words)), 3),
        "words_before_long_pauses": long_before.most_common(15),
        "words_after_long_pauses": long_after.most_common(15),
    }, toks


def openers(turns, k=2, last=False):
    c = Counter()
    for t in turns:
        tok = [norm(w["w"]) for w in t["words"]]
        tok = [v for v in tok if v]
        if len(tok) >= 4:
            c[" ".join(tok[-k:] if last else tok[:k])] += 1
    return c.most_common(15)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("speaker")
    ap.add_argument("works", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-prosody", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    markers = jload(SKILL / "references/markers.json")
    by = defaultdict(list)
    audio = defaultdict(list)
    corpus = []
    for wd in a.works:
        wd = Path(wd)
        W = jload(wd / "words.json")["turns"]
        x = load_audio(jload(wd / "turns.json")["source"], wd)
        sp, _ = speech_mask(x)
        per = defaultdict(list)
        for t in W:
            t["pauses"] = pauses_in(t, sp)
            by[t["who"]].append(t)
            per[t["who"]].append(t)
        if not a.no_prosody:
            for who, ts in per.items():
                audio[who].append((x, ts))
        prev = None
        parts = jload(wd / "parts.json")["parts"] if (wd / "parts.json").exists() else [[0, ""]]

        def where(s):
            p0, nm = max((p for p in parts if p[0] <= s + 0.5), key=lambda p: p[0])
            return f"{wd.name}{(' ' + nm.strip()) if nm else ''} {mmss(s - p0)}"
        corpus.append(f"\n## {wd.name}\n")
        for t in W:
            if t["who"] == a.speaker and t["words"]:
                if prev and prev["who"] != a.speaker and prev["words"]:
                    corpus.append(f"> {prev['who']}: … {' '.join(w['w'] for w in prev['words'][-14:])}")
                txt, ps = [], [p for p, d in t["pauses"] if d >= 0.7]
                for i, w in enumerate(t["words"]):
                    if i and any(t["words"][i - 1]["s"] < p <= w["s"] for p in ps):
                        txt.append("…")
                    txt.append(f"⟨{w['w']}⟩" if w.get("p", 1) < 0.4 else w["w"])
                corpus.append(f"[{where(t['s'])}] {' '.join(txt)}\n")
            prev = t
    if a.speaker not in by:
        raise SystemExit(f"no turns for {a.speaker}; speakers: {sorted(by)}")
    M = {}
    toks = {}
    for who, ts in by.items():
        m, tk = basics(ts)
        m["markers_per_1000"] = {c: round(sum(v.values()) / max(1, len(tk)) * 1000, 1)
                                 for c, v in count_markers(tk, markers).items()}
        if not a.no_prosody:
            m["prosody"] = prosody(ts, audio[who])
        M[who], toks[who] = m, tk
    t = by[a.speaker]
    oth = [x for w, ts in by.items() if w != a.speaker for x in ts]
    dist = {}
    for n in (1, 2, 3):
        ct, co = ngrams(t, n), ngrams(oth, n)
        prior = Counter(ct) + Counter(co)
        dist[n] = logodds(ct, co, prior, n_min=3 if n > 1 else 6)
    M[a.speaker]["markers"] = count_markers(toks[a.speaker], markers)
    M[a.speaker]["distinctive"] = {f"{n}gram": v for n, v in dist.items()}
    M[a.speaker]["turn_openers"] = openers(t)
    M[a.speaker]["turn_closers"] = openers(t, last=True)
    M[a.speaker]["top_trigrams"] = ngrams(t, 3).most_common(30)
    jsave({"speaker": a.speaker, "recordings": [Path(w).name for w in a.works], "speakers": M}, out / "metrics.json")
    (out / "corpus.md").write_text(f"# {a.speaker}: corpus\n" + "\n".join(corpus), encoding="utf-8")

    keys = ["talk_time", "turns", "words", "wpm_overall", "wpm_articulation", "turn_s_median", "turn_s_p90",
            "share_turns_over_30s", "pauses_per_min", "pause_median_s", "long_pauses_per_min", "english_share",
            "repeats_per_1000", "numbers_per_1000", "low_conf_share"]
    names = [a.speaker] + sorted(w for w in M if w != a.speaker)
    L = [f"# {a.speaker}: style metrics ({', '.join(Path(w).name for w in a.works)})", "",
         "| metric | " + " | ".join(names) + " |", "|---" * (len(names) + 1) + "|"]
    for k in keys:
        L.append(f"| {k} | " + " | ".join(str(M[w][k]) for w in names) + " |")
    for c in M[a.speaker]["markers_per_1000"]:
        L.append(f"| {c} /1000 | " + " | ".join(str(M[w]["markers_per_1000"][c]) for w in names) + " |")
    if not a.no_prosody:
        for k in M[a.speaker]["prosody"]:
            L.append(f"| {k} | " + " | ".join(str(M[w].get("prosody", {}).get(k, "")) for w in names) + " |")
    S = M[a.speaker]
    L += ["", "## Distinctive phrases (z = how much more than the others; count him / others)"]
    for n in (1, 2, 3):
        L.append(f"- {n}-word: " + " · ".join(f"{w} ({z}; {yt}/{yo})" for w, z, yt, yo in dist[n][:25]))
    L += ["", "## Markers he uses (count)"]
    for c, v in S["markers"].items():
        if v:
            L.append(f"- {c}: " + " · ".join(f"{k} {n}" for k, n in list(v.items())[:12]))
    L += ["", "## English terms", " · ".join(f"{w} {n}" for w, n in S["english_terms"]),
          "", "## Turn openers", " · ".join(f"{w} {n}" for w, n in S["turn_openers"]),
          "", "## Turn closers", " · ".join(f"{w} {n}" for w, n in S["turn_closers"]),
          "", "## Words right before a pause >= 0.7 s (searching? or a beat?)",
          " · ".join(f"{w} {n}" for w, n in S["words_before_long_pauses"]),
          "", "## Words right after a pause >= 0.7 s (what he lands on)",
          " · ".join(f"{w} {n}" for w, n in S["words_after_long_pauses"]),
          "", "## Most frequent 3-word phrases", " · ".join(f"{w} {n}" for w, n in S["top_trigrams"])]
    (out / "metrics.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out / 'metrics.md'}, metrics.json, corpus.md")


if __name__ == "__main__":
    main()
