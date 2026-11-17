# Intake — golden example (simulated answers)

> **EXAMPLE.** This file shows what the tcs-orchestrator one-round intake looks like for this request. The answers below
> stand in for a real user's replies; nothing here came from a real person or organisation.

**Request:** "90-second security micro-drama + branching scenario + knowledge check on BEC / CEO-fraud payment requests,
English (en-US), 16:9, for all staff incl. finance."

## Parsed from the request (not asked)
| Parameter | Value |
|---|---|
| topic | BEC / CEO-fraud payment requests |
| language | en-US, no subtitles |
| length | one ~90 s micro-lesson |
| formats | cartoon (micro-drama) + branching |
| assessment | knowledge check |
| aspect | 16:9 |
| audience | all staff, including finance |
| domain pack | security-awareness |

## Orchestrator message (one round)

> **Proposed objectives** — after this lesson, staff can: 1) Spot the warning signs of a fake payment or bank-detail
> change request (analyze) 2) Decide the safe response: verify by calling back a known number and keep two-person
> approval (evaluate) 3) Report a suspicious payment request to IT Security (apply).
>
> 1. Sources: a) ★ your payment policy (paste path) b) general knowledge (labelled) c) both
> 2. Outputs: a) ★ MP4 + interactive HTML lesson + SCORM 1.2 b) MP4 only c) MP4 + 9:16 nudge cut

## Answers (simulated)
| # | Answer | Recorded as |
|---|---|---|
| objectives | "Looks right, keep all three." | decision `objectives`, source user |
| 1 Sources | "1c — use `sources/northwind-payment-verification-policy.md` (FIN-SEC-07); general knowledge OK for the red-flag basics, labelled." | `sources.yaml`, `general_knowledge_allowed: true` |
| 2 Outputs | "2a — MP4 16:9, HTML lesson and SCORM for the LMS." | decision `targets`, source user |

Assumed (shown at the gate, not asked): level beginner-intermediate, pace 140 wpm, standard verbosity,
renderer = standalone Remotion kit (tcs-render-remotion), persona cast rookie (Sam) + exec impersonated by vex + mentor.
