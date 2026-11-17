---
name: tcs-storyboard
description: Converts a finished lesson script into the render-agnostic `<lesson>.storyboard.json` — picks a kit template per scene with schema-valid props, b-roll queries, text-free generated-image prompts, cast, voices, theme and aspect, derives on-screen text, validates cues/claims/board sizes, and prints a markdown preview table for the lesson-1 approval gate. Use to turn a script into a storyboard JSON — "storyboard this", "convert the script into scenes", "choose the visuals/templates", "show me the storyboard preview", or "fix the storyboard validation errors". Not for writing or retiming narration (tcs-scriptwriter), rendering (tcs-render-*) or translating (tcs-localize).
---

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
