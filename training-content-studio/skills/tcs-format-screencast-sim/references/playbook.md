# Screencast + simulation playbook

## When to use
- "How do I do X in system Y": portals, forms, settings, reporting a phishing email, enabling MFA, filing a claim.
- Learners must perform, not just recognise. Pairs naturally with a job-aid.
- Avoid for judgement calls (branching) or concepts (explainer).

## Duration
| Variant | Tasks | Length |
|---|---|---|
| Micro how-to | 1 task, ≤ 5 steps | 45–90 s |
| Standard | 2–3 tasks | 3–6 min incl. practice |
| System course | 4–8 tasks | split into lessons (one task each) |

## Beat structure (watch → try → do)
| # | Beat | Time | Template / sim.mode |
|---|---|---|---|
| 1 | Title + goal | 5 s | `title` |
| 2 | Overview of steps | 10–15 s | `steps` |
| 3 | Watch (demo) | 15–40 s | `screencast` · `demo` |
| 4 | Try (guided) | 20–60 s | `screencast` · `guided` (highlights + hints) |
| 5 | Do (practice) | 20–60 s | `screencast` · `practice` (no highlights, hints on error) |
| 6 | Errors to avoid | 10–15 s | `popup` / `do_dont` |
| 7 | Check | 10–15 s | `quiz` or `screencast` · `assess` |
| 8 | Recap | 8–12 s | `checklist` |

## Action vocabulary
| do | Effect | Narration cue |
|---|---|---|
| `move` | pointer glides to target | "go to…" |
| `click` | pointer + ripple | "click…" |
| `type` | text types into field (`value`) | "type…" |
| `select` | dropdown opens, `value` picked | "choose…" |
| `highlight` | field glows | "notice…" |
| `callout` | label + arrow to field | "don't forget…" |
| `toast` | system message (`label`) | "you'll see…" |
| `zoom` | camera eases to field | small UI |

## Sim spec modes
| mode | Interactive targets | Video targets |
|---|---|---|
| demo | autoplay | autoplay |
| guided | learner clicks highlighted target | overlay shows pointer doing it |
| practice | learner does task; hints on wrong input | narrated walkthrough |
| assess | scored, no hints | skipped or shown as answer replay |

## Do / Don't
| Do | Don't |
|---|---|
| Fictional data ("23.50 taxi") | Real names, emails, IDs |
| One task per scene | 15-step marathons |
| Explain *why* on tricky steps | Narrate every pixel |
| Pair with a job-aid | Expect recall of long procedures from video alone |

## Worked example (`templates/example.storyboard.json`)
"File an Expense Claim" (fictional Northwind Expenses): demo with 6 actions (date → category → amount → receipt →
submit → toast); practice with `expect` [Taxi, 23.50, receipt, submit], hint on receipt, 3 attempts; recap checklist.
