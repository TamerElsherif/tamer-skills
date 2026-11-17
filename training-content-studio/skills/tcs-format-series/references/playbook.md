# Series + gamification + nudges playbook

## When to use
- Annual/ongoing programmes (security awareness, compliance refreshers, onboarding over weeks).
- Behaviour change that decays without reinforcement; audiences with low attention budgets.
- Avoid for one-off must-complete-today content (single lesson) or long certification courses (narrated-deck + SCORM).

## Season sizes
| Variant | Episodes | Episode length | Nudges | Cadence |
|---|---|---|---|---|
| Sprint | 4 | 2–3 min | 2 per episode | weekly |
| Season | 6–8 | 2–4 min | 2 per episode | weekly / fortnightly |
| Always-on | 12 | 2–3 min | 1–2 per episode | monthly |
Nudges: 30–60 s, 9:16, one behaviour.

## Episode beat structure (any base format)
| # | Beat | Time |
|---|---|---|
| 1 | Cold open with the recurring cast | 10–20 s |
| 2 | Lesson body (base format playbook) | 1.5–3 min |
| 3 | Quick check (points) | 10–15 s |
| 4 | Recap + teaser for next episode | 10–15 s |

## Nudge beat structure (30–60 s)
| # | Beat | Time | Template |
|---|---|---|---|
| 1 | Hook: the risky moment | 8–15 s | `chat_mock` / `email_mock` / `mfa_prompt` / `cartoon` |
| 2 | The move | 6–12 s | `flashcard` (front = situation, back = action) |
| 3 | Retrieval | 8–12 s | `quiz` (2–3 options) |
| 4 | Reward + next | 4–6 s | `outro` ("Streak +1 · Episode 4 Monday") |

## Gamification defaults
| Element | Default |
|---|---|
| Points | episode 50 · correct quiz answer 10 · nudge watched 5 · reported simulated phish 25 |
| Streak | consecutive weeks with ≥ 1 activity; freeze 1 week per season |
| Badges | 3–5, behaviour-based (e.g. "Verifier", "Reporter", "Streak 4") |
| Leaderboard | opt-in, team-level, top 5 shown, no bottom ranks |
| Certificate | season completion ≥ 80% quiz average (evidence record) |

## Spacing schedule
Episode on day 0 → nudge A day +2 (retrieval) → nudge B day +7 (scenario/decision) → season recap quiz at the end.
Shift to working days per locale (Egypt: Sun–Thu; most of Europe/US: Mon–Fri).

## Do / Don't
| Do | Don't |
|---|---|
| Same cast, same world | New characters each week |
| One behaviour per nudge | Mini-lectures as nudges |
| Reward learning actions | Public shaming / bottom ranks |
| Captions on (silent autoplay) | Audio-only messages |

## Worked example
`templates/example.storyboard.json` — nudge E03N1 "Smishing in 45 seconds": `chat_mock` parcel-fee lure with callout →
`flashcard` → `quiz` (+10 points) → `outro` streak line. Plan + calendar examples in `templates/`.
