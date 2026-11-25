# public-speaking-coach

A coach for one speaker and one talk: mainly stage talks, also recorded-to-camera talks and online
lectures. It helps build the talk in the speaker's own style, then measures recorded rehearsals and gives
focused, timestamped feedback. Built on the speaker's profile from the speaking-style skill, so the advice
sharpens their delivery without turning them into someone else.

## What it's for
Most speaking advice is generic: "more energy", "open with a statistic", "no fillers". This skill starts from
how the speaker actually talks (pace, pitch, signature moves, stories, language mix), sets targets relative to
that for the setting (stage: slower, more pauses and vocal contrast, bigger gestures), and checks each
rehearsal against them with numbers and video frames. At most 3 priorities per round, compared take by take.

## When to use it
- Preparing a keynote, conference session, lecture, workshop or webinar
- Building a presentation and deciding what to say: message, structure, opening, stories, closing, time budget
- Reviewing a rehearsal video or the recording of a past talk ("انتقدني", "قيّم الإلقاء")
- The day before a talk: final run-through and nerves routine
- **Not for:** building the slides themselves (use a slides/pptx skill); speakers without any recording
  for a profile (record 10+ minutes first); speech-language therapy.

## Install
```bash
npx skills add TamerElsherif/tamer-skills --skill public-speaking-coach --agent claude-code
npx skills add TamerElsherif/tamer-skills --skill speaking-style --agent claude-code   # required
# manual: copy both folders to .claude/skills/ (project) or ~/.claude/skills/ (user), side by side
```
Prerequisites: the speaking-style skill and its Python stack (torch, faster-whisper, librosa, soundfile,
numpy), `ffmpeg` on PATH; NVIDIA GPU recommended for Whisper large-v3.

## How to use
1. **Build:** "I'm giving a 20-minute talk on X to Y next month, help me build it." Claude writes
   `brief.md`, `talk.md` (one sentence, 3 points, stories, time budget, opening options, closing, Q&A) and
   `script.md` (marked opening/transitions/closing + slide cues) under `projects/speaking-coach/<talk>/`.
2. **Rehearse:** record standing, full body, phone on a tripod, then:
   ```
   python .claude/skills/public-speaking-coach/scripts/review_take.py rehearsal.mp4 --out projects/speaking-coach/<talk>/takes/01 \
     --mode stage --profile projects/speaking-style/<name>/metrics.json --target-min 20 [--sections s.json] [--compare takes/00/review.json]
   ```
   Claude reads the report, every contact sheet and the transcript, and writes `feedback.md`.
3. **Day before:** opening + closing run-through, checks, the last round's 3 priorities.
4. **After:** review the real recording, write `debrief.md`, update the profile.

- **Inputs:** speaker profile (`metrics.json`, `profile.md`), rehearsal video/audio, optional section
  start times, talk length.
- **Outputs:** `review.md` / `review.json` (duration, pace vs target, pitch movement vs target, pauses and
  beats per minute, fillers vs profile, opening and ending energy, monotone and rushed stretches, silences,
  time per section, 10 s timeline with text, before/after deltas), `sheet_NN.jpg` frame grids,
  `transcript.md`, and Claude's `feedback.md`.
- **Options:** `--mode stage|camera|online`, `--every` (seconds between frames), `--lang`.

## Examples
**Example 1: build a keynote**
Prompt: `I have a 25-minute stage talk at a CIO summit about AI governance. Build it with me.`
Result: questions about audience and room, the one sentence, 3 points each anchored on one of the
speaker's own stories, 3 openings in their style, a marked opening and closing, a word budget at stage pace.

**Example 2: review a rehearsal**
Prompt: `Here's my rehearsal video, critique my delivery for the stage`
Result: metrics vs stage targets plus a look at every 3-second frame; feedback in the speaker's language
with 3–5 strengths, the 3 priorities (e.g. "pause 1 s before the punchline at 4:10", "gestures above the
waist", "ending drops 4 dB"), and one drill for the next take.

**Example 3: second take**
Prompt: `Take 2 is ready`
Result: the same review with `--compare` against take 1: what moved, what to keep, the next 3 priorities.

## Layout
```
public-speaking-coach/
├── SKILL.md                  # phases (build, rehearse, day-of, after), recording guide, gotchas
├── README.md                 # this file
├── references/
│   ├── delivery.md           # stage vs camera vs online targets, stagecraft, mic, slides, Q&A, nerves
│   ├── build.md              # brief → one sentence → architecture → opening → stories → slides → marked script
│   └── feedback.md           # review rubric and feedback format (max 3 priorities)
└── scripts/
    └── review_take.py        # rehearsal analyzer: voice timeline, pauses, fillers, energy, sections, contact sheets
```

## Dependencies
- [speaking-style](../speaking-style): speaker profile, shared audio helpers, Whisper loader, marker lexicon
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [librosa](https://librosa.org/), ffmpeg

## Changelog
- 2026-11-25: initial version (stage-first coaching, build phase, rehearsal analyzer with take comparison)
