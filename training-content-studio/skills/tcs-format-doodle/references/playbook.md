# Doodle / whiteboard playbook

## When to use
- Abstract mechanisms (how an attack chain works, why a rule exists), mental models, short "rules of three".
- Low budget, fast to localize (few on-screen words), calm tone.
- Avoid for software procedures (screencast-sim) or emotional behaviour change (cartoon).

## Duration
| Lesson | Length | Boards | Draw cues per board |
|---|---|---|---|
| Micro | 45–90 s | 3–4 | 3–5 |
| Standard | 2–4 min | 6–10 | 4–8 |
| Deep | 4–6 min | 10–16 | 4–8 |

## Beat structure (2.5 min)
| # | Beat | Time | Template |
|---|---|---|---|
| 1 | Title | 4–6 s | `title` (ink style) |
| 2 | Character + problem drawn | 12–18 s | `whiteboard` (person, note, arrow) |
| 3 | How it works (chain) | 15–25 s | `whiteboard` (icons + arrows L→R) |
| 4 | Levers / signs | 12–20 s | `whiteboard` (3 icons + notes + underline) |
| 5 | Consequence | 10–15 s | `whiteboard` (cross on the bad outcome) |
| 6 | Rules (what to do) | 12–20 s | `whiteboard` (checks + notes, `safe`) |
| 7 | Quick check | 10–14 s | `quiz` |
| 8 | Recap | 8–12 s | `checklist` |
| 9 | Outro | 4–6 s | `outro` |

## Layout grid (16:9 stage 1920×1080)
| Zone | x | y | Use |
|---|---|---|---|
| Left figure | 300–480 | feet 860–900 | protagonist |
| Centre | 760–1160 | 300–700 | chain icons/notes |
| Right figure | 1440–1620 | feet 860–900 | other party |
| Title band | 96–1824 | 80–160 | `props.title` |
9:16: stack zones vertically (title 120–220, figure feet ~1100, notes 1300–1700). Keep 96 px margins.

## Draw-on timing
- Each item draws in ~1.2 s from its cue; notes write at ~12 chars/s.
- Hold ≥ 1.5 s after the last item (`hold`) so the finished board reads.
- Camera: one board per scene; the renderer may pan between consecutive boards.

## Do / Don't
| Do | Don't |
|---|---|
| 1 idea per board, ≤ 8 items | Fill the board with paragraphs |
| One attention-coloured element per board | Colour everything orange |
| Notes ≤ 4 words | Full sentences in handwriting |
| Draw the person first, then the action | Reveal items before they are said |

## Worked example (`templates/example.storyboard.json`)
"How Social Engineering Works": attacker (vex, sly) → arrow → learner on phone → note "tricks people" → key circled
(4 cues); levers board (clock/badge/heart + notes + underline); rules board (3 checks); quiz; outro. ~45 s fragment;
add consequence + example boards for a 2.5-min lesson.
