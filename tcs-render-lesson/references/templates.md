# Template rendering map

HTML = `scripts/render_html.py` (lesson + deck.html), PPTX = `scripts/deck.py` (native shapes), Job aid = `scripts/jobaid.py`.
Progressive = "Reveal next / Show all" buttons step through `cue` order (reduced-motion safe; print shows all).

| Template | HTML lesson | PPTX | Job aid |
|---|---|---|---|
| title / section | hero, icon badge, kicker/sub/part | navy full-bleed title | header (title scene) |
| bullets | icon list, tone colours, optional side b-roll | rows with tone dots | block |
| icon_grid | card grid (`cols`) | grid of cards | block (list) |
| steps | numbered circles (`danger` = orange) | numbered circles + connector | numbered list |
| process_flow | layered grid + JS SVG arrows, vertical on narrow screens | boxes/diamonds + arrow connectors | — |
| timeline | horizontal line (vertical on mobile) | line + dots | — |
| do_dont / comparison | two tinted columns | two columns (stacked in 9:16) | two columns |
| stat | count-up number (final value in print) | big number | — |
| definition / statement | card / big quote with accent | centred text | block |
| table | `<table>` with caption, row headers | pptx table (RTL flag) | table (wide if >2 cols) |
| checklist | real checkboxes (state bookmarked) | rows with empty boxes | checkbox list |
| quiz | interactive item from quiz.json (or inline q/options/answer) | question + A/B/C, answer in notes | — |
| outro | line + tips + evidence line | centred, evidence line footer | note block + footer |
| broll / broll_panel / image | `<video muted loop>` / `<img>`; placeholder if missing | picture or placeholder box | — |
| email_mock | mail client + numbered pins; "Show red flags" reveals callouts | mock card + numbered callouts | — |
| chat_mock / browser_mock / mfa_prompt / popup / code_mock | device/browser/dialog/editor mock-ups, callouts | native mock-ups | — |
| screencast (demo) | step-through with pulsing hotspot, Next step / Restart | app frame + action list | — |
| screencast + `sim` guided/practice/assess | real inputs validated vs `sim.expect` | as demo | — |
| cartoon | set backdrop + persona SVGs, bubbles revealed by cue, optional overlay mock | panel + persona shapes + bubble text | — |
| comic | panel grid by `layout`, captions, bubbles, sfx word | panel grid | — |
| whiteboard | white board, hand font, items revealed by cue | positioned shapes/text | — |
| mindmap | radial layout, lines + labels, reveal + focus by cue | root + nodes + connectors | — |
| decision | choice buttons → branching player | choices; routes in notes | — |
| flashcard | flip card (aria-pressed) | front/back halves | — |

Coordinates (`x`, `y`, `w`, `h`) accept fractions (0–1), percents (1–100) or kit pixels (1920×1080).
RTL mirrors x for cartoon people, whiteboard items and mindmaps; comic panel order follows `dir`.
Persona names in bubbles/transcripts use `display_name` (en/ar) from personas.yaml; ids never shown if a name exists.
