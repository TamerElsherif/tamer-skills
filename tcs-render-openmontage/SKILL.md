---
name: tcs-render-openmontage
description: Renders a lesson storyboard.json to MP4 through the user's local OpenMontage install (video_compose atelier render with OpenMontage's own venv), so the lesson also appears as a project on the OpenMontage Backlot board. Use when OPENMONTAGE_ROOT is set or the user asks to "render via/in OpenMontage". Do NOT use when OpenMontage is not installed (use tcs-render-remotion), for decks/HTML/SCORM (tcs-render-lesson), or to edit storyboards.
---

# tcs-render-openmontage

## Purpose
Same output as tcs-render-remotion (same kit, same prepared run dir), but the final render runs inside OpenMontage:
`VideoCompose.execute(operation="render")` with `render_runtime: remotion`, `composition_mode: atelier` and a
`bespoke` entry that bundles the TCS kit + this lesson's timeline. OpenMontage is called as an external tool
(AGPLv3 — no OpenMontage source is copied into the plugin, and OpenMontage source is never modified).

## Inputs
- A prepared work dir from `tcs-render-remotion/scripts/prepare.py` (timeline.ts + public/), or a storyboard / `runs/<id>`
  via `render_lesson.py --engine openmontage` (prepares first).
- `OPENMONTAGE_ROOT` (alias `OPENMONTAGE_DIR`; default `~/OpenMontage`) containing `.venv/bin/python` and
  `remotion-composer/node_modules` (`cd remotion-composer && npm install` once).
- Same optional keys as tcs-render-remotion (`TCS_ENV_FILE`, OPENAI_API_KEY, PEXELS_API_KEY) for the prepare step.

## Outputs
- `<work>/renders/<L>_<tag>[_draft]_om.mp4` (+ `.json`, loudness −16 LUFS); copy in `$OPENMONTAGE_ROOT/projects/<slug>/renders/`.
- Run-dir mode: `runs/<id>/renders/<L>/<target>/<L>[.<lang>]_<tag>.mp4`, or `RENDER_PENDING.md` (with commands) if OpenMontage
  or Node is unavailable — the pipeline never fails.
- OpenMontage project `projects/tcs-<lesson>/`: `project.json` (via `lib.checkpoint.init_project`, pipeline `animated-explainer`),
  `composition/` (index.tsx, timeline.ts, kit/…, art-direction.md), `assets/public` → link to the work dir's public/,
  `artifacts/edit_decisions.json` (render_runtime + composition_mode + bespoke), `artifacts/render_report.json`, `decision_log.json`.

## Steps
```bash
export OPENMONTAGE_ROOT=~/OpenMontage            # where OpenMontage lives
export TCS_ENV_FILE=$OPENMONTAGE_ROOT/.env       # optional: reuse its keys (read only, never copied)
# one shot (prepare + render + frame grid), run-folder contract:
.venv/bin/python skills/tcs-render-remotion/scripts/render_lesson.py runs/<id> --engine openmontage [--target video-vertical] [--draft]
# or on an already prepared work dir:
.venv/bin/python skills/tcs-render-openmontage/scripts/om_render.py <work_dir> [--draft] [--slug my-slug]
.venv/bin/python skills/tcs-render-remotion/scripts/stills.py --video <work_dir>/renders/<L>_16x9_om.mp4
```
What om_render.py does, in order:
1. `init_project(<slug>, title=…, pipeline_type="animated-explainer")` with OpenMontage's venv (Backlot marker).
2. Copies `kit/src` → `projects/<slug>/composition/kit/`, `timeline.ts` beside it (atelier staging copies only
   .ts/.tsx/.js/.css, so the timeline is a TS module, not JSON), writes `index.tsx` = `registerRoot(makeFixedRoot(T, '<lesson-id>'))`.
3. Writes `edit_decisions.json` and the decision log, then runs
   `VideoCompose().execute({"operation":"render","edit_decisions":ed,"output_path":…})` from `$OPENMONTAGE_ROOT`
   (atelier stages the project into `remotion-composer/projects/<slug>/` and runs `npx remotion render`).
4. Loudness-normalises and copies the result back; prints OpenMontage's final review status.

## Rules / QA
- QA (stills, frame grid, missing_assets.json) is identical to tcs-render-remotion — do it on the work dir before rendering.
- Composition id = lesson id with only `[a-zA-Z0-9-]`; slug = `tcs-<lesson>` lowercased.
- The kit imports only remotion, @remotion/google-fonts, react, lucide-react — all present in OpenMontage's composer.
  If OpenMontage upgrades and a kit import breaks, render with tcs-render-remotion and note it.
- "transcript_comparison skipped" in the review is expected (TCS checks narration itself).
- Never edit files under `$OPENMONTAGE_ROOT` other than the project folder this skill created.
