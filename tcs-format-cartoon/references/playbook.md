# Cartoon / micro-drama playbook

## When to use
- Behaviour under pressure (urgency, authority, fatigue, kindness exploited), culture, soft skills.
- Audience is broad and fatigued by "slides"; you need recall through story.
- Avoid for dense reference content (narrated-deck / job-aid) or exact UI procedures (screencast-sim).

## Duration
| Variant | Length | Story scenes | Teaching scenes |
|---|---|---|---|
| Micro-drama | 60–120 s | 3–5 | 1–2 + quiz |
| Standard | 2.5–5 min | 8–14 | 3–5 + quiz |
| Two-part | 2 × 3–5 min | part 1 story + cliff-hanger, part 2 mentor fix | |

## Beat structure (3 min)
| # | Beat | Time | Template | Acting |
|---|---|---|---|---|
| 1 | Title | 4–6 s | `title` | |
| 2 | Setup (normal day) | 10–15 s | `cartoon` | protagonist idle → happy |
| 3 | Inciting moment | 10–15 s | `cartoon` + `chat_mock`/`email_mock`/`mfa_prompt` | phone pose, worried |
| 4 | Temptation / pressure | 10–20 s | `cartoon` (antagonist bubble `villain`) | sly, rub |
| 5 | Mistake or near-miss | 8–12 s | `cartoon` + `popup` | facepalm / shocked, camera zoom |
| 6 | Consequence | 10–15 s | `cartoon` / `bullets` warn | sad |
| 7 | Mentor turn | 12–20 s | `cartoon` (mentor present/stop) | |
| 8 | The rule | 12–20 s | `steps` / `do_dont` | |
| 9 | Replay done right | 10–15 s | `cartoon` | cheer |
| 10 | Quick check | 10–14 s | `quiz` | |
| 11 | Recap + outro | 10–15 s | `checklist`, `outro` | |

## Staging cheat-sheet (16:9, 1920×1080)
- Two-shot: x 700 / 1250, `s` 1.2, second person `flip: true` to face the first.
- Single close: x 960, `s` 1.3–1.5, camera `{zoom:1.35–1.5, x:960, y:520}` on the punchline cue.
- Desk scenes: `desk: true`, `lowerHidden: true` for seated persons.
- 9:16: one person per frame, `s` 1.6, feet y ≈ 1700; bubbles above head.
- Night/home for "after hours" pressure (MFA fatigue, smishing); `den` for the antagonist.

## Voices
One voice per persona (assets/voices.yaml), instructions describe acting ("flustered, fast, comic").
Narrator ≠ any character voice. Arabic: Egyptian colloquial for characters, narrator may be MSA or Egyptian per brief.

## Do / Don't
| Do | Don't |
|---|---|
| Short lines, big reactions | Monologues > 20 s in a bubble |
| Show the mistake *and* the redo | End on the failure |
| Mentor explains the why in one line | Mock the protagonist |
| Antagonist playful, not scary | Gore, threats, hoodie hacker clichés |

## Worked example (`templates/example.storyboard.json`)
"Midnight Push Notifications" (MFA fatigue): rookie at home at night → `mfa_prompt` counting to 12 → vex in den
("Everyone taps Approve eventually") → mentor in office (deny + report + reset) → `steps` → `quiz` → `outro`.
~50 s fragment; add consequence + replay beats for a 2.5-min lesson.
