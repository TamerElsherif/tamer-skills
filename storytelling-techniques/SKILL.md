---
name: storytelling-techniques
description: Build, rewrite and review stories for talks, lectures, podcasts and social content using proven storytelling mechanics, starting with the Chappelle method (dialogue instead of labels, expectation then a turn, specific detail, the five beats Setup → Escalation → Turn → Peak → Button), adapted to the speaker's own voice. Use when the user wants to tell a story in a talk or reel, asks to make a story land, "احكيها أحسن", "ازاي أحكي القصة دي", wants a hook or an opening story, wants a story reviewed in a script or rehearsal, or shares a video about a storyteller's technique to add to the library. Works with public-speaking-coach (build phase, stories bank) and speaking-style (the speaker's profile).
---

# Storytelling techniques

A library of storytelling mechanics plus a way to apply them to one speaker's real stories without changing
their voice. Techniques live in `references/`, one file per source; `chappelle-method.md` is the first.

## Rules
1. **Their story, their voice.** Read the speaker's profile first (`projects/speaking-style/<name>/profile.md`:
   §3 signature moves, §8 guardrails; Tamer: Egyptian colloquial Arabic, English for terms, self-deprecating
   humour). Borrow mechanics, never another performer's material, persona or jokes.
2. **No invented facts.** Specific details make stories work, but they must be true. When a detail is missing,
   ask for it («كانت الساعة كام؟ قالّك إيه بالظبط؟») or mark it `[؟]`; never fill it in.
3. **Fair turns.** A turn may hide a fact, never contradict what was said before it.

## Rewrite a story (main use)
1. Get the raw story: from the user, or find candidates in `projects/speaking-style/<name>/corpus.md`.
2. Ask what it's for: the point of the talk section it serves, setting (stage / camera / reel), time (30 s, 90 s, 3 min).
3. Map it onto the five beats (`references/chappelle-method.md` §4). Missing Turn or Button is the usual gap.
4. Apply the tools: labels → 2–4 lines of dialogue; adjectives → one or two exact details; find or build the turn.
5. Write it as the speaker talks, marked for delivery:
   `/` short pause, `//` 1 s pause, **bold** = stress, `[صوت فلان]` voiced line, `[↻]` turn head / change spot,
   `[↑]` keep volume up (Buttons and endings).
6. Show a beat table (beat · line · seconds) and the marked text. Offer one alternative Turn or Button.
7. Save in the talk's folder when there is one (`projects/speaking-coach/<talk>/stories/<slug>.md`), else
   `projects/storytelling/stories/<slug>.md`.

## Review a story (script or recording)
Check, with the line or timestamp for each:
- Five beats present and in order; Setup ≤ 20 % of the story; Button exists and is one sentence.
- Labels left that should be dialogue; adjectives that should be details.
- Turn: there is one, it's fair, and there's a pause before it.
- Peak acted (voice, face, pause), not narrated; ending not falling in volume.
For a recording, run public-speaking-coach's `review_take.py` and use its timeline; at most 3 fixes.

## Add a new technique source
When the user shares a video/article about a storyteller's method:
1. Get it locally into `projects/storytelling/sources/<slug>/`. Instagram blocks yt-dlp without login: open it
   in the user's Chrome and record the playing `<video>` with `captureStream()` + `MediaRecorder`, then download
   the blob (no cookies or sign-in). Remux to mp4, `audio.wav` 16 kHz mono.
2. Transcribe (faster-whisper large-v3, `language` set) and make frame sheets; Whisper garbles names and
   numbers in Arabic, so take quotes and numbers from on-screen text when the video shows it.
3. Write `references/<name>-method.md` in the shape of `chappelle-method.md`: source and caveats, a tools table,
   one section per tool (what, the source's example, how to apply, stage delivery), fit with the speaker's profile.
4. Add it to the list below.

## Library
- `references/chappelle-method.md`: Dialogue · Expectation → Turn · Specific detail · Setup → Escalation → Turn → Peak → Button
