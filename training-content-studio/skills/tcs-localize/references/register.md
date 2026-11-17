# Adapting EN ↔ AR (Egyptian vs MSA) — not literal translation

## Choose the register
| Situation | Register |
|---|---|
| Egyptian staff, internal training, friendly tone (default for Egyptian orgs) | **ar-EG** Cairene colloquial |
| Pan-Arab audience, formal compliance/legal, regulator-facing, printed policy | **ar-MSA** |
| Mixed Gulf/Levant/Egypt audience | ar-MSA narration + simple vocabulary |
On-screen text: ar-EG lessons may use light MSA on boards (titles read cleaner) but keep labels short and consistent;
narration is fully colloquial. Never mix registers inside one sentence.

## Adaptation rules (EN → AR)
1. Translate meaning per scene, then re-fit the cues: same number of `^` in the same order, before the words that
   name each revealed item. Reorder clauses freely around them.
2. Shorter is better: Arabic TTS runs ~10 % slower (wpm × 0.9). Cut filler, not content; target the same duration.
3. Address: ar-EG "إنت/حضرتك", imperative singular ("صوّر الإيصال"); ar-MSA "أنت" or impersonal ("يجب على الموظف").
4. Keep English product/UI names as they appear on screen (Northwind Expenses, New Claim); ar-EG narration keeps common
   English tech terms (MFA, email → "الإيميل"); glossary `keep` field decides.
5. Numbers: words in narration (`tcs-scriptwriter/scripts/speakable.py --lang ar-EG`), digits on screen (one numeral system).
6. Idioms/humour: replace with local equivalents or drop; cartoon dialogue rewritten in character, not translated.
7. Claims stay as written in the source language (grounding needs them); only narration/props/titles are localized.
8. Character names in bubbles come from persona `display_name.ar` (assets/characters/personas.yaml).

## AR → EN
- Source Arabic (often Egyptian meeting recordings): translate to plain international English; drop colloquial fillers
  (يعني، بقى، طب); resolve implicit subjects; keep Egyptian examples unless cultural swap needed.
- wpm × 1/0.9; en-US spelling unless the course uses en-GB.

## Egyptian ↔ MSA quick map
| EN | ar-EG | ar-MSA |
|---|---|---|
| this / these | ده، دي / دول | هذا، هذه / هؤلاء |
| not | مش | ليس / لا |
| we will see | هنشوف | سنرى |
| why / how / what | ليه / إزاي / إيه | لماذا / كيف / ماذا |
| because / so that | عشان | لأن / لكي |
| now | دلوقتي | الآن |
| don't open it | متفتحوش | لا تفتحه |
| let's | يلا / خلّينا | لِنـ / دعونا |
| check it | اتأكد منه | تحقّق منه |
| report it | بلّغ عنه | أبلِغ عنه |
`rtl_lint.py` flags ar-EG narration with no colloquial markers and ar-MSA narration with several.
