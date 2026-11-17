# Placeholders

Word-free stand-ins so a lesson always renders end-to-end when an asset is missing (no API key, no licensed music,
no B-roll yet). Renderers substitute them and set `storyboard.assets[] = {slot, status: "placeholder", path}`;
QA (`QUALITY.md` → assets) blocks release while any `placeholder` remains unless the run is a draft.

Generate (stdlib only): `.venv/bin/python assets/placeholders/make_placeholders.py` → `assets/placeholders/generated/`

| File | Stands in for | Notes |
|---|---|---|
| `missing_16x9.png` / `missing_9x16.png` / `missing_1x1.png` | B-roll clip, `image` scene, background | loop as a still |
| `missing_character.png` | generated character art | kit SVG personas normally make this unnecessary |
| `missing_thumb.png` | thumbnails / LMS tiles | 320×180 |
| `missing.svg` | any vector slot (logo slot must stay EMPTY, not placeholder) | |
| `music_bed_placeholder.wav` | music bed | 4 s silence, loop |
| `sfx_placeholder.wav` | any SFX name | soft 880 Hz blip, −18 dBFS |
| `narration_placeholder_tone.wav` | TTS when `voices.*.provider: placeholder` | 1 s 440 Hz tone; renderer stretches to estimated line length (words ÷ wpm) |
| `silence_1s.wav` | gaps, padding | |

The glyph (frame + hills + sun + diagonal slash) contains no text, digits or logos, so placeholders never leak
untranslated words into Arabic renders.
