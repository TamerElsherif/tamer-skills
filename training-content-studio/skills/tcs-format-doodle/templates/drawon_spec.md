# Draw-on sequence spec — <scene id>

Board title: <≤ 5 words>   Aspect: 16:9 | 9:16 | 1:1   Duration ~<s>

| cue | kind | cast/pose/expr or icon | text (≤4 words) | x | y | w×h / to | color | spoken trigger word |
|---|---|---|---|---|---|---|---|---|
| 0 | person | vex / rub / sly | | 380 | 880 | | ink | "Meet…" |
| 1 | arrow | | | 560 | 600 | to 1180,600 | attention | "goes straight…" |
| 1 | person | learner / phone / neutral | | 1400 | 880 | | ink | |
| 2 | note | | tricks people | 760 | 520 | | ink | "tricks" |
| 3 | icon | key | | 1600 | 300 | | attention | "password" |
| 3 | circle | | | 1600 | 300 | 180×180 | attention | |

Checks: max cue + 1 ≤ number of `^` in narration · ≤ 8 items · ≤ 3 items per cue · arrows land on targets · 96 px margins.
→ Copy rows into `scenes[].props.items[]` of a `whiteboard` scene.
