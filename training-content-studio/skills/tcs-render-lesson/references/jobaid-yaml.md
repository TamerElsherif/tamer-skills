# jobaid.yaml (optional dedicated input for scripts/jobaid.py)

Schema: `templates/jobaid.schema.json`. Usually you don't need it — a storyboard (preferably `<L>-jobaid.storyboard.json`
from tcs-format-job-aid) converts automatically. Use jobaid.yaml for a one-off card that is not a lesson.

```yaml
schema: tcs-jobaid/1.0
title: Phishing Red-Flag Card          # header
kicker: Job aid · keep at your desk    # optional
subtitle: ...                          # optional
language: en-US                        # en-US | en-GB | ar-EG | ar-MSA (ar → RTL)
paper: A4                              # A4 | Letter (CLI --paper wins)
pages: 1                               # page budget 1 | 2; text auto-shrinks to fit (min scale 0.66)
footer: Supports ISO 27001 A.6.3 awareness evidence.
theme: {preset: neutral}               # same as storyboard.theme
blocks:                                # props are identical to the storyboard template props
  - {type: checklist, title: Pause if you see, items: [...]}
  - {type: steps, title: Clicked already?, danger: true, steps: [{label: Disconnect}, {label: Call the service desk}]}
  - {type: do_dont, title: Then, dont: [...], do: [...]}
  - {type: table, title: Who to contact, columns: [What, Where], rows: [[..., ...]]}
  - {type: bullets|icon_grid, title: ..., items: [{text|label: ..., sub: ..., icon: ...}]}
  - {type: definition, term: ..., def: ..., note: ...}
  - {type: comparison, left: {head, items}, right: {head, items}}
  - {type: note, title: ..., text: ..., items: [...]}
```

## Derivation from a storyboard
| Scene template | Job-aid part |
|---|---|
| title | header (kicker / title / sub) |
| checklist, steps, do_dont, table, bullets, icon_grid, definition, comparison, statement | blocks, in scene order |
| outro | note block (line + tips); `evidence_line` → footer (else `theme.evidence_line`) |
| everything else | ignored (mock-ups, quizzes, cartoons…) |

`scenes[].notes` (author notes) and narration are never printed. Keep ≤ 6–7 items per block; a 1-page A4 holds ~6 blocks.
Output: `<name>.pdf`, `<name>.html` (editable/printable), `<name>.png` (page-1 preview for QA).
