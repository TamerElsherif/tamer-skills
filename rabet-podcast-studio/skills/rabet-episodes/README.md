# rabet-episodes

## What it is
A Claude skill that cuts Rabet (رابط) Podcast full episodes into 16:9 mini episodes, sub-episodes and topic
episodes for YouTube and Facebook. You describe the episode as data (a JSON cut list). The scripts find safe cut
points, then render it with a cold-open hook, intro/outro logos, jump cuts with punch-ins, swipe transitions, name
cards and a follow & subscribe pop-up. They also write a .docx brief.

## What it's for
On Ep 3, the PLP framework came up in six different places in a 65-minute conversation. Rebuilding it as one
coherent 22-minute episode took a day of transcript reading, cut hunting and checks. This skill captures that
workflow so the next one takes an hour: prep once, write the story as a spec, check edges, render, QA, brief.

## When to use it
- "Break episode N into smaller episodes" / "make a sub-episode about X" / "one episode that explains X start to finish"
- Re-cutting or re-rendering a mini episode after review
- Adding the follow & subscribe pop-up to a full or mini episode, or preparing one for publishing (the skill always
  asks whether you want the pop-up)

Not for 9:16 reels, thumbnails or social posts: use **rabet-reels**.

## Install
```bash
npx skills add TamerElsherif/tamer-skills --skill rabet-episodes --agent claude-code
npx skills add TamerElsherif/tamer-skills --skill rabet-reels --agent claude-code   # required sister skill
```
Manual: copy `rabet-episodes/` next to `rabet-reels/` under `.claude/skills/`.

## How to use
1. `prep_episode.py <master.mp4> <work_dir>` once per full episode, then label the speakers in `shots.json`.
2. Write `episodes/<name>.json` (see `references/spec.md`): hook, body pieces with joins, `cta`, brief text.
3. `check_edges.py <spec>` → `build_episode.py <spec> --dry-run` → `build_episode.py <spec>`.
4. `qa_episode.py <spec>` (joint transcription + contact sheet), then `brief_episode.py <spec>`.

The follow & subscribe pop-up: `"cta": {"at": ["after_intro", "middle", "end"], "lang": "en"}` (or `"ar"`).
It's a white card with the Rabet mark, the channel name and handle, a YouTube-red Subscribe button and a bell. A
cursor clicks Subscribe, then the bell, and the card pops out after 6 s. `render_cta.py` renders it once
(transparent ProRes) and caches it.

## Examples
- "Make an Ep 4 episode that explains the hiring framework start to finish." → the skill reads the transcript,
  proposes a storyline, asks about the pop-up, writes the spec, checks edges and renders the episode and brief.
- "Re-render the PLP episode with the subscribe pop-up after the intro and at the end." → it sets `cta` in
  `plp.json`, re-renders, QAs and refreshes the brief.
- "Split Ep 5 into 6 sub-episodes." → one spec per sub-episode, rendered in a batch.

## Layout
```
SKILL.md                      rules, fast path, gotchas
references/spec.md            spec / episode.json / config keys
references/editing.md         storyline patterns, join choice, edges, CTA placement
scripts/prep_episode.py       wav, words, proxy, shots + sheets, transcript, episode.json
scripts/tx.py                 speaker-tagged transcript windows
scripts/pauses.py             real pauses around a time (cut candidates)
scripts/check_edges.py        isolated transcription of every piece edge (pre-render)
scripts/build_episode.py      plan + ffmpeg render (--dry-run)
scripts/render_cta.py         follow & subscribe pop-up renderer (cached)
scripts/qa_episode.py         joint transcription + contact sheet (post-render)
scripts/brief_episode.py      .docx brief
scripts/ep.py                 shared loaders
templates/subscribe-cta/      HyperFrames pop-up template
```

## Dependencies
rabet-reels (cutsafe, edge_check, transcribe_words, config, fonts, SFX) · ffmpeg with NVENC · Python: numpy,
python-docx, Pillow, faster-whisper on CUDA · Node + `npx hyperframes@0.8.163` (pop-up render only) ·
`~/.rabet-reels.json` with an `episodes` block.

## Bundle
Part of the planned Rabet podcast bundle: **rabet-reels** (reels, thumbnails, YouTube text, Postiz/Zernio) and
**rabet-episodes** (16:9 mini episodes + subscribe pop-up). A B-roll explainer skill can join later.

## Changelog
- 2026-10-31 v0.1: first version, from the Ep 3 sub-episodes and the PLP framework episode; follow & subscribe pop-up.
