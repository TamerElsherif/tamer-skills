# Run folder layout — `runs/<run-id>/` (shared by tcs-orchestrator and tcs-autopilot)

`runs/` lives at the working directory root (gitignored in the plugin repo). Run id: `YYYYMMDD-HHMM-<slug>`
(`skills/tcs-autopilot/scripts/run_state.py new-id "<request>"`). Everything for one course lives in one folder, so a
run can be resumed, re-rendered, zipped or deleted as a unit.

```
runs/<run-id>/
  state.json                     # stage + lesson status, cost (schemas/run_state.schema.json) — run_state.py
  sources/                       # copies or links of user files; downloaded transcripts/frames (tcs-source-ingest)
  sources.yaml                   # citable sources + facts (schemas/sources.schema.json)
  decisions.json                 # every decision: value, signal, confidence, source, alternative (schemas/decisions.schema.json)
  decisions.md                   # human table (decide.py / report.py)
  curriculum.draft.yaml          # autopilot decision engine's skeleton (Stage 2)
  curriculum.yaml                # approved / auto-approved plan (schemas/curriculum.schema.json)
  lessons/
    M1L1/
      M1L1.storyboard.json       # primary-language storyboard (schemas/storyboard.schema.json)
      M1L1.quiz.json             # assessment (schemas/quiz.schema.json)
      M1L1.ar-EG.storyboard.json # localized variants: <L>.<lang>.storyboard.json / <L>.<lang>.quiz.json
      M1L1.grounding_report.json # claim verification (schemas/grounding_report.schema.json)
      notes.md                   # optional: format playbook notes, open questions
  qa/
    M1L1.qa.json                 # {result: pass|fail|needs-human, attempts, checks:[{name, ok, detail}]}
  renders/
    M1L1/video/…mp4              # one folder per lesson per target
    M1L1/video-vertical/…mp4
    M1L1/jobaid/…pdf
    M1L1/video/RENDER_PENDING.md # when the renderer is unavailable: spec + exact command
    course/scorm/<course-id>-scorm12.zip
    course/deck/<course-id>.pptx
  REPORT.md                      # final report (report.py)
```

## Conventions

- Lesson ids `M<n>L<n>` everywhere (folder, file prefix, state.json `lessons` key, storyboard `lesson_id`).
- Language codes in file names: `en-US`, `en-GB`, `ar-EG`, `ar-MSA`. The un-suffixed storyboard is `course.languages.primary`.
- Stages write only their own files; re-running a stage overwrites its outputs (idempotent) and nothing else.
- Paths inside JSON/YAML are relative to the run folder.
- Never write secrets or absolute user paths into run files (source `uri` may hold the user-given path).

## state.json stages

`ingest → decide → plan → produce → qa → render → report`, each `pending|running|done|failed|skipped|needs-human`.
Orchestrator runs use the same stages (`decide` = intake answers recorded as decisions). Resume = first stage not
`done/skipped`; `plan: needs-human` = waiting at the approval gate.
