# Words-per-minute budgeting

| Audience level | English wpm | Arabic wpm (−10 %) | Notes |
|---|---|---|---|
| beginner | 130 | 117 | new topic, non-native listeners, procedures |
| beginner-intermediate / mixed | 135 | 122 | default for all-staff courses |
| intermediate | 140 | 126 | |
| advanced | 150–160 (155) | 135–144 (140) | experts, refreshers, exec summaries |

Arabic is slower in TTS and denser per word (clitics), so the same content runs ~10–25 % longer in Arabic.
Plan Arabic lessons with the Arabic wpm and the **same** target duration → fewer words, not faster speech.

## Formula
```
speaking_s  = target_s − scenes × (lead 0.35 + hold 0.75) − lines × pause 0.28 − quiz think-pauses (2.2 each)
words_total = speaking_s × wpm / 60
words/scene = words_total / scenes          (scene = 5–35 s; ~18 s average → scenes ≈ target_s / 18)
```
`script_md.py budget --minutes 3 --level beginner --lang en-US` prints the numbers.

| Target | Scenes (≈) | EN beginner words | AR-EG beginner words |
|---|---|---|---|
| 1 min (series micro) | 4 | ~100 | ~90 |
| 3 min | 10 | ~300 | ~270 |
| 5 min | 17 | ~500 | ~450 |
| 10 min | 33 | ~1000 | ~900 |

## Checks (`script_md.py check`)
- Estimated duration within ±15 % of `target_min` (warn) — trim or add an example, never speed up the voice.
- Scene estimate 5–35 s; sentence ≤ 25 words; digits in narration flagged.
- After TTS (renderer): actual wpm per line outside 0.6–1.6 × plan ⇒ truncated or garbled clip → regenerate (known
  gpt-4o-mini-tts Arabic truncation). Renderer owns that check; budget assumptions here.
- Aim for 100–120 % of an original video's length when remaking existing content (cover everything).
