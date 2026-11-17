# HTML lesson player (templates/lesson.js)

## Navigation model
- Linear order = storyboard scene order + `__check` (final Knowledge check, only when quiz items are not embedded) + `__end`.
- Branching (`storyboard.branching`): when linear navigation reaches the first scene that belongs to any node, the
  player enters `branching.start`, plays each node's `scenes`, and on a `decision` scene the chosen `next`
  (node id or scene id) routes. Next is disabled on decisions. Node `score` values add up.
- A node with `outcome` good/bad/neutral ends on an outcome card (`feedback`, score, "Replay scenario"); Next then
  resumes linear order after the last branch scene. `outcome: continue` without a decision falls through to the next node.
- Decisions outside a branching graph show correct/incorrect feedback and jump to `next` if it is a scene.
- Keyboard: ←/→ follow reading direction (reversed in RTL); Esc closes the menu; everything is reachable by Tab.

## Scoring
Scored items = quiz.json items except flashcards (+ inline quiz scenes, + `sim.mode: assess` screencasts).
First attempt counts; "Try again" on the end page resets all answers. raw = round(100 × points correct / points).

## Screencast sims (`props.sim`)
| mode | behaviour |
|---|---|
| demo (or no sim) | step-through: pulsing hotspot on the target, Next step / Restart, toast labels |
| guided | real inputs; the expected target is highlighted and its hint shown |
| practice | real inputs, no highlight; wrong target/value → hint + attempt count; at `max_attempts` → `on_fail` (`replay_demo` animates `actions`, `show_hint` outlines the target, `continue` ends) |
| assess | like practice without hints; result (1/0) stored as `sim.quiz_item` or `SIM_<scene_id>` |
Values compare case-insensitively (`,` = `.`); `"*"` = any non-empty; no `value` = just act on the target.

## QA URL flags (local only)
`#s-<scene_id>` open a scene · `?reveal=1` reveal all progressive items/callouts · `?all=1` stacked static view of all
scenes (like print). `deck.html#slide-3`, `deck.html?notes=1` (N toggles notes).
