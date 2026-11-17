# Routing — which skill does what (Step 3, also autopilot Stages 1–6)

## Pipeline per course

| Stage | Skill | Reads | Writes (in `runs/<id>/`) |
|---|---|---|---|
| Ingest | tcs-source-ingest | user files/links | `sources.yaml`, `sources/` |
| Plan | tcs-curriculum | request, `sources.yaml`, decisions | `curriculum.yaml` |
| Gate | (this skill) | `curriculum.yaml` | `approval` block |

## Pipeline per lesson (after approval)

| # | Step | Skill | Output |
|---|---|---|---|
| 1 | Format playbook(s) — scene plan, templates, cast, sets | `tcs-format-<format>` for each lesson format (primary first) | scene plan notes |
| 2 | Script — narration lines `{who,text}`, `^` cue markers, claims with `source_ids` | tcs-scriptwriter | script in storyboard draft |
| 3 | Storyboard — templates + props, assets, b-roll, generated_images (no text) | tcs-storyboard | `lessons/<L>/<L>.storyboard.json` |
| 4 | Assessment — items mapped to objectives | tcs-assessment | `lessons/<L>/<L>.quiz.json` |
| 5 | Localize (if secondary language or Arabic primary from EN sources) | tcs-localize | `lessons/<L>/<L>.<lang>.storyboard.json`, `<L>.<lang>.quiz.json` |
| 6 | Grounding + QA | tcs-grounding-check (+ schema validation, QUALITY.md checks) | `lessons/<L>/<L>.grounding_report.json`, `qa/<L>.qa.json` |
| 7 | Render per target | see table below | `renders/<L>/<target>/…` |

Format skills: tcs-format-explainer · -doodle · -cartoon · -comic · -narrated-deck · -mindmap · -branching ·
-screencast-sim · -job-aid · -series. Series is course-level: run it once after the core lessons (episodes + nudges).

## Render targets

| Target | Adapter | Fallback when unavailable |
|---|---|---|
| video (16:9) / video-vertical (9:16) | tcs-render-openmontage if OpenMontage is reachable (`OPENMONTAGE_ROOT`), else tcs-render-remotion (kit/) | write spec + exact command to `renders/<L>/<target>/RENDER_PENDING.md`, status `render-pending` |
| deck (PPTX) | tcs-render-lesson (deck) ; narrated MP4 via the video adapter | spec + command |
| lesson (interactive HTML) | tcs-render-lesson | — (pure HTML, always possible) |
| scorm (SCORM 1.2 zip, course-level) | tcs-render-lesson (packages all lessons + quizzes) | — |
| jobaid (PDF/HTML one-pager) | tcs-render-lesson | HTML only if PDF engine missing |

Missing assets (voice, b-roll, images, music) never block: use placeholders (`assets[].status: placeholder`) and list them
in the report. Remotion needs a company licence above 3 employees — mention once if rendering commercially.

## Blends (composed here, not in the format skills)

- Primary format owns the lesson's scene list; secondary adds its scenes **after** (job aid, branching node, flashcards) or
  **inside** at a marked beat (branching decision after the cartoon conflict). Both write into one storyboard with
  `formats: [primary, secondary]`.
- Max 2 formats per lesson, 3 distinct per course — refuse more and explain the trade-off.
- Job aid content = the lesson's steps/checklist, never new material.

## Parallelism

- Lessons are independent after the plan: run steps 1–6 per lesson in parallel, **max 5 at a time** (8 parallel agents
  hit session limits in the worked example; 5 was stable).
- Within a lesson, steps are sequential (each reads the previous output). Localize can run in parallel with assessment.
- Render: video renders are CPU/GPU heavy — 1–2 at a time; HTML/SCORM/job aids in parallel. SCORM last (needs all lessons).
- Each parallel worker gets: lesson id, `curriculum.yaml`, `sources.yaml`, its format skill name(s), decisions summary,
  and the file paths it must write. It must not edit other lessons' files.

## Re-running one lesson

`/tcs-orchestrator` (or `/tcs-autopilot --resume <id> --lesson M1L2 [--override formats=explainer]`): reset that lesson
in `state.json` (`run_state.py lesson … --status planned`), redo steps 1–7 for it, regenerate SCORM and the report.
