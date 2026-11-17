# Item writing rules

## Item types (quiz.schema.json `type`)
| type | Use for | Rules |
|---|---|---|
| mcq | one best answer | 3–4 options, exactly 1 correct, feedback on every option |
| multi | "select all that apply" | 4–6 options, ≥ 1 correct; say "Select all that apply" in the stem |
| true_false | quick recall/misconception | options `True`/`False` (or صح/خطأ), exactly 1 correct; avoid absolutes as giveaways |
| scenario | apply/evaluate in context | `scenario` 1–3 sentences (fictional persona, Northwind Co.), stem asks for the action; 3–4 options |
| ordering | procedures | 3–6 steps, `order` 1..n, from `step` facts with `procedure_order` |
| matching | terms ↔ definitions, signs ↔ actions | 3–6 pairs, `match` on every option |
| flashcard | spaced recall, glossary | `stem` = front, `back` = answer; not graded |

## Bloom alignment (objective verb → item)
| Objective bloom | Item style | Distractors built from |
|---|---|---|
| remember | recall a rule/number/term (mcq, true_false, flashcard) | near numbers (30 vs 60 days), sibling terms |
| understand | explain why / classify (mcq, matching) | plausible but wrong reasons, confused concepts |
| apply | short scenario → correct action (scenario, mcq) | common shortcuts, partly-right procedures, wrong order |
| analyze | spot red flags / what's wrong (multi, scenario) | true-but-irrelevant details, missed signs |
| evaluate | choose the best of several acceptable actions (scenario) | acceptable-but-weaker options, over-reactions |
| create | plan/compose (rare in auto quizzes) → use scenario with "which plan" | incomplete plans |

Item bloom ≤ objective bloom +0; every objective of the lesson gets ≥ 1 item (post-test ≥ 2).

## Distractors
- Plausible, same length/grammar as the key, drawn from real misconceptions (source warnings, rookie mistakes in the script).
- No "all/none of the above", no double negatives, no trick wording, no overlapping options.
- Numeric distractors: other numbers from the same source (e.g. 30 vs 90 days, $25 vs $60) — teaches discrimination.

## Feedback
- Every option gets feedback: why right/wrong in ≤ 25 words, restating the rule; cite the rule, not "Incorrect".
- `explanation` = the general rationale (shown after answering) with a source pointer ("Expense Policy §4.1").

## Grounding
- `source_ids` on every item (the fact behind the key); `general_knowledge: true` only when allowed and labelled.
- Scenario numbers that are fictional (a $12 taxi) are fine; the rule tested must be sourced.

## Kinds
| kind | Items | Notes |
|---|---|---|
| pre-test | 1 per objective, mixed difficulty | diagnostic; no pass mark gating |
| knowledge-check | 3–5 per lesson | in-lesson; storyboard `quiz` scenes reference item ids (`props.quiz_item`) |
| post-test | 2+ per objective, pass_mark 80 | SCORM-tracked |
| scenario | 3–6 scenario items | branching-format companion |
| flashcards | 1 per key term/rule | from glossary + policy facts |

## Arabic
- `language: ar-EG|ar-MSA` quizzes: stems and options in Arabic (`stem`, `text`), or bilingual with `stem_ar`/`text_ar`.
- Same register as the lesson (Egyptian colloquial for ar-EG). Digits: follow the lesson's numeral choice.
- True/false labels: صح / غلط (ar-EG) or صحيح / خطأ (ar-MSA).

## Exports
- `to_gift.py` → Moodle GIFT (ordering exported as matching to positions; flashcards as description).
- `to_csv.py` → flat CSV (UTF-8 BOM) for spreadsheets/other LMS importers. SCORM packaging is done by the render-lesson skill.
