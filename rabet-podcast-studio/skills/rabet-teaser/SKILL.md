---
name: rabet-teaser
description: Make a Rabet (رابط) Podcast teaser / promo / highlights / cold open — the most exciting, curiosity-triggering moments of an episode cut into a short montage (hard cuts at real word gaps, name cards, optional music bed, logo sting) — for a full episode (30–75 s), a mini episode (15–30 s cold open) or a reel (3–10 s hook). Use when the user says "teaser", "promo", "trailer", "highlights", "cold open", "hook for this episode/reel", or "what should open the episode". Part of the rabet-podcast-studio set.
---

# Rabet teaser / promo

## 1. Pick the moments (the part that matters)
Read the whole transcript (rabet-episodes `prep_episode.py` → `transcript.txt`, or the reel's words). Score lines:
- **Contrarian / myth-busting claim** — «الـ Product Manager مش Project Manager», «الكودينج ليابيليتي مش أسد»
- **A number or a concrete case** — «Nokia كانت واخدة market share 70 %», «60 % من الكود مكتوب بـ AI»
- **A consequence or tension** — «اللي مش هيقدر يكتشف طريقه بدري ممكن يتساب في السكة»
- **An open question the episode answers** — «مين هيتأخر؟», «هل الـ AI هياخد شغلك؟»
Avoid: greetings, inside jokes without context, lines that need the previous sentence, invented claims (rabet-reels rule 1).

| Target | Length | Pieces | Shape |
|---|---|---|---|
| Full-episode teaser (Ep 2/3 style) | 30–75 s | 5–9 | question → stakes → 2–3 strongest claims → open loop; card on each speaker's first piece; logo sting |
| Mini-episode cold open | 15–30 s | 2–3 | strongest claim + the question the episode answers (goes in the spec `hook`) |
| Reel hook | 3–10 s | 1 | one complete micro-idea (rabet-reels rules 1, 10) |

Each piece is a **complete micro-idea**: starts on a sentence start, ends on a sentence end; never ends on
«أو / و / ف…», never starts on «كده / فالحقيقة» (rabet-reels rules 9–10). Alternate speakers; order for curiosity,
not episode order. Present the list (time, speaker, first … last words, why it hooks) before rendering when the
user asked to review.

## 2. Build
```
python scripts/make_teaser.py teaser.json            # spec format in the script docstring
python ../rabet-reels/scripts/edge_check.py <source> <out>.cuts.json   # REQUIRED: whole first/last words
```
- In/out times only need to be near the words: every edge is moved into a real word gap by rabet-reels `cutsafe`
  (rule 13). A `cutsafe: … no word gap` warning or a `CutError` = the speech runs on → pick another phrase break,
  don't force it. Find good edges with `../rabet-episodes/scripts/pauses.py <episode.json> T`.
- edge_check lists each piece's words with offsets: a first word with a negative offset (e.g. `نوكيا[-0.22]`) is
  clipped → move the in earlier to the previous pause; a stray syllable at the end → move the out.
- `"card": "<Name>"` on a piece adds that speaker's name card (from `~/.rabet-reels.json` episodes.name_cards) on
  a solo shot. `"end": "intro"` appends the logo sting. `"music"` adds a bed ~15 dB under the voice, ducked on speech
  (Ep 3 v3 used the Ep 2 bed, separated with Demucs — music only on teasers, never on reels).
- For a mini episode, put the snapped pieces into the rabet-episodes spec `hook` instead of rendering separately.
- For the full episode: teaser → intro logo → episode. Every later time (chapters, pop-ups) shifts by the teaser
  length — say so in the YouTube description notes.

## 3. Check
Pull frames at each cut and each card from the rendered file; listen to every joint. Report what you didn't watch.
