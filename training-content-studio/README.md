# Training Content Studio

A plugin of skills that turns a subject and your source material into finished training: **intake → approval gate →
script → storyboard → assessment → grounding check → render**. It works for any subject (technical, compliance, soft skills,
onboarding, product, sales, safety, academic) and treats **English and Arabic (Egyptian and MSA, right-to-left) equally**.
`/tcs-autopilot` runs the same pipeline with no questions and records why it decided each thing.

Generalized from a real production run: 61 security-awareness courses, 70 videos (see `_extraction.md`).

## Outputs

| Target | Renderer | Files |
|---|---|---|
| Video 16:9 / 9:16 / 1:1 | `tcs-render-remotion` (standalone kit), or `tcs-render-openmontage` (your local OpenMontage) | MP4 normalized to −16 LUFS, captions timing, frame grids |
| Narrated deck | `tcs-render-lesson` | PPTX with speaker notes + HTML slides (+ narrated MP4 via the video renderers) |
| Interactive lesson | `tcs-render-lesson` | Self-contained HTML: branching player, knowledge checks, screencast simulations |
| LMS package | `tcs-render-lesson` | SCORM 1.2 zip (score, status, bookmarking), tested in a mock LMS |
| Job aid | `tcs-render-lesson` | One-page PDF (A4/Letter) checklist / cheat sheet |

## Hard rules built into every skill

- **Grounded:** every claim carries a `source_id` or is labelled `general_knowledge: true`; `tcs-grounding-check` verifies it.
- **No text in generated imagery:** all on-screen text, captions, diagrams, mind maps and UI mock-ups come from templates.
- **Approval before generation** (orchestrator); autopilot skips the gate unless `--review skeleton|final`.
- **Lean context:** SKILL.md files stay under 300 lines; references load on demand; large sources are chunked and summarized.
- **Model-agnostic:** contracts are JSON Schema + Markdown, and `portable/` packages the workflow for a ChatGPT GPT or Gemini Gem.

## Skills

| Skill | Job |
|---|---|
| `tcs-orchestrator` | Interactive entry: one round of intake questions with defaults → approval gate → routes everything |
| `tcs-autopilot` | `/tcs-autopilot "<request>"`: fully automated, resumable, writes `decisions.md` + `REPORT.md` |
| `tcs-source-ingest` | Files, folders, URLs, YouTube/Vimeo, Drive/OneDrive (rclone), pasted text → `sources.yaml` |
| `tcs-curriculum` | Objectives (Bloom), modules, durations; prioritization (impact × frequency × gap × urgency × compliance) → `curriculum.yaml` |
| `tcs-scriptwriter` | Format-aware narration, EN + AR, `^` visual cues, source-tagged claims |
| `tcs-storyboard` | Script → render-agnostic `storyboard.json` (32 templates) + approval-gate preview |
| `tcs-assessment` | Knowledge checks, scenarios, pre-tests, flashcards → `quiz.json` (+ GIFT/CSV export) |
| `tcs-grounding-check` | Verifies claims against sources; flags unsupported, conflicting, outdated |
| `tcs-localize` | AR↔EN adaptation, RTL rules, glossary, voices, subtitles |
| `tcs-render-remotion` | Standalone video render (default) |
| `tcs-render-openmontage` | Video render through your OpenMontage install (Backlot board project) |
| `tcs-render-lesson` | HTML lesson, deck, SCORM 1.2, PDF job aid |
| `tcs-format-explainer` · `-doodle` · `-cartoon` · `-comic` · `-narrated-deck` · `-mindmap` · `-branching` · `-screencast-sim` · `-job-aid` · `-series` | One skill per format family: playbook, beat structure, templates, examples. Blends are composed by the orchestrator (max 2 formats per lesson, 3 per course) |

## Contracts (`schemas/`)

`sources.yaml` · `curriculum.yaml` · `<L>.storyboard.json` · `<L>.quiz.json` · `grounding_report.json` · `decisions.json` ·
`state.json` (+ `series_plan`). Every skill reads and writes only these. A run lives in `runs/<run-id>/`
(layout: `skills/tcs-orchestrator/references/run-layout.md`).

## Install

```bash
# Claude Code: load the plugin (all 22 skills); add --plugin-dir to your usual claude command
git clone https://github.com/TamerElsherif/tamer-skills && claude --plugin-dir tamer-skills/training-content-studio
# or one skill only (its scripts still need the plugin root)
npx skills add TamerElsherif/tamer-skills --skill tcs-orchestrator --agent claude-code
# Python helpers
uv venv -p 3.12 .venv && uv pip install -p .venv/bin/python -r tools/requirements.txt
# Video kit (Node 18+, ffmpeg)
bash kit/setup.sh
```
Keys come from the environment or a file named in `TCS_ENV_FILE`: `OPENAI_API_KEY` (narration + transcription),
`PEXELS_API_KEY` (stock b-roll, optional). Set `OPENMONTAGE_ROOT` to render through OpenMontage.

## Quickstart

**3-module Arabic microlearning course from an SOP folder**
```
/tcs-autopilot "كورس قصير للموظفين الجدد عن إجراءات المشتريات" --sources ./sop/ --lang ar --targets video,lesson,scorm,jobaid
```
**90-second security micro-drama + branching + quiz**
```
/tcs-orchestrator "90-second micro-drama on CEO-fraud payment requests, with a branching choice and a quick quiz, for all staff"
```
Or say "make a course on …". The orchestrator asks only what's missing, then shows the skeleton for approval.

## Examples (`examples/`)

| Folder | What it proves |
|---|---|
| `golden-security-microdrama/` | Intake → approved skeleton → script → storyboard (cartoon + branching) → quiz → grounding → MP4 + HTML + SCORM |
| `golden-sop-deck-jobaid/` | SOP PDF → sources → narrated deck (EN + Egyptian Arabic) + PDF job aid + SCORM |
| `autopilot-runs/g1…g3` | The three golden autopilot decisions (procedure → screencast + job aid; Arabic phishing → micro-drama + branching; policy for managers → deck + job aid, pausing after the plan) |

## Quality

`QUALITY.md` is the release checklist. Run checks with:
```bash
.venv/bin/python tools/validate.py           # schemas, all contract files, SKILL.md limits, trigger routing (24 cases)
.venv/bin/python tools/qa.py runs/<run-id>   # per-lesson gate: storyboard lint + quiz + grounding → qa/<L>.qa.json
.venv/bin/python skills/tcs-autopilot/scripts/test_decisions.py   # golden autopilot decisions
bash skills/tcs-render-lesson/tests/run_all.sh                     # HTML/deck/SCORM/job-aid regression
```

## Layout

```
.claude-plugin/plugin.json   plugin manifest (plugin.json mirrors it)
skills/                      22 skills (SKILL.md + references/ templates/ scripts/ tests/)
schemas/                     JSON Schemas for every contract + enums.json
kit/                         Remotion template kit shared by both video renderers (32 templates, personas, RTL)
assets/                      MANIFEST.md, theme/layout/caption presets, voices, personas, placeholders
domains/                     _template/ and security-awareness/ (glossary, personas, scenarios, weights, compliance)
examples/                    golden examples + autopilot golden runs
portable/                    system prompt + attachments for a ChatGPT GPT / Gemini Gem
tools/                       validate.py, qa.py, trigger_cases.yaml, requirements.txt
QUALITY.md  _extraction.md
```

## Licensing notes

The plugin calls OpenMontage (AGPLv3) as an external tool and contains none of its source. Remotion needs a company licence
for organisations above 3 employees. Fonts are OFL. Stock b-roll comes from Pexels (licence recorded per clip).

## Changelog

- 2026-11-17 — 1.0.0: first release (22 skills, 7 schemas, render kit, 2 golden examples, 3 golden autopilot runs).
