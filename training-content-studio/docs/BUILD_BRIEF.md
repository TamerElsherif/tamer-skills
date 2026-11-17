# Build brief — Training Content Studio (internal, for build agents)

Plugin root: the plugin folder (git repo, separate from OpenMontage which is AGPLv3 —
never copy OpenMontage source into this repo; call it as an external tool only).
Python: `.venv/bin/python` (3.12; deps in `tools/requirements.txt`: pyyaml, jsonschema, requests, python-pptx,
pymupdf, python-docx, openpyxl). Add deps there if you need more and `uv pip install -p .venv/bin/python <pkg>`.
Node/Remotion only inside `kit/` (its own package.json; node_modules gitignored).
Read `_extraction.md` first: it is the worked example this plugin generalizes.

## Contracts (single source of truth — do NOT change without telling the orchestrator agent)
`schemas/`: sources, curriculum, storyboard, quiz, decisions, grounding_report, run_state (`*.schema.json`, Draft 2020-12)
and `schemas/enums.json` (templates, formats, targets, poses, expressions, sets). Every skill reads/writes only these files:
`sources.yaml`, `curriculum.yaml`, `storyboard.json` (one per lesson: `<lesson_id>.storyboard.json`), `quiz.json`
(`<lesson_id>.quiz.json`), `grounding_report.json`, `decisions.json` (+ `decisions.md`), `state.json`.
YAML files validate against the same JSON Schemas after `yaml.safe_load`.

Key storyboard rules:
- `scenes[].template` ∈ enums.templates; `props` per template (see `$defs`-style `allOf` in storyboard.schema.json).
- Narration lines `{who, text}`; `^` in text marks a visual cue; components read `cue(i)` = i-th `^` across the scene.
- Every scene has `claims[]`; each claim has `source_ids` (e.g. `S01`, `S01#c3`) or `general_knowledge: true`.
- ALL on-screen text comes from template props. `generated_images[].prompt` must never ask for text and must end with
  "no text, no letters, no numbers, no signage, no logos".
- Languages: `en-US|en-GB|ar-EG|ar-MSA`; Arabic → `direction: rtl`.

## Persona ids (character system, shared by kit + assets + formats)
`host` (narrator on screen), `learner`, `manager`, `mentor` (expert), `customer`, `rookie` (mistake-maker),
plus `colleague`, `exec`, `support` extras. Domain packs may add personas (security pack adds `vex`, the attacker — the
only persona wearing the attention colour). Personas are neutral (no real people), diverse, flat vector.

## Skill file format
`skills/<name>/SKILL.md` < 300 lines with YAML frontmatter:
```
---
name: <name>
description: <what it does + WHEN to use + when NOT to use; distinct trigger phrases; 2–4 sentences>
---
```
Body sections: Purpose · Inputs · Outputs · Steps · Rules/QA · References (load on demand). Long material goes in
`references/*.md` (≤150 lines each where possible), fill-in files in `templates/`, executable helpers in `scripts/`
(python, run with the plugin venv; paths relative to the plugin root via `Path(__file__).resolve()`; no absolute paths,
no secrets). Model-agnostic: steps are plain Markdown a ChatGPT/Gemini user could follow; scripts are optional accelerators.
Descriptions must not overlap: each skill claims a distinct request. Skills are invoked as `/<name>` in Claude Code.

## Other hard rules
- Arabic (Egyptian + MSA, RTL) and English are first-class everywhere (templates, decks, HTML, SCORM, PDFs, kit).
- Fonts: Latin Poppins/Inter; Arabic Cairo / IBM Plex Sans Arabic / Noto Kufi Arabic; mono IBM Plex Mono; hand Caveat.
- Default theme preset `neutral` (navy #363E77, blue #006AB3 → cyan #6FC7DA gradient, attention orange #FF6700, bg #F4F7FB);
  never cream/terracotta "Claude-like" palettes; logo slot optional and empty by default.
- No real people, no real brand logos in mock-ups; fictional company "Northwind Co." for examples.
- Secrets: read API keys from env (`OPENAI_API_KEY`, `PEXELS_API_KEY`) or a file named in `TCS_ENV_FILE`; never write keys.
- QA lessons from the worked example (encode where relevant): no one-sided thick accent borders on cards; stock clips loop/slow
  to fill a scene; Remotion composition ids use only `[a-zA-Z0-9-]`; detect truncated TTS by words-per-minute outliers;
  cue times from word timestamps; text ≥ 24 px at 1080p; ≤ 6 bullets per board.
- Keep tokens lean: no giant prose; tables and bullets.

## Ownership (who writes what — do not edit other agents' folders)
- A `kit/`, `skills/tcs-render-remotion/`, `skills/tcs-render-openmontage/`
- B `skills/tcs-render-lesson/`
- C `skills/tcs-orchestrator/`, `skills/tcs-autopilot/`, `skills/tcs-curriculum/`
- D `skills/tcs-source-ingest/`, `skills/tcs-scriptwriter/`, `skills/tcs-storyboard/`, `skills/tcs-assessment/`,
  `skills/tcs-grounding-check/`, `skills/tcs-localize/`
- E `skills/tcs-format-*` (10), `assets/`, `domains/`, `QUALITY.md`, `portable/`
- Orchestrator (main session): `schemas/`, `tools/`, `examples/`, `plugin.json`, root `README.md`.
If you need a change in someone else's area, write it in `NOTES_FOR_ORCHESTRATOR.md` (append a dated bullet) instead.
