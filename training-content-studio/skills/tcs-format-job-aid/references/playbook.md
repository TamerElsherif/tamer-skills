# Job-aid playbook

## When to use
- Infrequent or high-stakes tasks (report an incident, approve a payment change), long checklists, lookup data.
- After any lesson as the takeaway. Not a substitute for teaching new skills.

## Types and sizes
| Type | Sections | Size | Best for |
|---|---|---|---|
| Checklist | 1–2 | half page / desk card | verify before acting |
| Cheat sheet | 3–5 | A4/Letter | lookups, shortcuts, terms |
| Decision card | 2–3 | desk card / 1:1 | if-then rules |
| One-pager | 4–5 | A4/Letter | mixed takeaway after a lesson |
| Poster | 2–3 | A3 / 9:16 screen | awareness at the point of risk |
Optional narrated walkthrough: 30–60 s.

## Section order (one-pager)
| # | Section | Template |
|---|---|---|
| 1 | Header: what this card is for | `title` (kicker "Job aid") |
| 2 | Spot it / before you start | `checklist` or `icon_grid` |
| 3 | Do / don't | `do_dont` |
| 4 | If it goes wrong | `steps` (`danger: true`) |
| 5 | Who to contact / limits | `table` |

## Writing rules
- Verb-first, ≤ 8 words: "Check the sender's domain".
- Numbers and contacts exact and sourced; placeholders flagged in `notes`.
- Same wording as the lesson (learners recognise it).
- One golden rule max (`statement`).

## Do / Don't
| Do | Don't |
|---|---|
| One page, white space | Shrink fonts to fit |
| Icons that aid scanning | Decorative clip-art |
| Real text in PDF/HTML | Exported image of text |
| Version + date in footer (renderer) | Undated cards that go stale |

## Worked example (`templates/example.storyboard.json`)
"Phishing Red-Flag Card": header → 6 red flags (`checklist`) → `do_dont` → "Clicked already?" `steps` (danger) →
contacts `table` (fictional extension flagged in `notes`). No narration.
