---
name: tcs-render-lesson
description: Renders a lesson's storyboard.json / quiz.json / curriculum.yaml into the NON-VIDEO deliverables — an interactive HTML lesson (branching, knowledge checks, screencast sims), a narrated deck (PPTX with speaker notes + HTML slides), a SCORM 1.2 package for an LMS (e.g. Tandrik), and a printable PDF job aid (A4/Letter). Use for targets lesson, deck, scorm or jobaid, or when asked to "export to SCORM", "make slides/PPTX", "build the e-learning page", "print a cheat sheet". Not for MP4/video renders (tcs-render-remotion / tcs-render-openmontage) and not for writing or changing content (tcs-storyboard, tcs-assessment, tcs-format-*).
---

# tcs-render-lesson

## Purpose
Turn finished, validated lesson data into deliverables learners and LMSs can use, with **no new text**: every visible
string comes from storyboard props, quiz items or curriculum titles (UI chrome labels like Next/Back come from a fixed
EN/AR table). No generated images with text; icons are inline SVG; personas are SVG (kit art if present, else neutral
placeholders in the persona palette from `assets/characters/personas.yaml`).

## Inputs
| File | Used by |
|---|---|
| `<L>.storyboard.json` (schemas/storyboard.schema.json) | all |
| `<L>.quiz.json` (schemas/quiz.schema.json) — optional | lesson, deck notes, SCORM score |
| `curriculum.yaml` (schemas/curriculum.schema.json) | SCORM organisation |
| `jobaid.yaml` (references/jobaid-yaml.md) — optional | jobaid |
| `audio/<scene_id>.mp3|m4a|wav` next to the storyboard — optional | lesson (player + captions), deck (embedded) |

Every script accepts **a file or a run folder** (`runs/<id>/`, see `skills/tcs-orchestrator/references/run-layout.md`);
with a run folder, `--lesson M1L1` and `--lang ar-EG` select files, and outputs default to the run layout.

## Outputs (run layout)
| Target | Output |
|---|---|
| lesson | `renders/<L>/lesson/index.html` (self-contained, CSS/JS inline) + `media/` + `lesson.json` |
| deck | `renders/<L>/deck/<L>.pptx` + `deck.html` |
| jobaid | `renders/<L>/jobaid/<L>.pdf` (+ `.html`, `.png` preview) |
| scorm | `renders/course/scorm/<course-id>-scorm12.zip` (one SCO per lesson) |
| missing dependency | `RENDER_PENDING.md` in the target folder with exact commands — never a hard failure |

## Steps
Run from the plugin root with `.venv/bin/python` (deps in `tools/requirements.txt`; Chrome needed for PDF/QA only).
1. **Validate** — scripts validate against `schemas/` and cross-check references (decision `next` ids, branching
   scenes, `quiz_item`s). Fix the data (tcs-storyboard / tcs-assessment), don't patch outputs. `--no-strict` = warn only.
2. **HTML lesson** — `scripts/html_lesson.py <storyboard|run> [--quiz q.json] [--out dir] [--audio dir]`
   One page per scene, all 32 templates (references/templates.md). Branching player follows `storyboard.branching`;
   quiz scenes embed items; remaining items form a final Knowledge check; end page shows score vs `pass_mark`.
   Screencast scenes with `props.sim.mode` guided|practice|assess become hands-on sims (validated against
   `sim.expect`, hints, `max_attempts`, `on_fail`); assess counts as a scored item (`sim.quiz_item` or `SIM_<scene>`).
3. **Deck** — `scripts/deck.py <storyboard|run> [--out dir] [--audio dir] [--quiz q.json]`
   One slide per scene, native editable shapes, size from `aspect` (16:9 / 9:16 / 1:1), theme colours, RTL paragraphs
   for Arabic. Speaker notes = narration (+ quiz answer, decision routes, `scenes[].notes` as "Presenter:").
   Audio per scene is embedded (click to play). For a **narrated MP4** use tcs-render-remotion / tcs-render-openmontage.
4. **Job aid** — `scripts/jobaid.py <storyboard|jobaid.yaml|run> [--out x.pdf] [--paper A4|Letter] [--pages 1|2]`
   Blocks from checklist / steps / do_dont / table (+ bullets, definition, comparison, icon_grid, statement); title
   scene = header, outro = footer. Auto-shrinks (scale 1.0 → 0.66) to fit the page budget. `aspect` is ignored.
   In a run folder `<L>-jobaid.storyboard.json` is preferred when present.
5. **SCORM** — `scripts/scorm.py --run <run>` or `--lesson-dir <dir>... --curriculum c.yaml --out x.zip`
   Re-uses the rendered HTML lessons, injects `shared/scorm12.js`, writes `imsmanifest.xml` (modules → items, one SCO
   per lesson, `adlcp:masteryscore` = pass_mark). Details: references/scorm-1.2.md.
6. **Check** — `scripts/scorm_check.py <zip>` (must print OK). Visual QA: `tests/shoot.py <index.html> --out <png dir>
   --query reveal=1` then `tests/contact_sheet.py`; look at every sheet (overlaps, clipped text, RTL order).
   Full regression: `bash skills/tcs-render-lesson/tests/run_all.sh`.

## Rules / QA
- Text only from data; never invent labels, never put text into images. Missing media → labelled placeholder + listed
  in `lesson.json.missing_media`.
- Arabic (`ar-*` or `direction: rtl`): `dir=rtl`, Cairo / IBM Plex Sans Arabic, mirrored arrows, mindmaps,
  cartoon/whiteboard staging; PPTX paragraphs `rtl=1`, cs-font set, tables RTL. Keyboard arrows follow reading direction.
- Colour: theme from `assets/theme_presets.yaml` + `theme.colors`; orange (#FF6700) is fill/stroke only — text uses
  `attention_text` (#B34700), text on orange uses dark ink. No one-sided thick accent borders; ≤ 6 bullets per board.
- Accessibility: skip link, landmarks, focus moves to the scene heading, aria-live progress/feedback, fieldset/legend
  quizzes, visible focus, ≥ 44 px targets, transcripts for every scene, captions (VTT) when audio exists,
  `prefers-reduced-motion`, print stylesheet (all scenes, transcripts expanded).
- Branching linear exports (deck, job aid) keep storyboard order; decision routes are written to speaker notes.
- SCORM: plain 1.2 only (no xAPI/2004), suspend_data ≤ 4096 chars, never downgrade a `passed` status.

## References (load on demand)
- `references/templates.md` — how each template renders in HTML / PPTX / job aid
- `references/scorm-1.2.md` — tracking model, manifest, Tandrik/LMS notes, troubleshooting
- `references/jobaid-yaml.md` — jobaid.yaml shape and derivation from storyboards
- `references/player.md` — branching/quiz/sim runtime, bookmarking, QA URL flags
