# Voices per language

Source of truth for slots: `assets/voices.yaml` (narrator per language + persona voices). `localize.py skeleton` copies
voice ids and swaps instructions to the target language. Record final choices in `decisions.json` (orchestrator).

| Language | OpenAI (gpt-4o-mini-tts, primary) | ElevenLabs (alt) | Azure (alt) |
|---|---|---|---|
| en-US | `marin` (narrator), personas per voices.yaml | eleven_multilingual_v2, warm narrator | en-US-AvaMultilingualNeural |
| en-GB | `marin` + "British English" | — | en-GB-SoniaNeural |
| ar-EG | `marin` + "natural Egyptian Arabic (Cairene colloquial), warm colleague…" | multilingual v2 voice auditioned for Egyptian | ar-EG-SalmaNeural / ar-EG-ShakirNeural |
| ar-MSA | `marin` + "clear Modern Standard Arabic, calm professional" | multilingual v2 | ar-SA-ZariyahNeural / ar-SA-HamedNeural |

## Instruction recipes
- Narrator ar-EG: "Speak natural Egyptian Arabic (Cairene colloquial), warm and friendly like a respected colleague
  explaining to the team. Clear, relaxed pace; pronounce English technical terms the way Egyptian professionals say them."
- Character: `"<language line> <acting note>"` e.g. "Speak natural Egyptian Arabic (Cairene colloquial). Good-natured,
  over-eager new starter; expressive, quick to panic, comic."
- MSA narrator: avoid "news-anchor" stiffness — ask for "friendly, conversational MSA".

## Gotchas
- gpt-4o-mini-tts occasionally truncates Arabic clips → renderer checks words-per-minute outliers and regenerates.
- Digits and acronyms read inconsistently → narration uses words (speakable.py) and spelled acronyms.
- Same voice id across languages keeps character identity; narrator voice ≠ any character voice in the lesson.
- Azure Egyptian voices need SSML `xml:lang="ar-EG"`; ElevenLabs needs `language_code` hint for Arabic.
