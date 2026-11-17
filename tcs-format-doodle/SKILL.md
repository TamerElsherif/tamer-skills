---
name: tcs-format-doodle
description: Builds the doodle/whiteboard-format scenes of a lesson storyboard — hand-drawn line-art figures, marker arrows and handwritten notes drawn on in sync with narration (a draw-on sequence spec). Use when the chosen or requested format is "doodle", "whiteboard", "sketch", "draw-my-life" or "hand-drawn explainer". Not for flat motion graphics with B-roll (tcs-format-explainer) or coloured character stories (tcs-format-cartoon).
---

# tcs-format-doodle

## Purpose
Express one approved lesson as a whiteboard draw-on sequence: every visual element is a `whiteboard` item that is
"drawn" when its `^` cue is spoken. Ideal for cause→effect chains, mental models and simple processes.

## Inputs
- Approved lesson from `curriculum.yaml` (objectives, `duration_min`), facts from `sources.yaml`.
- Persona ids (`assets/characters/personas.yaml`, domain `personas.yaml`) — doodle draws them in ink line-art.
- Domain `format_defaults.yaml` (music `whiteboard`), theme preset `whiteboard` from `assets/theme_presets.yaml`.

## Outputs
- `scenes[]` built mainly from `whiteboard` (the draw-on spec), framed by `title`, `quiz`, `checklist`, `outro`
  (render in ink style when `theme.preset: whiteboard`). Optional `definition` / `steps` for dense recaps.
- `theme.preset: "whiteboard"`, `music.bed: "whiteboard"`, `cast[]` of personas drawn.
- The draw-on sequence spec = `props.items[]` in cue order:
  `{cue, kind: person|icon|note|arrow|circle|underline|box|cross|check, cast?, pose?, expr?, icon?, text?, x, y, w?, h?, to?, color: ink|attention|safe}`.
- Fill-ins: `templates/script_template.md`, `templates/drawon_spec.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Map objectives to 3–6 "boards" (one idea each, 10–25 s). Plan a left→right / top→bottom reading path per board.
2. Script narration per board; place `^` before the word that should trigger each drawing. Several items may share a cue.
3. Lay out items on the 1920×1080 stage (9:16: 1080×1920; 1:1: 1080×1080). Keep a 96 px safe margin;
   people feet `y` ≈ 860–900 on 16:9; notes ≤ 4 words, handwriting ≥ 40 px.
4. Use `color: attention` only for the one thing to notice per board; `safe` for correct actions; `ink` otherwise.
5. Add claims per scene, quick check (`quiz`), recap (`checklist`), `outro`.
6. Validate schema + cue counts (max `cue` + 1 ≤ number of `^`).

## Rules / QA
- ≤ 8 items per board, ≤ 3 per cue; leave ≥ 1.2 s between draw cues so strokes finish (renderer draws in ~1.2 s).
- Text only in `note`/`text` props (≥ 40 px handwriting at 1080p); never as part of drawings or generated images.
- Arrows: `x,y` → `to{x,y}` must land on the target item's bounding box — verify with QA stills.
- White ground, navy ink, one attention colour (orange) — never cream paper or terracotta.
- RTL: notes are mirrored by the kit; place reading order right→left for Arabic (`x` mirrored automatically if `direction: rtl`).

## Blends
- **doodle + job-aid**: the last board's checks become the job-aid checklist.
- **doodle + series**: each board is a 30–45 s nudge (one board + flashcard).
- **doodle + branching**: whiteboard sets up the dilemma, `decision` scene branches (keep ink style).

## References
- `references/playbook.md` — beats, timings, layout grid, do/don't, worked example.
- `templates/drawon_spec.md`, `templates/script_template.md`, `templates/example.storyboard.json`.
