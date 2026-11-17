# Intake — golden example 2 (narrated deck + job aid from an SOP)

Request (as typed): "Create a narrated deck and a one-page job aid from our expense SOP for new employees
(beginners), English with an Egyptian Arabic version of the deck."
Source given: `examples/_shared/sop/expenses.pdf` (fictional Northwind Co. SOP-FIN-007 v3.2, effective 2026-03-01).

Already specified in the request → not asked: topic (expense claims), source, audience (new employees, beginner),
languages (en-US primary + ar-EG deck), formats (narrated-deck + job-aid).

## One question round (orchestrator Step 1) — answers

| # | Question | ★ default offered | Answer |
|---|---|---|---|
| 1 | Objectives (proposed from the SOP) | O1 submit a compliant claim (apply) · O2 self-check a claim before submitting (apply) | ★ accepted |
| 2 | General knowledge allowed? | Only for titles/intros, labelled | ★ accepted — SOP is the only authority |
| 3 | Length / pace | 1 lesson ≈ 3 min narrated deck + 1-page job aid · 130 wpm (beginner) | "keep the deck 2–3 min" |
| 4 | Outputs + aspect | PPTX + HTML deck, narrated MP4 16:9, A4 PDF job aid, SCORM 1.2 | ★ accepted |
| 5 | Arabic variant | ar-EG (Egyptian colloquial narration, RTL, Western digits) for the deck lesson | ★ accepted |

Assumed (stated at the gate): domain pack `_template` (no domain-specific pack), theme `neutral`, voice OpenAI
`gpt-4o-mini-tts` marin, no logo, currency shown as US$ exactly as in the SOP.
