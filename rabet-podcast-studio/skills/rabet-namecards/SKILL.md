---
name: rabet-namecards
description: Create and place Rabet (رابط) Podcast name cards — the animated lower third with the Arabic name and English title (aqua bar, white sweep reveal), rendered as transparent ProRes MOVs — for new guests, new titles or new episodes, and burn them into a video on the right shot. Use when the user says "make a name card for <guest>", "Tamer's title changed", "add the name cards", "lower third", or when a new guest appears. Part of the rabet-podcast-studio set.
---

# Rabet name cards

Full-frame transparent card (overlay at 0,0), bottom-left: aqua bar grows, a white block sweeps right and reveals the
Arabic name (Alexandria 800) and the English title in capitals, then hides them again. 6 s (or 4.3 s "fast").

## Rules (do not regress)
1. **Use the name and title the user gives**, never photo file names. House titles (2026):
   تامر الشريف — IT & AI Transformation Expert · حسام عزت — Software Engineering Advocate ·
   هيثم فؤاد — Founder - prodXeed. Ask for any new guest's exact Arabic spelling and title.
2. **One card per speaker, early, on a SOLO shot of that speaker** (never a split/wide shot) — check shots
   (`../rabet-episodes` `shots.json`, or look at frames). Hold it ≥ 6.8 s of the same shot.
3. **Burned-in cards in a master** (Ep 3 had them): don't add a second one; list them in the spec `burned_in`, and tell
   the user if a burned card shows an outdated title.
4. Name cards bottom-left, subscribe pop-up bottom-right — never at the same moment.
5. RTL: the Arabic name line is RTL, the title is LTR on its own line (no mixed line starting with English).
6. Look at the preview JPG before using a new card.

## Usage
```
python scripts/make_namecard.py --name "هيثم فؤاد" --title "Founder - prodXeed" --key haitham           # 4K, 6 s
python scripts/make_namecard.py --name "تامر الشريف" --title "IT & AI Transformation Expert" --key tamer --speed 1.4
python scripts/add_namecard.py "<video>.mp4" NameCard_tamer.mov@0:44 NameCard_haitham.mov@1:58 [--test]
```
`make_namecard.py` → `NameCard_<key>.mov` (+ `_preview.jpg`) in `--out-dir`, default the folder of the existing
cards in `~/.rabet-reels.json` `episodes.name_cards`. Then register it there (`"Haitham": "<path>"`) so
rabet-episodes / rabet-teaser can place it with `"cards": "auto"` or `"card": "Haitham"`.
`--res 1080` renders ~4× faster for 1080p-only use. Rendering needs Node + `npx hyperframes@0.8.163`.

Template: `templates/namecard.html` (`{{NAME}}`, `{{TITLE}}`, `{{DURATION}}`, `{{SPEED}}`). Fonts come from
`../rabet-reels/assets/fonts`.
