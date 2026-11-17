# Branching script — <lesson_id> · <title>

Dilemma: <one line> · Ideal behaviour: <rule + source id> · Skin: cartoon | comic | doodle | explainer

| node | scene id | template | lines (who: text, `^` cues) | choices (id → next, correct) | outcome / score | feedback (what happened + red flag + do instead) |
|---|---|---|---|---|---|---|
| n_intro | b01_setup | cartoon | narrator: …; caller: ^ … | | continue | |
| n_intro | b02_choice1 | decision | narrator: What do you do? | a → n_bad1 ✗ · b → n_mid ✓ | | |
| n_bad1 | b03_bad1 | statement | mentor: ^ … | | bad / 0 | |
| n_mid | b04_mid | cartoon | … | | continue / 5 | |
| n_mid | b05_choice2 | decision | … | a → n_bad2 ✗ · b → n_good ✓ | | |
| n_bad2 | b06_bad2 | statement | | | bad / 2 | |
| n_good | b07_good | cartoon | | | good / 10 | |
