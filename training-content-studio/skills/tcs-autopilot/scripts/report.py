#!/usr/bin/env python3
"""Render REPORT.md (+ refresh decisions.md) from a run folder. Read-only on everything except those two files.

Usage: report.py runs/<run-id> [--stdout]

Reads (all optional except decisions.json): state.json, decisions.json, curriculum.yaml | curriculum.draft.yaml,
lessons/<id>/<id>.storyboard.json, lessons/<id>/<id>.grounding_report.json, qa/<id>.qa.json, renders/**,
RENDER_PENDING.md files. Layout: skills/tcs-orchestrator/references/run-layout.md.
"""
from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decide  # noqa: E402  (shared decisions.md renderer)


def jload(p: Path):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def rel(p: Path, root: Path) -> str:
    return str(p.relative_to(root))


def esc(x) -> str:
    return str(x).replace("|", "\\|").replace("\n", " ")


def lesson_ids(cur, state, run: Path) -> list[str]:
    ids = []
    if cur:
        ids = [les["id"] for m in cur.get("modules", []) for les in m.get("lessons", [])]
    ids += [k for k in (state or {}).get("lessons", {}) if k not in ids]
    if (run / "lessons").is_dir():
        ids += [d.name for d in sorted((run / "lessons").iterdir()) if d.is_dir() and d.name not in ids]
    return ids


def build_report(run: Path) -> str:
    state = jload(run / "state.json") or {}
    dec = jload(run / "decisions.json")
    if dec is None:
        raise SystemExit(f"{run}/decisions.json missing — run decide.py first")
    cur_path = run / "curriculum.yaml" if (run / "curriculum.yaml").exists() else run / "curriculum.draft.yaml"
    cur = yaml.safe_load(cur_path.read_text()) if cur_path.exists() else None
    run_id = dec["run_id"]
    L = [f"# Run report — {run_id}", "", f"**Request:** {dec.get('request', '')}", ""]

    # status line
    stages = (state.get("stages") or {})
    if stages:
        L.append("**Stages:** " + " · ".join(f"{s} {v.get('status', 'pending')}" for s, v in stages.items()))
        L.append("")

    # needs attention
    attention = list(dec.get("flagged_top") or [])
    for lid, les in (state.get("lessons") or {}).items():
        if les.get("status") == "needs-human" or les.get("qa") == "needs-human":
            attention.append(f"Lesson {lid} failed QA after {les.get('attempts', 0)} attempt(s): needs a human (see qa/{lid}.qa.json).")
    pend = sorted(run.glob("renders/**/RENDER_PENDING.md"))
    if pend:
        attention.append(f"{len(pend)} render(s) pending — specs + commands written (see 'Produced').")
    if dec.get("pause_after") and stages.get("plan", {}).get("status") == "needs-human":
        attention.append("Paused after Plan for review (--review skeleton). Approve with: "
                         f"`/tcs-autopilot --resume {run_id}` (edit curriculum.yaml first if needed).")
    if attention:
        L += ["## Needs attention", ""] + [f"- {a}" for a in attention] + [""]
    for w in dec.get("warnings") or []:
        L.append(f"> {w}")
    if dec.get("warnings"):
        L.append("")

    # produced
    L += ["## Produced", ""]
    files = sorted(p for p in run.glob("renders/**/*") if p.is_file() and "work" not in p.relative_to(run).parts)
    core = [run / n for n in ("sources.yaml", "decisions.md", cur_path.name)]
    lessons_dir = sorted(p for p in run.glob("lessons/**/*") if p.is_file())
    if not (files or lessons_dir):
        L.append("- (nothing produced yet)")
    for p in core + lessons_dir + files:
        if p.exists():
            tag = " — **render pending**" if p.name == "RENDER_PENDING.md" else ""
            L.append(f"- `{rel(p, run)}`{tag}")
    L.append("")

    # decisions (compact; full table in decisions.md)
    L += ["## Decisions", "", "| decision | value | confidence | source |", "|---|---|---|---|"]
    for d in dec["decisions"]:
        v = d["value"]
        if isinstance(v, list) and v and isinstance(v[0], dict):
            v = f"{len(v)} objectives (see decisions.md)"
        elif not isinstance(v, str):
            v = json.dumps(v, ensure_ascii=False)
        flag = " ⚑" if d.get("flagged") else ""
        L.append(f"| {esc(d['key'] + (' (' + d['name'] + ')' if d.get('name') else ''))}{flag} | {esc(v)[:90]} | {d['confidence']:.2f} | {d['source']} |")
    L += ["", "Full signals and rejected alternatives: `decisions.md`.", ""]

    # plan
    if cur:
        L += ["## Plan", "", f"Approval: **{cur.get('approval', {}).get('status', '?')}**", "",
              "| lesson | title | objectives | formats | min | status |", "|---|---|---|---|---|---|"]
        for m in cur["modules"]:
            for les in m["lessons"]:
                st = (state.get("lessons") or {}).get(les["id"], {}).get("status", les.get("status", "planned"))
                L.append(f"| {les['id']} | {esc(les['title'])} | {', '.join(les['objective_ids'])} | {' + '.join(les['formats'])} | "
                         f"{les['duration_min']:g} | {st} |")
        L.append("")

    # QA + claims + assets
    qa_rows, gk, unsupported, missing = [], [], [], []
    for lid in lesson_ids(cur, state, run):
        g = jload(run / "lessons" / lid / f"{lid}.grounding_report.json")
        q = jload(run / "qa" / f"{lid}.qa.json") or {}
        les_state = (state.get("lessons") or {}).get(lid, {})
        if g:
            s = g["summary"]
            qa_rows.append(f"| {lid} | {s['supported']}/{s['total']} | {s['general_knowledge']} | {s['unsupported']} | "
                           f"{s['conflicting']} | {les_state.get('qa', q.get('result', '-'))} | {les_state.get('attempts', q.get('attempts', 0))} |")
            for c in g["claims"]:
                if c["status"] == "general-knowledge":
                    gk.append(f"{lid}/{c['scene_id']}: {c['text']}")
                elif c["status"] in ("unsupported", "conflicting", "outdated", "partial"):
                    unsupported.append(f"{lid}/{c['scene_id']} [{c['status']}]: {c['text']}" + (f" — fix: {c['fix']}" if c.get("fix") else ""))
        sb = jload(run / "lessons" / lid / f"{lid}.storyboard.json")
        if sb:
            if not g:
                for sc in sb.get("scenes", []):
                    for c in sc.get("claims", []):
                        if c.get("general_knowledge"):
                            gk.append(f"{lid}/{sc['id']}: {c['text']}")
            for a in sb.get("assets", []):
                if a.get("status") in ("missing", "placeholder"):
                    missing.append(f"{lid}: `{a['slot']}` ({a['status']}){' → ' + a['path'] if a.get('path') else ''}")
        if not g and les_state:
            qa_rows.append(f"| {lid} | - | - | - | - | {les_state.get('qa', '-')} | {les_state.get('attempts', 0)} |")
    if qa_rows:
        L += ["## QA results", "", "| lesson | supported | general knowledge | unsupported | conflicting | QA | attempts |",
              "|---|---|---|---|---|---|---|"] + qa_rows + [""]
    if unsupported:
        L += ["## Unsupported / conflicting claims", ""] + [f"- {x}" for x in unsupported] + [""]
    if gk:
        L += ["## General-knowledge claims (not from your sources — verify)", ""] + [f"- {x}" for x in gk[:60]]
        if len(gk) > 60:
            L.append(f"- … {len(gk) - 60} more (see lessons/*/*.grounding_report.json)")
        L.append("")
    if missing:
        L += ["## Missing assets (placeholders used)", ""] + [f"- {x}" for x in missing] + [""]

    # cost
    e, c = dec.get("estimate") or {}, state.get("cost") or {}
    L += ["## Cost", "", f"- Estimate: ~{e.get('tokens', 0):,} tokens, ~${e.get('usd', 0)} "
                         f"(TTS {e.get('tts_minutes', 0)} min, {e.get('images', 0)} images)",
          f"- Actual so far: {c.get('tokens', 0):,} tokens, ${c.get('usd', 0)}" + (f" (budget {c['budget']})" if c.get("budget") else ""), ""]

    # re-run commands
    flags = dec.get("flags") or {}
    base = f"/tcs-autopilot --resume {run_id}"
    L += ["## Re-run", "", f"- Whole run from the last unfinished stage: `{base}`"]
    req = shlex.quote(dec.get("request", ""))
    fl = " ".join(f"--{k.replace('_', '-')} {' '.join(v) if isinstance(v, list) else v}" for k, v in flags.items()
                  if k not in ("request", "sources_summary"))
    L.append(f"- Fresh run, same inputs: `/tcs-autopilot {req} {fl}`".rstrip() + "")
    if cur:
        other_lang = "en" if cur["course"]["languages"]["primary"].startswith("ar") else "ar"
        for m in cur["modules"]:
            for les in m["lessons"]:
                alt = "explainer" if les["formats"][0] != "explainer" else "doodle"
                L.append(f"- {les['id']}: `{base} --lesson {les['id']}` · other format: "
                         f"`{base} --lesson {les['id']} --override formats={alt}` · other language: "
                         f"`{base} --lesson {les['id']} --override lang={other_lang}`")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args(argv)
    run = Path(a.run_dir)
    md = build_report(run)
    dec = jload(run / "decisions.json")
    (run / "decisions.md").write_text(decide.to_markdown(dec))
    (run / "REPORT.md").write_text(md)
    if a.stdout:
        print(md)
    else:
        print(f"wrote {run / 'REPORT.md'} and {run / 'decisions.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
