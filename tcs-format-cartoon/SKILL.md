---
name: tcs-format-cartoon
description: Builds the cartoon-format scenes of a lesson storyboard — a 2D animated micro-drama with recurring personas acting on kit sets (poses, expressions, speech bubbles, camera beats) plus a mentor who turns the story into the lesson. Use when the chosen or requested format is "cartoon", "animated story", "micro-drama", "character scenario" or "skit". Not for static panel comics/webtoons (tcs-format-comic), hand-drawn whiteboard (tcs-format-doodle) or choose-your-path stories (tcs-format-branching, which may reuse these scenes).
---

# tcs-format-cartoon

## Purpose
Change behaviour through story: a relatable persona makes (or nearly makes) the mistake, consequences land,
a mentor shows the right move, and teaching beats (steps/quiz/recap) lock it in.

## Inputs
- Approved lesson (`curriculum.yaml`), facts (`sources.yaml`).
- Personas: `assets/characters/personas.yaml` (+ each `character_sheet.md`) and domain `personas.yaml`
  (e.g. security pack adds `vex`). Scenario premises: domain `scenarios.md`.
- Voices: `assets/voices.yaml` (one distinct voice per speaking persona, per language).

## Outputs
- `cast[]` (persona ids), `voices{}` keyed by persona id (key = `who` in lines = `people[].cast`, so mouths lip-sync).
- `scenes[]`: story beats as `cartoon` scenes —
  `{set, night?, desk?, people[≤5]{cast,x,y,s,pose,expr,flip,holding,lowerHidden}, beats[]{cue,cast,pose,expr,move_to,camera,sfx}, bubbles[]{cue,out_cue,who,text,think,tone}}`;
  UI moments as `email_mock`/`chat_mock`/`mfa_prompt`/`popup`/`browser_mock`; teaching beats as `steps`/`do_dont`/`icon_grid`;
  `quiz`, `checklist`, `outro`. `music.bed: "cartoon"`.
- Fill-ins: `templates/script_template.md`, `templates/cast_sheet.yaml`; fragment `templates/example.storyboard.json`.

## Steps
1. Pick a premise (domain `scenarios.md`) that hits the lesson objectives; choose 2–4 personas (protagonist `rookie`
   or `learner`, antagonist if any, `mentor`). Keep personas consistent across the course.
2. Outline the arc (playbook): setup → temptation → mistake/near-miss → consequence → mentor fix → rule → check.
3. Write lines: narrator frames, characters speak short lines (≤ 15 words). `^` before each acting beat or bubble.
4. Stage each `cartoon` scene: pick `set` from enums; place people (feet `y` ≈ 1060 at `s` 1.2–1.4 for 16:9);
   change pose/expression on cues; ≤ 1 camera move per scene; bubbles ≤ 10 words, `tone: villain` only for the antagonist.
5. Add teaching scenes after the story turns (not inside long dialogue). Add `quiz`, recap, outro.
6. Claims: story events are `general_knowledge` only if illustrative; every rule/sign stated must be sourced.
7. Validate schema + cues; check every `who` has a `voices` entry.

## Rules / QA
- Use only enum poses/expressions/sets; the antagonist is the only persona wearing the attention colour.
- No real people, brands or recognisable likenesses; fictional company "Northwind Co.".
- Every story scene has acting (≥ 1 pose/expr change on a cue) and the narrator/mentor ties it back to the lesson.
- Humour punches at the situation, never at a group or nationality; Egyptian-Arabic jokes reviewed by a native speaker.
- Character voices: distinct timbre + acting `instructions`; avoid two personas on the same voice in one scene.
- Generated character images (if any) use the locked prompt in `assets/characters/<id>/prompt.txt` (no text).

## Blends
- **cartoon + branching**: story stops at a `decision` scene; outcomes are short cartoon scenes (see tcs-format-branching).
- **cartoon + series**: recurring cast = the series hook; one micro-drama per episode, nudges replay the key beat.
- **cartoon + job-aid**: the mentor's steps become the job-aid.
- **cartoon + explainer**: cartoon cold-open + explainer teaching body.

## References
- `references/playbook.md`, `templates/cast_sheet.yaml`, `templates/script_template.md`, `templates/example.storyboard.json`.
