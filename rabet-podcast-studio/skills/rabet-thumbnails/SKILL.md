---
name: rabet-thumbnails
description: Create Rabet (رابط) Podcast thumbnails — 16:9 YouTube thumbnails for full and mini episodes (classic A/B/C variants plus collage, dark, giant-word and stage styles, 1280×720) and 9:16 covers for Reels, YouTube Shorts, TikTok, Instagram and Facebook (1080×1920, with a cover-intro version) — using speaker cut-outs from the episode, the Rabet brand and RTL-safe Arabic headlines. Use when the user asks for a thumbnail, cover, poster frame, "thumbnail variants", a thumbnail "in this style" / like a reference image, or a Shorts/Reels/TikTok cover. Part of the rabet-podcast-studio set.
---

# Rabet thumbnails

Scripts live in the shared engine `../rabet-reels` (same fonts, logo and templates as the reels).

## Pick the style first: ask if the user didn't name one
Before building any thumbnail, check whether the user named a style (or attached a reference). **If not, ask them**
(AskUserQuestion, multi-select) and wait; don't default silently. Offer the styles below with a one-line look each.
For a full episode, recommend **collage** plus **giant** for a YouTube "Test & Compare" pair. A reference image counts
as a choice: build the closest style and match the reference.

| Style | Look | Script |
|---|---|---|
| **classic A/B/C** | A navy grid + cut-outs left + orange l2 box · B cream board + outlined number · C huge aqua English word | `make_episode_thumbs.py` |
| **collage** | big cut-outs in front of two pinned photos on blue smoke, huge white l1 + orange l2 bar | `make_episode_styles.py` |
| **dark** | dark close-up, small aqua kicker + l1 with orange l2, tilted low centre, «#N» top right | `make_episode_styles.py` |
| **giant** | bright blurred office, huge orange word behind the speakers, name tags, navy bottom bar | `make_episode_styles.py` |
| **stage** | navy curtain + teal spotlight, aqua frame, stacked centre title with l2 between cream rules | `make_episode_styles.py` |

Strongest at phone size: collage (largest faces + topic pictures), then giant (largest word). Dark has small text,
stage is busier; use them when the user wants that mood.

## 16:9 YouTube (full or mini episode)
Classic: `python ../rabet-reels/scripts/make_episode_thumbs.py spec.json` → `<prefix>.jpg/.png`, `_B`, `_C` (1280×720).
- **A** navy grid, cut-outs left with a white outline, «الحلقة …» chip + logo, l1 (cream) + l2 (orange tilted box) + kicker.
- **B** cream board, navy slanted block with the outlined episode number, l1 navy + l2 orange + English chips.
- **C** like A with a huge aqua English word between l1 and l2.
Spec fields are in the script docstring (`out`, `prefix`, `ep`, `num`, `guests[{id,img,name,left,top,width}]`, `a`, `b`, `c`).

Reference styles: `python ../rabet-reels/scripts/make_episode_styles.py spec.json [collage dark giant stage]` →
`<prefix>_<style>.png/.jpg`. Exactly 3 guests, listed left, centre, right (centre = host, `"host": true` gives the
aqua name tag). Spec: `l1`, `l2`, optional `k` (dark kicker), `mid` (stage middle line), `giant`/`small` (giant word
and line, default l2 / l1 + "…"), `pins` (2 collage photos), `fade_right` per guest (fades the right edge: mic
clips, cropped shoulders), `pos` per-style overrides `[left, top, width]`. Defaults fit trimmed 1080p cut-outs
facing the centre; nudge with `pos` after looking at the render.
- Collage pins: two free photos that show the topic at a glance (e.g. wireframe notebook + falling chart for
  "why products fail"): `python ../rabet-reels/scripts/make_episode_styles.py stock "<query>" <dir>` (Pexels,
  `PEXELS_API_KEY`), look at them, pick dark/high-contrast ones. Backgrounds (smoke, office) ship in
  `assets/thumb_bg`. Ask before using paid image generation.

Cut-outs (EP1 recipe):
1. Scan frames (one every 10–12 s with the time printed) and pick, per person, a sharp frame with the face toward
   camera or the text side, mouth closed or neutral. Seeking is not frame-exact: re-check the exact frame you extract.
2. Crop away the burned-in logo and the neighbours, then `npx --yes hyperframes@0.8.163 remove-background in.png -o cut.png`.
3. Trim to the bounding box; cut away mic booms that point into the text area.
4. Order guests back → front (front speaker last = rightmost head). Heads stay at x < ~700; no head under the text;
   the back guest's face must stay visible (move them up/left rather than letting the front guest cover the eyes).
5. For the reference styles pick frames where each person faces the camera or the centre (left guest looking right,
   right guest looking left); a host who looks asleep or away gets a new frame. Eyes open, not mid-blink.
6. Look at every render before delivering (faces not covered, nothing sticking into the text, no hard cut edges).

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
