# speaking-style

Builds an evidence-based profile of how one person really talks, from their recorded videos (podcast
episodes, interviews, reels). It finds that person's voice, transcribes only them, measures their delivery
against the other speakers, and writes a profile of their style with verbatim quotes. Works for Egyptian
Arabic, English or a mix.

## What it's for
Public-speaking coaching and ghost-writing usually push everyone toward the same generic style. This skill
captures what makes a speaker sound like themselves first: signature moves, vocabulary, how they build an
explanation, pace, pitch and energy. Coaching, talk scripts and posts can then improve delivery without
erasing the voice. The profile also lists habits to polish, each with a measured rate, and guardrails for
what must never change.

## When to use it
- "Analyze my speaking style / طريقة كلامي from my podcast episodes"
- Building or updating a voice/speaker profile from new recordings
- Comparing how several speakers talk in the same show
- Before writing a talk, script or post that must sound like a specific person
- Before public-speaking coaching, so the advice keeps the speaker's own voice
- **Not for:** cutting or editing video (diarization edges are ±0.5 s), live coaching without recordings, or
  generic speaking tips.

## Install
```bash
npx skills add TamerElsherif/tamer-skills --skill speaking-style --agent claude-code
# manual: copy the folder to .claude/skills/speaking-style/ (project) or ~/.claude/skills/speaking-style/ (user)
```
Prerequisites: Python 3.11+ with `torch`, `speechbrain`, `faster-whisper`, `librosa`, `soundfile`, `numpy`;
`ffmpeg` on PATH; an NVIDIA GPU is recommended (Whisper large-v3 and the ECAPA speaker model; CPU works, ~10× slower).

## How to use
Ask Claude, e.g. "build my speaking profile from these episodes", or run the pipeline yourself from the repo root:
```
S=.claude/skills/speaking-style/scripts
python $S/diarize.py <video|wav> work/<rec> --shots shots.json      # camera labels [[start,end,who],…]
python $S/diarize.py <video|wav> work/<rec> --seed "Name=1:20-2:05,5:10-5:40" --seed "Other=…"
python $S/transcribe_turns.py work/<rec>                             # every speaker (they are the baseline)
python $S/style_metrics.py <Name> work/<rec1> [work/<rec2> …] --out profiles/<name>
```
Then Claude reads `metrics.md` + `corpus.md` and writes `profile.md` from `references/profile-template.md`.

- **Inputs:** one or more recordings, plus where each speaker talks alone: camera labels, 2–3 hand-picked
  spans per speaker (`--seed`), or `--voices voices.npz` from an earlier run with the same room and mics.
  Several short clips (reels) are joined into one `audio.wav` with a `parts.json` index.
- **Outputs (per speaker):** `metrics.md` / `metrics.json` (pace, pauses, fillers, English share, examples,
  questions, hedges, pitch and loudness vs co-speakers, distinctive phrases), `corpus.md` (the speaker's
  turns with timestamps and context), `profile.md` (fingerprint, signature moves with quotes, vocabulary,
  explanation skeleton, delivery, habits to polish, authenticity guardrails, open questions).
- **Options:** `--min-margin` / `--min-sim` (diarization strictness), `--only` (transcribe some speakers),
  `--prompt` (Whisper initial prompt, off by default), `--redo`, `--no-prosody`. `references/markers.json`
  holds the Egyptian/English discourse-marker lexicon to grow.

## Examples
**Example 1: profile from a podcast episode**
Prompt: `Analyze how I talk in episode 3. I'm Tamer; the camera labels are in shots.json`
Result: voice diarization seeded from the camera labels (seed purity printed), turn-by-turn transcription
of all three speakers, metrics comparing Tamer with the guests, and a `profile.md` with ~10 signature moves
quoted with timestamps.

**Example 2: add reels to an existing profile**
Prompt: `Add these 12 reels from episode 1 to my profile`
Result: the reels' audio is joined with a `parts.json` index, one frame per clip shows who is on screen,
each speaker is seeded from single-speaker clips, and the metrics are recomputed over both recordings.

**Example 3: feedback on a clip**
Prompt: `Watch this reel and give me constructive feedback on energy and body language`
Result: pitch, loudness, pace and pauses every 5 s plus a frame every 2 s, set against the profile, give
timestamped feedback (flat hooks, rushed punchlines, fading endings, gaze, hand position) that keeps the
speaker's style.

## Layout
```
speaking-style/
├── SKILL.md                        # workflow, how to read the numbers, gotchas
├── README.md                       # this file
├── references/
│   ├── profile-template.md         # sections of profile.md
│   └── markers.json                # Egyptian Arabic + English discourse markers by category
└── scripts/
    ├── common.py                   # audio loading, speech mask, JSON / time helpers
    ├── diarize.py                  # who speaks when (ECAPA embeddings, seeds / known voices) → turns.json
    ├── transcribe_turns.py         # Whisper large-v3 per turn, loop filter → words.json
    └── style_metrics.py            # metrics vs co-speakers, distinctive phrases, prosody → metrics.md, corpus.md
```

## Dependencies
- [SpeechBrain ECAPA-TDNN](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb) speaker embeddings
  (downloaded once to `~/.cache/speaking-style/ecapa`)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) large-v3
- [librosa](https://librosa.org/) for pitch (YIN) and loudness
- Optional: a Whisper spelling-fix glossary (`--fixes`, defaults to the rabet-reels glossary when present)

## Changelog
- 2026-11-25: initial version (voice diarization with seeds/known voices, per-turn transcription, style
  metrics vs co-speakers, profile template; first profile and reel feedback for Rabet Podcast)
