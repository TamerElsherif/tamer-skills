# Decisions — golden-sop-deck-jobaid

Request: Create a narrated deck and a one-page job aid from our expense SOP for new employees (beginners), English with an Egyptian Arabic version of the deck

| decision | value | signal | confidence | source | alternative rejected |
|---|---|---|---|---|---|
| language | {"primary": "en-US", "secondary": ["ar-EG"], "subtitles": ["ar-EG"]} | --lang both; request script Latin (0% Arabic letters) | 1.00 | flag | single language |
| audience | {"id": "new-hires", "roles": ["learner"], "segment": "staff"} | wording 'new employees' | 0.80 | request | general staff |
| level | beginner | wording 'beginners' | 0.95 | request | intermediate |
| other (objective_type) | procedure | procedure: 'SOP', 'sources:procedurex1', 'sources:stepx6' | 0.71 | sources | policy=0.967742, behavior=0.290323, concept=0.580645 |
| domain | _template | --domain _template | 1.00 | flag | - |
| domain_pack | _template | --domain flag | 1.00 | flag | _template |
| objectives | O1: Submit an expense claim in the Northwind Expenses app that meets the receipt, deadline and approval rules (apply); O2: Check a claim against the pre-submit checklist and avoid the three warning-level mistakes (apply) | proposed from SOP §4-§6 at intake; user accepted the 2 proposed objectives | 1.00 | user | decide.py draft (3 objectives with mis-parsed topic) |
| formats | ["narrated-deck", "job-aid"] | user: narrated deck for the procedure, separate one-page job aid | 1.00 | user | ['explainer', 'job-aid'] (rule) |
| other (assessment) | {"assessment": "scenario", "evidence": false, "broll": false} | assessment for procedure | 0.80 | rule | no assessment |
| blend | {"M1L1": ["narrated-deck"], "M1L2": ["job-aid"]} | user: deck lesson + separate job-aid lesson | 1.00 | user | narrated-deck + job-aid blend in every lesson |
| length | {"lessons": 2, "minutes_per_lesson": {"M1L1": 3, "M1L2": 2}, "total_minutes": 5} | user: 'keep the deck 2-3 min'; job aid = 1 A4 page (~2 min read) | 1.00 | user | 3 x 5 min lessons |
| wpm | 130 | beginner 130 wpm | 0.80 | rule | 145 wpm |
| verbosity | standard | new-hires / beginner | 0.70 | rule | detailed |
| targets | ["video", "deck", "lesson", "scorm", "jobaid"] | --targets video,deck,lesson,scorm,jobaid | 1.00 | flag | derived from formats |
| aspect | ["16:9"] | --aspect 16:9 | 1.00 | flag | 16:9 primary |
| renderer | remotion | --renderer | 1.00 | flag | openmontage |
| other (localization) | {"M1L1": ["ar-EG"]} | user: Egyptian Arabic version of the deck | 1.00 | user | ar-EG subtitles only |
| other (grounding) | SOP only; general knowledge only for titles/intros, labelled | intake Q2 | 1.00 | user | general knowledge allowed |
| other (approval) | {"status": "approved", "edits": []} | approval gate shown (approved_skeleton.md); user pre-authorised | 1.00 | user | edit and re-show gate |

Estimate: ~117,000 tokens, ~$1.74 (TTS 30.0 min, 6 images). Scope: full. Pause after: plan.

Warnings:
- decide.py mis-parsed the topic from the request wording (format words kept); objectives replaced at intake
