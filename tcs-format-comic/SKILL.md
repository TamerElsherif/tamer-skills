---
name: tcs-format-comic
description: Builds the comic-format scenes of a lesson storyboard — static panel strips or vertical webtoons with a panel layout, persona staging, captions and dialogue balloons, optionally read aloud as a motion comic. Use when the chosen or requested format is "comic", "comic strip", "webtoon", "graphic story", "panels" or "motion comic". Not for fully animated stories (tcs-format-cartoon) or whiteboard drawings (tcs-format-doodle).
---

# tcs-format-comic

## Purpose
Tell a short scenario in 3–12 panels that work both as a readable page (lesson/job-aid/HTML/PDF targets) and as a
motion comic (video: panels reveal on `^` cues with narration and character voices).

## Inputs
- Approved lesson (`curriculum.yaml`), facts (`sources.yaml`), domain `scenarios.md` premises.
- Personas (`assets/characters/personas.yaml`, domain `personas.yaml`), voices (`assets/voices.yaml`).

## Outputs
- `scenes[]` of `comic` pages: `{layout: "1"|"2"|"3"|"2x2"|"1+2"|"3-row", panels[≤4]{cue, set, people[]{cast,x,y,s,pose,expr,flip,holding}, caption, bubbles[]{who,text,think}, sfx_word}}`,
  framed by `title`, a teaching scene (`do_dont`/`steps`/`checklist`), `quiz`, `outro`.
- Panel layout plan (fill-in `templates/panel_layout.md`) and dialogue script (`templates/script_template.md`).
- `aspect`: `9:16` + `3-row`/`1+2` for webtoon/mobile; `16:9` + `2x2`/`3`/`2` for desktop strips; `1:1` + `2x2` for social.
- Fragment `templates/example.storyboard.json`.

## Steps
1. Choose premise + 2–3 personas; outline 3 acts: situation → wrong move/pressure → right move.
2. Split into pages of ≤ 4 panels (layout picks), 1 action per panel; plan "camera" (wide → medium → close).
3. Write captions (≤ 12 words, narrator voice) and balloons (≤ 12 words, max 2 per panel).
4. Stage people in panel coordinates (panel = 1280×1000 virtual stage; feet y ≈ 1000; `s` 0.9–1.1).
5. Narration for motion comic: one `^` per panel reveal (panel `cue`), characters' lines read with their voices.
6. Add the teaching scene, quiz and outro; claims per scene; validate.

## Rules / QA
- Text only in `caption`, `bubbles[].text`, `sfx_word` props — never in generated art.
- ≤ 4 panels per scene (schema max), ≤ 2 balloons per panel, ≥ 28 px balloon text at 1080p.
- Reading order: LTR → left-to-right/top-down; RTL (`direction: rtl`) → panels and balloon tails mirror (kit handles);
  write Arabic balloons in Egyptian colloquial for dialogue, MSA for captions only if the brief asks.
- Antagonist balloons may use `think` for asides; keep humour kind.
- Static targets (PDF/HTML/job-aid) must read without audio: captions carry the narration's key point.

## Blends
- **comic + job-aid**: last page = the job-aid card; good for printable posters.
- **comic + series**: one page per week (webtoon episode) + flashcard nudge.
- **comic + branching**: final panel is a `decision` scene; outcomes are one-page comics.
- **comic + quiz** (via tcs-assessment): "spot the red flag in panel 2" scenario items.

## References
- `references/playbook.md`, `templates/panel_layout.md`, `templates/script_template.md`, `templates/example.storyboard.json`.
