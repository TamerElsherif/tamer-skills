# ASSETS — themes, layouts, captions, voices, audio, brand, personas

## assets/MANIFEST.md
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


## assets/theme_presets.yaml
```yaml
# Theme presets → storyboard.json `theme.preset` (+ optional `theme.colors` overrides).
# Rules: neutral is the default. Never cream/beige paper or terracotta ("Claude-like") palettes.
# `attention` (#FF6700) is ~2.9:1 on white: use it ONLY for fills, strokes, icons and the antagonist's outfit — never as
# text colour on light backgrounds (use `attention_text`) and never white text on an orange fill (use dark ink).
# Contrast is checked by: .venv/bin/python assets/scripts/check_contrast.py  (pairs in `text_pairs`, WCAG AA 4.5:1;
# `large_pairs` need 3:1 = text ≥ 24 px bold / ≥ 32 px regular at 1080p).
default: neutral
fonts:                      # shared by all presets unless overridden
  latin: Poppins            # headings; body may use Inter
  latin_body: Inter
  arabic: IBM Plex Sans Arabic   # alternates: Cairo (friendly, rounded), Noto Kufi Arabic (display/headings)
  mono: IBM Plex Mono
  hand: Caveat              # whiteboard notes (Latin); Arabic handwriting falls back to Cairo
presets:
  neutral:
    description: "Default corporate-neutral: navy ink, blue→cyan accents, one orange attention colour."
    colors:
      bg: "#F4F7FB"
      surface: "#FFFFFF"
      ink: "#363E77"          # headings + body text
      ink_strong: "#1E2350"
      muted: "#5A6385"
      accent: "#006AB3"
      accent_2: "#6FC7DA"     # gradient end (accent → accent_2); decorative, not for text on light bg
      attention: "#FF6700"
      attention_text: "#B34700"
      safe: "#1E7F4F"
      line: "#D5DCE8"
    gradient: ["#006AB3", "#6FC7DA"]
    text_pairs: [[ink, bg], [ink, surface], [muted, surface], [accent, surface], [attention_text, surface], [safe, surface], [surface, accent], [surface, ink]]
    large_pairs: [[ink_strong, attention]]   # text ON an orange fill (callout chips) must be dark ink, never white
  whiteboard:
    description: "Doodle format: pure white board, navy marker ink, orange attention marker, green ticks."
    colors:
      bg: "#FFFFFF"
      surface: "#FFFFFF"
      ink: "#1F2A5A"
      muted: "#5A6385"
      accent: "#006AB3"
      attention: "#FF6700"
      attention_text: "#B34700"
      safe: "#1E7F4F"
      line: "#1F2A5A"
    text_pairs: [[ink, bg], [muted, bg], [accent, bg], [attention_text, bg], [safe, bg]]
    large_pairs: [[ink, attention]]
  midnight:
    description: "Dark variant for executive/leadership or night-scene series; cyan accents on deep navy."
    colors:
      bg: "#0F1530"
      surface: "#1A2246"
      ink: "#F4F7FB"
      muted: "#B9C2DD"
      accent: "#6FC7DA"
      attention: "#FF8A3D"
      attention_text: "#FF8A3D"
      safe: "#5BD39A"
      line: "#2C3866"
    text_pairs: [[ink, bg], [ink, surface], [muted, surface], [accent, surface], [attention_text, surface], [safe, surface]]
    large_pairs: []
  executive:
    description: "Leadership audiences: more white space, navy-dominant, restrained accent use."
    colors:
      bg: "#FFFFFF"
      surface: "#F2F4F8"
      ink: "#1E2350"
      muted: "#4F587A"
      accent: "#006AB3"
      attention: "#FF6700"
      attention_text: "#A84300"
      safe: "#1E7F4F"
      line: "#D5DCE8"
    text_pairs: [[ink, bg], [ink, surface], [muted, bg], [accent, bg], [attention_text, bg], [safe, bg]]
    large_pairs: [[ink, attention]]
  high_contrast:
    description: "Accessibility preset (low vision / projectors): black on white, saturated darker accents."
    colors:
      bg: "#FFFFFF"
      surface: "#FFFFFF"
      ink: "#000000"
      muted: "#2B2B2B"
      accent: "#0047AB"
      attention: "#C2410C"
      attention_text: "#A33608"
      safe: "#0B6B3A"
      line: "#000000"
    text_pairs: [[ink, bg], [muted, bg], [accent, bg], [attention, bg], [attention_text, bg], [safe, bg]]
    large_pairs: []
```

## assets/layout_presets.yaml
```yaml
# Layout presets per aspect (px at the reference resolution). Renderers scale proportionally for other resolutions.
# Minimum on-screen text: 24 px at 1080p short side (body), captions per caption_styles.yaml.
"16:9":
  size: [1920, 1080]
  safe_margin: 96            # title/action safe; nothing important outside
  caption_zone: {y: 900, h: 140}          # bottom band reserved when captions are burned in
  title: {size: 64, weight: 700, max_lines: 2}
  body: {size: 36, min: 24, max_lines_per_item: 2}
  grid: {cols: 12, gutter: 32}
  max_bullets: 6
  person_feet_y: 1060
  broll_panel_width: 760     # frosted panel beside footage
  lower_third: {x: 96, y: 820, w: 900, h: 120}
"9:16":
  size: [1080, 1920]
  safe_margin: 80
  top_unsafe: 220            # platform UI (status bar, account name)
  bottom_unsafe: 380         # platform UI (captions, buttons) — keep key content above
  caption_zone: {y: 1380, h: 180}
  title: {size: 72, weight: 700, max_lines: 3}
  body: {size: 44, min: 32, max_lines_per_item: 2}
  grid: {cols: 6, gutter: 24}
  max_bullets: 4
  person_feet_y: 1700
  lower_third: {x: 80, y: 1200, w: 920, h: 140}
"1:1":
  size: [1080, 1080]
  safe_margin: 72
  caption_zone: {y: 900, h: 120}
  title: {size: 60, weight: 700, max_lines: 2}
  body: {size: 36, min: 28, max_lines_per_item: 2}
  grid: {cols: 6, gutter: 24}
  max_bullets: 4
  person_feet_y: 1020
  lower_third: {x: 72, y: 800, w: 820, h: 110}
rtl:
  mirror: [grid, lower_third, broll_panel, callout_side, panel_order, mindmap_growth]
  keep_ltr: [code_mock, url bars, email addresses, phone numbers, illustration SVG text anchoring]
print:                        # job-aid target
  A4: {size_mm: [210, 297], margin_mm: 15, body_pt: 11, title_pt: 22}
  Letter: {size_in: [8.5, 11], margin_in: 0.6, body_pt: 11, title_pt: 22}
  desk_card: {size_mm: [148, 105], margin_mm: 8, body_pt: 12}
```

## assets/caption_styles.yaml
```yaml
# Caption style spec (burned-in captions, WebVTT/SRT sidecars). Text comes from narration (minus `^`).
# Accessibility: WCAG 2.x 1.2.2 captions for prerecorded media; contrast ≥ 4.5:1 against the caption box.
default: boxed
rules:
  max_lines: 2
  max_chars_per_line: {latin: 42, arabic: 38}
  min_duration_s: 1.0
  max_duration_s: 6.0
  max_cps: {latin: 17, arabic: 15}     # characters per second reading speed
  gap_frames: 2
  line_break: "at phrase boundaries; never split a name, number or URL"
  speaker_labels: "only when off-screen or ambiguous: [Mentor]"
  sfx_tags: "[phone buzzes] — only when meaningful"
  numerals: {ar-EG: "match on-screen digits (Western 0-9 by default; Arabic-Indic ٠-٩ if brief says)", ar-MSA: same}
  bidi: "wrap Latin runs (URLs, product names) in LRI…PDI / U+2066…U+2069 inside Arabic captions"
styles:
  boxed:
    font: {latin: Inter, arabic: IBM Plex Sans Arabic}
    weight: 600
    size_px: {"16:9": 40, "9:16": 52, "1:1": 44}
    color: "#FFFFFF"
    box: {color: "#1E2350", opacity: 0.85, radius: 10, pad_x: 18, pad_y: 8}
    position: bottom_center
  outline:            # over busy B-roll
    font: {latin: Inter, arabic: IBM Plex Sans Arabic}
    weight: 700
    size_px: {"16:9": 42, "9:16": 56, "1:1": 46}
    color: "#FFFFFF"
    stroke: {color: "#0F1530", width: 4}
    position: bottom_center
  social_karaoke:     # 9:16 nudges, silent autoplay; word highlight from word timestamps
    font: {latin: Poppins, arabic: Cairo}
    weight: 800
    size_px: {"9:16": 64}
    color: "#FFFFFF"
    highlight: "#6FC7DA"
    stroke: {color: "#0F1530", width: 6}
    position: {y: 1380}
    max_words_per_chunk: 4
sidecars:
  formats: [vtt, srt]
  naming: "<lesson_id>.<lang>.vtt"
```

## assets/voices.yaml
```yaml
# TTS voice slots → storyboard.json `voices{}` (key = persona id = `who` in narration lines).
# Primary provider: OpenAI gpt-4o-mini-tts (voices: alloy ash ballad coral echo fable nova onyx sage shimmer verse marin cedar).
# Alternates are suggestions — audition before use; record the final choice in decisions.json.
# Known gotchas: occasional truncated clips (detect words-per-minute outliers and retry); Arabic numerals/acronyms read
# better spelled out in the narration text; keep each line ≤ ~40 words for stable prosody.
slots:
  narrator:
    en-US:
      openai: {model: gpt-4o-mini-tts, voice: marin, instructions: "Warm, confident corporate trainer speaking American English to colleagues. Clear, friendly, professional; natural conversational pace, brief pauses between list items. Never robotic."}
      elevenlabs: {voice: "<pick a warm narrator from the voice library>", model: eleven_multilingual_v2}
      azure: {voice: en-US-AvaMultilingualNeural}
    en-GB:
      openai: {model: gpt-4o-mini-tts, voice: marin, instructions: "Warm, confident trainer speaking British English. Clear, friendly, measured pace."}
      azure: {voice: en-GB-SoniaNeural}
    ar-EG:
      openai: {model: gpt-4o-mini-tts, voice: marin, instructions: "Speak natural Egyptian Arabic (Cairene colloquial), warm and friendly like a respected colleague explaining to the team. Clear, relaxed pace; pronounce English technical terms the way Egyptian professionals say them."}
      elevenlabs: {voice: "<Egyptian-Arabic-capable voice; audition>", model: eleven_multilingual_v2}
      azure: {voice: ar-EG-SalmaNeural, alt: ar-EG-ShakirNeural}
    ar-MSA:
      openai: {model: gpt-4o-mini-tts, voice: marin, instructions: "Speak clear Modern Standard Arabic (فصحى) in a calm, professional training tone. Moderate pace, precise pronunciation."}
      azure: {voice: ar-SA-ZariyahNeural, alt: ar-SA-HamedNeural}
  # Character personas (cartoon/comic/branching). Same voice id across languages; swap `instructions` language line.
  host:      {openai: {voice: marin,   instructions: "On-screen host; warm, upbeat, clear."}}
  learner:   {openai: {voice: ash,     instructions: "Friendly, curious employee; casual and quick."}}
  manager:   {openai: {voice: onyx,    instructions: "Brisk, good-humoured team manager; decisive."}}
  mentor:    {openai: {voice: echo,    instructions: "Calm, friendly expert; warm, clear, a touch of dry humour."}}
  customer:  {openai: {voice: coral,   instructions: "Polite customer/partner; slightly impatient when stakes rise."}}
  rookie:    {openai: {voice: ballad,  instructions: "Good-natured, over-eager new starter; expressive, quick to panic, comic."}}
  colleague: {openai: {voice: sage,    instructions: "Supportive co-worker; natural and relaxed."}}
  exec:      {openai: {voice: cedar,   instructions: "Senior executive; composed, low and confident."}}
  support:   {openai: {voice: nova,    instructions: "Helpful, busy help-desk agent; friendly and fast."}}
  # domain-pack personas declare their own voice in domains/<pack>/personas.yaml (e.g. vex → verse)
rules:
  - "Narrator voice ≠ any character voice in the same lesson."
  - "Arabic characters speak Egyptian colloquial unless the brief requires MSA; narrator follows the course language."
  - "Recording a human voice instead? Fill license fields in MANIFEST.md (talent, consent, usage, term)."
```

## assets/audio.yaml
```yaml
# Music beds + SFX slots. Files are NOT shipped (licensing); drop licensed files at `path` and fill `license`.
# Missing files → renderer uses assets/placeholders/generated/*.wav (silence/tone) and marks `assets[].status: placeholder`.
music_beds:
  explainer:  {path: assets/audio/music/explainer.mp3,  mood: "light corporate, steady pulse, 95–110 bpm, no vocals", loop: true, gain_db: -22, license: null}
  cartoon:    {path: assets/audio/music/cartoon.mp3,    mood: "playful pizzicato/ukulele, bouncy, 110–125 bpm, no vocals", loop: true, gain_db: -22, license: null}
  whiteboard: {path: assets/audio/music/whiteboard.mp3, mood: "soft acoustic/piano, gentle, 85–100 bpm, no vocals", loop: true, gain_db: -24, license: null}
  executive:  {path: assets/audio/music/executive.mp3,  mood: "minimal ambient piano + strings, confident, 70–90 bpm", loop: true, gain_db: -24, license: null}
mix:
  ducking: "sidechain the bed under narration (−8 to −12 dB)"
  loudness: "integrated −16 LUFS (web), true peak ≤ −1 dBTP"
sfx:                        # names usable in scenes[].sfx[].name and cartoon beats[].sfx
  beeps:   {use: "alarm / system alert"}
  chime:   {use: "correct answer / reward"}
  ding:    {use: "notification arrives"}
  pop:     {use: "item reveal"}
  reel:    {use: "rewind / flashback"}
  ring:    {use: "phone call"}
  scratch: {use: "record-scratch stop"}
  sparks:  {use: "malfunction"}
  whoosh:  {use: "transition / camera move"}
  womp:    {use: "mistake"}
  zap:     {use: "attack lands"}
  zipper:  {use: "data leaving / exfiltration"}
sfx_path: assets/audio/sfx/<name>.wav
license_fields: [source, title, author, license, url, retrieved_at, attribution_required]
```

## assets/brand.yaml
```yaml
# Brand slots (per client; copy into the run folder and fill). All optional; neutral defaults apply when empty.
logo: null                 # path to SVG/PNG. EMPTY BY DEFAULT — only set when the client supplies one and asks for it.
logo_placement: none       # none | title | outro | corner
theme_preset: neutral      # assets/theme_presets.yaml
color_overrides: {}        # e.g. {accent: "#0B5FA5"} — re-run assets/scripts/check_contrast.py
company_name: "Northwind Co."   # fictional default for examples/mock-ups
mock_domain: "northwind.example"
intro: null                # path to a ≤ 4 s intro sting (video) or null → `title` scene only
outro: null                # path to a ≤ 4 s outro sting or null → `outro` scene only
lower_third_style: clean   # clean | bar (no one-sided thick accent borders)
evidence_line: null        # e.g. "Completion recorded for ISO/IEC 27001 A.6.3 awareness evidence."
```

## assets/characters/personas.yaml
```yaml
# Persona registry: id → kit cast look. Shared contract between assets/ (agent E) and kit/ personas (agent A).
# kit_cast = the SVG persona id rendered by kit/ (same id). Reference images for each persona are produced by rendering
# the kit SVG persona (idle pose, neutral) — not by image generation. Domain packs add personas in
# domains/<pack>/personas.yaml (e.g. security-awareness adds `vex`, the only persona wearing attention #FF6700).
# display_name is localizable on-screen/bubble text; ids never change.
schema_version: '1.0'
personas:
  host:
    display_name:
      en: Lina
      ar: لينا
    role: On-screen host / narrator who introduces and wraps up lessons
    kit_cast: host
    look: woman in her mid-30s, medium-brown skin, shoulder-length wavy dark-brown hair, small stud earrings, navy blazer over a light-cyan top,
      charcoal trousers, flat shoes
    palette:
      skin: '#A86B4C'
      hair: '#3B2A22'
      top: '#6FC7DA'
      jacket: '#363E77'
      bottom: '#3A3F55'
    voice: openai marin (narrator slot) — warm, confident trainer
    poses:
    - present
    - wave
    - point
    - pointUp
    expressions:
    - happy
    - neutral
    sheet: assets/characters/host/character_sheet.md
    prompt: assets/characters/host/prompt.txt
  learner:
    display_name:
      en: Nour
      ar: نور
    role: Everyday employee the audience identifies with; usually makes the right call after thinking
    kit_cast: learner
    look: young woman in her 20s, light-olive skin, wears a smooth blue hijab, soft grey cardigan over a white top, dark-blue trousers, white
      trainers, ID badge on a lanyard
    palette:
      skin: '#D9A982'
      hijab: '#006AB3'
      cardigan: '#9AA3B5'
      top: '#FFFFFF'
      bottom: '#26305C'
    voice: openai ash — friendly, curious, casual
    poses:
    - think
    - phone
    - type
    - point
    expressions:
    - think
    - neutral
    - happy
    - worried
    sheet: assets/characters/learner/character_sheet.md
    prompt: assets/characters/learner/prompt.txt
  manager:
    display_name:
      en: Karim
      ar: كريم
    role: Line manager / approver; source of authority pressure (real or impersonated)
    kit_cast: manager
    look: man in his 40s, dark-brown skin, short greying hair, neatly trimmed grey-black beard, white shirt with rolled sleeves, navy waistcoat,
      grey trousers, wristwatch
    palette:
      skin: '#6B4532'
      hair: '#4A4A4A'
      shirt: '#FFFFFF'
      waistcoat: '#363E77'
      bottom: '#5A6385'
    voice: openai onyx — brisk, good-humoured
    poses:
    - handsHips
    - point
    - phone
    - armsOut
    expressions:
    - neutral
    - happy
    - worried
    sheet: assets/characters/manager/character_sheet.md
    prompt: assets/characters/manager/prompt.txt
  mentor:
    display_name:
      en: Omar
      ar: عمر
    role: Subject-matter expert (IT/security/HR/finance) who explains the rule and the why
    kit_cast: mentor
    look: man in his 30s, light-brown skin, short black hair, rectangular glasses, short beard, blue polo shirt, khaki trousers, lanyard badge,
      tablet in hand
    palette:
      skin: '#B98563'
      hair: '#1F1A17'
      polo: '#006AB3'
      bottom: '#C9B48A'
      glasses: '#363E77'
    voice: openai echo — calm, warm, clear
    poses:
    - present
    - stop
    - point
    - pointUp
    expressions:
    - happy
    - neutral
    - think
    sheet: assets/characters/mentor/character_sheet.md
    prompt: assets/characters/mentor/prompt.txt
  customer:
    display_name:
      en: Dana
      ar: دانة
    role: Customer, supplier or external partner; requests and payments come from (or are faked as) her
    kit_cast: customer
    look: woman in her 50s, fair skin with freckles, short silver bob haircut, green blazer over a cream-white blouse, dark trousers, tote bag
    palette:
      skin: '#F0CFB4'
      hair: '#C8CCD4'
      blazer: '#1E7F4F'
      blouse: '#F7F7F2'
      bottom: '#2E3446'
    voice: openai coral — polite, slightly impatient under pressure
    poses:
    - phone
    - handsHips
    - hold
    - wave
    expressions:
    - neutral
    - worried
    - happy
    - angry
    sheet: assets/characters/customer/character_sheet.md
    prompt: assets/characters/customer/prompt.txt
  rookie:
    display_name:
      en: Sam
      ar: سام
    role: New starter / mistake-maker whose slips drive the story (then gets it right)
    kit_cast: rookie
    look: young man in his 20s, tan skin, curly black hair, light-blue shirt half-untucked, dark-grey chinos, white trainers, ID badge on a lanyard,
      often holding a coffee cup
    palette:
      skin: '#C68B5E'
      hair: '#141414'
      shirt: '#A9D4F5'
      bottom: '#4A4F5E'
      cup: '#FFFFFF'
    voice: openai ballad — expressive, quick to panic, comic
    poses:
    - phone
    - facepalm
    - type
    - cheer
    - shrug
    expressions:
    - worried
    - shocked
    - happy
    - sad
    sheet: assets/characters/rookie/character_sheet.md
    prompt: assets/characters/rookie/prompt.txt
  colleague:
    display_name:
      en: Maya
      ar: مايا
    role: Supportive co-worker / bystander
    kit_cast: colleague
    look: woman in her 30s, deep-brown skin, short natural curls, teal sweater, grey trousers
    voice: openai sage
    extra: true
  exec:
    display_name:
      en: Hana
      ar: هنا
    role: Senior executive (CEO/CFO), often impersonated
    kit_cast: exec
    look: woman in her 50s, light-brown skin, grey streaked hair in a low bun, dark navy suit, pearl studs
    voice: openai cedar
    extra: true
  support:
    display_name:
      en: Dina
      ar: دينا
    role: Help-desk / service-desk agent
    kit_cast: support
    look: woman in her late 20s, medium skin, black ponytail, headset, light-blue company polo
    voice: openai nova
    extra: true
```

## assets/characters/customer/character_sheet.md
# Character sheet — `customer` (Dana / دانة)

**Role:** Customer, supplier or external partner; requests and payments come from (or are faked as) her
**Kit cast id:** `customer` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
woman in her 50s, fair skin with freckles, short silver bob haircut, green blazer over a cream-white blouse, dark trousers, tote bag.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#F0CFB4` |
| hair | `#C8CCD4` |
| blazer | `#1E7F4F` |
| blouse | `#F7F7F2` |
| bottom | `#2E3446` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Polite and professional; becomes impatient when stakes rise (useful pressure without villainy).

## Voice
openai coral — polite, slightly impatient under pressure (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `phone`, `handsHips`, `hold`, `wave` · expressions: `neutral`, `worried`, `happy`, `angry` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Represent legitimate external contacts | Be portrayed as the attacker |
| Be the person whose identity is spoofed |  |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.

Locked prompt:
```text
Flat vector illustration of one original cartoon character for a corporate training video, full body, standing, front three-quarter view, clean uniform outlines, flat colours with minimal soft shading, simple rounded shapes, friendly proportions (head about one-sixth of height), plain light #F4F7FB background, consistent character-sheet style, not a real person. Character: woman in her 50s, fair skin with freckles, short silver bob haircut, green blazer over a cream-white blouse, dark trousers, tote bag. Colour palette: skin #F0CFB4, hair #C8CCD4, blazer #1E7F4F, blouse #F7F7F2, bottom #2E3446. Expression friendly and neutral, arms relaxed. {SCENE}. no text, no letters, no numbers, no signage, no logos
```

## assets/characters/host/character_sheet.md
# Character sheet — `host` (Lina / لينا)

**Role:** On-screen host / narrator who introduces and wraps up lessons
**Kit cast id:** `host` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
woman in her mid-30s, medium-brown skin, shoulder-length wavy dark-brown hair, small stud earrings, navy blazer over a light-cyan top, charcoal trousers, flat shoes.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#A86B4C` |
| hair | `#3B2A22` |
| top | `#6FC7DA` |
| jacket | `#363E77` |
| bottom | `#3A3F55` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Warm, upbeat, clear; speaks to the viewer directly; never preachy.

## Voice
openai marin (narrator slot) — warm, confident trainer (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `present`, `wave`, `point`, `pointUp` · expressions: `happy`, `neutral` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Address the camera | Act out mistakes (that is the rookie's job) |
| Bookend lessons (title, recap, outro) | Appear in the same scene as a character voiced by marin |
| Point at boards with `point`/`present` |  |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.

Locked prompt:
```text
Flat vector illustration of one original cartoon character for a corporate training video, full body, standing, front three-quarter view, clean uniform outlines, flat colours with minimal soft shading, simple rounded shapes, friendly proportions (head about one-sixth of height), plain light #F4F7FB background, consistent character-sheet style, not a real person. Character: woman in her mid-30s, medium-brown skin, shoulder-length wavy dark-brown hair, small stud earrings, navy blazer over a light-cyan top, charcoal trousers, flat shoes. Colour palette: skin #A86B4C, hair #3B2A22, top #6FC7DA, jacket #363E77, bottom #3A3F55. Expression friendly and neutral, arms relaxed. {SCENE}. no text, no letters, no numbers, no signage, no logos
```

## assets/characters/learner/character_sheet.md
# Character sheet — `learner` (Nour / نور)

**Role:** Everyday employee the audience identifies with; usually makes the right call after thinking
**Kit cast id:** `learner` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
young woman in her 20s, light-olive skin, wears a smooth blue hijab, soft grey cardigan over a white top, dark-blue trousers, white trainers, ID badge on a lanyard.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#D9A982` |
| hijab | `#006AB3` |
| cardigan | `#9AA3B5` |
| top | `#FFFFFF` |
| bottom | `#26305C` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Curious, polite, a little hesitant; asks the question the audience is thinking.

## Voice
openai ash — friendly, curious, casual (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `think`, `phone`, `type`, `point` · expressions: `think`, `neutral`, `happy`, `worried` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Pause and think (`think`) before acting | Be shown as foolish |
| Model the correct behaviour in replays | Wear orange (reserved for the antagonist) |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.

Locked prompt:
```text
Flat vector illustration of one original cartoon character for a corporate training video, full body, standing, front three-quarter view, clean uniform outlines, flat colours with minimal soft shading, simple rounded shapes, friendly proportions (head about one-sixth of height), plain light #F4F7FB background, consistent character-sheet style, not a real person. Character: young woman in her 20s, light-olive skin, wears a smooth blue hijab, soft grey cardigan over a white top, dark-blue trousers, white trainers, ID badge on a lanyard. Colour palette: skin #D9A982, hijab #006AB3, cardigan #9AA3B5, top #FFFFFF, bottom #26305C. Expression friendly and neutral, arms relaxed. {SCENE}. no text, no letters, no numbers, no signage, no logos
```

## assets/characters/manager/character_sheet.md
# Character sheet — `manager` (Karim / كريم)

**Role:** Line manager / approver; source of authority pressure (real or impersonated)
**Kit cast id:** `manager` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
man in his 40s, dark-brown skin, short greying hair, neatly trimmed grey-black beard, white shirt with rolled sleeves, navy waistcoat, grey trousers, wristwatch.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#6B4532` |
| hair | `#4A4A4A` |
| shirt | `#FFFFFF` |
| waistcoat | `#363E77` |
| bottom | `#5A6385` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Brisk, good-humoured, busy; decisive; supportive when people verify.

## Voice
openai onyx — brisk, good-humoured (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `handsHips`, `point`, `phone`, `armsOut` · expressions: `neutral`, `happy`, `worried` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Praise verification ('Thanks for checking with me') | Bully or shout |
| Appear as the impersonated authority in scams | Be the villain himself |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.

Locked prompt:
```text
Flat vector illustration of one original cartoon character for a corporate training video, full body, standing, front three-quarter view, clean uniform outlines, flat colours with minimal soft shading, simple rounded shapes, friendly proportions (head about one-sixth of height), plain light #F4F7FB background, consistent character-sheet style, not a real person. Character: man in his 40s, dark-brown skin, short greying hair, neatly trimmed grey-black beard, white shirt with rolled sleeves, navy waistcoat, grey trousers, wristwatch. Colour palette: skin #6B4532, hair #4A4A4A, shirt #FFFFFF, waistcoat #363E77, bottom #5A6385. Expression friendly and neutral, arms relaxed. {SCENE}. no text, no letters, no numbers, no signage, no logos
```

## assets/characters/mentor/character_sheet.md
# Character sheet — `mentor` (Omar / عمر)

**Role:** Subject-matter expert (IT/security/HR/finance) who explains the rule and the why
**Kit cast id:** `mentor` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
man in his 30s, light-brown skin, short black hair, rectangular glasses, short beard, blue polo shirt, khaki trousers, lanyard badge, tablet in hand.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#B98563` |
| hair | `#1F1A17` |
| polo | `#006AB3` |
| bottom | `#C9B48A` |
| glasses | `#363E77` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Calm, friendly, slightly dry humour; explains in one line, then shows how.

## Voice
openai echo — calm, warm, clear (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `present`, `stop`, `point`, `pointUp` · expressions: `happy`, `neutral`, `think` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Turn the story into the lesson | Lecture for more than ~20 s |
| Use `stop` pose for the key rule | Mock the rookie |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.

Locked prompt:
```text
Flat vector illustration of one original cartoon character for a corporate training video, full body, standing, front three-quarter view, clean uniform outlines, flat colours with minimal soft shading, simple rounded shapes, friendly proportions (head about one-sixth of height), plain light #F4F7FB background, consistent character-sheet style, not a real person. Character: man in his 30s, light-brown skin, short black hair, rectangular glasses, short beard, blue polo shirt, khaki trousers, lanyard badge, tablet in hand. Colour palette: skin #B98563, hair #1F1A17, polo #006AB3, bottom #C9B48A, glasses #363E77. Expression friendly and neutral, arms relaxed. {SCENE}. no text, no letters, no numbers, no signage, no logos
```

## assets/characters/rookie/character_sheet.md
# Character sheet — `rookie` (Sam / سام)

**Role:** New starter / mistake-maker whose slips drive the story (then gets it right)
**Kit cast id:** `rookie` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
young man in his 20s, tan skin, curly black hair, light-blue shirt half-untucked, dark-grey chinos, white trainers, ID badge on a lanyard, often holding a coffee cup.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#C68B5E` |
| hair | `#141414` |
| shirt | `#A9D4F5` |
| bottom | `#4A4F5E` |
| cup | `#FFFFFF` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Good-natured, over-eager, easily rushed; big comic reactions; learns fast.

## Voice
openai ballad — expressive, quick to panic, comic (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `phone`, `facepalm`, `type`, `cheer`, `shrug` · expressions: `worried`, `shocked`, `happy`, `sad` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Make the relatable mistake, then redo it right | Be humiliated or punished harshly |
| Carry a running gag (coffee cup) | Stay wrong at the end of a lesson |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.

Locked prompt:
```text
Flat vector illustration of one original cartoon character for a corporate training video, full body, standing, front three-quarter view, clean uniform outlines, flat colours with minimal soft shading, simple rounded shapes, friendly proportions (head about one-sixth of height), plain light #F4F7FB background, consistent character-sheet style, not a real person. Character: young man in his 20s, tan skin, curly black hair, light-blue shirt half-untucked, dark-grey chinos, white trainers, ID badge on a lanyard, often holding a coffee cup. Colour palette: skin #C68B5E, hair #141414, shirt #A9D4F5, bottom #4A4F5E, cup #FFFFFF. Expression friendly and neutral, arms relaxed. {SCENE}. no text, no letters, no numbers, no signage, no logos
```
