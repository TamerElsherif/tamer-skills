---
name: tcs-format-job-aid
description: Builds a job aid for a lesson — checklist, cheat sheet, quick-reference card or one-pager — as storyboard scenes that render to a printable/HTML page (target jobaid), usually paired with another format's lesson. Use when the chosen or requested format is "job aid", "checklist", "cheat sheet", "quick reference", "one-pager", "poster" or "desk card", or when any lesson needs a performance-support takeaway. Not for teaching from scratch (pair it with explainer/cartoon/screencast-sim etc.) or for slide decks (tcs-format-narrated-deck).
---

# tcs-format-job-aid

## Purpose
Give learners the thing they use *at the moment of need*: short, scannable, actionable. It summarises; it does not teach.
Usually derived from a sibling lesson (same objectives) — formats `["<main>", "job-aid"]` on the main storyboard, or a
separate `<lesson_id>-jobaid.storyboard.json` with `formats: ["job-aid"]` and target `jobaid`.

## Inputs
- Approved lesson (`curriculum.yaml`, objectives of type procedure/behavior/policy) and its storyboard if it exists
  (reuse its `do_dont`, `steps`, `checklist`, `table` props verbatim for consistency).
- Facts (`sources.yaml`) — contacts, thresholds, steps; domain `glossary.yaml` for terms.

## Outputs
- Page sections as scenes (order = top-to-bottom on the page): `title` (header), `checklist`, `do_dont`, `steps`
  (`danger: true` for "if it goes wrong"), `table` (contacts/limits), `definition` (key term), `icon_grid` (signs),
  `statement` (golden rule), optional `flashcard` deck for the series/nudge pairing.
- `narration` may be `[]` (static page) or 30–60 s walkthrough lines if a video version is wanted.
- `scenes[].notes` for placeholders the client must fill (phone numbers, URLs).
- Fill-ins `templates/onepager_template.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Decide the job-aid type: **checklist** (do in order / verify), **cheat sheet** (lookup), **decision card**
   (if-then), **one-pager** (mix, max 5 sections).
2. Pull content from the lesson; cut every word that isn't an action, a sign, a threshold or a contact.
3. Lay out ≤ 5 sections for A4/Letter portrait (≤ 3 for a desk card / 1:1 social tile; 9:16 for a phone wallpaper).
4. Mark client-specific placeholders in `notes` (fictional values in examples; never invent real contacts).
5. Claims per section; validate. Renderer: target `jobaid` → PDF/HTML/PNG (aspect ignored for A4; used for tiles).

## Rules / QA
- ≤ 7 items per checklist, ≤ 8 words per item, verbs first; ≥ 11 pt print / ≥ 24 px screen; contrast ≥ 4.5:1.
- One page. If it doesn't fit, make two job aids, not a smaller font.
- No generated imagery with text; icons from the kit only; logo slot empty unless supplied.
- Arabic: separate RTL page (not side-by-side) unless the brief asks for a bilingual card; digits consistent.
- Accessible PDF/HTML: real text (not images of text), heading order, alt text on icons that carry meaning.

## Blends (pairs with any format)
- **explainer + job-aid**: reuse `do_dont` + recap `checklist`.
- **screencast-sim + job-aid**: step script → numbered `steps` card.
- **cartoon/comic + job-aid**: mentor's rule → golden-rule `statement` + checklist.
- **branching + job-aid**: decision card of the red flags behind each choice.
- **series + job-aid**: one card per episode; nudges link to it.

## References
- `references/playbook.md`, `templates/onepager_template.md`, `templates/example.storyboard.json`.
