# Autopilot stages — detail

All stages read/write `runs/<run-id>/` (layout: `skills/tcs-orchestrator/references/run-layout.md`) and update
`state.json` via `scripts/run_state.py`. A stage is **idempotent**: re-running overwrites only its own outputs.
Resume = `run_state.py next runs/<id>` → run that stage and everything after it.

## 1. Ingest — tcs-source-ingest
- `--sources` paths/URLs/folders → `sources.yaml` (+ `sources/`). Unreadable source → note in state, continue with the rest.
- No sources → stage `skipped`, note "general knowledge".

## 2. Analyze & decide — scripts/decide.py
```
.venv/bin/python skills/tcs-autopilot/scripts/decide.py "<request>" [flags] [--sources-summary runs/<id>/sources.yaml] --out runs/<id>
```
→ `decisions.json`, `decisions.md`, `curriculum.draft.yaml`. Without Python: apply `decision-rules.md` by hand and
write the same files. Record `cost --estimate-usd` from `decisions.json.estimate`.

## 3. Plan — tcs-curriculum
- Refine `curriculum.draft.yaml` → `curriculum.yaml`: real lesson titles from the sources, objectives rewritten to be
  specific (keep ids, Bloom levels, `source_ids`), durations, `rationale` per lesson. Validate with
  `skills/tcs-curriculum/scripts/validate_curriculum.py`.
- Lesson-1 storyboard preview (scene list) — kept in `lessons/M1L1/notes.md`.
- `scope: plan-only` (high-stakes, no sources) → stop here: stage `plan` done, later stages `skipped`, go to Report.
- `--review skeleton` → print the skeleton + preview (approval-gate templates), set `plan` = `needs-human`, write REPORT.md,
  **stop**. `--resume` after approval sets `approval.status: approved` and continues.
- Otherwise `approval.status: auto-approved`.

## 4. Produce — per lesson, parallel (max 5)
`tcs-format-<format>` (primary, then secondary) → tcs-scriptwriter → tcs-storyboard → tcs-assessment →
tcs-localize (secondary language, or Arabic primary from English sources). Blend: primary owns scenes, secondary appends
(routing.md). Lesson status: planned → scripted → storyboarded.

## 5. QA loop — per lesson
Checks (write `qa/<L>.qa.json` = `{result, attempts, checks:[{name, ok, detail}]}`):
1. Schema: storyboard, quiz, grounding report validate (jsonschema, Draft 2020-12).
2. Grounding (tcs-grounding-check): unsupported = 0; conflicting = 0; every claim has `source_ids` or `general_knowledge`.
3. Coverage: every lesson objective appears in `coverage` and in ≥ 1 quiz item.
4. QUALITY.md checks (text ≥ 24 px at 1080p, ≤ 6 bullets/board, generated-image prompts forbid text, composition ids
   `[a-zA-Z0-9-]`, no one-sided thick accent borders, narration length fits duration at the chosen wpm).
Auto-fix: cite or relabel or cut unsupported claims; shorten over-long narration; split boards > 6 bullets; re-run checks.
**≤ 2 retries**; still failing → lesson `needs-human` (`run_state.py lesson … --qa needs-human`), keep its files, continue.
`--review final` → after QA set `render` = `needs-human` and stop until `--resume`.

## 6. Render — adapters
| Target | Adapter |
|---|---|
| video, video-vertical | tcs-render-openmontage (if `OPENMONTAGE_ROOT`) else tcs-render-remotion |
| deck, lesson, scorm, jobaid | tcs-render-lesson |
Rules: missing voice/b-roll/images/music → placeholders, never block. GPU/OpenMontage/Node unavailable → write the
render spec + exact command to `renders/<L>/<target>/RENDER_PENDING.md`, lesson status `render-pending`. Skip
`needs-human` lessons for video (render HTML preview only). SCORM last, packaging all QA-passed lessons.

## 7. Report — scripts/report.py
`.venv/bin/python skills/tcs-autopilot/scripts/report.py runs/<id>` → `REPORT.md` (+ refreshed `decisions.md`):
needs-attention block (flagged low-confidence decisions, plan-only, needs-human lessons, pending renders), produced
paths, decisions table, plan, QA table, unsupported and general-knowledge claims, missing assets, cost (estimate vs
actual), one-line re-run commands per lesson with overrides. Then reply to the user with ≤ 10 lines: where REPORT.md
is, what's done, what needs them.

## Command grammar for resume / overrides
```
/tcs-autopilot --resume <run-id>                                  # continue from the first unfinished stage
/tcs-autopilot --resume <run-id> --lesson M1L2                    # redo one lesson (produce → qa → render), then report
/tcs-autopilot --resume <run-id> --lesson M1L2 --override formats=explainer,job-aid
/tcs-autopilot --resume <run-id> --override lang=ar               # re-decide language, re-localize, re-render
```
Overrides update `curriculum.yaml` (and a `source: user` decision), reset the affected lessons to `planned`, and re-run.
