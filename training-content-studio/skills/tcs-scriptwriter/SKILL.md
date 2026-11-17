---
name: tcs-scriptwriter
description: Writes the spoken narration script for one lesson — English or Arabic (Egyptian colloquial or MSA) — with format-specific beats, word budgets from words-per-minute, `^` visual-cue markers, character dialogue for cartoon/comic/branching, speakable numbers and a source-tagged claim under every scene; outputs `<lesson>.script.md` and the script stage of `storyboard.json`. Use for "write the script/narration/voice-over", "make it shorter/longer", "rewrite in Egyptian Arabic", or "add dialogue". Not for choosing visuals/templates (tcs-storyboard), translating an existing lesson (tcs-localize) or quiz items (tcs-assessment).
---

# tcs-scriptwriter

## Purpose
Turn an approved lesson (curriculum objectives + sources) into narration that sounds human, fits the duration, cues the
visuals and can be verified claim by claim. One script per lesson per language.

## Inputs
- `curriculum.yaml` lesson: `id, title, objective_ids, formats (≤2), duration_min`; course `audience.level`, `languages`, `wpm`.
- `sources.yaml` facts (+ chunk files for cited chunks only). Never write from memory when a source exists.
- Format beats: `skills/tcs-format-<format>/references/playbook.md`; fallback `references/beats.md`.
- Domain pack (optional, `domains/<pack>/`): glossary, personas, red-flag patterns.

## Outputs
- `runs/<run>/lessons/<lesson_id>/<lesson_id>.script.md` (contract: `references/script-contract.md`).
- `runs/<run>/lessons/<lesson_id>/<lesson_id>.storyboard.json` — script stage (narration + claims per scene, placeholder templates),
  produced by `script_md.py to-storyboard`. tcs-storyboard completes it.

## Steps
1. **Budget**: `.venv/bin/python skills/tcs-scriptwriter/scripts/script_md.py budget --minutes <duration_min> --level <level> --lang <lang>`
   → wpm, scene count, words per scene (beginner 130, advanced 150–160, Arabic −10 %; `references/wpm-budget.md`).
2. **Beats**: open the format skill's beats (e.g. `tcs-format-explainer`); map each objective to ≥ 1 beat; check-beat per lesson.
3. **Pick facts**: for each beat list the fact ids (from `sources.yaml`) it will state. Gaps → `[general]` claim
   (only if `general_knowledge_allowed`) or drop the point; never invent policy numbers.
4. **Draft** from the family template: `templates/script-explainer.md` (explainer, doodle, narrated-deck, mindmap,
   screencast-sim, job-aid, series), `templates/script-story.md` (cartoon, comic), `templates/script-branching.md`.
   - Narration in the lesson language; Arabic per `references/arabic-narration.md` (ar-EG colloquial vs ar-MSA).
   - `^` right before the words that reveal each item; N items ⇒ N markers; quiz: question `{pause: 2.2}` then `^` answer.
   - Story formats: characters (persona ids from `cast`) speak short in-character lines; narrator ties back to the rule.
   - One `claim:` per checkable statement, tagged `[S01#c1]` / `[general]`; claims keep exact figures.
5. **Speakable numbers**: write numbers as words in narration; `scripts/speakable.py --lang <lang> "<text>"` helps.
6. **Check**: `script_md.py check <lesson>.script.md` → 0 errors; fix warnings on duration (±15 %), scene length (5–35 s),
   long sentences, digits.
7. **Script stage**: `script_md.py to-storyboard <lesson>.script.md --out <lesson>.storyboard.json` → hand to tcs-storyboard.
8. Report: words, est. duration vs target, cue count, claims (sourced vs general), open questions.

## Rules / QA
- Exact source content; cover every objective; no skipped topics the user asked for.
- No real people or brands; fictional "Northwind Co." unless the user's organisation is given; personas, not names, in cast.
- ≤ 25 words per sentence; 1 idea per scene; scenes 5–35 s; total within ±15 % of target (never "speed up" to fit).
- Every scene ≥ 1 claim; `general_knowledge` only when allowed and labelled.
- Don't write on-screen text here except via `template:` hints and `visual:` lines (on-screen text comes from storyboard props).
- Arabic is written natively, not translated line-by-line; keep English product terms when staff say them in English.
- Voices default to OpenAI `gpt-4o-mini-tts` `marin` + language instructions; characters get distinct voices
  (`script_md.py` persona map); override in front matter `voices:`.

## References (load on demand)
- `references/script-contract.md` — script.md format, cue rules, claims, style, script→storyboard mapping.
- `references/wpm-budget.md` — wpm table, formula, duration checks.
- `references/arabic-narration.md` — Egyptian vs MSA writing, Arabic numbers, TTS notes.
- `references/beats.md` — fallback beats per format + beat→template hints.
- Scripts: `script_md.py` (budget/check/to-storyboard), `speakable.py`. Tests: `tests/`.
