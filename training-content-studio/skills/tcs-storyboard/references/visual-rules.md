# Visual rules: text, images, b-roll, cast, voices, theme, aspect

## On-screen text
- ALL visible text comes from template props (never from images or b-roll). `on_screen_text` = derived list of those strings
  (`derive_text.py --write`) for translation, accessibility and grounding. Re-derive after any props edit.
- Digits on screen, words in narration. Every number on screen must also appear in a claim of that scene.
- Arabic storyboards: props in Arabic, English terms allowed (bidi rules in tcs-localize `references/rtl-rules.md`).

## Generated images (`generated_images[]`)
- Use for metaphors, scenes without stock footage, backgrounds. Prompt = subject + setting + style + palette, then **always end with**
  `no text, no letters, no numbers, no signage, no logos`.
- Style default: "flat vector illustration, clean shapes, soft shadows, navy #363E77, blue #006AB3, cyan #6FC7DA accents,
  light background #F4F7FB" (theme `neutral`). Never cream/terracotta palettes.
- No real people, celebrities, brands, uniforms with insignia; diverse neutral characters; screens shown blank or abstract.
- `character_ref` = persona id when an image must match a cast persona.
- Example: `"Office worker photographing a paper receipt with a phone at a café table, flat vector illustration, navy and cyan palette, light background, no text, no letters, no numbers, no signage, no logos"`.

## B-roll (`broll_shots[]`)
- `query` = 4–9 concrete words (who/what/where/action), provider `pexels` default; `min_s` ≥ scene length (clips loop/slow
  to fill, but long clips look better). Reject: visible logos/text, hooded hackers, matrix code, off-topic.
- Max one b-roll scene per 20 s; pair with `chips` (≤ 2 topic words) or `broll_panel` points.

## Cast and voices
- `cast[]` = persona ids used anywhere (people, bubbles, beats, whiteboard, comic). Base: host learner manager mentor customer
  rookie colleague exec support; domain packs add more (security: `vex`, the only persona in the attention colour).
- `voices` keys = every narration `who` (narrator + speaking personas). Default OpenAI `gpt-4o-mini-tts`; narrator `marin`;
  personas distinct voices from `assets/voices.yaml` slots (learner ash, manager onyx, mentor echo, customer coral, rookie ballad, colleague sage, exec cedar,
  support nova; pack personas e.g. vex verse from `domains/<pack>/personas.yaml`) with acting `instructions`. Arabic: same voices, dialect in instructions (tcs-localize `references/voices.md`).
- Cartoon: every story scene has a pose/expression change on a cue and a bubble for the key line; people ≤ 5.

## Theme and brand
- `theme.preset: neutral` (navy #363E77, blue #006AB3 → cyan #6FC7DA, attention orange #FF6700, bg #F4F7FB) unless the
  domain pack/user brand says otherwise. `theme.logo: null` by default (logo slot optional, empty unless asked).
- Fonts: latin Poppins/Inter, arabic Cairo / IBM Plex Sans Arabic / Noto Kufi Arabic, mono IBM Plex Mono, hand Caveat.
- Compliance line (e.g. ISO 27001 A.6.3 evidence) → `theme.evidence_line` / outro `evidence_line`.
- Design lessons: no one-sided thick accent borders; no fades that read as blank frames; text ≥ 24 px at 1080p.

## Aspect
- `16:9` default; `9:16` for `video-vertical` targets (series/micro-learning) — fewer items, bigger type; `1:1` for social/LMS tiles.
- One storyboard per aspect if layouts differ materially; otherwise renderers adapt from 16:9.

## Durations
- Scene estimate = lead 0.35 + words/wpm + pauses (0.28/line, quiz 2.2) + hold 0.75; `duration_hint_s` from the script stage;
  `min_s` for scenes that need time without narration (b-roll breathers, cartoon actions).
