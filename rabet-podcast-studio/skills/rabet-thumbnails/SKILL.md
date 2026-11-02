---
name: rabet-thumbnails
description: Create Rabet (رابط) Podcast thumbnails — 16:9 YouTube thumbnails for full and mini episodes from an open, extendable style catalog (classic grid/board/word = A/B/C, collage, dark, giant word, stage, and any style added later; 1280×720) and 9:16 covers for Reels, YouTube Shorts, TikTok, Instagram and Facebook (1080×1920, with a cover-intro version) — using speaker cut-outs from the episode, the Rabet brand and RTL-safe Arabic headlines. Use when the user asks for a thumbnail, cover, poster frame, "thumbnail variants", a thumbnail "in this style" / like a reference image, a new thumbnail style, or a Shorts/Reels/TikTok cover. Part of the rabet-podcast-studio set.
---

# Rabet thumbnails

Scripts live in the shared engine `../rabet-reels` (same fonts, logo and templates as the reels).

## Styles are an open catalog
YouTube thumbnail styles are not a fixed A/B/C set. Each style is one file in `../rabet-reels/scripts/yt_styles/`;
`python ../rabet-reels/scripts/yt_thumbs.py --list` prints every installed style with its look, guest count and
text fields. Any combination can be rendered in one run, and the classic Ep2/Ep3 styles stay available.

| Style | Look | Guests |
|---|---|---|
| **grid** (classic A) | navy grid, outlined cut-outs left, episode chip + logo, cream l1 + orange tilted l2 box + kicker | 2–3 |
| **board** (classic B) | cream board, navy slanted block with the outlined episode number, navy l1 + orange l2 + English chips | 2–3 |
| **word** (classic C) | grid layout with a huge aqua English word between l1 and the orange l2 box | 2–3 |
| **collage** | big cut-outs in front of two pinned topic photos on blue smoke, huge white l1 + orange l2 bar | 3 |
| **dark** | dark close-up, small aqua kicker + l1 with orange l2 tilted low centre, «#N» top right | 3 |
| **giant** | bright blurred office, huge orange word behind the speakers, name tags, navy bottom bar | 3 |
| **stage** | navy curtain + teal spotlight, aqua frame, stacked centre title with orange l2 between cream rules | 3 |

This table can fall behind; `--list` is the source of truth (a style added later shows up there first).

## Pick the style first: ask if the user didn't name one
Before building any 16:9 thumbnail, check whether the user named one or more styles, said "the classic ones / A, B
and C" (= grid, board, word), or attached a reference image. **If not, run `--list` and ask them** (AskUserQuestion,
multi-select, one option per style with its look; more than 4 styles: ask in text or group them) and wait. Don't
default silently. Strongest at phone size: collage (largest faces + topic pictures), then giant (largest word); for a
full episode suggest those two as a YouTube "Test & Compare" pair. A reference image that matches no style: build it
as a new style (below) after confirming.

## 16:9 YouTube (full or mini episode)
`python ../rabet-reels/scripts/yt_thumbs.py spec.json <style> [<style> ...]` → `<out>/<prefix>_<style>.png/.jpg`.
With no style it prints the list instead of rendering. Spec fields are in the `yt_thumbs.py` docstring:
- Shared text `l1`, `l2`, `k` for every style; per-style text in `"text": {"<style>": {...}}` (pair each title option
  with one thumbnail, e.g. board with its own l1/l2/chips, word with `sw`).
- `guests` listed left, centre, right (the host in the centre with `"host": true` gets the aqua tag). Classic styles
  place guests by each guest's `left`/`top`/`width` (back to front, front speaker last); the other styles have
  defaults that fit trimmed 1080p cut-outs facing the centre. Nudge any style with `"pos": {"<style>": {"<id>":
  [left, top, width]}}` after looking at the render. `fade_right` per guest fades the right edge (mic clips,
  cropped shoulders).
- `pins` = 2 photos for collage; optional `mid` (stage), `giant`/`small` (giant), `num` (dark, board).
- `"names": {"grid": ""}` sets the output suffix per style. `make_episode_thumbs.py spec.json` still renders the
  three classic styles as `<prefix>`, `_B`, `_C` from old specs with `a`/`b`/`c` blocks.
- Collage pins: two free photos that show the topic at a glance (e.g. wireframe notebook + falling chart for "why
  products fail"): `python ../rabet-reels/scripts/yt_thumbs.py stock "<query>" <dir>` (Pexels, `PEXELS_API_KEY`),
  look at them, pick dark/high-contrast ones. Backgrounds (smoke, office) ship in `../rabet-reels/assets/thumb_bg`.
  Ask before using paid image generation.

## Adding a style
1. Copy the closest file in `yt_styles/` to `yt_styles/<name>.py` (lowercase, one word). Set `NAME`, `LOOK`
   (one line), `GUESTS` (min, max), `TEXT` (fields it reads) and write `render(s)` returning `(css, body)`; reuse
   `_common.py` (`CUT` css, `cut()`, `tags()`) or `_classic.py`. New background images go in `assets/thumb_bg`.
2. Brand only: the colour tokens in `_common.HEAD`, Lalezar for headlines, Alexandria for small text, the logo, no
   coloured glow shadows, RTL rules below.
3. Render it on a real episode spec, look at it, tune the default positions, then add a row to the table above and
   (when publishing the skill set) an example image to the plugin README.

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
