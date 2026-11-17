---
name: tcs-format-branching
description: Builds a choose-your-path scenario for a lesson — decision scenes plus the decision graph in storyboard.branching (nodes, outcomes, feedback, scores) — so it plays as interactive HTML/SCORM and as a linear "best path + consequences" video. Use when the chosen or requested format is "branching", "scenario", "choose your own path", "decision simulation" or "what would you do". Not for knowledge-check quizzes alone (tcs-assessment) or software practice (tcs-format-screencast-sim).
---

# tcs-format-branching

## Purpose
Let learners practise judgement: they face realistic pressure, choose, see consequences, and get feedback.
Skins: cartoon (default), comic, doodle or explainer mock-ups — the graph is independent of the look.

## Inputs
- Approved lesson (`curriculum.yaml`) — objectives at Bloom `apply`/`analyze`/`evaluate`.
- Facts (`sources.yaml`), scenario premises + red flags (domain `scenarios.md`), personas, voices.

## Outputs
- `decision` scenes: `{prompt, choices[≤4]{id, label, next (branching node id), correct?}, video_choice?}`.
- Outcome/feedback scenes in any template (usually `cartoon`, `statement`, `popup`, `email_mock`, `chat_mock`).
- `storyboard.branching = {start, nodes[]{id, scenes[] (scene ids in play order), outcome: continue|good|bad|neutral, feedback, score}}`.
- `formats`: `["branching", <skin>]` e.g. `["branching","cartoon"]`.
- Linear video cut: renderer plays `start` → the `correct: true` path, then optional "what if" recap of bad outcomes;
  `video_choice` names the choice id to follow in video targets (default: the correct one).
- Fill-ins `templates/decision_graph.yaml`, `templates/script_template.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Pick one realistic dilemma (domain `scenarios.md`) per objective; define the ideal behaviour and 1–2 tempting wrong ones.
2. Draw the graph (`templates/decision_graph.yaml`): 2–4 decision points, depth ≤ 3, ≤ 8 nodes; every path ends in an
   outcome node (`good`/`bad`/`neutral`). Prefer "recoverable" mistakes (bad choice → feedback → second chance).
3. Write scenes per node: setup scenes, one `decision` scene per decision node (last scene of the node), outcome scenes.
4. Feedback: say *why* (link to the red flag / rule), 1–2 sentences, never shaming. Put it in node `feedback`
   and voice it in the outcome scene.
5. Scores: good path max (e.g. 10), partial (2–5), bad 0. `pass_mark` lives in quiz.json (tcs-assessment adds a
   `scenario` item per decision, mapped to the objective).
6. Validate: every `choices[].next` is a node id; every node scene id exists; every node reachable from `start`;
   every non-outcome node ends with a `decision` scene.

## Rules / QA
- Choices are plausible, similar length, no joke options; ≤ 4 choices, labels ≤ 10 words.
- Exactly one best choice per decision (`correct: true`); others `false`.
- Bad outcomes realistic, not catastrophic for laughs; always show the recovery action (report, call IT).
- Accessibility: choices keyboard-selectable in HTML/SCORM; video version announces choices in narration.
- Arabic: choice labels and feedback translated; branches mirror nothing (graph is logical).

## Blends
- **branching + cartoon** (default), **branching + comic** (static pages), **branching + doodle**.
- **explainer + branching**: teach first, one scenario at the end (formats `["explainer","branching"]`).
- **branching + quiz**: tcs-assessment turns each decision into a `scenario` item for SCORM scoring.
- **series + branching**: weekly "what would you do?" nudge with one decision.

## References
- `references/playbook.md`, `templates/decision_graph.yaml`, `templates/script_template.md`, `templates/example.storyboard.json`.
