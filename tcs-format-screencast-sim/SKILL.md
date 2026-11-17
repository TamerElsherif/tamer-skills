---
name: tcs-format-screencast-sim
description: Builds screencast and software-simulation scenes for a lesson — a step script played on a template-drawn app screen (watch), then a guided-practice / try-it simulation spec (do) that becomes interactive in HTML/SCORM. Use when the chosen or requested format is "screencast", "software demo", "simulation", "guided practice", "try it", "click-through" or "system training". Not for decision dilemmas (tcs-format-branching) or concept explainers (tcs-format-explainer).
---

# tcs-format-screencast-sim

## Purpose
Teach a software procedure with the watch → try → do pattern, without recording real screens (screens are drawn by
the kit from `screencast.app` fields, or from a supplied, scrubbed screenshot).

## Inputs
- Approved lesson (`curriculum.yaml`) — procedure objectives (`type: procedure`).
- Procedure facts with `procedure_order` from `sources.yaml` (SOPs, user guides, recorded demos ingested by tcs-source-ingest).
- Optional screenshots (must be scrubbed of real personal data; record license/owner in `assets[]`).

## Outputs
- `screencast` scenes: `{app{kind: form|table|list|settings|dashboard|screenshot, title, screenshot?, fields[]{id,label,value?,kind}}, actions[]{cue, do: move|click|type|select|highlight|callout|toast|zoom, target (field id), value?, label?}}`.
- **Step script** = ordered `actions[]` (one `^` per action) — the "watch" demo.
- **Interactive sim spec** = optional `props.sim` (extension, allowed by `additionalProperties`):
  `{mode: demo|guided|practice|assess, task, expect[]{target, value? ("*" = any)}, hints{target: text}, max_attempts, on_fail: replay_demo|show_hint|continue}`.
  Video targets render `guided`/`practice` as an overlay walkthrough; lesson/SCORM targets make it clickable.
- Supporting: `title`, `steps` (overview), `checklist`, `quiz`, `outro`; mock-ups (`browser_mock`, `popup`) where useful.
- Fill-ins `templates/sim_spec.yaml`, `templates/script_template.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Extract the procedure (ordered facts). Group into tasks of ≤ 7 steps; one task per screencast scene.
2. Define the screen: fields with stable ids (`date`, `amount`, `submit`), labels exactly as in the real UI (or neutral
   if the UI is not to be shown), fictional values only.
3. Demo scene (`sim.mode: demo`): one action per `^`; narrate the *why* for non-obvious steps.
4. Practice scene (`guided` then `practice`): task statement, `expect[]` in order, hints for common errors, attempts.
5. Optional `assess` scene (no hints) mapped to a quiz item (tcs-assessment adds a `scenario`/`ordering` item).
6. Overview `steps` before, `checklist` after; claims per scene (procedure facts); validate.

## Rules / QA
- Never show real personal data, real customer names, real URLs of internal systems, or real brand logos.
- Pointer actions ≥ 1.0 s apart; `zoom` on fields < 24 px; callouts ≤ 6 words.
- Field labels on screen are template text → translated for Arabic; RTL forms mirror (labels right).
- Keyboard path documented for accessibility (Tab order = `fields[]` order) for interactive targets.
- If the real UI changes often, prefer `kind` generic screens + labels over screenshots.

## Blends
- **screencast-sim + job-aid** (strongly recommended): the step script becomes a quick-reference card.
- **narrated-deck + screencast-sim**: policy in slides, practice in sim.
- **screencast-sim + series**: one task per nudge ("60-second how-to").
- **screencast-sim + branching**: error-handling decisions (e.g. "the system rejects your claim — what next?").

## References
- `references/playbook.md`, `templates/sim_spec.yaml`, `templates/script_template.md`, `templates/example.storyboard.json`.
