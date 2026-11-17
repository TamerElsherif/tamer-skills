# RTL, numerals, punctuation, bidi

## Layout (renderers implement; storyboard declares `direction: rtl`)
- Mirror layout: reading order right→left; lists, steps, timelines and process flows run right→left; progress bars fill from the right.
- Mirror directional icons (arrows, chevrons, undo/redo, send, back/next) — not logos, clocks, media play, checkmarks, charts' data.
- Do/don't and comparison: "don't/bad" column stays first in reading order (right side in RTL).
- Characters: cartoon people/positions mirror (x → width − x); set `flip` accordingly; speech-bubble tails follow.
- SVG `<text>` inherits RTL anchoring — illustrations with Latin labels set `direction: ltr` on the SVG (known kit gotcha).
- Mock-ups of English software (email client, browser) stay LTR inside the frame; call-out labels around them are Arabic.
- Fonts: Arabic Cairo / IBM Plex Sans Arabic / Noto Kufi Arabic; Latin runs in Poppins/Inter; line-height ≥ 1.4 for Arabic.

## Numerals
- Default: Western digits (0-9) on screen for Egyptian corporate audiences (matches source documents, systems, prices).
- Eastern Arabic digits (٠-٩) only if the org style guide requires; then everywhere (`localize.py skeleton --numerals eastern`).
- Never mix systems in one lesson (`rtl_lint.py` warns). Percent: "18%" (Western) / "١٨٪" (Eastern). Currency as source: "$25", "25 دولار".
- Dates: "1 مارس 2026" (ar) — avoid numeric-only dates (ambiguous order).

## Punctuation
| Latin | Arabic |
|---|---|
| , | ، |
| ; | ؛ |
| ? | ؟ |
| “ ” | « » or " " |
Full stop, colon, exclamation stay. No space before punctuation. Use ← not → for "leads to" in RTL text.

## Bidi (English inside Arabic)
- Short English terms (MFA, Northwind Expenses) are fine inline.
- URLs, e-mail addresses, file paths, code, phone numbers, and strings starting/ending with Latin or digits: isolate with
  FSI … PDI (U+2068 … U+2069) or put them on their own line/chip; otherwise punctuation jumps to the wrong side.
- Never start an Arabic label with a Latin word + punctuation ("MFA: …") without isolation — rewrite ("التحقق بخطوتين (MFA)").
- Subtitles: each Arabic line starts with RLM (U+200F) — `subtitles.py` does it.
- Narration TTS text: no isolation characters (strip them); spell URLs as spoken.

## Checks (`rtl_lint.py`)
direction/fonts/voices language, leftover «TR», non-Arabic narration, cue counts vs source, mixed digits, Latin
punctuation, unisolated URLs/e-mails/code, → arrows, register drift.
