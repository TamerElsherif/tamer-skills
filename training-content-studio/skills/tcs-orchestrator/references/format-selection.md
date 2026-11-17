# Format selection (shared by tcs-orchestrator and tcs-autopilot)

Machine version with tunable keywords: `skills/tcs-autopilot/decision-rules.yaml` (`formats_by_type`,
`segment_overrides`, `explicit_formats`, `format_targets`). Keep the two in sync.

## 1. Objective type → default formats

| Objective type (signal words) | Primary | Secondary | Assessment | Notes |
|---|---|---|---|---|
| **concept** (explain, what is, overview, basics) | explainer | — | knowledge-check | + B-roll scenes if the subject is visual (equipment, site, product) |
| **structure** (architecture, framework, taxonomy, how parts fit) | mindmap | — | knowledge-check | progressive reveal |
| **procedure — software** (how to, submit, configure + a system/app name) | screencast-sim | job-aid | scenario (try-it) | watch → do → job aid |
| **procedure — physical/office** (how to, steps, process) | explainer (or doodle) | job-aid | scenario | |
| **behavior / judgment** (awareness, spot, handle, respond, phishing, conversations) | cartoon (micro-drama) | branching | knowledge-check | consequences shown, not told |
| **policy / compliance** (policy, rules, regulation, retention, mandatory) | cartoon (micro-drama) | — | post-test (pass 80 %) | + evidence: SCORM completion + attestation |
| **recall-heavy** (terms, specs, catalogue, exam) | series (flashcards + nudges) | — | flashcards | spaced repetition |
| **multi-week adoption** (roll-out, habit, change, campaign) | series | — | knowledge-check | nudge calendar |

## 2. Audience overrides

| Audience | Change |
|---|---|
| executives / managers / board | **narrated-deck** primary (concise, decision-focused); keep job-aid (procedure, policy) or branching (judgment) as secondary |
| new hires / beginners | keep defaults; slower pace (130 wpm), more examples; add a job-aid for any procedure |
| technical (engineers) on a technical topic | explainer/mindmap with code_mock/table scenes; skip cartoon unless behaviour is the goal |
| frontline / low-literacy / multilingual | cartoon or doodle (visual-first), short lines, subtitles always |
| MENA / Arabic | same formats; Arabic primary + English subtitles; RTL kit; Egyptian dialect only if requested or Egyptian context |

## 3. Effort (production cost and time)

| Effort | Formats | Pick when |
|---|---|---|
| low | job-aid, narrated-deck, mindmap | tight deadline/budget, executives, reference material |
| medium | explainer, doodle, screencast-sim, comic | most courses |
| high | cartoon, branching, series | behaviour change, high stakes, campaigns |

User says "quick / cheap / this week" → shift one effort level down (cartoon → explainer, branching → knowledge-check
only, series → single lesson + flashcards). Budget overrun in autopilot does the same automatically.

## 4. Blend rules

- Max **2 formats per lesson** (primary teaches, secondary reinforces or practises) and **3 distinct per course**.
- Good pairs: screencast-sim + job-aid · cartoon + branching · explainer + job-aid · narrated-deck + job-aid ·
  mindmap + flashcards (series) · cartoon + comic (same cast, print take-away).
- Avoid: two video formats in one lesson (explainer + cartoon) — pick one; branching without a story or scenario to branch from.
- Wording in the request pins a format ("as a deck", "cartoon", "whiteboard", "checklist"); explicit always wins.

## 5. Format → output targets

| Format | Targets | Notes |
|---|---|---|
| explainer, doodle, cartoon, screencast-sim, mindmap, series | video (16:9 MP4) + video-vertical (9:16 nudge cut) | |
| narrated-deck | deck (PPTX) + video (narrated MP4) | |
| branching, comic | lesson (interactive HTML) | branching also linear "best path" video if video target chosen |
| job-aid | jobaid (PDF / HTML one-pager) | |
| any course with ≥ 2 lessons, or compliance evidence | + scorm (SCORM 1.2) | |

## 6. One-line rationales (use in the intake recommendation and `lessons[].rationale`)

- "Procedure in {system} → screencast-sim so they see each click, plus a job aid for the desk."
- "Judgment call → cartoon micro-drama shows the cost of the wrong choice; branching lets them try it."
- "Managers need the decision, not the detail → narrated deck with a one-page job aid."
- "Lots of terms to remember → flashcards and spaced nudges beat one long video."
- "Abstract structure → mindmap reveals the parts one at a time."
