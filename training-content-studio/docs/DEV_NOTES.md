# Notes for the orchestrator

- 2026-11-17 (agent E) **Contrast:** attention `#FF6700` is 2.92:1 on white — fails AA even for large text. Kit (A) must never
  render orange text on light backgrounds or white text on orange fills: use `attention_text` (#B34700, 5.5:1) for text and
  dark ink on orange chips. Encoded in `assets/theme_presets.yaml` + `assets/scripts/check_contrast.py`.
- 2026-11-17 (E) **Persona looks:** `assets/characters/personas.yaml` is the look spec (skin/hair/outfit hex) for kit SVG personas
  host, learner, manager, mentor, customer, rookie (+ colleague, exec, support extras). Security pack adds `vex` (orange jacket,
  only orange persona) and `voice_clone` (renders `exec` with a glitch overlay → cartoon `props.overlay: {kind: glitch}` suggested).
  Agent A: please align SVG cast to these, or tell E to update the yaml.
- 2026-11-17 (E) **screencast `props.sim` extension** (allowed by `additionalProperties`): `{mode: demo|guided|practice|assess, task,
  expect[]{target,value}, hints{}, max_attempts, on_fail, quiz_item}`. B (tcs-render-lesson) should make guided/practice/assess
  interactive in HTML/SCORM; video renderers play it as a narrated overlay. Consider adding it to storyboard.schema.json.
- 2026-11-17 (E) **Series files:** `series_plan.yaml` + `nudge_calendar.yaml` have a local schema at
  `skills/tcs-format-series/templates/series_plan.schema.json` (oneOf plan|calendar). Propose promoting to `schemas/`.
- 2026-11-17 (E) **Conventions used by format skills that renderers should honour:** `scenes[].notes` = presenter-only notes
  (narrated-deck; narration text → PPTX speaker notes); job-aid storyboards may have `narration: []` and `aspect` is ignored for
  A4/Letter jobaid output; branching linear video = start → `correct: true` path (or `decision.props.video_choice`);
  `theme.preset: whiteboard` for doodle (ink style); mindmap/comic/panel mirroring when `direction: rtl`.
- 2026-11-17 (E) **Portable bundle:** run `.venv/bin/python portable/build_portable.py` after all agents finish — it bundles
  pipeline skills that exist at build time (5/9 when E finished) and re-validates every format example + domain mock-up preset.
- 2026-11-17 (E) **Schema nit (no change made):** `generated_images[].prompt` description says the suffix is "no text, no letters,
  no signage, no logos" but BUILD_BRIEF requires "…, no numbers, …". E's checks enforce the BRIEF wording; align the description.
- 2026-11-17 (C) **Run folder contract** (`skills/tcs-orchestrator/references/run-layout.md`): per-lesson files live in
  `runs/<id>/lessons/<L>/<L>.storyboard.json|.quiz.json|.grounding_report.json`, localized `<L>.<lang>.storyboard.json`,
  QA in `qa/<L>.qa.json` (`{result, attempts, checks[]}`), renders in `renders/<L>/<target>/`, course-level SCORM/deck in
  `renders/course/{scorm,deck}/`, and unavailable renders as `renders/<L>/<target>/RENDER_PENDING.md`. `report.py` reads exactly
  these paths — D (grounding/localize) and A/B (renderers): please write there, or tell C.
- 2026-11-17 (C) **decisions.json extras:** decide.py adds top-level keys beyond the schema (allowed — no additionalProperties
  false): `summary`, `plan`, `estimate`, `scope`, `pause_after`, `warnings`, `flagged_top`, `flags`; and `name` on items with
  `key: other` (objective_type, assessment, grounding, approval). Consider adding `name` to the item schema.
- 2026-11-17 (C) **Domain pack ↔ prioritize.py:** `domains/security-awareness/prioritization.yaml` (E) is descriptive (quotas use
  `exec`, `audiences{}` labels, `clusters{id:{members}}`); prioritize.py adapts it (exec→executives alias, labels extend segment
  matching, clusters → extra subject families) and layers it over C's scoring profile
  `skills/tcs-curriculum/templates/prioritization.security-awareness.yaml` (keywords, filters, segments, families). Suggest E
  either moves that scoring profile into the pack or keeps both. Pack manifests are read for `detect_keywords` by decide.py.
- 2026-11-17 (C) **Format-default mismatch:** `domains/security-awareness/format_defaults.yaml` says behavior → [cartoon],
  exec → [explainer], policy → [narrated-deck, job-aid]; the autopilot spec (and golden runs) say behavior → cartoon + branching,
  executive/manager audience → narrated-deck primary, policy → cartoon micro-drama + post-test + evidence. decide.py follows the
  spec and does not read pack format_defaults. Decide which wins; if packs should override, C can add it behind a flag.
- 2026-11-17 (C) **Renderer routing assumption:** deck (PPTX), lesson (HTML), scorm and jobaid → tcs-render-lesson; video and
  video-vertical → tcs-render-openmontage when `OPENMONTAGE_ROOT` is set, else tcs-render-remotion. decide.py's `renderer`
  decision uses the same env var. Confirm with A/B.
- 2026-11-17 (C) **Autopilot command grammar additions:** `--resume <id> --lesson M1L2 --override key=value` (formats, lang, …)
  used in REPORT.md re-run lines and stages.md; `--renderer` and `--sources-summary` are decide.py-only flags.
- 2026-11-17 (B) **tcs-render-lesson done.** Scripts accept a storyboard file or a run folder and write the run layout:
  `renders/<L>/lesson|deck|jobaid/`, `renders/course/scorm/<course>-scorm12.zip`; missing Chrome → RENDER_PENDING.md.
  Course-level `renders/course/deck/` (merged PPTX) is NOT implemented — decks are per lesson; ask if needed.
  Regression: `bash skills/tcs-render-lesson/tests/run_all.sh` (also renders every `skills/tcs-format-*/templates/example*`).
- 2026-11-17 (B) **Schema requests:** (1) add `sim` sub-schema to screencast props (B implements mode/task/expect/hints/
  max_attempts/on_fail/quiz_item); (2) storyboard has no `jobaid` options — job aids use defaults (A4, 1 page) or a
  local `skills/tcs-render-lesson/templates/jobaid.schema.json` (jobaid.yaml); consider `targets_options.jobaid {paper,pages}`.
  (3) `screencast.app.fields[]` has no `options` for select fields — sims derive options from expect/actions values only.
- 2026-11-17 (B) **For A (kit):** persona SVGs are read from `assets/characters/<cast>/<pose>.svg` or `<cast>.svg` if present;
  otherwise B draws neutral placeholders using personas.yaml palettes. Please export kit personas there (or tell B the path).
- 2026-11-17 (B) **For C:** html_lesson/deck/jobaid take `--lesson` and `--lang` (localized `<L>.<lang>.storyboard.json` →
  `renders/<L>/<target>/<lang>/`). SCORM: `scorm.py --run <run>` packages every `renders/*/lesson/`.

## 2026-11-17 — agent D (ingest, scriptwriter, storyboard, assessment, grounding-check, localize)
- Golden sources written to `examples/_shared/sop/expenses.{md,pdf}` and `examples/_shared/policies/data-retention-policy.md` (deliberate 7-yr vs 6-yr receipt-retention conflict + 2019 outdated source). PDF regenerable via `skills/tcs-source-ingest/scripts/md_to_pdf.py`.
- Optional dep: `yt-dlp` for YouTube/Vimeo ingest (not in tools/requirements.txt; ingest reports how to install). Consider adding.
- grounding_report.json `summary` also carries `partial` (schema allows extra keys). Gate = exit code of check.py (0 pass / 2 fixes needed). Who writes `qa/<L>.qa.json`? I don't — suggest orchestrator/autopilot fold validate_storyboard --json, validate_quiz --json, check.py summary, rtl_lint --json into it.
- Renderers: please emit `lessons/<L>/<L>[.<lang>].timing.json` = `{"lines":[{"scene_id","idx","start","end"}]}` so `tcs-localize/scripts/subtitles.py --timing` uses real timing (else it estimates from wpm).
- Script stage: `script_md.py to-storyboard` writes a schema-valid storyboard with placeholder `statement`/`decision` templates and `notes: "script-stage: …"`; `validate_storyboard.py --stage final` fails while those remain.
- Persona discovery: base ids + `assets/characters/` (folders + personas.yaml keys) + `domains/*/personas.yaml` `personas:` keys. Voices default from `assets/voices.yaml` slots.
- Agent E: all `skills/tcs-format-*/templates/example*.storyboard.json` pass validate_storyboard (whiteboard boards now count only text notes). `tcs-format-explainer/templates/example.ar-EG.storyboard.json` is a 3-scene excerpt, so `rtl_lint --source example.storyboard.json` reports differing scene ids (expected for an excerpt; fine standalone).
- 2026-11-17 (A) Render kit + tcs-render-remotion + tcs-render-openmontage done. Entry point for autopilot:
  `skills/tcs-render-remotion/scripts/render_lesson.py runs/<id> [--lesson L] [--lang ar-EG] --target video|video-vertical [--engine openmontage] [--draft]`
  (writes renders/<L>/<target>/…mp4 or RENDER_PENDING.md, exit 0). prepare.py also writes `<L>[.<lang>].timing.json` beside the storyboard for subtitles.
- (A) Kit extensions read from props (schema allows via additionalProperties): `broll_shots[].pick`/`ss`, `cartoon.props.overlay.{cue,out_cue}`,
  `screencast.props.sim.expect` (used when `actions` is empty). Suggest documenting `pick` in storyboard.schema.json.
- (A) Persona SVGs exported to assets/characters/<cast>/<cast>.svg (+ wave/point/think/present.svg) via `cd kit && node scripts/export_personas.mjs`; re-run after look changes.
- (A) Theme presets in kit mirror assets/theme_presets.yaml roles; `midnight` is rendered navy-dominant with light content surfaces (kit templates assume light cards).

## 2026-11-17 — golden example 1 (`examples/golden-security-microdrama/`, dogfood run)
Fixes made (minimal):
- **decide.py** — "90-second" wording was ignored (→ 3 lessons × 5 min). Now `N sec/second(s)` → one micro-lesson holding
  all objectives, `duration_min = N/60`. test_decisions.py still passes. Still open (not fixed): `extract_topic` keeps the
  whole request as the topic for long requests, so template objectives read badly — orchestrator must rewrite them.
- **prepare.py `linear_path`** — branching video dropped every scene outside the branching nodes (title, rule, quiz,
  outro). Now non-branch scenes before the first / after the last branch scene stay in place (matches the HTML player).
- **kit `mocks.tsx` EmailMock** — body paragraphs were `inline-block`, so short lines ("Sam,") ran onto the next line;
  now `display: table`. Avatar initials stripped punctuation ("Hana (CEO)" gave "H(", now "HC").
- **tcs-render-lesson `figures.py`** — persona lookup missed `assets/characters/<cast>/<cast>.svg` (where A exports),
  so HTML lessons showed placeholder figures. Added that path.
Open issues (not fixed):
- `script_md.py check` and `validate_storyboard.py` duration estimates count off-path branch scenes, so a branching
  lesson reads ~25 % over target although the linear video is on target (86.8 s vs 90 s here).
- `tools/qa.py` re-runs check.py and overwrites the grounding report, dropping LLM verdicts from `apply_verdicts.py`;
  re-apply `<L>.verdicts.yaml` after QA (done here), or let qa.py apply it automatically if present.
- `report.py` "Produced" lists every file under `renders/*/work/` (audio clips, timeline…); consider skipping `work/`.
- No `assets/music` / `assets/sfx` shipped → cartoon bed and `ding` sfx are silent placeholders.

## 2026-11-17 — golden example 2 dogfood (`examples/golden-sop-deck-jobaid`, narrated deck + job aid, EN + ar-EG)
- FIXED `tcs-source-ingest/scripts/merge_facts.py`: crashed with `KeyError: 'tags'` after every `--batch` merge (tags popped only
  when the source was outdated). Now `if "tags" in f and not f["tags"]`. Minor: fact ids continue after dropped auto-candidates (F026…).
- FIXED `tcs-storyboard/scripts/sbtools.py` `revealed_items`: process_flow (and mindmap) nodes count as revealed items (kit
  reveals nodes on cues) — removed false "N '^' markers but only 0 used" warning.
- FIXED `tcs-grounding-check/scripts/check.py`: ordering quiz items with > 4 steps could never be "supported" (whole key vs
  per-fact overlap). If the joined key is not supported, each option is now verified separately; all supported → supported.
- decide.py (C): topic extraction keeps format words ("How to narrated deck and a one-page job aid from our expense SOP…") →
  garbage objectives/title when the request says "create a narrated deck … from our SOP". Strip format/target/language
  words and prefer the source title/procedure when sources exist.
- Quiz schema (D/orchestrator): only `stem_ar`/`text_ar` exist; no `scenario_ar`/`feedback_ar`/`explanation_ar`. A natively
  Arabic `<L>.ar-EG.quiz.json` fails grounding (lexical match vs English facts), so the working pattern is: English keys +
  `stem_ar`/`text_ar` + Arabic feedback/scenario. Consider `*_ar` for all text fields, or grounding against the source-language quiz.
  tcs-localize SKILL doesn't mention localizing the quiz at all — deck.html showed the English quiz in the Arabic deck until added.
- kit (A): process_flow edge labels (e.g. "> $1,000") overflow the gap between nodes in a 4-node row — labels removed in storyboard.
- tcs-render-lesson (B): deck.html process_flow with 4 nodes in a row leaves ~4 px gaps, so connectors/arrows are nearly invisible
  (EN and AR). `tests/shoot.py` doesn't page deck.html (always slide 1) — needs `#slide-N` support.
- report.py (C): QA table lists only primary-language lessons (no `M1L1.ar-EG` row from qa/M1L1.ar-EG.qa.json); cost stays 0
  unless someone calls `run_state.py cost` — the render scripts don't record TTS spend.
