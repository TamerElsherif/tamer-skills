# Run report — golden-sop-deck-jobaid

**Request:** Create a narrated deck and a one-page job aid from our expense SOP for new employees (beginners), English with an Egyptian Arabic version of the deck

**Stages:** ingest done · decide done · plan done · produce done · qa done · render done · report done

> decide.py mis-parsed the topic from the request wording (format words kept); objectives replaced at intake

## Produced

- `sources.yaml`
- `decisions.md`
- `curriculum.yaml`
- `lessons/M1L1/M1L1.ar-EG.grounding_report.json`
- `lessons/M1L1/M1L1.ar-EG.grounding_report.md`
- `lessons/M1L1/M1L1.ar-EG.quiz.json`
- `lessons/M1L1/M1L1.ar-EG.srt`
- `lessons/M1L1/M1L1.ar-EG.storyboard.json`
- `lessons/M1L1/M1L1.ar-EG.translate.yaml`
- `lessons/M1L1/M1L1.ar-EG.vtt`
- `lessons/M1L1/M1L1.en-US.srt`
- `lessons/M1L1/M1L1.en-US.vtt`
- `lessons/M1L1/M1L1.grounding_report.json`
- `lessons/M1L1/M1L1.grounding_report.md`
- `lessons/M1L1/M1L1.preview.md`
- `lessons/M1L1/M1L1.quiz.json`
- `lessons/M1L1/M1L1.script.md`
- `lessons/M1L1/M1L1.storyboard.json`
- `lessons/M1L1/M1L1.timing.json`
- `lessons/M1L2/M1L2.grounding_report.json`
- `lessons/M1L2/M1L2.grounding_report.md`
- `lessons/M1L2/M1L2.quiz.json`
- `lessons/M1L2/M1L2.storyboard.json`
- `renders/M1L1/deck/M1L1.pptx`
- `renders/M1L1/deck/ar-EG/M1L1.pptx`
- `renders/M1L1/deck/ar-EG/deck.html`
- `renders/M1L1/deck/deck.html`
- `renders/M1L1/lesson/index.html`
- `renders/M1L1/lesson/lesson.json`
- `renders/M1L1/video/M1L1_16x9.grid.jpg`
- `renders/M1L1/video/M1L1_16x9.json`
- `renders/M1L1/video/M1L1_16x9.mp4`
- `renders/M1L2/jobaid/M1L2.html`
- `renders/M1L2/jobaid/M1L2.pdf`
- `renders/M1L2/jobaid/M1L2.png`
- `renders/M1L2/lesson/index.html`
- `renders/M1L2/lesson/lesson.json`
- `renders/course/scorm/northwind-expenses-scorm12.zip`

## Decisions

| decision | value | confidence | source |
|---|---|---|---|
| language | {"primary": "en-US", "secondary": ["ar-EG"], "subtitles": ["ar-EG"]} | 1.00 | flag |
| audience | {"id": "new-hires", "roles": ["learner"], "segment": "staff"} | 0.80 | request |
| level | beginner | 0.95 | request |
| other (objective_type) | procedure | 0.71 | sources |
| domain | _template | 1.00 | flag |
| domain_pack | _template | 1.00 | flag |
| objectives | 2 objectives (see decisions.md) | 1.00 | user |
| formats | ["narrated-deck", "job-aid"] | 1.00 | user |
| other (assessment) | {"assessment": "scenario", "evidence": false, "broll": false} | 0.80 | rule |
| blend | {"M1L1": ["narrated-deck"], "M1L2": ["job-aid"]} | 1.00 | user |
| length | {"lessons": 2, "minutes_per_lesson": {"M1L1": 3, "M1L2": 2}, "total_minutes": 5} | 1.00 | user |
| wpm | 130 | 0.80 | rule |
| verbosity | standard | 0.70 | rule |
| targets | ["video", "deck", "lesson", "scorm", "jobaid"] | 1.00 | flag |
| aspect | ["16:9"] | 1.00 | flag |
| renderer | remotion | 1.00 | flag |
| other (localization) | {"M1L1": ["ar-EG"]} | 1.00 | user |
| other (grounding) | SOP only; general knowledge only for titles/intros, labelled | 1.00 | user |
| other (approval) | {"status": "approved", "edits": []} | 1.00 | user |

Full signals and rejected alternatives: `decisions.md`.

## Plan

Approval: **approved**

| lesson | title | objectives | formats | min | status |
|---|---|---|---|---|---|
| M1L1 | Submitting an expense claim | O1 | narrated-deck | 3 | rendered |
| M1L2 | Expense claim checklist | O2 | job-aid | 2 | rendered |

## QA results

| lesson | supported | general knowledge | unsupported | conflicting | QA | attempts |
|---|---|---|---|---|---|---|
| M1L1 | 29/31 | 2 | 0 | 0 | pass | 0 |
| M1L2 | 24/24 | 0 | 0 | 0 | pass | 0 |

## General-knowledge claims (not from your sources — verify)

- M1L1/s01_title: This lesson covers submitting an expense claim at Northwind Co.
- M1L1/s07_check: Scenario: a $3,200 conference trip claim (fictional example).

## Cost

- Estimate: ~117,000 tokens, ~$1.74 (TTS 30.0 min, 6 images)
- Actual so far: 0 tokens, $0.0

## Re-run

- Whole run from the last unfinished stage: `/tcs-autopilot --resume golden-sop-deck-jobaid`
- Fresh run, same inputs: `/tcs-autopilot 'Create a narrated deck and a one-page job aid from our expense SOP for new employees (beginners), English with an Egyptian Arabic version of the deck' --sources examples/_shared/sop/expenses.pdf --lang both --targets video,deck,lesson,scorm,jobaid --aspect 16:9 --review skeleton --domain _template --renderer remotion`
- M1L1: `/tcs-autopilot --resume golden-sop-deck-jobaid --lesson M1L1` · other format: `/tcs-autopilot --resume golden-sop-deck-jobaid --lesson M1L1 --override formats=explainer` · other language: `/tcs-autopilot --resume golden-sop-deck-jobaid --lesson M1L1 --override lang=ar`
- M1L2: `/tcs-autopilot --resume golden-sop-deck-jobaid --lesson M1L2` · other format: `/tcs-autopilot --resume golden-sop-deck-jobaid --lesson M1L2 --override formats=explainer` · other language: `/tcs-autopilot --resume golden-sop-deck-jobaid --lesson M1L2 --override lang=ar`
