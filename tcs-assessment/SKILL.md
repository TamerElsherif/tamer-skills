---
name: tcs-assessment
description: Builds the assessment for a lesson or course — knowledge checks, pre/post-tests, scenario questions and flashcards mapped to curriculum objectives with Bloom-aligned distractors, per-option feedback and source tags — as `<lesson>.quiz.json`, validates coverage, and exports Moodle GIFT and CSV for LMS import. Use for "make a quiz/test/knowledge check/flashcards", "add questions for objective O2", or "export the quiz to Moodle/CSV". Not for in-video quiz scene layout (tcs-storyboard), SCORM packaging (tcs-render-lesson) or fact checking (tcs-grounding-check).
---

# tcs-assessment

## Purpose
Measurable objectives need measurable items. Every objective gets items at its Bloom level, every item is grounded in a
source fact, and the result travels to any LMS.

## Inputs
- `curriculum.yaml` (objectives with `bloom`, lesson `objective_ids`), `sources.yaml` (facts, glossary, warnings),
  the lesson script/storyboard (examples, rookie mistakes = distractor material). Language from the lesson.
- Requested kind: knowledge-check (default), pre-test, post-test, scenario, flashcards.

## Outputs
- `runs/<run>/lessons/<L>/<L>.quiz.json` (schema `schemas/quiz.schema.json`); course-level tests `runs/<run>/<course>.post-test.quiz.json`.
- Optional exports next to it: `<L>.quiz.gift.txt`, `<L>.quiz.csv`.
- Storyboard `quiz` scenes reference items by id (`props.quiz_item`); tell tcs-storyboard which ids to use.

## Steps
1. List the lesson objectives (id, text, bloom). Pick item types per `references/item-writing.md` (Bloom table).
2. For each objective choose the facts behind it (policy/step/warning/definition); collect misconceptions from
   warnings, the script's mistake beats and near-miss numbers in the same source.
3. Write items from `templates/quiz.example.json`: ids `Q1…`, `objective_id`, `bloom`, `difficulty`, stem, options with
   exactly one `correct` (mcq/true_false/scenario), feedback per option, `explanation`, `source_ids` (or `general_knowledge`).
   Counts: knowledge-check 3–5 per lesson; post-test ≥ 2 per objective; flashcards 1 per key term/rule.
4. Arabic lessons: write natively (register of the lesson) or add `stem_ar`/`text_ar` for bilingual delivery.
5. Validate:
   `.venv/bin/python skills/tcs-assessment/scripts/validate_quiz.py <quiz> --curriculum runs/<run>/curriculum.yaml --sources runs/<run>/sources.yaml`
   (or `--storyboard <L>.storyboard.json` / `--objectives O1,O2`). Fix all errors; review warnings.
6. Export if asked: `scripts/to_gift.py <quiz> [--lang ar]`, `scripts/to_csv.py <quiz> [--lang ar]`.
7. Run tcs-grounding-check (it verifies quiz keys against sources together with storyboard claims).

## Rules / QA
- Every objective covered; items test the objective's verb, not trivia.
- One unambiguous key; distractors plausible, parallel in length/grammar; no "all/none of the above", no tricks.
- Feedback teaches (why), ≤ 25 words, per option. Fictional people/companies only.
- Keys must be supported by cited facts; scenario details may be fictional but the rule must be sourced.
- Pass mark default 80; `shuffle: true` unless ordering matters (ordering items are shuffled by the LMS anyway).

## References (load on demand)
- `references/item-writing.md` — types, Bloom table, distractors, feedback, kinds, Arabic, exports.
- `templates/quiz.example.json` — valid Northwind knowledge check (mcq, true_false, ordering, scenario, flashcard).
- Scripts: `validate_quiz.py`, `to_gift.py`, `to_csv.py`. Tests: `tests/`.
