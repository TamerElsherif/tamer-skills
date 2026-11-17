#!/usr/bin/env python3
"""Resumable run state for tcs-autopilot / tcs-orchestrator: runs/<run-id>/state.json (schemas/run_state.schema.json).

Usage:
  run_state.py new-id "<request>"                                  -> prints a run id (YYYYMMDD-HHMM-<slug>)
  run_state.py init <run_dir> --request "..." [--flags-json '{..}'] [--force]
  run_state.py set <run_dir> <stage> <status> [--output PATH ...] [--note TEXT]
  run_state.py lesson <run_dir> <lesson_id> [--status S] [--qa pass|fail|needs-human] [--attempt]
  run_state.py cost <run_dir> [--tokens N] [--usd X] [--estimate-usd X] [--budget TEXT]
  run_state.py next <run_dir>          -> prints the stage to run next (or 'paused:<stage>' / 'complete')
  run_state.py show <run_dir>

Stages: ingest decide plan produce qa render report. Statuses: pending running done failed skipped needs-human.
Every write validates against the schema; writes are atomic (tmp + rename). Idempotent: init never clobbers without --force.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
SCHEMA = PLUGIN_ROOT / "schemas" / "run_state.schema.json"
STAGES = ["ingest", "decide", "plan", "produce", "qa", "render", "report"]
STATUSES = ["pending", "running", "done", "failed", "skipped", "needs-human"]
FINISHED = {"done", "skipped"}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def path(run_dir) -> Path:
    return Path(run_dir) / "state.json"


def load(run_dir) -> dict:
    p = path(run_dir)
    if not p.exists():
        raise SystemExit(f"no state.json in {run_dir} — run `run_state.py init` first")
    return json.loads(p.read_text())


def save(run_dir, st: dict) -> None:
    try:
        import jsonschema
        jsonschema.validate(st, json.loads(SCHEMA.read_text()))
    except ImportError:
        pass
    p = path(run_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def new_id(request: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", request.lower()).strip("-")[:32].strip("-")
    return f"{dt.datetime.now():%Y%m%d-%H%M}-{slug or 'run'}"


def init(run_dir, request: str, flags: dict | None = None, force: bool = False) -> dict:
    if path(run_dir).exists() and not force:
        st = load(run_dir)
        print(f"state exists; resume at: {next_stage(st)}")
        return st
    st = {"run_id": Path(run_dir).name, "request": request, "flags": flags or {}, "created": now(),
          "stages": {s: {"status": "pending"} for s in STAGES}, "lessons": {}, "cost": {"tokens": 0, "usd": 0.0}}
    save(run_dir, st)
    return st


def set_stage(run_dir, stage: str, status: str, outputs=None, note=None) -> dict:
    if stage not in STAGES or status not in STATUSES:
        raise SystemExit(f"stage must be one of {STAGES}, status one of {STATUSES}")
    st = load(run_dir)
    s = st["stages"].setdefault(stage, {})
    s["status"], s["at"] = status, now()
    if outputs:
        s["outputs"] = list(dict.fromkeys((s.get("outputs") or []) + list(outputs)))
    if note:
        s["note"] = note
    save(run_dir, st)
    return st


def set_lesson(run_dir, lesson_id: str, status=None, qa=None, attempt=False) -> dict:
    st = load(run_dir)
    les = st.setdefault("lessons", {}).setdefault(lesson_id, {"status": "planned", "attempts": 0})
    if status:
        les["status"] = status
    if qa:
        les["qa"] = qa
    if attempt:
        les["attempts"] = int(les.get("attempts", 0)) + 1
    save(run_dir, st)
    return st


def add_cost(run_dir, tokens=None, usd=None, estimate_usd=None, budget=None) -> dict:
    st = load(run_dir)
    c = st.setdefault("cost", {"tokens": 0, "usd": 0.0})
    if tokens:
        c["tokens"] = int(c.get("tokens", 0)) + int(tokens)
    if usd:
        c["usd"] = round(float(c.get("usd", 0)) + float(usd), 4)
    if estimate_usd is not None:
        c["estimate_usd"] = float(estimate_usd)
    if budget:
        c["budget"] = budget
    save(run_dir, st)
    return st


def next_stage(st: dict) -> str:
    for s in STAGES:
        status = st["stages"].get(s, {}).get("status", "pending")
        if status in FINISHED:
            continue
        if status == "needs-human" and s == "plan":
            return "paused:plan"  # --review skeleton: waiting for approval of the plan
        if status == "needs-human" and s == "render":
            return "paused:render"  # --review final: waiting for approval before render
        return s
    return "complete"


def show(st: dict) -> str:
    rows = [f"run {st['run_id']}: {st.get('request', '')}"]
    for s in STAGES:
        v = st["stages"].get(s, {})
        rows.append(f"  {s:<8} {v.get('status', 'pending'):<12} {v.get('at', ''):<26} {v.get('note', '')}")
    for lid, les in sorted((st.get("lessons") or {}).items()):
        rows.append(f"  lesson {lid:<6} {les.get('status', ''):<14} qa={les.get('qa', '-')} attempts={les.get('attempts', 0)}")
    c = st.get("cost") or {}
    rows.append(f"  cost: {c.get('tokens', 0)} tokens, ${c.get('usd', 0)} (estimate ${c.get('estimate_usd', '-')}, budget {c.get('budget', '-')})")
    rows.append(f"  next: {next_stage(st)}")
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new-id"); p.add_argument("request")
    p = sub.add_parser("init"); p.add_argument("run_dir"); p.add_argument("--request", required=True)
    p.add_argument("--flags-json", default="{}"); p.add_argument("--force", action="store_true")
    p = sub.add_parser("set"); p.add_argument("run_dir"); p.add_argument("stage"); p.add_argument("status")
    p.add_argument("--output", nargs="*"); p.add_argument("--note")
    p = sub.add_parser("lesson"); p.add_argument("run_dir"); p.add_argument("lesson_id"); p.add_argument("--status")
    p.add_argument("--qa", choices=["pass", "fail", "needs-human"]); p.add_argument("--attempt", action="store_true")
    p = sub.add_parser("cost"); p.add_argument("run_dir"); p.add_argument("--tokens", type=int); p.add_argument("--usd", type=float)
    p.add_argument("--estimate-usd", type=float); p.add_argument("--budget")
    p = sub.add_parser("next"); p.add_argument("run_dir")
    p = sub.add_parser("show"); p.add_argument("run_dir")
    a = ap.parse_args(argv)
    if a.cmd == "new-id":
        print(new_id(a.request))
    elif a.cmd == "init":
        init(a.run_dir, a.request, json.loads(a.flags_json), a.force)
        print(show(load(a.run_dir)))
    elif a.cmd == "set":
        set_stage(a.run_dir, a.stage, a.status, a.output, a.note)
    elif a.cmd == "lesson":
        set_lesson(a.run_dir, a.lesson_id, a.status, a.qa, a.attempt)
    elif a.cmd == "cost":
        add_cost(a.run_dir, a.tokens, a.usd, a.estimate_usd, a.budget)
    elif a.cmd == "next":
        print(next_stage(load(a.run_dir)))
    elif a.cmd == "show":
        print(show(load(a.run_dir)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
