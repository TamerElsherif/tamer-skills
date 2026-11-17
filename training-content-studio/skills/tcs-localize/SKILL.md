---
name: tcs-localize
description: Produces a second-language version of an existing lesson — English ↔ Arabic (Egyptian colloquial or MSA) adaptation rather than literal translation — with RTL layout rules, numerals/punctuation/bidi handling, cultural example swaps, a bilingual glossary, per-language voice selection and SRT/VTT subtitles; outputs `<lesson>.<lang>.storyboard.json` plus subtitles and an RTL lint report. Use for "make an Arabic version", "translate/localize this lesson", "Egyptian or MSA?", "add Arabic/English subtitles". Not for writing a lesson natively in Arabic from scratch (tcs-scriptwriter) or rendering (tcs-render-*).
---

# tcs-localize

## Purpose
Arabic and English are first-class. A localized lesson keeps the same scenes, cues, claims and timing logic, but reads
and sounds native: right register, RTL-correct, culturally fitting, consistent terms.

## Inputs
- Final source storyboard `runs/<run>/lessons/<L>/<L>.storyboard.json` (validated, grounded).
- Target language `ar-EG | ar-MSA | en-US | en-GB` (from curriculum `languages.secondary` / `subtitles`).
- Glossary: `templates/glossary.yaml` + `domains/<pack>/glossary.yaml` + course glossary in `sources.yaml`.
- Optional renderer timing `timing.json` for accurate subtitles.

## Outputs
- `runs/<run>/lessons/<L>/<L>.<lang>.storyboard.json` (e.g. `M1L1.ar-EG.storyboard.json`), schema-valid.
- `<L>.<lang>.translate.yaml` (worklist, kept for review/re-use), `<L>.<lang>.srt` / `.vtt` subtitles.

## Steps
1. **Register** — pick ar-EG vs ar-MSA with `references/register.md` (default ar-EG for Egyptian staff).
2. **Skeleton + worklist**:
   `.venv/bin/python skills/tcs-localize/scripts/localize.py skeleton <L>.storyboard.json --lang ar-EG [--numerals western|eastern]`
   → language/direction/fonts/voices switched, every translatable string marked `«TR» …`, worklist with glossary hints and
   the `^` count per string. Claims, URLs, e-mails, code and file names are left untouched.
3. **Adapt** each worklist entry (`tr:`) — meaning, not words (`references/register.md`); keep exactly the same `^`
   count in the same order; narration numbers as words, on-screen digits in one numeral system; cultural swaps from
   `references/cultural-swaps.md`; glossary terms consistent; persona bubbles use Arabic display names.
   Batch 20–40 entries per LLM call; give the model the scene context (template + neighbouring strings).
4. **Apply**: `localize.py apply <L>.<lang>.storyboard.json <L>.<lang>.translate.yaml` (fails on missing text or cue drift;
   re-derives on_screen_text).
5. **Lint**: `scripts/rtl_lint.py <L>.<lang>.storyboard.json --source <L>.storyboard.json` (RTL/bidi/numerals/register/cues)
   and `skills/tcs-storyboard/scripts/validate_storyboard.py <L>.<lang>.storyboard.json --stage final`.
6. **Voices**: confirm per `references/voices.md` (OpenAI `marin` + dialect instructions; alternates ElevenLabs/Azure).
7. **Subtitles**: `scripts/subtitles.py <L>.<lang>.storyboard.json [--timing timing.json]` (and for the source language
   too when the curriculum asks for subtitles). Real timing from the renderer is preferred; estimate otherwise.
8. **Grounding**: run tcs-grounding-check on the localized storyboard (claims unchanged; on-screen numbers must still
   appear in claims).

## Quiz
Localize `<L>.quiz.json` into `<L>.<lang>.quiz.json`: keep item/option ids and correct keys (grounding still matches), translate `stem`/`options[].text`/`feedback`/`explanation` (or fill `stem_ar`/`text_ar` for a bilingual file). Renderers pick the quiz that matches the storyboard language.

## Rules / QA
- Same scene ids, order and `^` counts as the source; duration within ±15 % (Arabic wpm × 0.9 → tighten wording).
- No literal calques; no mixed registers; product/UI names as they appear on screen.
- RTL: `direction: rtl`, Arabic font, mirrored directional icons, isolated URLs/e-mails/code, Arabic punctuation (، ؛ ؟),
  one numeral system. SVG illustrations with Latin labels stay LTR (renderer).
- Never change facts, limits or currencies while adapting; cultural swaps touch examples, names and visuals only.
- Subtitles ≤ 42 chars × 2 lines, ≤ 7 s per cue; RLM at the start of Arabic lines.

## References (load on demand)
- `references/register.md` — Egyptian vs MSA, adaptation rules EN→AR and AR→EN, quick map.
- `references/rtl-rules.md` — layout mirroring, numerals, punctuation, bidi, lint checks.
- `references/cultural-swaps.md` — names, currencies, holidays, workplace norms, visuals.
- `references/voices.md` — voice per language/provider, instruction recipes, TTS gotchas.
- `templates/glossary.yaml` — security + workplace + UI starter terms (en / ar_eg / ar_msa / keep).
- Scripts: `localize.py` (skeleton/apply), `rtl_lint.py`, `subtitles.py` (timing.json format in its docstring). Tests: `tests/`.
