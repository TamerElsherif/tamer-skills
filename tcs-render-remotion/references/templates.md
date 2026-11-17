# Template behaviour (kit/src/templates)

Props are exactly those in `schemas/storyboard.schema.json`. `cue(i)` = time of the i-th `^` across the scene's
narration lines. If a scene has fewer `^` than items, the rest are spread evenly (never blocks; prepare warns).
All layouts reflow for 16:9 / 9:16 / 1:1 (columns stack, grids shrink, stage people re-space) — nothing is cropped.

| template | reveals on | notes / reflow |
|---|---|---|
| title | intro anim | disc right (16:9) / above (9:16, 1:1) |
| section | intro anim | `n` shown as 01, 02… |
| bullets | item i → cue(i) | ≤6; `side_broll` = shot id → clip right (16:9) or on top |
| icon_grid | item i → cue(i) | ≤6; cols auto (16:9: n≤4 → n, else 3; 9:16: 1–2) |
| steps | step i → cue(i) | horizontal 16:9 (≤5), vertical list otherwise; `danger` = attention colour |
| process_flow | node i (array order) → cue(i) | layered by edges (left→right, top→bottom in 9:16); decision = diamond, start/end = pill; edge labels |
| timeline | event i → cue(i) | horizontal alternating cards (16:9, ≤6) else vertical rail |
| do_dont | dont items, then do items | two cards; stacked in 9:16 |
| comparison | left items, then right | as do_dont, neutral colours |
| stat | count-up at cue(0) (else 0.4 s) | decimals inferred from `value` |
| definition | def → cue(0), note → cue(1) | |
| statement | sub → cue(0) | `accent` = substring highlighted |
| table | row i → cue(i) | 9:16 with >2 columns → one card per row |
| checklist | item i → cue(i) | ≤7, navy |
| quiz | answer reveal → cue(0) (else 65 %) | `q/options/answer/why` or resolved from quiz.json `quiz_item` |
| outro | intro anim | `evidence_line` (or theme.evidence_line) at bottom |
| broll | — | `shot` id; `chips` ≤2; `dim` 0–1; clip slowed ≥0.6× and looped to fill |
| broll_panel | item i → cue(i) | frosted panel `side` (mirrored in RTL); bottom sheet in 9:16 |
| image | Ken-Burns | `image` = generated_images id (placeholder until `path` exists) |
| email_mock | callout k → its `cue` | target gets ring + numbered badge; numbered notes beside/below (no pixel arrows) |
| chat_mock | messages: `cue` or successive free cues | `device` phone/desktop; callouts as above |
| browser_mock | callouts | `page` login/checkout/article/blank/error; targets url/form/heading/body |
| mfa_prompt | prompts start cue(0), count up to `count_to` by cue(1) | `caption` under phone |
| popup | popup at cue(0) | tone warn/bad/info; CTA pulses |
| code_mock | highlight → its cue | always LTR; labelled highlights become numbered notes |
| screencast | actions at cue | see below |
| cartoon | beats/bubbles at cue | see below |
| whiteboard | item → its cue | see below |
| comic | panel → `cue` or cue(i) | layouts 1, 2, 3, 2x2, 1+2, 3-row; panels mirrored in RTL; bubbles stack at panel top |
| mindmap | node → its `cue`; `focus` camera | root centre, level-1 on an ellipse (mirrored in RTL), children fanned out; focus zooms to node + its children |
| decision | pick → cue(0) (else 70 %) | highlights `video_choice`, else the `correct` choice |
| flashcard | flip → cue(0) (else 50 %) | 3-D flip front→back |

## screencast
`app.kind`: form | table | list | settings | dashboard | screenshot. `fields[]` are laid out deterministically, so the
cursor always lands on `target` (a field id, or `"x,y"` fractions of the content area for screenshots).
Actions: `move`, `click` (checkbox toggles, button press), `type` (types `value` or the field value; field empty before),
`select`, `highlight` (orange ring), `callout` (`label` box beside the target), `toast` (`label` + `value`),
`zoom` (`value` = zoom factor, default 1.6; zoom with no target resets). `props.sim` (interactive practice for HTML/SCORM)
plays as a narrated demo; if `actions` is empty, `sim.expect[]` becomes type/click actions on cues 0,1,2…

## cartoon
- `people[]`: omitted `x` → spread evenly; `y` = feet (default 1000, 1060 with `desk`/`lowerHidden`); `s` default 1.35.
  Coordinates are 1920×1080 stage units; characters right of centre face left automatically; RTL mirrors positions.
- `beats[]` at cue: `pose`, `expr`, `move_to` (walks over 1.1 s), `camera {zoom,x,y}`, `sfx` (name in sfx dir).
- `bubbles[]` at `cue` until `out_cue` or the speaker's next bubble; placed above the speaker (16:9) or stacked at the top
  (9:16/1:1) with a tail toward the speaker; `who` not on stage → caption bubble at top. `tone` plain/warn/villain, `think`.
- `overlay: {template, props, cue?, out_cue?}` renders any other template on a screen panel (people squeeze aside).
- Lip-flap: a person's mouth moves when a narration line's `who` equals their `cast`.

## whiteboard
White ground (use `theme.preset: whiteboard` for doodle lessons). `items[]` kinds: person (ink line-art drawn top→down),
icon (wipe-in), note (Caveat handwriting typed on; Arabic falls back to the Arabic face), arrow, circle, underline, box,
cross, check (draw-on strokes). `x,y,w,h` ≤ 1 = fractions of the canvas, larger = 1920×1080 units. Omitted coords:
content items (person/icon/note) auto-grid in reading order; annotations target the previous content item; an arrow
without coords goes from the previous content item to the next one. `color`: ink | attention | safe.

## Personas
host, learner, manager, mentor, customer, rookie, colleague, exec, support (+ security pack: `vex`, the only persona in
attention orange; `voice_clone` = exec with a glitch). Looks follow `assets/characters/personas.yaml`. Unknown ids get a
stable neutral look. Poses/expressions = `schemas/enums.json`.
