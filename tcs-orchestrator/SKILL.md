---
name: tcs-orchestrator
description: Interactive entry point for making training content end to end — acts as senior instructional designer and SME, asks only the missing parameters in one round (with recommended defaults), shows an approval gate (course skeleton + lesson-1 storyboard preview), then routes every lesson through the format, script, storyboard, assessment, localization, grounding and render skills. Use when the user is present, wants to be asked and to see the plan before anything is produced, and asks to "design / make / create / build a course, lesson, training video, e-learning module, onboarding or awareness training". Not when they say autopilot, "no questions" or "fully automated" (tcs-autopilot), and not for outline/prioritization only (tcs-curriculum).
---

# tcs-orchestrator — interactive course production

## Purpose
Get from a request ("train my team on X") to finished, grounded training outputs with the fewest questions possible
and one explicit approval. You are a senior instructional designer + subject-matter expert: propose, recommend,
justify in one line, and let the user correct.

## Inputs
- The request (topic, plus anything already stated: audience, language, length, format, outputs, sources).
- Optional sources: files, folders, URLs, videos, pasted text.
- Plugin contracts: `schemas/*.schema.json`, `schemas/enums.json`, domain packs in `domains/`.

## Outputs (all in `runs/<run-id>/`, layout: `references/run-layout.md`)
`state.json`, `sources.yaml`, `decisions.json/.md`, `curriculum.yaml` (with `approval`), per lesson
`<L>.storyboard.json`, `<L>.quiz.json`, `<L>.grounding_report.json`, localized variants, `renders/…`, `REPORT.md`.

## Steps

### 0. Set up the run
1. `.venv/bin/python skills/tcs-autopilot/scripts/run_state.py new-id "<request>"` → `<id>`;
   `run_state.py init runs/<id> --request "<request>"`. (No Python? Create the folders and a state.json by hand.)
2. If sources were given → run **tcs-source-ingest** now (objectives are better from sources). Mark stage `ingest`.

### 1. Intake (one round, only what is missing)
1. Parse the request: fill every parameter already given — topic, sources, objectives, audience/role/level, language,
   total & per-lesson length, complexity/verbosity/wpm, format(s), output targets + aspect, domain pack.
   Parsing table and defaults: `references/intake-questions.md` §0.
   Accelerator: `skills/tcs-autopilot/scripts/decide.py "<request>" [flags] --out runs/<id>` proposes every default
   (with signals) — use its `decisions.json` as your starting proposal, not as final.
2. **Fully specified?** (topic, audience, language, length, format, targets all given) → skip to Step 2.
3. Otherwise ask the missing ones in **one round**: proposed 3–5 objectives (Bloom-matched) in the message text +
   up to 4 tappable questions (AskUserQuestion) or a numbered list — sources/permission for general knowledge,
   audience+level+language, length+pace, format(s) with your recommendation and one-line rationale, outputs+aspect.
   Every question has a ★ default, so "go with defaults" answers everything. Bank + merging rules:
   `references/intake-questions.md`. Format recommendation: `references/format-selection.md`.
4. High-stakes topic (medical, legal, financial, safety-critical) and no sources → ask for sources; do not offer
   general knowledge as the default.
5. Record answers as decisions (`source: user`) and mark stage `decide` done.

### 2. Approval gate (always)
1. Build the plan with **tcs-curriculum** (objectives → path → modules/lessons → format per lesson → durations).
   Validate: `.venv/bin/python skills/tcs-curriculum/scripts/validate_curriculum.py runs/<id>/curriculum.yaml`.
2. Show the skeleton table (modules → lessons → objective (Bloom) → format → minutes) and a lightweight lesson-1
   storyboard (scenes: visual, narration gist, on-screen text, seconds). Templates: `references/approval-gate.md`.
3. Wait. Apply edits and show the gate again. On approval write `approval: {status: approved, by, at, edits}` and set
   stage `plan` done. Never script or render before this.

### 3. Generate
1. Per lesson, in order (routing table: `references/routing.md`):
   `tcs-format-<format>` (primary, then secondary) → **tcs-scriptwriter** → **tcs-storyboard** → **tcs-assessment** →
   **tcs-localize** (if a second language / Arabic) → **tcs-grounding-check** (+ schema validation, QUALITY.md checks).
   Lessons run in parallel, max 5 at a time; update `run_state.py lesson runs/<id> <L> --status …`.
2. Blends are composed here: primary format owns the scene list, secondary adds its scenes (max 2/lesson, 3/course).
3. QA: fix failures from the grounding report (unsupported claim → cite, relabel `general_knowledge`, or cut);
   up to 2 retries, then mark the lesson `needs-human` and continue with the others.
4. Render each chosen target with its adapter: video/video-vertical → **tcs-render-openmontage** (if available) or
   **tcs-render-remotion**; lesson/scorm/jobaid/deck → **tcs-render-lesson**. Missing assets → placeholders;
   renderer unavailable → write spec + command (`RENDER_PENDING.md`), status `render-pending`. SCORM last.
5. Report: `.venv/bin/python skills/tcs-autopilot/scripts/report.py runs/<id>` → `REPORT.md`. Tell the user, briefly:
   what was produced (paths), what is pending, missing assets, general-knowledge/unsupported claims to verify, and the
   one-line command to redo any lesson.

## Rules / QA
- One question round, max. Ambiguous answers → take the ★ default and say so at the gate.
- Always the gate — even when the user pre-authorised; it is cheap and catches wrong objectives early.
- Explicit user wording beats rules (format, language, length, outputs).
- Every claim has `source_ids` or `general_knowledge: true`; no sources → say so at the gate and in the report.
- On-screen text only via template props; generated image prompts never ask for text and end with
  "no text, no letters, no numbers, no signage, no logos".
- Arabic and English are equal: Arabic primary → RTL, `ar-EG` or `ar-MSA`, English subtitles by default.
- Neutral fictional personas and "Northwind Co." in examples; never real people or real brand logos; logo slot empty by default.
- Keep chat output lean: tables, not prose. Don't paste whole storyboards into the chat — link the files.

## References (load on demand)
- `references/intake-questions.md` — parse table, question bank with ★ defaults, plain-text fallback.
- `references/format-selection.md` — objective type × audience × effort matrix, blends, format → targets (shared with autopilot).
- `references/approval-gate.md` — skeleton and storyboard-preview templates, how approval is recorded.
- `references/routing.md` — skill per step and target, blend composition, parallelism, re-running a lesson.
- `references/run-layout.md` — `runs/<run-id>/` folder layout and conventions (shared with autopilot).
