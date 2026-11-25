---
name: speaking-style
description: Extract and analyze a person's real speaking style from their recorded videos (podcast episodes, talks, interviews), in Egyptian Arabic, English or mixed. It finds who speaks when by voice, transcribes only that person, measures pace, pauses, fillers, English code-switching, pitch and loudness against the other speakers, and writes a style profile (signature moves with verbatim quotes, vocabulary, how explanations are built, habits to polish, authenticity guardrails). Use when the user asks to analyze "my speaking style" / "طريقة كلامي", build or update a voice/speaker profile from videos, compare speakers, prepare for public speaking while keeping their own voice, or before writing a talk, script or post meant to sound like them. Foundation for a public-speaking coach skill.
---

# Speaking style

You turn recordings of a speaker into an evidence-based profile of how they talk. The point is **authenticity**:
the profile describes the voice so later work (coaching, talk scripts, posts) keeps it. Never turn it into
generic speaking advice, and never "correct" a signature move.

Scripts run from the OpenMontage repo root with `.venv/Scripts/python.exe` (GPU: RTX 5050; Whisper needs the
cuBLAS DLLs described in rabet-reels §5). Work and profiles live in `projects/speaking-style/`:
`work/<recording>/` per video, `<speaker>/` per person (metrics.md, metrics.json, corpus.md, profile.md).

## Pipeline

```
S=.claude/skills/speaking-style/scripts
python $S/diarize.py <video|wav> projects/speaking-style/work/<rec> --shots <camera shots.json> | --seed "Name=a-b,c-d"
python $S/transcribe_turns.py projects/speaking-style/work/<rec>            # all speakers (they are the baseline)
python $S/style_metrics.py <Name> projects/speaking-style/work/<rec1> [<rec2> …] --out projects/speaking-style/<name>
```
Then read `metrics.md` and `corpus.md` and write `profile.md` from `references/profile-template.md`.

1. **Diarize.** Rabet episodes have camera labels (`projects/rabet-ep3-reels/hq/ep3_camera_segments.json`,
   rabet-episodes `shots.json`). For other videos, give 2–3 `--seed` spans per speaker (≥ 20 s each, solo
   speech). Check the printed seed purity: below ~90 % kept means the labels or seeds are wrong; and the
   speaking times must be believable. Spot-check: transcribe 3 random turns per speaker and read them; a turn
   in the wrong voice usually reads like the other person's topic.
   **Voiceprints don't travel between rooms.** Ep3 voices matched against Ep1 (other studio, other mics)
   swapped Tamer and Haitham. Seed every recording from its own material; `--voices` is only safe for the same
   setup. Identify people on screen before seeding: Tamer = grey hair and beard; Haitham = glasses, dark
   beard; Hossam = often a cap (Ep1) / green tee (Ep3). File names lie: the «#26518_Tamer Elsherif … Reel N» Ep1
   reels are mostly Haitham and Hossam (Tamer: Reel 07, Reel 2, parts of Reel 1 / 15).
   **Several short clips (reels):** join their audio with 2 s gaps into `work/<rec>/audio.wav` (ffmpeg concat,
   16 kHz mono), write `parts.json` `{"parts": [[start_s, "Reel 6"], …]}`, pull one frame per clip to see who
   is on screen, then seed with whole clips of a single speaker. Turns never cross a part boundary.
2. **Transcribe** turn by turn (resumable; `--redo` to start over). No initial prompt by default: Whisper
   repeats it into short turns («فيها مصطلحات English…» showed up as Tamer's words). Repetition loops
   («الوصول إلى الوصول إلى…») are collapsed; a real triple for emphasis («أبسط أبسط أبسط») is kept.
   A wav at 16 kHz mono is used as is; video is converted once into `work/<rec>/audio.wav`.
3. **Metrics** for the speaker vs everyone else in the same recordings (same room, mic, topic: a fair
   baseline). Add recordings as they come; more talk time = steadier numbers (aim for ≥ 30 min of the speaker).
4. **Profile.** Read the whole corpus, not only the numbers. Every claim needs evidence: a quote with
   `[rec m:ss]` or a number from metrics.md. Keep quotes verbatim (Egyptian Arabic + English as spoken).
   Show the draft to the user; they know their voice best: what they reject goes into §8 as a guardrail.

## Reading the numbers

- **Conversation is not a stage talk.** Podcast turns are answers and reactions; short turns, interruptions and
  «صح / بالظبط» are normal there. Say which traits are conversational before applying them to a speech.
- **Distinctive phrases** (log-odds z vs the other speakers): z > 2 with ≥ 4 uses is real. Check each in the
  corpus before calling it a signature; transcription errors also come out as "distinctive".
- **Fillers undercount**: Whisper drops «اه / امم». Hesitation shows better in the pauses, which come from the
  audio level (Whisper stretches word ends over pauses, so word gaps are useless). A pause ≥ 0.7 s after
  «اللي هو / يعني / الـ» = searching for a word; one right before a key term (`words_after_long_pauses`) = a
  deliberate beat. Say which, from the corpus.
- **Pace**: articulation wpm excludes pauses. Arabic words are longer than English: compare only to the
  co-speakers, never to English norms (~150 wpm).
- **Pitch**: range in semitones (p10–p90): < 5 reads flat, 5–9 conversational, > 9 animated. Loudness range is
  mic- and room-dependent: compare inside a recording only.
- `low_conf_share` > 0.15: audio or transcription is weak there; treat that speaker's numbers with care.
- Diarization edges are ±0.5 s and overlap becomes "?": fine for style, not for cutting video.

## Gotchas

- `speechbrain` ECAPA model downloads once to `~/.cache/speaking-style/ecapa` (Windows: copy strategy, no symlinks).
- Never run Whisper while a HyperFrames render or another large-v3 job runs (RAM).
- `markers.json` is the Egyptian/English marker lexicon. Grow it when the corpus shows a frequent marker that's missing.
