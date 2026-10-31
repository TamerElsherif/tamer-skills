# Editing playbook (what worked on Ep 3)

## Kinds of mini episode

- **Sub-episode:** one contiguous stretch of the episode (or 2–3 neighbouring stretches) that holds one idea,
  10–25 min. Ep 3 had 9: hook → intro → parts → host's closing call to action → outro.
- **Topic episode:** one idea that the conversation visits in several places (Ep 3: the PLP framework was spread
  over 6 places). Rebuild it as a story in the framework's own order. This is where the editing matters most.

## Storyline (topic episode)

1. **Cold open (5–25 s):** 2–3 short, punchy lines from the episode, hard cuts, each a complete micro-idea
   (start on a sentence start, end on a sentence end). Pick claims that make the audience ask "why?": a
   contrarian line, a number, a consequence. PLP: «الكودينج ليابيليتي مش أسد» · the "30% of features used by
   under 1% of users" case · «قفل الـ feature أصعب من بنائها».
2. **Intro logo.**
3. **Why it matters:** the host's set-up question and the guest's definition. Keep the name cards here (the
   opening usually has them burned in).
4. **The map:** the moment the guest lists the stages / parts. Swipe to it even if it comes late in the episode.
5. **One act per stage, in order,** each opened by a host question where one exists (the question is the
   chapter's natural title card). Inside an act, drop asides with jump cuts.
6. **Close the loop:** a line that ties the stages together (PLP: the kill switch needs numbers from every stage).
7. **Host's thanks + call to action, outro logo.** If the host's thanks is long, start at the first clean pause.
   PLP started at «الراجل ده بيقول كلام زي الفول…» because speech ran on before it.

Audience for Rabet: software developers, product managers, engineering managers, founders, investors. Favour
pieces with a concrete example, a number, or a decision rule over general talk.

## Choosing joins

| Situation | Join |
|---|---|
| Hook montage, logo boundaries | `cut` |
| Same conversation, an aside / repetition / tangent removed | `jump` (punch-in automatic when framing matches) |
| Next piece comes from another time in the episode | `swipe` |
| Next piece is an answer to a question asked elsewhere | `swipe`, and keep the question in the piece before |

- Two jumps in a row with the same framing: the builder punches in on the first and zooms back out on the second.
  Don't fight that: it's the standard jump-cut rhythm.
- Don't put a jump inside continuous speech (rule 6), or across a meaningful pause (rule 7).
- Too many swipes in a row feel like a montage: if three pieces from different places each run under 20 s,
  look for one longer piece that covers the same point.

## Edges, step by step

1. `tx.py` around the candidate: find the sentence start/end by words (± 1 s).
2. `pauses.py T`: pick the pause whose left words end the thought and whose right words start the next one.
   Ins: the pause before the first kept word. Outs: the pause after the last kept word.
3. No pause (speech runs on, or two voices overlap): take the "quietest" time, or move the edge to the next
   sentence break. Never force it.
4. `check_edges.py`: the START part must begin on the first word, the END part must finish on the last word, with
   nothing clipped. Ep 3 fixes found this way: Hossam's piece moved 776.27 → 777.64 (started «إنت بقى من ناحية…»);
   the close moved 3849.15 → 3844.545 (it had started on «وخصوصًا»).

## CTA placement (follow & subscribe)

- Ask first (SKILL.md rule 1). Recommended: after the intro (≈ 20 s into the body, once the topic is set), the
  middle, and the end (during the host's closing call to action when it is there).
- The builder keeps it off joints, name cards, burned-in cards and the other pop-ups. If the log says "no free 6 s
  window", give an explicit output time in `at`.
- One language per episode: `en` matches the YouTube UI most viewers see; `ar` for Arabic-UI audiences.

## Brief contents (what the user reviews)

Main idea · storyline · audience · editing notes (what was kept or dropped on purpose and why) · cut list with
episode time, source time (plus the teaser offset for the uploaded file), join, speaker, first/last words, what
happens · YouTube chapters (from section starts, ≥ 10 s apart) · CTA times · B-roll ideas per section (for the
explainer pass) · Arabic description draft.
