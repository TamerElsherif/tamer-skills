---
name: tcs-render-remotion
description: Renders a lesson storyboard.json (or every lesson in a runs/<id> folder) to MP4 with the plugin's own standalone Remotion kit — narration TTS, cue timing, stock b-roll, 16:9 / 9:16 / 1:1, QA stills and frame grids — self-contained, needing only Node and ffmpeg. Use for "render the video with Remotion", "standalone render", "make the vertical version", or "QA stills of the lesson"; it is the default video renderer. Not for rendering through the user's OpenMontage install (tcs-render-openmontage), decks/HTML/SCORM/job aids (tcs-render-lesson), or writing/fixing storyboards (tcs-storyboard).
---

# tcs-render-remotion

## Purpose
Turn any schema-valid `storyboard.json` into a finished MP4 with zero hand-written scene code. The shared kit
(`kit/`, Remotion 4) has one component per `enums.templates` entry; scripts here voice the narration, time every
`^` cue, fetch assets and render. Missing keys/assets never block: placeholders are used and listed.

## Inputs
- `<L>.storyboard.json` (schemas/storyboard.schema.json) — or a run dir `runs/<id>/` holding
  `lessons/<L>/<L>[.<lang>].storyboard.json`. Optional `<L>.quiz.json` beside it (quiz scenes without `q/options`).
- Keys (env or the file named in `TCS_ENV_FILE`): `OPENAI_API_KEY` (gpt-4o-mini-tts + whisper-1 word timing),
  `PEXELS_API_KEY` (b-roll; `PIXABAY_API_KEY` optional). None are required.
- Optional media dirs: `TCS_MUSIC_DIR` / `assets/music/<bed>.mp3`, `TCS_SFX_DIR` / `assets/sfx/<name>.wav`.
- Tools: Node ≥ 18, ffmpeg/ffprobe, plugin venv `.venv/bin/python`. First use runs `kit/setup.sh` (npm install).

## Outputs
- Run dir mode: `runs/<id>/renders/<L>/<target>/<L>[.<lang>]_<16x9|9x16|1x1>.mp4` + `.json` report + `.grid.jpg`;
  prepared work in `…/<target>/work/`. `target`: `video` (16:9, or 1:1 if the storyboard says so) | `video-vertical` (9:16).
- If a renderer/tool is unavailable: `RENDER_PENDING.md` in that target folder (reason + exact commands); exit 0.
- Work dir (`prepare.py --out`): `timeline.json` (`{"tl": …}` Remotion props), `timeline.ts` (same, as a module),
  `public/` (audio, broll, images, music, sfx), `missing_assets.json`, `prepare_report.json`, `qa/broll_sheet.jpg`.

## Steps
1. One shot (preferred):
   ```bash
   export TCS_ENV_FILE=/path/to/.env      # optional
   .venv/bin/python skills/tcs-render-remotion/scripts/render_lesson.py runs/<id> [--lesson M1L1] [--lang ar-EG] \
       [--target video --target video-vertical] [--draft]
   .venv/bin/python skills/tcs-render-remotion/scripts/render_lesson.py path/L.storyboard.json --out DIR --target video
   ```
2. Or step by step (gives you a QA loop before the final render):
   ```bash
   S=skills/tcs-render-remotion/scripts
   .venv/bin/python $S/prepare.py L.storyboard.json --out WORK [--aspect 9:16] [--placeholder-voice] [--no-broll]
   .venv/bin/python $S/stills.py WORK            # one still per scene → WORK/qa/stills_<tag>/sheet.jpg  — LOOK at it
   .venv/bin/python $S/stills.py WORK --at 12.5,40 --aspect 9:16
   .venv/bin/python $S/render.py WORK [--draft] [--aspect 1:1]   # → WORK/renders/<L>_<tag>.mp4, loudnorm −16 LUFS
   .venv/bin/python $S/stills.py --video WORK/renders/<L>_16x9.mp4 --n 12      # frame grid of the final
   ```
3. Read `missing_assets.json` and the b-roll contact sheet; fix the storyboard (queries, `pick`, paths) and re-run.
   TTS is hash-cached (`~/.cache/training-content-studio`), so re-runs only voice changed lines.
4. Studio preview (optional): `cd kit && npx remotion studio src/index.ts` then load `timeline.json` as props.

## What prepare.py does
- Validates against `schemas/storyboard.schema.json` (hard stop on errors) + warnings (unknown shot ids, fewer cues than items).
- Branching storyboards: linear video = `branching.start` → each decision's `video_choice`, else its `correct: true` choice.
- TTS per line with `voices[who]` (fallback `narrator`); Arabic adds Egyptian/MSA instructions and speed 0.9 (applied with
  ffmpeg atempo). Words-per-minute outliers (truncated clips) are retried. Language `ar-*` uses `text_ar` when present.
- Cue times: whisper-1 word timestamps aligned to the script words (difflib); fallback proportional timing.
- Timing per scene: `lead` (0.35) + lines (+`pre`, `pause` default 0.28; quiz/decision first line 2.2) + `hold` (0.75),
  ≥ `min_s`; scenes without narration use `duration_hint_s` (default 4 s).
- Mouth amplitude envelopes per line (lip-flap), b-roll fetch → normalised to the canvas, looped/slowed by the kit.

## Rules / QA
- Look at stills before the final render; check: text overflow, overlaps, empty half-screens, callouts on the right target,
  people inside frame in 9:16, Arabic reads right-to-left (bubbles, lists, panel order mirrored).
- Final MP4: duration ≈ `prepare_report.json` total, audio present, fades are not blanks.
- Reject b-roll with logos, readable text, hooded-hacker clichés; swap with `pick: 2` or a new query.
- Never edit kit files per lesson — fix the storyboard. Kit bugs: fix in `kit/src` (shared by both renderers).
- Composition id is always `tcs-lesson` (ids allow only `[a-zA-Z0-9-]`).

## References (load on demand)
- `references/templates.md` — every template's props, cue behaviour and reflow rules.
- `references/kit.md` — kit layout, theme presets, personas, adding a template.
