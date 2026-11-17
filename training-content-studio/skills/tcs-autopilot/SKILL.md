---
name: tcs-autopilot
description: Fully automated course production with no questions — `/tcs-autopilot "<request>" [--sources …] [--lang ar|en|both] [--targets …] [--aspect …] [--review none|skeleton|final] [--budget …] [--domain …] [--resume <run-id>]` decides audience, objectives, length, formats, language and outputs from the request and sources, logs every decision with confidence, produces, QA-fixes and renders every lesson, and ends with REPORT.md. Use when the user says "autopilot", "no questions", "just make it", "fully automated", "batch", or invokes /tcs-autopilot or a --resume. Not when the user is present and wants to be consulted (tcs-orchestrator), and not for planning only (tcs-curriculum).
---

# tcs-autopilot — request in, course out

## Purpose
Run the whole pipeline unattended: ingest → decide → plan → produce → QA → render → report, resumable at every stage,
never blocking on a missing asset or renderer, and transparent about every choice it made for the user.

## Inputs
```
/tcs-autopilot "<request>" [--sources PATH|URL ...] [--lang ar|en|both] [--targets video,deck,lesson,scorm,jobaid]
               [--aspect 16:9|9:16|1:1] [--review none|skeleton|final] [--budget <tokens|$>] [--domain <pack>]
               [--resume <run-id> [--lesson M1L2] [--override key=value]]
```
Defaults: `--review none`, everything else decided (`references/decision-rules.md`).

## Outputs — `runs/<run-id>/` (layout: `skills/tcs-orchestrator/references/run-layout.md`)
`state.json` · `sources.yaml` · `decisions.json` + `decisions.md` · `curriculum.draft.yaml` → `curriculum.yaml` ·
`lessons/<L>/…storyboard/quiz/grounding_report` · `qa/<L>.qa.json` · `renders/…` · `REPORT.md`.

## Steps
Scripts run with the plugin venv: `P=.venv/bin/python; A=skills/tcs-autopilot/scripts`.
Each stage: `$P $A/run_state.py set runs/<id> <stage> running` → work → `… <stage> done --output <files>`.
Stage detail, QA checks and resume grammar: `references/stages.md`.

0. **Start or resume.** `--resume <id>` → `$P $A/run_state.py next runs/<id>` and jump there (apply `--lesson` /
   `--override` first, see stages.md). New run → `$P $A/run_state.py new-id "<request>"` →
   `$P $A/run_state.py init runs/<id> --request "<request>" --flags-json '<flags as JSON>'`.
1. **Ingest** — tcs-source-ingest on `--sources` → `sources.yaml`. No sources → stage `skipped` (general knowledge).
2. **Analyze & decide** —
   `$P $A/decide.py "<request>" <flags> [--sources-summary runs/<id>/sources.yaml] --out runs/<id>`
   → `decisions.json` (decision, signal, confidence 0–1, source, alternative rejected), `decisions.md`,
   `curriculum.draft.yaml`. Record the estimate: `$P $A/run_state.py cost runs/<id> --estimate-usd <estimate.usd> [--budget …]`.
   Without Python, apply `references/decision-rules.md` by hand and write the same files.
3. **Plan** — tcs-curriculum refines the draft into `curriculum.yaml` (+ lesson-1 storyboard preview); validate with
   `skills/tcs-curriculum/scripts/validate_curriculum.py`. `scope: plan-only` → skip to Report.
   `--review skeleton` → show skeleton + preview (orchestrator `approval-gate.md` templates), set `plan` = `needs-human`,
   write the report, **stop**; `--resume` continues. Else `approval.status: auto-approved`.
4. **Produce** (per lesson, parallel, max 5) — `tcs-format-<format>` (primary, then secondary blend) → tcs-scriptwriter →
   tcs-storyboard → tcs-assessment → tcs-localize (if needed). Track with `run_state.py lesson`.
5. **QA loop** — tcs-grounding-check + JSON-schema validation + QUALITY.md checks → `qa/<L>.qa.json`; auto-fix and
   retry ≤ 2 times; still failing → lesson `needs-human`, continue with the others. `--review final` → stop before render.
6. **Render** — video/video-vertical → tcs-render-openmontage (if `OPENMONTAGE_ROOT`) else tcs-render-remotion;
   deck/lesson/scorm/jobaid → tcs-render-lesson. Missing assets → placeholders; renderer/GPU unavailable → spec +
   command in `RENDER_PENDING.md`, status `render-pending`. Never block. SCORM last.
7. **Report** — `$P $A/report.py runs/<id>` → `REPORT.md` (produced paths, decisions table, QA results,
   unsupported/general-knowledge claims, missing assets, cost/tokens, per-lesson re-run commands with overrides).
   Reply with ≤ 10 lines: REPORT.md path, what is done, what needs the user (flagged decisions first).

## Rules / QA
- **Never ask questions** (that is tcs-orchestrator). Decide, log, flag.
- Explicit flags and request wording always override rules; record them with `source: flag|request`.
- Critical decision (domain, audience, objectives) with confidence < 0.5 under `--review none` → proceed, but flag at the
  top of REPORT.md.
- No sources → general knowledge, every claim `general_knowledge: true`, warning in the report.
  No sources + high-stakes topic (medical, legal, financial, safety-critical) → plan only; ask for sources in the report.
- Conflicting sources → most recent, then most authoritative; log a `conflict-resolution` decision.
- Budget: estimate after Plan; over budget → reduce scope (secondary formats → 9:16 → second language → lessons), log
  `budget-tradeoff`.
- Stages are idempotent and resumable; never delete user files; write only inside `runs/<id>/`.
- Same contracts as every skill: on-screen text only via template props; no text in generated images; Arabic = RTL;
  fictional personas, no real logos; secrets only from env / `TCS_ENV_FILE`.
- Tuning the rules: edit `decision-rules.yaml`, then `$P $A/test_decisions.py` (golden runs in `tests/golden_runs.yaml`) must pass.

## References (load on demand)
- `references/decision-rules.md` — defaults, guardrails, confidence scale (human version of `decision-rules.yaml`).
- `references/stages.md` — per-stage detail, QA checks, render fallbacks, resume/override grammar.
- `skills/tcs-orchestrator/references/format-selection.md` · `routing.md` · `run-layout.md` · `approval-gate.md` (shared).
- Scripts: `decide.py`, `run_state.py`, `report.py`, `test_decisions.py` (all `--help`).
