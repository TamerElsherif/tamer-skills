---
name: tcs-format-explainer
description: Builds the explainer-format scenes of a lesson storyboard — classic narrated explainer with motion-graphics boards, red-flag mock-ups and a stock B-roll shot list. Use when the chosen or requested format for an approved lesson is "explainer" (also "motion graphics", "B-roll explainer", "talking-points video"). Not for hand-drawn/whiteboard looks (tcs-format-doodle), character stories (tcs-format-cartoon) or slide decks with speaker notes (tcs-format-narrated-deck).
---

# tcs-format-explainer

## Purpose
Turn one approved lesson into the explainer part of `<lesson_id>.storyboard.json`: an arc of title → hook → concept →
mechanism → example → warning signs → consequences → actions → quick check → recap → outro, alternating stock B-roll
(with topic chips) and template-driven motion graphics roughly every 8–20 s.

## Inputs
| File | Use |
|---|---|
| `curriculum.yaml` → lesson (`approval.status` ∈ approved/auto-approved) | objectives, `duration_min`, `formats`, `targets` |
| `sources.yaml` | facts (`F###`) + chunk ids for `claims[].source_ids` (`S01#c3`) |
| `domains/<pack>/format_defaults.yaml`, `mockups.yaml` | per-domain music bed, mock-up presets (email/sms/mfa) |
| `assets/theme_presets.yaml`, `assets/voices.yaml` | theme preset + narrator voice for the lesson language |
| scriptwriter draft (if any) | narration lines to keep; re-cut into scenes |

## Outputs
- `scenes[]` using only `enums.templates`: `title`, `section`, `bullets`, `icon_grid`, `steps`, `process_flow`, `timeline`,
  `do_dont`, `comparison`, `stat`, `definition`, `statement`, `table`, `checklist`, `quiz`, `outro`, `broll`, `broll_panel`,
  `email_mock`, `chat_mock`, `browser_mock`, `mfa_prompt`, `popup`, `code_mock`, `image`.
- `broll_shots[]` — the B-roll shot list (`id`, `query`, `provider`, `min_s`, later `path` + `license`).
- Optional `generated_images[]` (no text in prompt; see Rules).
- Top level: `formats: ["explainer"]` (or blend, max 2), `music.bed: "explainer"` (`executive` for leadership audiences).
- Fill-in helpers: `templates/script_template.md`, `templates/broll_shotlist.yaml`; reference fragment
  `templates/example.storyboard.json` + Arabic RTL `templates/example.ar-EG.storyboard.json` (both validate against
  `schemas/storyboard.schema.json`).

## Steps
1. Read the lesson's objectives; list the beats from `references/playbook.md` and drop any that serve no objective.
2. Budget time: `duration_min × 60 × wpm/60` words (default 150 wpm EN, 130 wpm AR). Scenes 5–35 s, one idea each.
3. For each beat pick the template (table in playbook). Every 2–3 graphics scenes insert a `broll` or `broll_panel` scene.
4. Write narration lines `{who:"narrator", text}`; put `^` right before the words that reveal each item. N items ⇒ N `^`.
5. Fill props — all on-screen text lives here. Bullets/steps/icon_grid ≤ 6 items, checklist ≤ 7, ≤ ~8 words per item.
6. Attach `claims[]` per scene: `source_ids` from `sources.yaml` or `general_knowledge: true` (be honest).
7. Build `broll_shots[]`: concrete, people-at-work queries (no logos, no hoodie-hacker clichés), `min_s` ≥ scene length.
8. Add the quick-check `quiz` scene (`quiz_item` → id in `quiz.json`; question line `pause: 2.2`, answer line starts `^`).
9. Validate (see Rules) and hand back to `tcs-storyboard` / orchestrator.

## Rules / QA
- Templates and props only; never invent a template or put text into imagery. Image prompts end with
  "no text, no letters, no numbers, no signage, no logos".
- Mock-ups use fictional brands/domains (`northwind.example`, look-alike `northwlnd.example`); no real logos.
- `^` count per scene ≥ highest `cue` used in props + 1; reveal nothing long before it is said.
- Stats need a source (`stat.source` + claim `source_ids`); never invent numbers.
- B-roll: review the contact sheet; reject clips with visible brands, text, screens with readable data, clichés.
  Clips loop/slow (≥ 0.6×) to fill a scene, but prefer `min_s` ≥ scene length.
- Remaking an existing video: total ≥ 90% of original duration (aim 100–120%); cover every original point.
- Validate: `.venv/bin/python -c "import json,jsonschema;jsonschema.validate(json.load(open('X.storyboard.json')),json.load(open('schemas/storyboard.schema.json')))"`.

## Blends (orchestrator composes; `formats` max 2)
- **explainer + job-aid** (most common): job-aid skill derives a one-pager from this lesson's do_dont/checklist scenes.
- **explainer + branching**: explainer teaches, then one `decision` scene + `branching` graph for a scenario check.
- **explainer + series**: cut 30–60 s nudges from the recap/flashcards (tcs-format-series).
- **explainer + cartoon**: short `cartoon` story cold-open, explainer body. Keep ≥ 60% explainer scenes.

## References (load on demand)
- `references/playbook.md` — when to use, beats + timings, template map, do/don't, worked example.
- `templates/script_template.md`, `templates/broll_shotlist.yaml`, `templates/example.storyboard.json`.
- `QUALITY.md` (plugin root) — release checklist.
