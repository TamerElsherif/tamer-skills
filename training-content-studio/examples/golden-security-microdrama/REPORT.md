# Run report — golden-security-microdrama

**Request:** 90-second security micro-drama + branching scenario + knowledge check on BEC / CEO-fraud payment requests, English (en-US), 16:9, for all staff incl. finance

**Stages:** ingest done · decide done · plan done · produce done · qa done · render done · report done

## Produced

- `sources.yaml`
- `decisions.md`
- `curriculum.yaml`
- `lessons/M1L1/M1L1.grounding_report.json`
- `lessons/M1L1/M1L1.grounding_report.md`
- `lessons/M1L1/M1L1.preview.md`
- `lessons/M1L1/M1L1.quiz.json`
- `lessons/M1L1/M1L1.script.md`
- `lessons/M1L1/M1L1.storyboard.json`
- `lessons/M1L1/M1L1.timing.json`
- `lessons/M1L1/M1L1.verdicts.yaml`
- `renders/M1L1/lesson/index.html`
- `renders/M1L1/lesson/lesson.json`
- `renders/M1L1/video/M1L1_16x9.grid.jpg`
- `renders/M1L1/video/M1L1_16x9.json`
- `renders/M1L1/video/M1L1_16x9.mp4`
- `renders/course/scorm/northwind-bec-microdrama-scorm12.zip`

## Decisions

| decision | value | confidence | source |
|---|---|---|---|
| language | {"primary": "en-US", "subtitles": []} | 1.00 | flag |
| audience | {"id": "all-staff", "roles": ["learner"], "segment": "staff", "notes": "all staff incl. fi | 1.00 | request |
| level | beginner-intermediate | 0.70 | rule |
| other (objective_type) | behavior | 0.81 | sources |
| domain | security-awareness | 1.00 | flag |
| domain_pack | security-awareness | 1.00 | flag |
| objectives | 3 objectives (see decisions.md) | 1.00 | user |
| formats | ["cartoon", "branching"] | 0.95 | request |
| other (assessment) | {"assessment": "knowledge-check", "evidence": false, "broll": false} | 0.80 | rule |
| blend | ["cartoon", "branching"] | 0.80 | rule |
| length | {"lessons": 1, "minutes_per_lesson": 1.5, "total_minutes": 1.5} | 1.00 | request |
| wpm | 140 | 0.80 | rule |
| verbosity | standard | 0.70 | rule |
| targets | ["video", "lesson", "scorm"] | 1.00 | user |
| aspect | ["16:9"] | 1.00 | flag |
| renderer | remotion | 0.80 | default |
| other (sources) | {"files": ["sources/northwind-payment-verification-policy.md"], "general_knowledge_allowed | 1.00 | user |
| other (cast) | ["rookie", "exec", "vex", "mentor"] | 0.80 | default |
| other (approval) | {"status": "approved", "edits": []} | 1.00 | user |

Full signals and rejected alternatives: `decisions.md`.

## Plan

Approval: **approved**

| lesson | title | objectives | formats | min | status |
|---|---|---|---|---|---|
| M1L1 | The Friday Wire | O1, O2, O3 | cartoon + branching | 1.5 | done |

## QA results

| lesson | supported | general knowledge | unsupported | conflicting | QA | attempts |
|---|---|---|---|---|---|---|
| M1L1 | 21/24 | 3 | 0 | 0 | pass | 0 |

## General-knowledge claims (not from your sources — verify)

- M1L1/s02_request: Scenario: Sam in Finance receives an urgent, secret payment request that appears to come from the CEO (fictional example).
- M1L1/s03_email: Scenario: the fake email asks for a USD 48,500 payment to a fictional supplier (fictional example).
- M1L1/s04_vex: Attackers use authority and time pressure to rush people past checks.

## Cost

- Estimate: ~37,000 tokens, ~$0.36 (TTS 1.5 min, 0 images)
- Actual so far: 0 tokens, $0.0

## Re-run

- Whole run from the last unfinished stage: `/tcs-autopilot --resume golden-security-microdrama`
- Fresh run, same inputs: `/tcs-autopilot '90-second security micro-drama + branching scenario + knowledge check on BEC / CEO-fraud payment requests, English (en-US), 16:9, for all staff incl. finance' --lang en --targets video,lesson,scorm --aspect 16:9 --review none --domain security-awareness --renderer remotion`
- M1L1: `/tcs-autopilot --resume golden-security-microdrama --lesson M1L1` · other format: `/tcs-autopilot --resume golden-security-microdrama --lesson M1L1 --override formats=explainer` · other language: `/tcs-autopilot --resume golden-security-microdrama --lesson M1L1 --override lang=ar`
