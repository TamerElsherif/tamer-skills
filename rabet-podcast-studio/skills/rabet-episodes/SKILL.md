---
name: rabet-episodes
description: Cut Rabet (رابط) Podcast full episodes into mini / sub-episodes and topic episodes (16:9 YouTube + Facebook), e.g. "one episode that explains the PLP framework start to finish" from pieces scattered across the full episode, with a cold-open hook, intro/outro logos, jump cuts with punch-ins, swipe transitions, name cards, a follow & subscribe pop-up (YouTube logo, Subscribe, bell, channel name) and a .docx brief with cut list, chapters and B-roll ideas. Use when the user asks to break an episode into smaller episodes, make a sub-episode / mini episode / topic episode / compilation, re-cut or re-render one, add the subscribe call to action to an episode, or prepare a full or mini episode for publishing. Not for 9:16 reels (that's rabet-reels).
---

# Rabet Episodes (mini / sub-episodes from a full episode)

> v0.1 (2026-10-31): built from the Ep 3 work: 9 sub-episodes + the PLP framework episode (15 pieces from 6
> places in the episode, 21:47). `build_episode.py` reproduces that render exactly from `plp.json`.
> Sister skill: **rabet-reels** (9:16 reels, thumbnails, YouTube text, Postiz/Zernio). This skill imports its
> `cutsafe.py`, `edge_check.py`, `transcribe_words.py`, `config.py`, fonts and SFX, so keep both installed.
> Assets (intro/outro logos, name cards, CTA cache, channel name) come from `~/.rabet-reels.json` → `episodes`
> (see `references/spec.md`); never hard-code them.

## 1. Rules (from the user; do not regress)

1. **Ask about the follow & subscribe pop-up every time** you create, edit, re-render or prepare to publish a full
   episode or a mini episode (user, 2026-10-31). One AskUserQuestion: *Add the follow & subscribe pop-up?* →
   after the intro + middle + end (recommended) / after the intro only / end only / no. Then set `cta` in the spec
   (`references/spec.md`). Don't add it silently and don't skip the question.
2. **Pop-up look is fixed**: white card, Rabet mark, channel name «رابط بودكاست» + @RabetPodcast, YouTube-red
   Subscribe button with the YouTube mark, bell; cursor clicks Subscribe → "Subscribed", clicks the bell → it rings,
   card pops out (6 s). **No dark-blue or orange backgrounds.** Bottom-right (name cards are bottom-left). Change
   it only in `templates/subscribe-cta`, then `render_cta.py --force`.
3. **No captions.** Name cards only (16:9 episodes, user, 2026-10-31).
4. **Never cut inside a word or a sentence.** Word times drift (Ep 3: unreliable after ~1:35), so they only tell
   you *where* the words are. Edges come from `pauses.py` (audio level), and every edge is verified in isolation by
   `check_edges.py` before render and `qa_episode.py` after. Where two voices overlap there is no silence: use the
   "quietest" time, then check it.
5. **Check both edges of every piece.** An in can pull in the previous speaker's last word; an out can catch the
   first syllable of the next word. Fix by moving the edge to the next pause, never by trimming a frame.
6. **A jump cut needs a real word gap.** If the speech runs on (no pause between the kept and dropped parts), drop
   the jump and keep the passage (PLP: planned jumps at 3:14 and inside Lean Delivery were dropped).
7. **Don't jump-cut a pause that carries content.** A "hesitation" in the transcript may be the speaker spelling
   out the key term (PLP 1:55: «Profit-Led Product Framework»). Listen first.
8. **Burned-in name cards in the master** (Ep 3: Tamer ~0:44 with his old title, Haitham ~1:58, Hossam ~3:45):
   when a piece covers them, add no card of your own (`cards: "none"`), list them in `burned_in` so the CTA avoids
   them, and tell the user if a burned card is outdated.
9. **Name cards only on solo shots** (shots.json `who`), never on a split screen (`episode.json` `split`).
10. **File name** = `<prefix> - <title> (src mmMss-mmMss + …) [mmMss].mp4` (title + timeline hint, user rule);
    `build_episode.py` builds it.
11. Report honestly: say what you didn't watch end to end and what isn't uploaded.

## 2. Fast path

```
projects/<episode>-reels/episodes/
  episode.json          prep output (pointers + split list + teaser offset)
  <name>.json           one spec per mini episode (cut list + cta + brief)
  <name>.render.json    written by the build; QA + brief read it
  <name>/edges, /qa     check outputs
```
Scripts live in `.claude/skills/rabet-episodes/scripts` (run with the repo `.venv` Python, from the repo root).

1. **Prep once per full episode:** `prep_episode.py <master.mp4> <work_dir> [--teaser-offset 58]` → wav, words
   (GPU Whisper), 2 fps proxy, `shots.json`, `shots_sheetN.jpg`, `transcript.txt`, `episode.json`. Label `who` in
   `shots.json` from the sheets (speaker name or `split`) and put split-shot indexes in `episode.json` `split`.
2. **Find the story** in `transcript.txt` / `tx.py <episode.json> a b …` (speaker-tagged windows). Write the
   storyline first (`references/editing.md`): hook lines, context, map, one act per idea, close.
3. **Pick pieces and edges:** for each in/out, `pauses.py <episode.json> T …` → choose a pause with the right words
   on each side. Write the spec (`references/spec.md`): `hook`, `body` (with `join`), `who/first/last/what`,
   `burned_in`, `cards`, `cta` (rule 1), `brief`.
4. `check_edges.py <spec>` → every START begins on `first`, every END finishes on `last`, no stray syllables.
   Fix and re-run only the bad ones (`--only B3,B7`).
5. `build_episode.py <spec> --dry-run` → check length, swipes, punch-ins, card and CTA times. Then render
   (NVENC, about 3× real time: the 21:47 PLP episode took 6:45; run it in the background).
6. `qa_episode.py <spec>` → `qa/joints.txt` (whole words on both sides of every joint) + `qa/sheet.jpg` (swipes,
   punch-ins, cards, CTA). Look at the sheet.
7. `brief_episode.py <spec>` → `<prefix>_Brief.docx` next to the video (cut list, chapters, CTA times, B-roll,
   description). For YouTube title/description/thumbnail use rabet-reels §8.

Re-cut after review: edit the spec, then steps 4–7. The CTA MOV is cached (`render_cta.py --force` after a
template or channel change).

## 3. What each piece does

| File | Role |
|---|---|
| `scripts/prep_episode.py` | one-time prep: wav, words, proxy, shot list + labelled contact sheets, readable transcript, `episode.json` |
| `scripts/tx.py` | speaker-tagged transcript windows (stamp at pauses, every 8 words, speaker change) |
| `scripts/pauses.py` | real pauses around T with the words on each side, level strip, quietest 10 ms |
| `scripts/check_edges.py` | pre-render isolated transcription of every piece's first/last 3 s |
| `scripts/build_episode.py` | plan (joins, punch-ins, name cards, CTA slots) + ffmpeg render; `--dry-run`; writes `<spec>.render.json` |
| `scripts/render_cta.py` | renders the follow & subscribe pop-up (ProRes 4444 alpha, 2000×440 at 4K) + SFX WAV, cached per language |
| `scripts/qa_episode.py` | post-render joint transcription + stream probe + contact sheet |
| `scripts/brief_episode.py` | the .docx brief |
| `scripts/ep.py` | shared loaders (episode/spec/assets), time formats |
| `templates/subscribe-cta` | HyperFrames + GSAP pop-up (edit here; cue times mirrored in `render_cta.py` `CUES`) |
| `references/spec.md` | spec + episode.json + config keys |
| `references/editing.md` | storyline patterns, join choice, hooks, CTA placement, lessons from Ep 3 |

## 4. Machine facts / gotchas

- Encode: `h264_nvenc p5`, VBR cq 21, 16M (28M max), AAC 256k. Each piece gets its own seeked input (one long
  4K input with many trims buffers GBs).
- Swipes: `xfade slideleft` 0.4 s; 0.2 s video handles each side; audio is cut exactly at the edge (25 ms fades)
  and concatenated, whoosh (×0.6) peaks 0.3 s before the joint. CTA SFX also ×0.6.
- Punch-in 1.12× (crop centred, 35 % from the top so heads stay in) runs to the master's next camera change; after a
  piece that ends punched in, the next jump zooms back out instead.
- Python prints Arabic into pipes: scripts reconfigure stdout to UTF-8 and pass `PYTHONIOENCODING` to children.
  ffmpeg `drawtext` needs an explicit `fontfile` on Windows (no fontconfig).
- Never run two Whisper large-v3 jobs at once, or Whisper during a render (RAM).
- HyperFrames MOV output = ProRes 4444 with alpha; the CTA canvas is transparent (`background: transparent`).
