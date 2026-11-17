# PIPELINE SKILLS — stage instructions (curriculum, ingest, script, storyboard, assessment, grounding, localize)


# SKILL: tcs-orchestrator


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


# SKILL: tcs-autopilot


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


# SKILL: tcs-curriculum


# tcs-curriculum — outline, objectives and prioritization

## Purpose
Turn a topic (and optional sources) or a catalogue of candidates into a validated `curriculum.yaml`: what learners will be
able to do, in which order, in which lessons, how long, in which format — with a recorded reason for every choice.
It is the planning step that tcs-orchestrator (interactive) and tcs-autopilot (Stage 3) call; it can also be used alone.

## Inputs
- Topic / request text; audience (roles, level), languages; total length if given.
- Optional `sources.yaml` (from tcs-source-ingest) — headings, procedures, policies seed the objectives.
- Optional candidate list: `.xlsx` / `.csv` catalogue (read-only) or `candidates.yaml`.
- Optional domain pack name (`domains/<pack>/`) for prioritization weights, quotas, clusters, glossary.

## Outputs
- `curriculum.yaml` — validates against `schemas/curriculum.schema.json` (course, objectives, modules → lessons,
  optional `prioritization`, `approval`).
- Optional `prioritization.md` — ranked table for the approval gate.

## Steps

### A. Course outline (single course)
1. **Frame**: one sentence — *who* must be able to *do what* *by when / to what standard*. Pick the domain pack
   (`domains/<pack>`; none → `_template`).
2. **Objectives (3–5)**: measurable verb + object + condition, Bloom level matched to the need
   (know → remember/understand · do → apply · decide → analyze/evaluate). Tag each with `type`
   (concept, structure, procedure, behavior, policy, recall, adoption) and `source_ids` when sourced.
   Verb table + Arabic verbs: `references/objectives-and-paths.md`.
3. **Path**: order objectives (why → how, simple → complex, normal → exceptions, prerequisites first).
4. **Lessons**: 1 objective per lesson; 3–7 min each; ≤ 6 lessons per module; ids `M<n>L<n>`.
5. **Format per lesson**: from objective type × audience × effort — matrix in
   `skills/tcs-orchestrator/references/format-selection.md` (max 2 formats/lesson, 3/course). Put the reason in `rationale`.
6. **Course fields**: level, languages (Arabic → also `title_ar`), `wpm` (beginner 130 … advanced 155, Arabic −10 %),
   verbosity, complexity, targets, aspects, renderer, compliance.
7. **Approval**: leave `approval.status: draft`. The orchestrator gate sets `approved` (+ by/at/edits); autopilot sets
   `auto-approved`.
8. **Validate**: `.venv/bin/python skills/tcs-curriculum/scripts/validate_curriculum.py curriculum.yaml [--sources sources.yaml]`.
   Fix every ERROR; read every WARN.

Fill-in starting point: `templates/curriculum.template.yaml`.

### B. Prioritize a catalogue / long topic list
1. Choose a profile: the domain pack's (`--pack security-awareness`) or `templates/prioritization.default.yaml`; copy and
   edit for a new organisation (weights, quotas per audience, filters, keywords, already-built list).
2. Run:
   ```
   .venv/bin/python skills/tcs-curriculum/scripts/prioritize.py catalogue.xlsx --pack <pack> \
       [--weights impact=.3,frequency=.25,gap=.2,urgency=.15,compliance=.1] [--quotas standard=10,it=5,executives=5] \
       [--existing "Course A;Course B"] --out curriculum.yaml --md prioritization.md
   ```
   Without the script: build the same table by hand — filter → score 0–5 → P = Σ w·s → dedupe by subject → fill quotas
   → tier 2 (next 15) / tier 3 — steps and signals in `references/prioritization.md`.
3. Review the top table: cross-segment duplicates, "story" originals worth keeping, source files that don't match their
   title (swap with a cluster sibling). Edit `prioritization.items[].decision/reason` rather than deleting rows.
4. Rewrite the DRAFT objective of each included lesson (step A2), split modules > 6 lessons, then validate (A8).

## Rules / QA
- Every objective is measurable and taught by ≥ 1 lesson; every lesson has ≥ 1 objective (validator errors otherwise).
- ≤ 2 formats per lesson, ≤ 3 distinct formats per course; lesson lengths 3–7 min (warn outside).
- `total_minutes` within ±15 % of the lesson sum.
- Every prioritized row keeps a reason, including skipped duplicates and out-of-scope rows.
- Weights sum to 1 (the script normalises and says so).
- No sources → state "general knowledge" in the course notes; never invent `source_ids`.
- Arabic primary: `title_ar` on course/modules/lessons (or hand to tcs-localize); RTL is handled downstream.
- Catalogue files are opened read-only; never write back to the user's spreadsheet.

## References (load on demand)
- `references/objectives-and-paths.md` — Bloom verbs (EN/AR), sequencing, durations, wpm, level-from-audience.
- `references/prioritization.md` — the 8-step method, scoring signals, config keys, validation against the worked example.
- `templates/prioritization.default.yaml`, `templates/prioritization.security-awareness.yaml` — profiles.
- `templates/curriculum.template.yaml` — fill-in example.
- Scripts: `scripts/prioritize.py`, `scripts/validate_curriculum.py` (both `--help`).


# SKILL: tcs-source-ingest


# tcs-source-ingest

## Purpose
Every later claim in a course must point at a source id. This skill builds that evidence base once, keeps full text in
`cache/` so large sources never have to be re-read, and surfaces contradictions and stale material before scripting.

## Inputs
- Any mix of: local files (`.pdf .docx .pptx .xlsx .md .txt .html`), folders, `https://` pages, YouTube/Vimeo links,
  local video/audio (with optional `.vtt/.srt` sidecar), pasted text, `gdrive:` / `onedrive:` rclone paths.
- Run folder `runs/<run>/` (created by tcs-orchestrator) — output goes to `runs/<run>/sources.yaml`.
- Optional: `--authority 1-5` (5 = official policy), `--language`, `--course-id`, existing `sources.yaml` (`--append`).
- Secrets: `OPENAI_API_KEY` (only for whisper transcription) from env or the file in `TCS_ENV_FILE`.

## Outputs
| File | Content |
|---|---|
| `sources.yaml` | schema `schemas/sources.schema.json`: sources[] with chunks (id, loc, summary, tokens, path), facts[], glossary[], conflicts[] |
| `cache/<Sxx>/<cN>.md` | full text of each chunk (load only what you cite) |
| `cache/candidates.yaml` | deterministic fact candidates per chunk |
| `cache/ingest_report.md` | sources, dates, outdated list, conflicts, skipped inputs + next action |

## Steps
1. **Collect inputs.** List what the user gave; ask only if nothing usable was given. For Drive/OneDrive follow
   `references/loaders.md#cloud-folders` (print the rclone commands; let the user/orchestrator run the copy).
2. **Deterministic ingest** (script optional — a non-Claude user can do this by hand: split into ~1000-token chunks with locations):
   ```bash
   .venv/bin/python skills/tcs-source-ingest/scripts/ingest.py <paths|urls...> \
       --out runs/<run>/sources.yaml --course-id <id> [--authority 5] [--paste notes.txt] [--append]
   ```
   Exit 3 = some inputs skipped (read the report: missing yt-dlp, no API key, rclone path).
3. **Read the report** (`cache/ingest_report.md`): sources, detected dates, outdated (> 3 years), auto conflicts.
4. **LLM pass per chunk** (this is the part that needs a model):
   - `merge_facts.py runs/<run>/sources.yaml --todo --limit 10` → next chunks.
   - For each chunk, fill `templates/chunk_extract_prompt.md` with the chunk file + its candidates; collect YAML outputs
     into `runs/<run>/cache/extract-01.yaml` (shape: `templates/facts_batch.example.yaml`).
   - `merge_facts.py runs/<run>/sources.yaml --batch runs/<run>/cache/extract-01.yaml`
   - Repeat until `--todo` prints "all chunks summarised". Small sources (≤ 3 chunks) → one batch.
5. **Resolve conflicts** using the order in `references/extraction-rules.md#conflicts` (authority → date → specificity → ask).
   Write `resolution` + `chosen_fact` into `conflicts[]`. Unresolvable → keep `unresolved`; the orchestrator raises it at the gate.
6. **Validate**: `.venv/bin/python skills/tcs-source-ingest/scripts/validate_sources.py runs/<run>/sources.yaml`
   (errors must be 0; warnings reviewed).
7. **Hand-off summary** (≤ 10 lines): n sources, n chunks, n facts by kind, conflicts, outdated, gaps
   (topics the user asked for that no source covers → later claims must be `general_knowledge: true` or skipped).

## Rules / QA
- Never invent facts; every fact is something the chunk states. Model knowledge never enters `facts[]`.
- Keep numbers, currencies, units and dates exactly; one atomic statement per fact.
- Arabic sources stay Arabic (facts in source language; translation happens in tcs-localize).
- Cite precisely: `S01#c3` beats `S01`. `loc` = page/section/slide/timestamp.
- Do not paste whole sources into later prompts; downstream skills read summaries/facts and open only cited chunk files.
- Private material: never upload sources anywhere except the transcription call the user configured.
- Sources with authority ≤ 2 (chats, informal notes) can support examples but not policy claims.
- Images/scanned PDFs: no OCR here — describe or OCR externally and re-ingest as text.

## References (load on demand)
- `references/loaders.md` — per-format behaviour, whisper/yt-dlp, rclone Drive/OneDrive commands, chunking, metadata.
- `references/extraction-rules.md` — fact kinds, auto-candidates, conflict + outdated rules, very large sources.
- `templates/chunk_extract_prompt.md`, `templates/facts_batch.example.yaml`.
- Scripts: `ingest.py`, `merge_facts.py`, `validate_sources.py`, `md_to_pdf.py` (fixtures). Tests: `tests/`.


# SKILL: tcs-scriptwriter


# tcs-scriptwriter

## Purpose
Turn an approved lesson (curriculum objectives + sources) into narration that sounds human, fits the duration, cues the
visuals and can be verified claim by claim. One script per lesson per language.

## Inputs
- `curriculum.yaml` lesson: `id, title, objective_ids, formats (≤2), duration_min`; course `audience.level`, `languages`, `wpm`.
- `sources.yaml` facts (+ chunk files for cited chunks only). Never write from memory when a source exists.
- Format beats: `skills/tcs-format-<format>/references/playbook.md`; fallback `references/beats.md`.
- Domain pack (optional, `domains/<pack>/`): glossary, personas, red-flag patterns.

## Outputs
- `runs/<run>/lessons/<lesson_id>/<lesson_id>.script.md` (contract: `references/script-contract.md`).
- `runs/<run>/lessons/<lesson_id>/<lesson_id>.storyboard.json` — script stage (narration + claims per scene, placeholder templates),
  produced by `script_md.py to-storyboard`. tcs-storyboard completes it.

## Steps
1. **Budget**: `.venv/bin/python skills/tcs-scriptwriter/scripts/script_md.py budget --minutes <duration_min> --level <level> --lang <lang>`
   → wpm, scene count, words per scene (beginner 130, advanced 150–160, Arabic −10 %; `references/wpm-budget.md`).
2. **Beats**: open the format skill's beats (e.g. `tcs-format-explainer`); map each objective to ≥ 1 beat; check-beat per lesson.
3. **Pick facts**: for each beat list the fact ids (from `sources.yaml`) it will state. Gaps → `[general]` claim
   (only if `general_knowledge_allowed`) or drop the point; never invent policy numbers.
4. **Draft** from the family template: `templates/script-explainer.md` (explainer, doodle, narrated-deck, mindmap,
   screencast-sim, job-aid, series), `templates/script-story.md` (cartoon, comic), `templates/script-branching.md`.
   - Narration in the lesson language; Arabic per `references/arabic-narration.md` (ar-EG colloquial vs ar-MSA).
   - `^` right before the words that reveal each item; N items ⇒ N markers; quiz: question `{pause: 2.2}` then `^` answer.
   - Story formats: characters (persona ids from `cast`) speak short in-character lines; narrator ties back to the rule.
   - One `claim:` per checkable statement, tagged `[S01#c1]` / `[general]`; claims keep exact figures.
5. **Speakable numbers**: write numbers as words in narration; `scripts/speakable.py --lang <lang> "<text>"` helps.
6. **Check**: `script_md.py check <lesson>.script.md` → 0 errors; fix warnings on duration (±15 %), scene length (5–35 s),
   long sentences, digits.
7. **Script stage**: `script_md.py to-storyboard <lesson>.script.md --out <lesson>.storyboard.json` → hand to tcs-storyboard.
8. Report: words, est. duration vs target, cue count, claims (sourced vs general), open questions.

## Rules / QA
- Exact source content; cover every objective; no skipped topics the user asked for.
- No real people or brands; fictional "Northwind Co." unless the user's organisation is given; personas, not names, in cast.
- ≤ 25 words per sentence; 1 idea per scene; scenes 5–35 s; total within ±15 % of target (never "speed up" to fit).
- Every scene ≥ 1 claim; `general_knowledge` only when allowed and labelled.
- Don't write on-screen text here except via `template:` hints and `visual:` lines (on-screen text comes from storyboard props).
- Arabic is written natively, not translated line-by-line; keep English product terms when staff say them in English.
- Voices default to OpenAI `gpt-4o-mini-tts` `marin` + language instructions; characters get distinct voices
  (`script_md.py` persona map); override in front matter `voices:`.

## References (load on demand)
- `references/script-contract.md` — script.md format, cue rules, claims, style, script→storyboard mapping.
- `references/wpm-budget.md` — wpm table, formula, duration checks.
- `references/arabic-narration.md` — Egyptian vs MSA writing, Arabic numbers, TTS notes.
- `references/beats.md` — fallback beats per format + beat→template hints.
- Scripts: `script_md.py` (budget/check/to-storyboard), `speakable.py`. Tests: `tests/`.


# SKILL: tcs-storyboard


# tcs-storyboard

## Purpose
`storyboard.json` is the single contract every renderer consumes (Remotion/OpenMontage video, deck, HTML lesson, SCORM,
job aid). This skill makes it complete, valid and reviewable, with all on-screen text in template props.

## Inputs
- Script stage `runs/<run>/lessons/<lesson_id>/<lesson_id>.storyboard.json` (from tcs-scriptwriter: narration + claims, placeholder
  `statement` templates, `notes: "script-stage: … hint=…"`) or a `script.md`.
- Format playbook `skills/tcs-format-<format>/references/playbook.md` (beat → template map, pacing).
- `schemas/storyboard.schema.json`, `schemas/enums.json` (templates, poses, expressions, sets).
- Personas `assets/characters/personas.yaml` + `domains/<pack>/personas.yaml`; voices `assets/voices.yaml`;
  theme `assets/theme_presets.yaml`; domain mock-up presets `domains/<pack>/mockups.yaml`.
- `<lesson_id>.quiz.json` (for `quiz` scenes) if tcs-assessment ran.

## Outputs
- `runs/<run>/lessons/<lesson_id>/<lesson_id>.storyboard.json` (final stage, schema-valid, lint-clean).
- `runs/<run>/lessons/<lesson_id>/<lesson_id>.preview.md` — preview table (lesson 1 is shown at the approval gate).

## Steps
1. **Load** the script stage; read each scene's beat/hint from `notes`, its narration cues (`^` count) and claims.
2. **Choose templates** per scene with `references/template-guide.md` + the format playbook. Rules: match the beat; vary
   (no 3 identical templates in a row); mock-ups for anything seen on a screen; story beats → `cartoon`/`comic`;
   checks → `quiz` (props `quiz_item` = quiz.json id); decisions keep `decision` props from the script.
3. **Fill props** (all visible text here): short labels (title ≤ 60, item ≤ 70 chars), ≤ 6 items per board, digits on
   screen. Item count = `^` count (or explicit `cue` fields within range). Never put text in images.
4. **Assets**: `broll_shots[]` (concrete 4–9-word queries, `min_s` ≥ scene), `generated_images[]` (prompt ends with
   `no text, no letters, no numbers, no signage, no logos`), `music.bed`, `cast[]` (every persona referenced),
   `voices{}` (every narration `who`), `theme` (`neutral`, `logo: null`), `aspect` (16:9 / 9:16 / 1:1). See `references/visual-rules.md`.
5. **Remove** the `script-stage` notes (keep useful notes), set `visual` one-liners.
6. **Derive text**: `.venv/bin/python skills/tcs-storyboard/scripts/derive_text.py <sb> --force`
7. **Validate**: `.venv/bin/python skills/tcs-storyboard/scripts/validate_storyboard.py <sb> --stage final [--quiz <quiz>] [--target-min <min>]`
   → 0 errors; review warnings (cue/item mismatch, scene length, unused assets).
8. **Preview**: `.venv/bin/python skills/tcs-storyboard/scripts/preview.py <sb> --out runs/<run>/lessons/<lesson_id>/<lesson_id>.preview.md`
   For lesson 1 the orchestrator shows this at the approval gate; apply edits by scene id and re-validate.
9. Hand off to tcs-grounding-check (claims) and the renderer named in curriculum (`tcs-render-*`).

## Rules / QA
- Template-only on-screen text; generated imagery never contains text; no real people/brands/logos; fictional "Northwind Co.".
- Every scene has ≥ 1 claim (sourced or `general_knowledge: true`); every on-screen number is in a claim.
- Cue integrity: props cue indices < number of `^` in the scene; N revealed items ⇒ N markers.
- Persona ids only from the registry; narration `who` ∈ `voices`; Arabic ⇒ `direction: rtl` + Arabic font.
- Ids: scene `^[a-z][a-z0-9_]*$`; course/lesson ids `[A-Za-z0-9-]` (renderer composition ids).
- No one-sided thick accent borders, no blank-looking fades (renderer concerns, but don't request them in props/notes).
- Language/translation is not done here: a second language = tcs-localize.

## References (load on demand)
- `references/template-guide.md` — all 32 templates: when, required props, cue behaviour, picking rules.
- `references/visual-rules.md` — on-screen text, image prompts, b-roll, cast/voices, theme, aspect, durations.
- `templates/storyboard.skeleton.json` — valid example (title, cartoon, email mock-up with call-outs, generated image).
- Scripts: `validate_storyboard.py`, `derive_text.py`, `preview.py`, `sbtools.py` (shared). Tests: `tests/`.


# SKILL: tcs-assessment


# tcs-assessment

## Purpose
Measurable objectives need measurable items. Every objective gets items at its Bloom level, every item is grounded in a
source fact, and the result travels to any LMS.

## Inputs
- `curriculum.yaml` (objectives with `bloom`, lesson `objective_ids`), `sources.yaml` (facts, glossary, warnings),
  the lesson script/storyboard (examples, rookie mistakes = distractor material). Language from the lesson.
- Requested kind: knowledge-check (default), pre-test, post-test, scenario, flashcards.

## Outputs
- `runs/<run>/lessons/<L>/<L>.quiz.json` (schema `schemas/quiz.schema.json`); course-level tests `runs/<run>/<course>.post-test.quiz.json`.
- Optional exports next to it: `<L>.quiz.gift.txt`, `<L>.quiz.csv`.
- Storyboard `quiz` scenes reference items by id (`props.quiz_item`); tell tcs-storyboard which ids to use.

## Steps
1. List the lesson objectives (id, text, bloom). Pick item types per `references/item-writing.md` (Bloom table).
2. For each objective choose the facts behind it (policy/step/warning/definition); collect misconceptions from
   warnings, the script's mistake beats and near-miss numbers in the same source.
3. Write items from `templates/quiz.example.json`: ids `Q1…`, `objective_id`, `bloom`, `difficulty`, stem, options with
   exactly one `correct` (mcq/true_false/scenario), feedback per option, `explanation`, `source_ids` (or `general_knowledge`).
   Counts: knowledge-check 3–5 per lesson; post-test ≥ 2 per objective; flashcards 1 per key term/rule.
4. Arabic lessons: write natively (register of the lesson) or add `stem_ar`/`text_ar` for bilingual delivery.
5. Validate:
   `.venv/bin/python skills/tcs-assessment/scripts/validate_quiz.py <quiz> --curriculum runs/<run>/curriculum.yaml --sources runs/<run>/sources.yaml`
   (or `--storyboard <L>.storyboard.json` / `--objectives O1,O2`). Fix all errors; review warnings.
6. Export if asked: `scripts/to_gift.py <quiz> [--lang ar]`, `scripts/to_csv.py <quiz> [--lang ar]`.
7. Run tcs-grounding-check (it verifies quiz keys against sources together with storyboard claims).

## Rules / QA
- Every objective covered; items test the objective's verb, not trivia.
- One unambiguous key; distractors plausible, parallel in length/grammar; no "all/none of the above", no tricks.
- Feedback teaches (why), ≤ 25 words, per option. Fictional people/companies only.
- Keys must be supported by cited facts; scenario details may be fictional but the rule must be sourced.
- Pass mark default 80; `shuffle: true` unless ordering matters (ordering items are shuffled by the LMS anyway).

## References (load on demand)
- `references/item-writing.md` — types, Bloom table, distractors, feedback, kinds, Arabic, exports.
- `templates/quiz.example.json` — valid Northwind knowledge check (mcq, true_false, ordering, scenario, flashcard).
- Scripts: `validate_quiz.py`, `to_gift.py`, `to_csv.py`. Tests: `tests/`.


# SKILL: tcs-grounding-check


# tcs-grounding-check

## Purpose
Nothing ships that the sources don't say (or that isn't openly labelled general knowledge). This is the gate between
storyboard/quiz and rendering.

## Inputs
- `runs/<run>/sources.yaml` (+ `cache/` chunk files), `runs/<run>/lessons/<L>/<L>.storyboard.json`,
  optional `<L>.quiz.json` and `curriculum.yaml` (objective coverage). Localized storyboards (`<L>.ar-EG.storyboard.json`)
  are checked the same way (claims usually stay in the source language).

## Outputs
- `runs/<run>/lessons/<L>/<L>.grounding_report.json` (schema `schemas/grounding_report.schema.json`; summary also has `partial`).
- `<L>.grounding_report.md` — counts + table of claims needing fixes + uncovered objectives.
- Exit code: 0 pass · 2 needs fixes · 1 bad input (orchestrator/autopilot gate and `qa/<L>.qa.json` use it).

## Steps
1. **Deterministic check**:
   ```bash
   .venv/bin/python skills/tcs-grounding-check/scripts/check.py --sources runs/<run>/sources.yaml \
     --storyboard runs/<run>/lessons/<L>/<L>.storyboard.json [--quiz …/<L>.quiz.json] [--curriculum runs/<run>/curriculum.yaml]
   ```
   Per claim: cited id exists → candidate facts (cited chunk first) → content-word overlap + number match →
   supported / partial / conflicting / unsupported; sources.yaml conflicts → conflicting; old source/fact → outdated;
   `general_knowledge` → general-knowledge (unsupported if the course forbids it); on-screen numbers missing from the
   scene's claims → unsupported. Quiz keys = correct option(s) + explanation vs cited facts.
2. **LLM verification** for every partial/unsupported/conflicting claim (and a 10 % sample of supported ones on
   policy/number claims): fill `templates/verify_prompt.md` with the claim, cited facts and chunk text; save YAML
   verdicts; `scripts/apply_verdicts.py <report> verdicts.yaml`. Lexical matching misses paraphrases and can't see
   dropped exceptions — the LLM pass is what catches "always" vs "unless…".
3. **Fix** with `references/autofix.md` (re-cite → soften → label general knowledge → remove), editing script,
   storyboard props/narration and quiz consistently; re-run step 1 until exit 0.
4. **Report** to the orchestrator: summary line, fixes applied, open conflicts/outdated items needing the owner.

## Rules / QA
- Evidence = sources.yaml facts + cited chunk text only; model knowledge never upgrades a claim to supported.
- Numbers must match exactly (units, currency, limits); conditions/exceptions must survive.
- Unresolved source conflicts block the claim until resolved in sources.yaml (tcs-source-ingest) or avoided.
- Outdated is a warning for the gate unless the claim is a policy number — then confirm with the owner.
- Fictional scenario details are fine when labelled (claim "Scenario: … (fictional example)" `[general]`).

## References (load on demand)
- `references/autofix.md` — fixes per status, what autopilot may auto-apply.
- `templates/verify_prompt.md` — LLM verification prompt + verdict format.
- Scripts: `check.py`, `apply_verdicts.py`. Tests: `tests/`.


# SKILL: tcs-localize


# tcs-localize

## Purpose
Arabic and English are first-class. A localized lesson keeps the same scenes, cues, claims and timing logic, but reads
and sounds native: right register, RTL-correct, culturally fitting, consistent terms.

## Inputs
- Final source storyboard `runs/<run>/lessons/<L>/<L>.storyboard.json` (validated, grounded).
- Target language `ar-EG | ar-MSA | en-US | en-GB` (from curriculum `languages.secondary` / `subtitles`).
- Glossary: `templates/glossary.yaml` + `domains/<pack>/glossary.yaml` + course glossary in `sources.yaml`.
- Optional renderer timing `timing.json` for accurate subtitles.

## Outputs
- `runs/<run>/lessons/<L>/<L>.<lang>.storyboard.json` (e.g. `M1L1.ar-EG.storyboard.json`), schema-valid.
- `<L>.<lang>.translate.yaml` (worklist, kept for review/re-use), `<L>.<lang>.srt` / `.vtt` subtitles.

## Steps
1. **Register** — pick ar-EG vs ar-MSA with `references/register.md` (default ar-EG for Egyptian staff).
2. **Skeleton + worklist**:
   `.venv/bin/python skills/tcs-localize/scripts/localize.py skeleton <L>.storyboard.json --lang ar-EG [--numerals western|eastern]`
   → language/direction/fonts/voices switched, every translatable string marked `«TR» …`, worklist with glossary hints and
   the `^` count per string. Claims, URLs, e-mails, code and file names are left untouched.
3. **Adapt** each worklist entry (`tr:`) — meaning, not words (`references/register.md`); keep exactly the same `^`
   count in the same order; narration numbers as words, on-screen digits in one numeral system; cultural swaps from
   `references/cultural-swaps.md`; glossary terms consistent; persona bubbles use Arabic display names.
   Batch 20–40 entries per LLM call; give the model the scene context (template + neighbouring strings).
4. **Apply**: `localize.py apply <L>.<lang>.storyboard.json <L>.<lang>.translate.yaml` (fails on missing text or cue drift;
   re-derives on_screen_text).
5. **Lint**: `scripts/rtl_lint.py <L>.<lang>.storyboard.json --source <L>.storyboard.json` (RTL/bidi/numerals/register/cues)
   and `skills/tcs-storyboard/scripts/validate_storyboard.py <L>.<lang>.storyboard.json --stage final`.
6. **Voices**: confirm per `references/voices.md` (OpenAI `marin` + dialect instructions; alternates ElevenLabs/Azure).
7. **Subtitles**: `scripts/subtitles.py <L>.<lang>.storyboard.json [--timing timing.json]` (and for the source language
   too when the curriculum asks for subtitles). Real timing from the renderer is preferred; estimate otherwise.
8. **Grounding**: run tcs-grounding-check on the localized storyboard (claims unchanged; on-screen numbers must still
   appear in claims).

## Quiz
Localize `<L>.quiz.json` into `<L>.<lang>.quiz.json`: keep item/option ids and correct keys (grounding still matches), translate `stem`/`options[].text`/`feedback`/`explanation` (or fill `stem_ar`/`text_ar` for a bilingual file). Renderers pick the quiz that matches the storyboard language.

## Rules / QA
- Same scene ids, order and `^` counts as the source; duration within ±15 % (Arabic wpm × 0.9 → tighten wording).
- No literal calques; no mixed registers; product/UI names as they appear on screen.
- RTL: `direction: rtl`, Arabic font, mirrored directional icons, isolated URLs/e-mails/code, Arabic punctuation (، ؛ ؟),
  one numeral system. SVG illustrations with Latin labels stay LTR (renderer).
- Never change facts, limits or currencies while adapting; cultural swaps touch examples, names and visuals only.
- Subtitles ≤ 42 chars × 2 lines, ≤ 7 s per cue; RLM at the start of Arabic lines.

## References (load on demand)
- `references/register.md` — Egyptian vs MSA, adaptation rules EN→AR and AR→EN, quick map.
- `references/rtl-rules.md` — layout mirroring, numerals, punctuation, bidi, lint checks.
- `references/cultural-swaps.md` — names, currencies, holidays, workplace norms, visuals.
- `references/voices.md` — voice per language/provider, instruction recipes, TTS gotchas.
- `templates/glossary.yaml` — security + workplace + UI starter terms (en / ar_eg / ar_msa / keep).
- Scripts: `localize.py` (skeleton/apply), `rtl_lint.py`, `subtitles.py` (timing.json format in its docstring). Tests: `tests/`.
