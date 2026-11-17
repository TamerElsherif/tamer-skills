# Writing Arabic narration (Egyptian colloquial and MSA)

Write Arabic natively from the objectives and facts — do not translate the English script line by line
(adaptation rules: tcs-localize). Both variants are RTL and cue markers work the same (`^` before the trigger words).

## Register
| | Egyptian (ar-EG, default for Egyptian staff) | MSA (ar-MSA, pan-Arab / formal compliance) |
|---|---|---|
| Tone | warm colleague, Cairene colloquial | clear, neutral, modern, not classical |
| Address | إنت / حضرتك (formal), plural إنتوا | أنت / أنتم, or impersonal (يجب على الموظف) |
| Demonstratives | ده، دي، دول | هذا، هذه، هؤلاء |
| Negation | مش، ما…ش | لا، ليس، لم |
| Future | هـ (هنشوف) | سـ / سوف (سنرى) |
| Why/how/what | ليه، إزاي، إيه | لماذا، كيف، ماذا |
| Because | عشان | لأن / لكي |
| Now | دلوقتي | الآن |
| Example opener | خلّينا نشوف مثال | لنأخذ مثالاً |
| Call to action | لو شاكك، كلّم… | إذا كنت تشك، تواصل مع… |

Mixing: in ar-EG keep technical/product terms in English when staff say them that way (Expense app, MFA, approver),
written in Latin script; in ar-MSA prefer the Arabic term with English once in parentheses on screen, not in narration.

## Speakable numbers
- Narration: words (`speakable.py --lang ar-EG`): 25 → خمسة وعشرين, 18% → تمنتاشر في المية, $1,000 → ألف دولار.
- MSA: خمسة وعشرون, ثمانية عشر بالمائة. Grammatical agreement of counted nouns is simplified by the helper — reread.
- Money: say the currency the audience uses (جنيه for Egypt) only if the source states it; never convert currencies yourself.
- On-screen: Western digits (0-9) by default for Egyptian corporate audiences; choose Eastern Arabic digits (٠-٩) only if
  the org style requires it — be consistent (tcs-localize `rtl_lint.py` checks).

## TTS notes (OpenAI gpt-4o-mini-tts)
- Voice `marin` works for both EN and Egyptian Arabic; put the dialect in `instructions` ("Egyptian Arabic, Cairene colloquial").
- Add tashkeel only to disambiguate a word the voice mispronounces (e.g. حَساب vs حِساب).
- Short sentences; avoid long English insertions (voice switches accent); spell acronyms (إم إف إيه or keep "MFA").
- Clips sometimes come back truncated in Arabic → renderer checks wpm outliers; keep lines ≤ 2 sentences to limit damage.

## Example (ar-EG, rules scene)
```
## s03_rules | rules | O1
narrator: فيه تلات قواعد بسيطة. ^ أي مصروف فوق خمسة وعشرين دولار لازم يبقى معاه إيصال. ^ قدّم الطلب خلال تلاتين يوم. ^ ومتقسمش فاتورة واحدة عشان تهرب من حد الموافقة.
claim: A receipt is required for every expense over $25. [S01#c1]
```
(Claims may stay in the source language; grounding matches numbers and cited facts.)
