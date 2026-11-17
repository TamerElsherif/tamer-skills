# Narrated-deck playbook

## When to use
- Policies, onboarding, compliance refreshers, processes with rules and limits; instructor-led sessions.
- Client needs an editable PPTX as well as video/HTML/SCORM.
- Avoid for emotional behaviour change (cartoon) or "how to use the tool" (screencast-sim).

## Duration
| Variant | Slides | VO | Notes |
|---|---|---|---|
| Micro | 5–8 | 3–6 min | 1 objective |
| Standard | 10–20 | 8–15 min | quiz every 5–8 slides |
| Live session | 15–30 | 30–60 min live | VO optional, notes required |

Per slide: 30–90 s VO (≈ 75–225 words at 150 wpm). Over 90 s → split the slide.

## Beat structure (standard)
| # | Slide | Template |
|---|---|---|
| 1 | Title | `title` |
| 2 | Why this matters | `statement` / `stat` (sourced) |
| 3 | Agenda / objectives | `section` + `bullets` |
| 4–n | One key point each | `bullets` / `steps` / `table` / `process_flow` / `comparison` / `definition` |
| … | Example or demo | mock-up / `image` |
| … | Practice | `quiz` / `decision` |
| n-1 | Summary | `checklist` |
| n | Next steps / contacts | `outro` (+ `evidence_line`) |

## Template map
| Content | Template |
|---|---|
| Rules, conditions | `bullets` (icons), `do_dont` |
| Limits, matrices | `table` |
| Approval path | `process_flow` |
| Chronology / deadlines | `timeline` |
| Options compared | `comparison` |
| Key term | `definition` |

## Speaker notes pattern
VO = what the narrator says (also exported as notes). `notes` = presenter extras:
`Ask: … · Example: … · If asked about X: … · Time: 2 min`.

## Do / Don't
| Do | Don't |
|---|---|
| Message title per slide | "Overview" titles |
| ≤ 6 bullets, keywords | Paragraphs on slides |
| Reveal one point per click (`^`) | Read the slide verbatim |
| Tables ≤ 5 rows | Screenshot of a spreadsheet |
| Consistent digits and RTL mirroring | Mixed LTR layout in an Arabic deck |

## Worked example (`templates/example.storyboard.json`)
"Submitting Expense Claims" (fictional Northwind policy): title → four rules (`bullets`) → limits (`table`) →
approval path (`process_flow` with decision) → pre-submit `checklist` → `quiz` → `outro`. Speaker `notes` on slides 1–3.
