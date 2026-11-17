# Portable version (ChatGPT custom GPT / Gemini Gem)

Runs the planning half of Training Content Studio — intake → approval gate → generate (and autopilot) — in a chat
assistant. It produces `curriculum.yaml`, `sources.yaml`, `<lesson>.storyboard.json`, `<lesson>.quiz.json` and
`decisions.json` as downloadable files. It **cannot render**: bring the files to Claude Code with this plugin to render
video, decks, HTML lessons, SCORM and job aids.

## 1. Build the attachments (keeps them in sync with the plugin)
```
.venv/bin/python portable/build_portable.py          # checks + regenerates portable/attachments/
.venv/bin/python portable/build_portable.py --check  # checks only
```
Never edit `attachments/` by hand; edit the source files (schemas, skills, domains, assets, QUALITY.md) and rebuild.

## 2. Files to attach
| File | Why | GPT | Gem |
|---|---|---|---|
| `SCHEMAS.md` | all schemas + enums (the contract) | ✓ | ✓ |
| `FORMATS.md` | 10 format skills, playbooks, templates | ✓ | ✓ |
| `EXAMPLES.md` | valid storyboard per format | ✓ | ✓ |
| `QUALITY.md` | release checklist | ✓ | ✓ |
| `ASSETS.md` | themes, layouts, captions, voices, personas | ✓ | ✓ |
| `DOMAIN_<pack>.md` | domain pack(s) you need (e.g. security-awareness) | ✓ | ✓ |
| `PIPELINE_SKILLS.md` | stage instructions (curriculum, ingest, script, storyboard, assessment, grounding, localize) | ✓ | ✓ |
| `schemas/*.json` | raw schemas so code execution can run `jsonschema` | ✓ (with Code Interpreter) | optional |

Bundles are ≤ 10 files so they also fit assistants with low knowledge-file limits; check your platform's current
limits and file-size caps.

## 3. ChatGPT custom GPT
1. Explore GPTs → Create → Configure.
2. Name "Training Content Studio"; description "Plans grounded, bilingual training and writes storyboard/quiz files."
3. Instructions: paste `SYSTEM_PROMPT.md` (≈ 5 k characters, under the instructions limit).
4. Knowledge: upload the files above. Capabilities: enable **Code Interpreter & Data Analysis** (validation + file
   downloads); web browsing optional (off for confidential sources).
5. Conversation starters: "Turn this policy PDF into a 3-lesson course (EN + Egyptian Arabic)", "Autopilot: 5-minute
   phishing cartoon for all staff", "Remake this 4-minute video as an explainer + job aid".

## 4. Gemini Gem
1. Gems manager → New Gem → paste `SYSTEM_PROMPT.md` into Instructions.
2. Add knowledge files (bundled `.md` files; skip `schemas/*.json` if you hit the limit — `SCHEMAS.md` covers them).
3. Gems may not offer file downloads: ask it to output each file in a single fenced code block named with the
   filename, then save them locally.

## 5. Handoff to rendering
Put the files in `runs/<run-id>/` of a project that has this plugin, then in Claude Code run `/tcs-orchestrator`
(it validates, resumes at the produce/render stage, and runs QA) or `/tcs-render-lesson` for one lesson.

## Limitations
- No rendering, TTS, B-roll fetch or SCORM packaging in chat.
- Validation depends on code execution; without it the assistant self-checks by reading the schema.
- Long sources may exceed the chat context; ingest large files in Claude Code (`/tcs-source-ingest`) and paste
  `sources.yaml` into the chat instead.
- Keep confidential documents out of assistants whose data policy you have not approved.
