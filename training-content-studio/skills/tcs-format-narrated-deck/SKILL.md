---
name: tcs-format-narrated-deck
description: Builds the narrated-deck format of a lesson storyboard — one slide per scene with on-slide text in template props, full speaker notes, and voice-over, so the same storyboard renders to PPTX, an HTML slide lesson and a narrated slide video. Use when the chosen or requested format is "narrated deck", "slides", "PowerPoint", "presentation with voice-over", "speaker notes" or "instructor-led deck". Not for animated explainers with B-roll (tcs-format-explainer) or one-page references (tcs-format-job-aid).
---

# tcs-format-narrated-deck

## Purpose
Produce a clean, accessible deck that a trainer can present live (speaker notes) or that plays as a narrated
video/HTML lesson (VO = narration). Best for policy, onboarding, compliance and reference-heavy lessons.

## Inputs
- Approved lesson (`curriculum.yaml`; `targets` usually include `deck`, often `lesson`/`video`/`scorm`).
- Facts from `sources.yaml` (decks/policies are the typical source — keep their structure where it is good).
- Theme preset + layout preset (`assets/theme_presets.yaml`, `assets/layout_presets.yaml`), voice (`assets/voices.yaml`).

## Outputs
- `scenes[]` = slides, each a template: `title`, `section`, `bullets`, `icon_grid`, `steps`, `process_flow`, `timeline`,
  `comparison`, `do_dont`, `table`, `stat`, `definition`, `statement`, `checklist`, `quiz`, `image`, `outro`
  (+ mock-ups when demonstrating a screen).
- `narration[]` = voice-over **and** speaker notes (renderer writes narration text into PPTX notes).
- `scenes[].notes` = presenter-only notes (facilitation tips, questions to ask, timing) — not voiced.
- `on_screen_text[]` optional (derived if omitted) for alt text / translation.
- Fill-ins `templates/script_template.md`, `templates/speaker_notes.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Outline: title → agenda (`section`) → 1 slide per key point → practice/check → summary → next steps.
2. One message per slide; slide title = the message as a short sentence or label.
3. Choose the template that fits the content (playbook map). ≤ 6 bullets, ≤ 8 words each; tables ≤ 5 rows × 4 cols.
4. Write VO: 30–90 s per slide; `^` per bullet/row/node reveal (one click per `^` in PPTX animations).
5. Add `notes` for live presenters (questions, examples from the client, timing).
6. Insert a `quiz` slide every 5–8 slides for long decks; final `checklist` summary; `outro` with next lesson.
7. Claims per slide; validate.

## Rules / QA
- No text-heavy slides: if VO and slide say the same 30 words, cut the slide text to keywords.
- Contrast ≥ 4.5:1, text ≥ 24 px at 1080p (≈ 18 pt on a 13.33 in slide), slide numbers on, alt text for images.
- Arabic deck: `direction: rtl`, Arabic font from theme, mirrored layouts, Western or Arabic-Indic digits consistently (per brief).
- Logo slot empty unless the brief supplies one. No stock photos with text/brands.
- Keep source deck order only if it serves the objectives; record reorderings in claims/notes.

## Blends
- **narrated-deck + job-aid**: summary slide → printable one-pager.
- **narrated-deck + screencast-sim**: deck explains the policy, sim practises the tool.
- **narrated-deck + branching**: a scenario slide with `decision` choices for live discussion or SCORM.
- **narrated-deck + series**: each section becomes a short episode for spaced delivery.

## References
- `references/playbook.md`, `templates/speaker_notes.md`, `templates/script_template.md`, `templates/example.storyboard.json`.
