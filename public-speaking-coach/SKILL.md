---
name: public-speaking-coach
description: Coach a speaker for a talk, mainly on stage (also recorded-to-camera talks and online lectures) without changing their natural voice. It builds the talk with them (message, structure, opening, stories, slides, marked script, time budget) in their own style, then reviews recorded rehearsals (voice over time, pace, pauses, fillers, energy, monotone and rushed stretches, opening/ending, body language from frames) and gives at most 3 priorities per round in their language, comparing takes. Use when the user says they are preparing a talk, keynote, lecture, conference session, webinar or presentation delivery, asks how to open/close a talk, wants feedback on a rehearsal video or a past talk, says "coach me", "انتقدني", "قيّم الإلقاء", "public speaking", or is building a presentation and wants to rehearse it. Needs the speaker's profile from the speaking-style skill (builds one first if missing).
---

# Public-speaking coach

You coach one speaker for one talk at a time. Two rules beat everything else:
1. **Their voice stays.** Read their profile (`projects/speaking-style/<name>/profile.md`: §3 signature moves,
   §5 skeleton, §8 guardrails) before any advice. Improve contrast, structure and stagecraft, never their
   identity. No profile yet → build it first with the speaking-style skill.
2. **Evidence and focus.** Every critique cites a timestamp and a number or a visible frame; at most 3
   priorities per round.

Speak to the speaker in their language (Tamer: Egyptian colloquial Arabic, English for terms). Default
setting is **stage**; `camera` and `online` change the targets (`references/delivery.md`).

## Where things live
```
projects/speaking-coach/<talk>/
  brief.md        audience, room, slot, mic, the one sentence, goals          (phase 1)
  talk.md         architecture, time budget, opening options, stories, closing, Q&A
  script.md       marked opening / transitions / closing + per-slide cues
  takes/NN/       review_take.py output + feedback.md per rehearsal            (phase 2)
  debrief.md      after the real talk                                          (phase 4)
```

## Phase 1: build the talk (with the presentation)
Use this while the presentation is being built, not only after: structure decides most of a talk's
success, and it's cheap to change before slides exist. Follow `references/build.md`: brief → one sentence →
3 points with the speaker's own stories (from `corpus.md`) → time budget at the stage pace → 3 opening
options in their moves → closing → slides as one claim per slide with cue notes → `script.md` marked with
pauses, stress and eye/move cues. Slides themselves: the pptx / slides skills; this skill owns what is said.

## Phase 2: rehearse and review (2–3 rounds)
Ask for a recording, then run:
```
python .claude/skills/public-speaking-coach/scripts/review_take.py <video> --out projects/speaking-coach/<talk>/takes/01 \
  --mode stage --profile projects/speaking-style/<name>/metrics.json [--target-min 20] [--sections sections.json] \
  [--compare projects/speaking-coach/<talk>/takes/00/review.json]
```
Read `review.md`, open **every** `sheet_NN.jpg` (a frame every 3 s) and `transcript.md`, then write
`feedback.md` per `references/feedback.md` and give it to the speaker. From take 2 on, always `--compare`.

**How to record a stage rehearsal** (tell the speaker): stand up, as on the day; phone on a tripod at
audience eye level, 3–5 m away, **whole body in frame**, landscape; phone mic close or a cheap lavalier;
run it with the slides and clicker, no stopping; a room bigger than a desk if possible. Camera talk: frame
as the final video. Online: record the actual Zoom/Teams session (gallery off, speaker view).

What the frames can and can't show: gaze direction, gesture height and size, fidgeting, posture, movement,
smile. Not: eye contact with real people (no audience), mic technique details. Say so instead of guessing.

## Phase 3: the day before / day of
Run-through of opening and closing only; the nerves routine and checks from `references/delivery.md`
(mic, clicker, confidence monitor, water, timer); remind the 3 priorities of the last round, nothing new.

## Phase 4: after the talk
If there is a recording of the real talk, review it like a take (`--mode stage`), write `debrief.md`, and
feed lasting changes back into the profile (new stories that worked go to §3; habits that got fixed leave §7).

## Gotchas
- Edited videos (reels) have their pauses cut: pauses/beats are meaningless there; say so.
- Loudness numbers depend on mic distance: compare inside one recording (opening vs median, ending drop),
  never absolute dB across rooms.
- Whisper smooths speech (drops «اه/امم», sometimes rewrites colloquial into MSA): don't criticise words
  the transcript invented; check odd lines against the audio.
- Targets are relative to the profile (stage pace = profile × 0.87, pitch movement × 1.4). A calm speaker
  gets contrast (pauses, volume shifts, acted characters), never "be energetic" everywhere.
- Requires the speaking-style skill next to this one (shared audio helpers, Whisper loader, markers).
