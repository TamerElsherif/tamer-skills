#!/usr/bin/env python3
"""Merge LLM chunk-extraction results back into sources.yaml (the LLM half of tcs-source-ingest).

Modes:
  merge_facts.py <run>/sources.yaml --todo [--limit N]
      list chunks whose summary is still [auto] with their cache paths (feed them to the LLM one by one).
  merge_facts.py <run>/sources.yaml --batch extract.yaml [--keep-auto]
      apply one or more batch files (format: templates/facts_batch.example.yaml):
        - replaces the chunk summary,
        - drops that chunk's auto-candidate facts (unless --keep-auto), adds the LLM facts with new F ids,
        - appends glossary terms and conflicts, re-runs numeric conflict detection, re-tags outdated sources.
Fact ids are never reused; existing non-auto facts are kept unless the batch lists them under `drop:`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest import detect_conflicts, outdated_sources  # noqa: E402

KINDS = {"fact", "definition", "procedure", "step", "example", "policy", "statistic", "warning", "term", "case", "quote"}


def todo(data: dict, limit: int) -> list[str]:
    out = []
    for s in data["sources"]:
        for c in s.get("chunks", []):
            if c["summary"].startswith("[auto]"):
                out.append(f"{s['id']}#{c['id']}\t{c.get('tokens', '?')} tok\t{c.get('path', '-')}\t{s['title']}")
    return out[:limit] if limit else out


def apply_batch(data: dict, batch: list[dict], keep_auto: bool = False) -> dict:
    srcs = {s["id"]: s for s in data["sources"]}
    next_f = max([int(f["id"][1:]) for f in data["facts"]] + [0]) + 1
    added, dropped = 0, 0
    for entry in batch:
        ref = entry["chunk"]
        sid, _, cid = ref.partition("#")
        if sid not in srcs:
            raise SystemExit(f"batch references unknown source {sid}")
        chunk = next((c for c in srcs[sid].get("chunks", []) if c["id"] == cid), None) if cid else None
        if cid and chunk is None:
            raise SystemExit(f"batch references unknown chunk {ref}")
        if chunk is not None and entry.get("summary"):
            chunk["summary"] = entry["summary"].strip()
        drop = set(entry.get("drop", []))
        before = len(data["facts"])
        data["facts"] = [f for f in data["facts"] if f["id"] not in drop and not (
            not keep_auto and f["source_id"] == sid and (not cid or f.get("chunk_id") == cid)
            and "auto-candidate" in f.get("tags", []))]
        dropped += before - len(data["facts"])
        for nf in entry.get("facts", []):
            if nf.get("kind") not in KINDS:
                raise SystemExit(f"{ref}: invalid fact kind {nf.get('kind')!r}")
            fact = {"id": f"F{next_f:03d}", "kind": nf["kind"], "text": nf["text"].strip(), "source_id": sid}
            next_f += 1
            if cid:
                fact["chunk_id"] = cid
            for k in ("loc", "date", "confidence", "procedure_order", "tags"):
                if nf.get(k) is not None:
                    fact[k] = nf[k]
            if "loc" not in fact and chunk is not None:
                fact["loc"] = chunk["loc"]
            fact.setdefault("confidence", 0.8)
            data["facts"].append(fact)
            added += 1
        for g in entry.get("glossary", []):
            g.setdefault("source_id", sid)
            data.setdefault("glossary", [])
            if not any(x["term"].lower() == g["term"].lower() for x in data["glossary"]):
                data["glossary"].append(g)
        for c in entry.get("conflicts", []):
            data.setdefault("conflicts", []).append(c)
        if entry.get("source_date") and not srcs[sid].get("date"):
            srcs[sid]["date"] = entry["source_date"]
    # drop conflicts that point at removed facts, then re-detect
    ids = {f["id"] for f in data["facts"]}
    data["conflicts"] = [c for c in data.get("conflicts", []) if all(i in ids for i in c["fact_ids"])]
    data["conflicts"] += detect_conflicts(data["facts"], data["conflicts"])
    if not data["conflicts"]:
        data.pop("conflicts")
    print(f"merged: +{added} facts, -{dropped} auto/dropped facts")
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources")
    ap.add_argument("--todo", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch", action="append", default=[])
    ap.add_argument("--keep-auto", action="store_true")
    ap.add_argument("--max-age-years", type=float, default=3.0)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    a = ap.parse_args(argv)
    p = Path(a.sources)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if a.todo:
        rows = todo(data, a.limit)
        print("\n".join(rows) if rows else "all chunks summarised")
        return 0
    if not a.batch:
        ap.error("--batch or --todo required")
    for b in a.batch:
        batch = yaml.safe_load(Path(b).read_text(encoding="utf-8"))
        data = apply_batch(data, batch if isinstance(batch, list) else [batch], a.keep_auto)
    old = {sid for sid, _d, _g in outdated_sources(data["sources"], dt.date.fromisoformat(a.today), a.max_age_years)}
    for f in data["facts"]:
        if f["source_id"] in old and "outdated?" not in f.setdefault("tags", []):
            f["tags"].append("outdated?")
        if "tags" in f and not f["tags"]:
            f.pop("tags")
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
