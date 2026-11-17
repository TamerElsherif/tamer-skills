# Asset manifest

What a run needs, what is optional, specs, and how licences are recorded. Nothing licensed is shipped in this repo;
missing items fall back to `placeholders/` (word-free) and are listed in `storyboard.assets[]` with `status`.

## Required vs optional
| Slot | Required? | Default / file | Spec |
|---|---|---|---|
| Theme preset | required | `theme_presets.yaml` → `neutral` | colours pass `scripts/check_contrast.py` (AA 4.5:1 text) |
| Fonts | required | see Fonts | installed in renderer (kit) or system |
| Layout presets | required | `layout_presets.yaml` (16:9, 9:16, 1:1, print) | safe margins, min text 24 px @1080p |
| Caption style | required for video | `caption_styles.yaml` → `boxed` | ≤ 2 lines, ≤ 42 (Latin) / 38 (Arabic) chars, ≤ 17/15 cps |
| TTS voice per language | required for video/lesson VO | `voices.yaml` | OpenAI primary; ElevenLabs/Azure alternates |
| Personas | required for cartoon/comic/branching | `characters/personas.yaml` + kit SVG cast | flat vector, no real people |
| Music beds (4) | optional | `audio.yaml` → explainer, cartoon, whiteboard, executive | instrumental, loopable, −16 LUFS mix |
| SFX (12 names) | optional | `audio.yaml` → `sfx` | WAV 48 kHz, ≤ 2 s |
| B-roll | optional (explainer) | fetched per `broll_shots[]` (Pexels/Pixabay) | ≥ 12 s, 1080p+, no logos/text |
| Logo | optional, **empty by default** | `brand.yaml: logo: null` | SVG preferred; only if client supplies + asks |
| Intro / outro sting | optional | `brand.yaml: intro/outro: null` | ≤ 4 s, no audio clash with VO |
| Lower-thirds | optional | kit component, `brand.yaml: lower_third_style` | clean/bar; no one-sided thick accent borders |
| Generated images | optional | storyboard `generated_images[]` | prompts end "no text, no letters, no numbers, no signage, no logos" |
| Domain pack | optional | `domains/<pack>/` | glossary, personas, scenarios, mock-up presets |

## Fonts (all SIL Open Font License 1.1 — free for commercial use, embedding allowed; keep the OFL text with redistributed files)
| Role | Family | Scripts | Use |
|---|---|---|---|
| Latin headings | Poppins | Latin | titles, big numbers |
| Latin body | Inter | Latin | body, captions |
| Arabic body (default) | IBM Plex Sans Arabic | Arabic + Latin | body, captions, decks |
| Arabic friendly | Cairo | Arabic + Latin | cartoon bubbles, social captions |
| Arabic display | Noto Kufi Arabic | Arabic | titles, section cards |
| Mono | IBM Plex Mono | Latin | code, URLs in mock-ups |
| Hand | Caveat | Latin | whiteboard notes (Arabic notes fall back to Cairo) |
Source: Google Fonts (verify licence file at download; record in the licence table below).

## Layout presets per aspect
See `layout_presets.yaml`: 16:9 (1920×1080, margin 96), 9:16 (1080×1920, platform-unsafe top 220 / bottom 380),
1:1 (1080×1080), print (A4, Letter, desk card) and RTL mirroring rules.

## Audio
- Music beds: `explainer` (light corporate), `cartoon` (playful), `whiteboard` (soft acoustic), `executive` (minimal piano).
  Sources: licensed library, royalty-free with licence file, or AI-generated with a licence that allows commercial use.
- SFX names: beeps, chime, ding, pop, reel, ring, scratch, sparks, whoosh, womp, zap, zipper.

## TTS voice slots
| Language | OpenAI (gpt-4o-mini-tts) | ElevenLabs alt | Azure alt |
|---|---|---|---|
| English (US/GB) | `marin` + trainer instructions | multilingual v2 narrator (audition) | en-US-AvaMultilingualNeural / en-GB-SoniaNeural |
| Egyptian Arabic | `marin` + "natural Egyptian Arabic (Cairene colloquial)…" | multilingual v2, Egyptian-capable voice (audition) | ar-EG-SalmaNeural / ar-EG-ShakirNeural |
| MSA | `marin` + "clear Modern Standard Arabic…" | multilingual v2 (audition) | ar-SA-ZariyahNeural / ar-SA-HamedNeural |
Character voices: `voices.yaml` (host marin, learner ash, manager onyx, mentor echo, customer coral, rookie ballad,
colleague sage, exec cedar, support nova; domain packs add e.g. vex verse). AI voices: disclose per client policy.

## Characters
`characters/<id>/character_sheet.md` + locked `prompt.txt` for host, learner, manager, mentor, customer, rookie;
`characters/personas.yaml` maps every id → kit cast look. Reference images = kit SVG persona renders (same ids).

## Licence recording (fill for every non-generated, non-OFL asset, and for AI-generated media)
Record in `storyboard.assets[]` (`slot`, `status`, `path`, `license`) and in the run's `assets_licenses.yaml`:

| Field | Example |
|---|---|
| slot | `music.explainer`, `broll.hook`, `voice.narrator.ar-EG`, `logo` |
| source / provider | Pexels, Pixabay, client, OpenAI TTS, ElevenLabs, human talent |
| title / id / url | clip URL or file id |
| author / talent | creator name or "AI-generated" |
| license | e.g. "Pexels License", "OFL-1.1", "Client-owned", provider ToS name |
| attribution_required | true/false (+ text) |
| commercial_use | true/false |
| retrieved_at | ISO date |
| consent (voices/likeness) | talent release reference, term, territory |
| restrictions | e.g. "no broadcast", "internal use only" |

QA blocks release if any shipped asset has `license` empty (see `QUALITY.md`).
