# Script contract (shared by all formats)

A lesson script is `runs/<run>/lessons/<lesson_id>.script.md`. It is human-editable and machine-parseable
(`script_md.py check|to-storyboard`). The *script stage* of `<lesson_id>.storyboard.json` is generated from it.

## Front matter
```yaml
---
course_id: northwind-expenses        # ^[a-z0-9][a-z0-9-]*$
lesson_id: M1L1
title: Getting expense claims right
language: en-US                      # en-US | en-GB | ar-EG | ar-MSA
format: explainer                    # or formats: [cartoon, explainer]  (max 2, enums.formats)
level: beginner                      # beginner | intermediate | advanced | mixed → wpm
target_min: 3                        # from curriculum lesson duration_min
objective_ids: [O1, O2]
cast: [host, rookie, manager]        # persona ids that appear or speak
voices: {}                           # optional overrides; defaults from script_md.py (OpenAI marin + persona map)
subtitle_languages: [ar-EG]          # optional
wpm: 130                             # optional override of the level default
---
```

## Scenes
```
## s03_rules | rules | O1
template: bullets                    # optional hint for tcs-storyboard
visual: Board with three receipt rules appearing one by one.
narrator: Three rules keep your claim moving. ^ Keep a receipt for anything over twenty-five dollars. ^ Submit within thirty days. ^ And never split a bill to dodge an approval limit.
narrator.ar: (optional same-line Arabic → narration.text_ar for bilingual review)
rookie: Wait, even for a coffee? {pause: 0.4, instr: "surprised, quick"}
claim: A receipt is required for every expense over $25. [S01#c1]
claim: Claims must be submitted within 30 days. [S01#c1]
claim: Splitting one expense to stay under a limit is forbidden. [S01#c1]
choice: Ask the manager first -> s06_good (correct)       # branching only → decision template
note: free text for the storyboarder
```
- Heading: `## <scene_id> | <beat> | <objective ids>` — scene id `^[a-z][a-z0-9_]*$`, prefix with order (`s01_`, `s02_`).
- Speaker lines `<who>: text {pause, pre, instr}` — `who` = `narrator`, a `voices` key or a persona id in `cast`.
- Reserved keys: `visual claim note template choice lead hold min sfx transition`.
- Continuation lines (no `key:`) append to the previous spoken line.

## `^` cue markers
- `^` goes right **before** the words that should trigger a reveal; cue(i) = i-th `^` across all lines of the scene.
- N revealed items ⇒ N markers (bullets, steps, icon grid, checklist, do/don't: dont items first, then do items).
- Mock-up call-outs (email/chat/browser), cartoon beats, bubbles, whiteboard items, mindmap nodes reference cues by index.
- Quiz scene: question line `{pause: 2.2}`, then answer line starting with `^` (answer reveal = cue 0).
- Never put `^` inside a number or a name; `^` is stripped before TTS.

## Claims
- Every scene ≥ 1 claim. Each claim = one checkable statement the scene makes (spoken **or** on screen).
- Tag `[S01#c3]`, `[S01, S02#c1]` or `[general]` (model knowledge, labelled `general_knowledge: true`).
- Claims keep digits and exact figures (the narration says them in words).
- Titles/outros: claim what the scene asserts (e.g. "This lesson covers submitting expense claims. [general]").
- Do not cite a source for an idea it does not contain; when unsure, `[general]` and let tcs-grounding-check decide.

## Narration style
- Spoken English/Arabic, not document prose: ≤ 25 words per sentence, 1 idea per sentence, contractions OK (EN).
- Second person ("you"), active voice, concrete verbs; no "In this video we will…" padding beyond one line.
- Numbers as words in narration (`speakable.py`); digits stay in claims and on-screen props.
- Names/products/URLs: write how they are said ("northwind dot com slash help"); spell acronyms with spaces if needed ("C F O").
- Fictional people only (persona ids or neutral names); company "Northwind Co." in examples unless the user's org is given.
- Character lines (cartoon/comic/branching): short (≤ 14 words), in character; the narrator ties every story beat to the rule.

## From script to storyboard (script stage)
`script_md.py to-storyboard <lesson>.script.md --out <lesson>.storyboard.json [--speakable]` →
schema-valid storyboard with `narration`, `claims`, `objective_ids`, `visual`, `duration_hint_s`, voices, cast;
placeholder `template: statement` (or `decision` with real choices) and `notes: "script-stage: …"`.
tcs-storyboard replaces placeholders; `validate_storyboard.py --stage final` fails while any `script-stage` note remains.
