# Explainer playbook

## When to use
- Concept + "how it works" + "what to do" topics (threats, policies, processes) for broad audiences.
- Source is a deck, policy or talking-head video; no strong story or characters needed.
- Prefer **doodle** for abstract cause→effect told visually, **cartoon** when behaviour change needs emotion/story,
  **screencast-sim** when the objective is a software procedure.

## Duration
| Lesson | Length | Scenes | Words @150 wpm |
|---|---|---|---|
| Micro | 1–2 min | 6–9 | 150–300 |
| Standard | 2.5–5 min | 10–18 | 375–750 |
| Deep | 5–8 min (split in parts ≥ 6 min) | 18–30 | 750–1200 |

## Beat structure (standard 3–4 min)
| # | Beat | Time | Template(s) |
|---|---|---|---|
| 1 | Title | 4–7 s | `title` |
| 2 | Hook (why it matters to *me*) | 10–15 s | `broll` + chips, or `stat` (sourced) |
| 3 | What it is | 10–15 s | `definition` |
| 4 | How it works | 15–25 s | `steps` / `process_flow` / `timeline` |
| 5 | Real-looking example | 20–35 s | `email_mock` / `chat_mock` / `browser_mock` / `mfa_prompt` / `popup` with callouts |
| 6 | Warning signs | 12–20 s | `broll_panel` / `icon_grid` / `bullets` |
| 7 | Consequences (personal → company) | 12–20 s | `bullets` (tone warn) / `comparison` |
| 8 | What to do | 15–25 s | `do_dont` / `steps` |
| 9 | Quick check | 10–15 s | `quiz` |
| 10 | Recap | 8–12 s | `checklist` |
| 11 | Outro | 4–6 s | `outro` (+ `evidence_line` if compliance) |

Rhythm: B-roll or mock-up every 8–20 s; never > 2 text boards in a row; one idea per scene; 5–35 s per scene.

## Motion graphics map
| Content | Template | Notes |
|---|---|---|
| 3–6 parallel points | `bullets` / `icon_grid` | icons from kit subset; `tone` warn/safe |
| Sequence | `steps` (≤6) / `process_flow` (branches) | |
| Before/after, wrong/right | `do_dont` / `comparison` | cues: left items then right items |
| Number | `stat` | only with `source` + claim |
| Quote / rule of thumb | `statement` | |
| Data | `table` (≤ 5 rows on screen) | |
| Over footage | `broll` (≤2 chips) / `broll_panel` (≤5 items) | |

## B-roll shot list rules
- Query = who + action + setting ("colleagues talking at office desk"). Avoid "hacker", "matrix", "code rain".
- One shot per scene; `min_s` ≥ planned scene seconds (fetch ≥ 12 s clips).
- Record `provider`, `path`, `license` (Pexels/Pixabay licence string + URL) after fetch.
- Reject: visible logos/brands, readable screens, text overlays, off-topic, low light.

## Do / Don't
| Do | Don't |
|---|---|
| Speak to "you"; concrete examples | Lecture definitions for > 20 s |
| Reveal with `^` as words are said | Show all bullets at once |
| Fictional brand `Northwind Co.`, `.example` domains | Real company logos, real people |
| Recap = the actions, not the theory | End on consequences without a "what to do" |
| Top or full subtle border on cards | One-sided thick accent borders |

## Worked example (fragment: `templates/example.storyboard.json`)
"Spot a Phishing Email" — 10 scenes, ~100 s of narration: title → broll hook → definition → steps (bait/hook/catch/damage)
→ `email_mock` with 4 callouts (look-alike domain, generic greeting, deadline, button) → `broll_panel` signs → `do_dont`
→ `quiz` (Q1) → `checklist` recap → `outro` with ISO 27001 evidence line. Extend to 3 min by adding consequences +
a second mock-up (`chat_mock` smishing) for a standard lesson.
