# Branching scenario playbook

## When to use
- Judgement under pressure: verify-or-comply calls, payment-change requests, data-sharing dilemmas, manager conversations.
- Objectives at Bloom apply/analyze/evaluate; audiences who "know the rule" but fail in the moment.
- Avoid for pure knowledge (quiz) or exact UI procedure (screencast-sim).

## Duration / size
| Variant | Decisions | Nodes | Path length |
|---|---|---|---|
| Micro scenario | 1 | 3 | 45–90 s |
| Standard | 2–3 | 5–8 | 2–4 min per path |
| Rich | 3–4 | 8–12 | 4–8 min (split by chapter) |

## Graph patterns
| Pattern | Shape | Use |
|---|---|---|
| Gauntlet | linear spine; wrong choices → short bad outcome → retry | beginners, compliance |
| Funnel | choices diverge, rejoin at next decision | standard; keeps production small |
| Tree | full divergence | rich scenarios only (expensive) |
Default: **funnel with recoverable mistakes**.

## Beat structure (standard funnel)
| # | Node | Scenes | Template |
|---|---|---|---|
| 1 | `n_intro` | setup (15–25 s) + decision 1 | `cartoon`/mock-up + `decision` |
| 2 | wrong-1 | consequence (8–15 s) | `statement`/`cartoon`, outcome `bad`, feedback |
| 3 | right-1 | escalation (10–20 s) + decision 2 | `cartoon` + `decision` |
| 4 | wrong-2 | partial consequence | outcome `bad`, score 2 |
| 5 | right-2 | resolution + rule | `cartoon` + `steps`, outcome `good`, score 10 |
| 6 | debrief | recap of the red flags | `checklist` (shared by all endings, optional) |

## Writing choices
- All choices start with a verb; similar length; one best, one tempting, optionally one "half-right".
- The tempting choice mirrors the attacker's lever (urgency, authority, kindness).
- Feedback formula: *what happened* + *the red flag you missed* + *what to do instead*.

## Do / Don't
| Do | Don't |
|---|---|
| Recoverable mistakes | Dead ends with no learning |
| Same consequences length for every branch | Long bad branches (rewarding failure with content) |
| Score + feedback per node | Silent outcomes |
| Narrate the choices in the linear video | Rely on clickable UI in video |

## Worked example (`templates/example.storyboard.json`)
"The Urgent Reset Call" (help-desk SE, formats `branching`+`cartoon`): `n_intro` (call + decision) →
`n_reset` (bad, 0) | `n_verify` (callback, second decision) → `n_cave` (bad, 2) | `n_good` (good, 10).
