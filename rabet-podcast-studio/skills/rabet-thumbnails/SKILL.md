---
name: rabet-thumbnails
description: Create Rabet (رابط) Podcast thumbnails — 16:9 YouTube thumbnails for full and mini episodes (A/B/C variants, 1280×720) and 9:16 covers for Reels, YouTube Shorts, TikTok, Instagram and Facebook (1080×1920, with a cover-intro version) — using speaker cut-outs from the episode, the Rabet brand and RTL-safe Arabic headlines. Use when the user asks for a thumbnail, cover, poster frame, "thumbnail variants", or a Shorts/Reels/TikTok cover. Part of the rabet-podcast-studio set.
---

# Rabet thumbnails

Scripts live in the shared engine `../rabet-reels` (same fonts, logo and templates as the reels).

## 16:9 YouTube (full or mini episode)
`python ../rabet-reels/scripts/make_episode_thumbs.py spec.json` → `<prefix>.jpg/.png`, `_B`, `_C` (1280×720).
- **A** navy grid, cut-outs left with a white outline, «الحلقة …» chip + logo, l1 (cream) + l2 (orange tilted box) + kicker.
- **B** cream board, navy slanted block with the outlined episode number, l1 navy + l2 orange + English chips.
- **C** like A with a huge aqua English word between l1 and l2.
Spec fields are in the script docstring (`out`, `prefix`, `ep`, `num`, `guests[{id,img,name,left,top,width}]`, `a`, `b`, `c`).

Cut-outs (EP1 recipe):
1. Scan frames (one every 10–12 s with the time printed) and pick, per person, a sharp frame with the face toward
   camera or the text side, mouth closed or neutral. Seeking is not frame-exact: re-check the exact frame you extract.
2. Crop away the burned-in logo and the neighbours, then `npx --yes hyperframes@0.8.163 remove-background in.png -o cut.png`.
3. Trim to the bounding box; cut away mic booms that point into the text area.
4. Order guests back → front (front speaker last = rightmost head). Heads stay at x < ~700; no head under the text;
   the back guest's face must stay visible (move them up/left rather than letting the front guest cover the eyes).
5. Look at all three renders before delivering.

## 9:16 covers (Reels, Shorts, TikTok, Instagram, Facebook)
`python ../rabet-reels/scripts/make_thumb.py thumb.json thumb.png` — T1 big two-line question/claim, T2 cinematic
background + cut-out, T3 editorial quote (see `../rabet-reels/templates/thumb`).
- Key content inside the centre 4:5 (Instagram/Facebook grid crops 9:16 to 4:5 / 3:4; TikTok and Shorts cover the
  bottom ~20 % with UI): headline in the upper-middle, nothing important in the bottom 400 px.
- Logo ~175 px, high (top 120–150 px).
- Platforms with no cover picker: `python ../rabet-reels/scripts/add_cover.py` puts the thumbnail as a 1.2 s intro
  (+ whoosh). Ship only the cover version + `_thumbnail.png` (rabet-reels rule 14).

## Text rules (all thumbnails)
- RTL (rabet-reels rule 8): no line starts with an English word; big wrapped headlines carry no English; English goes
  mid-line («الـ AI بيكتب الكود») or in its own element (chips, the C word). l1 ≤ ~18 characters.
- A question or tension, B2B tone, no clickbait claims the episode doesn't make (rule 1). Pair each title option
  with one thumbnail.
- Brand: navy #10335A · deep #0B2340 · teal #1AAAC1 · aqua #07C3BE · orange #FF6600 (accent only) · cream #FDF9F5;
  no coloured glow shadows.
