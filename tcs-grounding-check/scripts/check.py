#!/usr/bin/env python3
"""Deterministic grounding check: storyboard claims, quiz keys and on-screen numbers vs sources.yaml.

Usage: check.py --sources runs/x/sources.yaml --storyboard runs/x/lessons/M1L1/M1L1.storyboard.json
                [--quiz M1L1.quiz.json] [--curriculum runs/x/curriculum.yaml] [--lesson-id M1L1]
                [--out M1L1.grounding_report.json] [--today 2026-11-17] [--max-age-years 3]
Writes <out> (schemas/grounding_report.schema.json) + <out>.md summary. Exit 0 = all supported/general-knowledge/outdated-noted,
2 = unsupported/partial/conflicting claims remain (gate), 1 = bad input.

Per claim: cited source/chunk exists → candidate facts (cited chunk first, then source) → lexical overlap + number match →
supported | partial | conflicting (same topic, different number) | unsupported; then sources.yaml conflicts → conflicting;
old source/fact (outdated? tag or date > max age) → outdated. general_knowledge claims → general-knowledge
(unsupported if sources.general_knowledge_allowed is false). Uncited on-screen numbers → unsupported entries.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "tcs-storyboard" / "scripts"))
try:
    from sbtools import derive_on_screen_text  # noqa: E402
except Exception:  # storyboard skill missing: fall back to provided on_screen_text only
    def derive_on_screen_text(scene):
        return scene.get("on_screen_text", [])

STOP = set("a an the of to for and or in on at by with is are be been was were this that these those it its as from any "
           "every all each per must shall can may will should not no than more less up into after before within over under "
           "your you their our they them he she we i do does did has have had if then so but only also just about what which "
           "when how there here yes into onto".split())
SYN = {"keep": "retain", "kept": "retain", "store": "retain", "stored": "retain", "retention": "retain", "hold": "retain",
       "reimburse": "pay", "reimbursed": "pay", "paid": "pay", "refund": "pay", "submit": "file", "submitted": "file",
       "staff": "employee", "worker": "employee", "required": "require", "requires": "require", "needed": "require",
       "need": "require", "mandatory": "require", "receipts": "receipt", "photo": "photograph"}
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
           "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
           "ninety": 90, "hundred": 100, "thousand": 1000}
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def stem(w: str) -> str:
    w = SYN.get(w, w)
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            break
    return SYN.get(w, w)


def tokens(t: str) -> set[str]:
    return {stem(w) for w in re.findall(r"[^\W\d_]+", t.lower()) if w not in STOP and len(w) >= 3 and w not in WORDNUM}


def numbers(t: str) -> set[str]:
    t = re.sub(r"§\s?[\d.]+|\b(?:section|rule|step|para|p\.)\s?\d+(?:\.\d+)*", " ", t.translate(AR_DIGITS), flags=re.I)
    out = {n.replace(",", "").rstrip(".") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", t)}
    out = {re.sub(r"\.0+$", "", n) for n in out}
    for w in re.findall(r"[a-z]+", t.lower()):
        if w in WORDNUM and WORDNUM[w] >= 10:
            out.add(str(WORDNUM[w]))
    return out


def lex(claim_t: set[str], other: set[str]) -> float:
    return len(claim_t & other) / len(claim_t) if claim_t else 0.0


class Sources:
    def __init__(self, path: Path, today: dt.date, max_age: float):
        self.path = path
        self.d = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.src = {s["id"]: s for s in self.d["sources"]}
        self.facts = self.d.get("facts", [])
        self.today, self.max_age = today, max_age
        self.gk_allowed = self.d.get("general_knowledge_allowed", True)
        self.conflicts = self.d.get("conflicts", [])
        self._chunk_cache: dict[str, str] = {}
        for f in self.facts:
            f["_t"], f["_n"] = tokens(f["text"]), numbers(f["text"])

    def chunk_text(self, sid: str, cid: str) -> str:
        key = f"{sid}#{cid}"
        if key not in self._chunk_cache:
            c = next((c for c in self.src[sid].get("chunks", []) if c["id"] == cid), None)
            p = self.path.parent / c["path"] if c and c.get("path") else None
            self._chunk_cache[key] = p.read_text(encoding="utf-8") if p and p.exists() else (c or {}).get("summary", "")
        return self._chunk_cache[key]

    def is_old(self, date: str | None) -> bool:
        if not date:
            return False
        try:
            y = dt.date.fromisoformat(date[:10]) if len(date) >= 10 else dt.date(int(date[:4]), 12, 31)
        except ValueError:
            return False
        return (self.today - y).days / 365.25 > self.max_age


def verify(text: str, refs: list[str], S: Sources, required_numbers: set[str] | None = None,
           match_text: str | None = None) -> dict:
    """Return {status, source_ids, fact_ids, note, fix} for one sourced claim."""
    ct = tokens(match_text or text)
    cn = numbers(text) if required_numbers is None else required_numbers
    bad = [r for r in refs if r.split("#")[0] not in S.src or
           ("#" in r and not any(c["id"] == r.split("#")[1] for c in S.src[r.split("#")[0]].get("chunks", [])))]
    if bad:
        return {"status": "unsupported", "note": f"unknown source/chunk {', '.join(bad)}",
                "fix": "re-cite an existing source id from sources.yaml, or remove the claim"}
    sids = {r.split("#")[0] for r in refs}
    chunks = {tuple(r.split("#")) for r in refs if "#" in r}
    cand = [f for f in S.facts if f["source_id"] in sids]
    scored = []
    for f in cand:
        s = lex(ct, f["_t"])
        if (f["source_id"], f.get("chunk_id")) in chunks:
            s += 0.05
        scored.append((s, f))
    scored.sort(key=lambda x: -x[0])
    res = {"status": "unsupported", "fact_ids": [], "note": "", "fix": ""}
    good = [(s, f) for s, f in scored if s >= 0.3]
    if cn:
        full = [(s, f) for s, f in good if cn <= f["_n"]]
        union = set().union(*[f["_n"] for _, f in good[:3]]) if good else set()
        if full and full[0][0] >= 0.4:
            res.update(status="supported", fact_ids=[full[0][1]["id"]])
        elif good and good[0][0] >= 0.5 and good[0][1]["_n"] and not (cn & good[0][1]["_n"]):
            f = good[0][1]
            res.update(status="conflicting", fact_ids=[f["id"]],
                       note=f"claim numbers {sorted(cn)} vs source {f['id']} {sorted(f['_n'])}: \"{f['text'][:90]}\"",
                       fix=f"correct the number to match {f['id']} or cite the source that states it")
        elif good and cn <= union and good[0][0] >= 0.4:
            res.update(status="supported", fact_ids=[f["id"] for _, f in good[:3] if f["_n"] & cn])
        else:
            res.update(status="partial" if good else "unsupported", fact_ids=[f["id"] for _, f in good[:2]])
    else:
        if good and good[0][0] >= 0.5:
            res.update(status="supported", fact_ids=[good[0][1]["id"]])
        elif good:
            res.update(status="partial", fact_ids=[f["id"] for _, f in good[:2]])
    if res["status"] == "partial" and len(good) > 1:
        uni = set().union(*[f["_t"] for _, f in good[:4]])
        nun = set().union(*[f["_n"] for _, f in good[:4]])
        if lex(ct, uni) >= 0.7 and cn <= nun:
            res.update(status="supported", fact_ids=[f["id"] for _, f in good[:4]], note="supported by several facts")
    if res["status"] in ("partial", "unsupported"):
        # fallback: full chunk text of cited chunks (or all chunks of cited sources)
        texts = [S.chunk_text(s, c) for s, c in chunks] or [S.chunk_text(s, c["id"]) for s in sids
                                                            for c in S.src[s].get("chunks", [])]
        sents = [x for tx in texts for x in re.split(r"(?<=[.!?؟])\s+|\n+", tx) if x.strip()]
        windows = [" ".join(sents[i:i + 2]) for i in range(len(sents))]  # sentence pairs keep context
        for tx in windows:
            cov, tn = lex(ct, tokens(tx)), numbers(tx)
            if cov >= 0.7 and cn <= tn:
                res.update(status="supported", note="matched cited chunk text (no extracted fact) — consider adding a fact")
                break
        else:
            missing = sorted(cn - set().union(*[f["_n"] for _, f in good[:3]])) if cn and good else []
            if res["status"] == "partial":
                res["note"] = (f"numbers {missing} not found in cited facts; " if missing else "") + \
                              "only part of the claim matches the cited facts"
                res["fix"] = "soften to what the source says, split the claim, or cite the right chunk"
            else:
                res["note"] = "no cited fact or chunk text supports this claim"
                res["fix"] = "re-cite a source that states it, label general_knowledge (if allowed), or remove"
    # conflicts recorded in sources.yaml
    for c in S.conflicts:
        hit = set(res["fact_ids"]) & set(c["fact_ids"])
        if hit and res["status"] in ("supported", "partial"):
            chosen = c.get("chosen_fact")
            if not chosen and c.get("resolution") in (None, "", "unresolved", "ask owner"):
                res.update(status="conflicting", note=f"sources disagree ({', '.join(c['fact_ids'])}): {c['note'][:120]}",
                           fix="resolve the conflict in sources.yaml (authority → date → specificity) or avoid the number")
            elif chosen and chosen not in res["fact_ids"]:
                res.update(status="conflicting", note=f"conflict resolved in favour of {chosen}",
                           fix=f"rewrite the claim per {chosen} and cite it")
    # outdated
    if res["status"] in ("supported", "partial"):
        fmap = {f["id"]: f for f in S.facts}
        for fid in res["fact_ids"]:
            f = fmap[fid]
            if "outdated?" in f.get("tags", []) or S.is_old(f.get("date")) or S.is_old(S.src[f["source_id"]].get("date")):
                res.update(status="outdated", note=(res["note"] + "; " if res["note"] else "") +
                           f"{fid} comes from a source dated {S.src[f['source_id']].get('date', '?')}",
                           fix="confirm with the owner / prefer a newer source, or state the date on screen")
                break
    res["source_ids"] = refs
    return res


def collect(sb: dict | None, quiz: dict | None) -> list[dict]:
    items = []
    for sc in (sb or {}).get("scenes", []):
        for c in sc.get("claims", []):
            items.append({"scene_id": sc["id"], "text": c["text"], "refs": c.get("source_ids", []),
                          "gk": c.get("general_knowledge", False)})
        claim_nums = set().union(*[numbers(c["text"]) for c in sc.get("claims", [])]) if sc.get("claims") else set()
        ost = sc.get("on_screen_text") or derive_on_screen_text(sc)
        for s in ost:
            for m in re.finditer(r"([$€£%]?)\s?(\d[\d,]*(?:\.\d+)?)\s?(%?)", s.translate(AR_DIGITS)):
                n = m.group(2).replace(",", "").rstrip(".")
                if (m.group(1) or m.group(3) or float(n) >= 10) and n not in claim_nums:
                    items.append({"scene_id": sc["id"], "text": f"On-screen \"{s[:80]}\"", "refs": [], "gk": False,
                                  "uncited_number": n})
    for it in (quiz or {}).get("items", []):
        opts = it.get("options", [])
        if it["type"] == "ordering":
            key = " ".join(o["text"] for o in sorted(opts, key=lambda o: o.get("order", 0)))
        elif it["type"] == "flashcard":
            key = it.get("back", "")
        elif it["type"] == "matching":
            key = " ".join(f"{o['text']} {o.get('match', '')}" for o in opts)
        else:
            key = " ".join(o["text"] for o in opts if o.get("correct"))
        req = numbers(key + " " + it.get("explanation", ""))
        if it["type"] == "true_false":  # the statement itself is the claim when True is correct
            ok = next((o for o in opts if o.get("correct")), {})
            stmt_true = str(ok.get("text", "")).lower() in ("true", "صح", "صحيح")
            text = it["stem"] if stmt_true else f"{it['stem']} — this is false. {it.get('explanation', '')}"
            req = numbers(it["stem"]) if stmt_true else numbers(it.get("explanation", "")) & numbers(it["stem"]) or set()
            match = text
        else:
            text = f"{it['stem']} → {key}"
            fb = " ".join(o.get("feedback", "") for o in opts if o.get("correct"))
            match = f"{key} {fb} {it.get('explanation', '')}" if it["type"] not in ("flashcard",) else f"{it['stem']} {key}"
        items.append({"scene_id": f"quiz:{it['id']}", "text": text, "refs": it.get("source_ids", []),
                      "gk": it.get("general_knowledge", False), "required": req, "match": match,
                      "objective_id": it["objective_id"],
                      # ordering: each step is its own fact, so verify option by option
                      "parts": [o["text"] for o in opts] if it["type"] == "ordering" else None})
    return items


def run(S: Sources, sb: dict | None, quiz: dict | None, lesson_id: str, objectives: list[str]) -> dict:
    claims = []
    for it in collect(sb, quiz):
        if it.get("uncited_number"):
            claims.append({"scene_id": it["scene_id"], "text": it["text"], "status": "unsupported",
                           "note": f"number {it['uncited_number']} is on screen but in no claim of this scene",
                           "fix": "add a claim with its source (or label general_knowledge / fictional example), or remove"})
            continue
        if it["gk"] and not it["refs"]:
            c = {"scene_id": it["scene_id"], "text": it["text"], "status": "general-knowledge"}
            if not S.gk_allowed:
                c.update(status="unsupported", note="general knowledge not allowed for this course",
                         fix="find a source or remove the claim")
            claims.append(c)
            continue
        r = verify(it["text"], it["refs"], S, it.get("required"), it.get("match")) if it["refs"] else \
            {"status": "unsupported", "note": "no source_ids", "fix": "cite a source or label general_knowledge"}
        if it["refs"] and it.get("parts") and r["status"] != "supported":
            rs = [verify(x, it["refs"], S) for x in it["parts"]]
            if all(x["status"] == "supported" for x in rs):
                r = {"status": "supported", "fact_ids": [f for x in rs for f in x.get("fact_ids", [])],
                     "note": "each ordering option supported by its own fact"}
        c = {"scene_id": it["scene_id"], "text": it["text"], **{k: v for k, v in r.items() if v}}
        claims.append(c)
    summ = {k: 0 for k in ("total", "supported", "general_knowledge", "unsupported", "conflicting", "outdated", "partial")}
    for c in claims:
        summ["total"] += 1
        key = {"general-knowledge": "general_knowledge"}.get(c["status"], c["status"])
        summ[key] += 1
    cov = {o: [] for o in objectives}
    for sc in (sb or {}).get("scenes", []):
        for o in sc.get("objective_ids", []):
            cov.setdefault(o, []).append(sc["id"])
    for it in (quiz or {}).get("items", []):
        cov.setdefault(it["objective_id"], []).append(f"quiz:{it['id']}")
    return {"schema_version": "1.0", "lesson_id": lesson_id, "summary": summ, "claims": claims, "coverage": cov}


def markdown(rep: dict) -> str:
    s = rep["summary"]
    ok = s["unsupported"] + s["conflicting"] + s["partial"] == 0
    lines = [f"# Grounding — {rep['lesson_id']}: {'PASS' if ok else 'NEEDS FIXES'}", "",
             f"{s['total']} claims · {s['supported']} supported · {s['general_knowledge']} general knowledge · "
             f"{s['partial']} partial · {s['unsupported']} unsupported · {s['conflicting']} conflicting · {s['outdated']} outdated", ""]
    bad = [c for c in rep["claims"] if c["status"] not in ("supported", "general-knowledge")]
    if bad:
        lines += ["| scene | status | claim | note | fix |", "|---|---|---|---|---|"]
        for c in bad:
            cell = lambda x: " ".join(str(x).split()).replace("|", "\\|")[:110]  # noqa: E731
            lines.append(f"| {c['scene_id']} | {c['status']} | {cell(c['text'])} | {cell(c.get('note', ''))} | {cell(c.get('fix', ''))} |")
    gaps = [o for o, v in rep.get("coverage", {}).items() if not v]
    if gaps:
        lines += ["", f"Objectives with no scene or item: {', '.join(gaps)}"]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sources", required=True)
    ap.add_argument("--storyboard")
    ap.add_argument("--quiz")
    ap.add_argument("--curriculum")
    ap.add_argument("--lesson-id")
    ap.add_argument("--out")
    ap.add_argument("--today", default=dt.date.today().isoformat())
    ap.add_argument("--max-age-years", type=float, default=3.0)
    a = ap.parse_args(argv)
    if not (a.storyboard or a.quiz):
        ap.error("--storyboard and/or --quiz required")
    S = Sources(Path(a.sources), dt.date.fromisoformat(a.today), a.max_age_years)
    sb = json.loads(Path(a.storyboard).read_text(encoding="utf-8")) if a.storyboard else None
    quiz = json.loads(Path(a.quiz).read_text(encoding="utf-8")) if a.quiz else None
    lesson = a.lesson_id or (sb or {}).get("lesson_id") or (quiz or {}).get("lesson_id") or "lesson"
    objs = []
    if a.curriculum:
        cur = yaml.safe_load(Path(a.curriculum).read_text(encoding="utf-8"))
        objs = next((l["objective_ids"] for m in cur["modules"] for l in m["lessons"] if l["id"] == lesson), [])
    elif sb:
        objs = sb.get("objective_ids", [])
    rep = run(S, sb, quiz, lesson, objs)
    base = Path(a.storyboard or a.quiz)
    out = Path(a.out) if a.out else base.parent / f"{lesson}.grounding_report.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    md = markdown(rep)
    out.with_suffix(".md").write_text(md, encoding="utf-8")
    print(md)
    s = rep["summary"]
    return 2 if s["unsupported"] + s["conflicting"] + s["partial"] else 0


if __name__ == "__main__":
    sys.exit(main())
