# Beat structures per format

The authoritative beat list lives in the format skill playbook: `skills/tcs-format-<format>/references/playbook.md` (e.g. `tcs-format-explainer`,
`tcs-format-cartoon`, `tcs-format-branching`). Load it first. Use the fallback skeletons
below only if the format skill is unavailable. Beat names go in the scene heading (`## s04_example | example | O2`).

| Format | Fallback beats (in order) | Script family template |
|---|---|---|
| explainer | title · hook · why · what (definition) · how/rules · steps · example · mistakes/red-flags · check · recap · outro | `templates/script-explainer.md` |
| doodle | title · hook · metaphor · build-up (one doodle per cue) · example · mistakes · recap · outro | explainer |
| narrated-deck | title · agenda · one slide per key point (≤ 6 bullets) · example · check · summary | explainer |
| mindmap | root · branch per concept (focus each) · connections · recap (whole map) | explainer |
| screencast-sim | goal · setup · one UI action per cue (steps) · common errors · recap | explainer |
| job-aid | when to use · steps · watch-outs · who to contact (short, scannable; narration optional) | explainer |
| series | per episode (60–90 s): hook · one tip/rule · mini example · action · tease next | explainer |
| cartoon | cold open (story) · narrator tie-in · rule · mistake (rookie) · consequence · replay done right · check · recap | `templates/script-story.md` |
| comic | setup panel · complication · mistake · consequence · lesson panel (≤ 4 panels per scene) · recap | story |
| branching | setup · decision · consequence per choice (good/bad/neutral) · debrief · retry/recap | `templates/script-branching.md` |

## Beat → typical template (hint for tcs-storyboard)
| Beat | Template hints |
|---|---|
| title / outro | `title`, `outro` |
| hook | `broll`, `cartoon`, `stat`, `email_mock`/`chat_mock` (realistic trigger) |
| why / stat | `stat`, `statement`, `broll_panel` |
| what | `definition`, `icon_grid` |
| rules | `bullets`, `do_dont`, `checklist` |
| steps / procedure | `steps`, `process_flow`, `screencast` |
| example / story | `cartoon`, `comic`, `email_mock`, `chat_mock`, `browser_mock` |
| mistakes / red flags | `do_dont`, mock-up with `callouts` |
| check | `quiz` (item from quiz.json), `flashcard` |
| recap | `checklist`, `mindmap` |
| decision | `decision` |

## Universal rules
- One idea per scene; 5–35 s; alternate visual modes (b-roll / board / mock-up / story) every 8–20 s in explainers.
- Each objective of the lesson appears in ≥ 1 scene heading and is practised in the check beat.
- Recap = the 3–5 behaviours to remember; outro = one action line (who to contact, where the policy lives).
