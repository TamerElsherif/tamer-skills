---
name: rabet-subscribe
description: Add the Rabet (رابط) Podcast follow & subscribe pop-up (white card, Rabet logo, «رابط بودكاست» @RabetPodcast, red Subscribe button clicked by a cursor, bell ring, sound) to any video — full episode, mini episode, reel or short — or export it as a transparent asset for Premiere/DaVinci/CapCut. Use when the user says "add the subscribe button / animation / pop-up / CTA", "put subscribe at 4:30", "where should the subscribe go", or wants the subscribe asset file. Part of the rabet-podcast-studio set.
---

# Rabet Subscribe pop-up

6 s animation: card pops in → cursor clicks Subscribe (turns grey "Subscribed") → clicks the bell (it rings) →
card pops out. Sound (pop, two clicks, bell ping) at the house SFX gain 0.6. EN «SUBSCRIBE» or AR «اشترك».

## Rules (do not regress)
1. **Ask where before adding** (user rule, every full or mini episode): propose times first. Default suggestion:
   after the name cards (≈ 20 s into the body), at a topic change near the middle, and during the host's closing
   "لو وصلتوا لحد هنا…" line, before the outro logo. 3–4 per long episode, 1 per short/reel at most.
2. **Snap each time to a real pause** (word gap, not mid-sentence): find candidates in the transcript, check them with
   `../rabet-episodes/scripts/pauses.py` or Whisper word gaps. Never over a name card, a joint/swipe, or a face.
3. **Fixed look**: white card only — no dark-blue or orange backgrounds. Change the design only in
   `../rabet-episodes/templates/subscribe-cta`, then `render_cta.py --lang en --force`.
4. **Bottom-right by default** (name cards are bottom-left). Masters with a burned-in Rabet logo bottom-right (EP1):
   `--clear-logo` (card's right edge at x≈1650 of 1920). Vertical videos: `--pos tc` or `bc`, smaller `--size`.
5. Spot-check a frame at every pop-up in the **rendered** file (`--test` first for long episodes). Say what you didn't watch.

## Usage
```
python scripts/add_subscribe.py <video> 4:30 32:03 1:01:50 1:18:59            # burn in → "<video> - Subscribe.mp4"
python scripts/add_subscribe.py <video> 4:30 --clear-logo --test               # 16 s preview per pop-up
python scripts/add_subscribe.py <reel.mp4> 0:20 --pos tc --size 0.12 --lang ar
```
Options: `--lang en|ar` · `--pos br|bl|tr|tl|bc|tc` · `--clear-logo` · `--x N --y N` · `--size F` (card height /
video height, default 0.204) · `--sfx F` (default 0.6) · `-o out.mp4`. Refuses overlapping times and times past
the end. NVENC when available, else libx264; AAC 256k; the input is never overwritten.

Inside a mini episode built by rabet-episodes, don't burn it separately: set `cta` in the spec
(`{"at": ["after_intro", "middle", "end"], "lang": "en", "right_edge": 1650}`) and the builder places it.

## Source of the pop-up
`add_subscribe.py` uses `Rabet_Subscribe_<LANG>_4K.mov` (ProRes 4444 + sound) next to the script or in
`$RABET_SUBSCRIBE_DIR`; otherwise it renders once with `../rabet-episodes/scripts/render_cta.py` (HyperFrames,
~1 min) into `~/.cache/rabet-episodes/cta` and reuses it.

## Exporting editor assets
From the cached render (`cta_<lang>.mov` 2000×440 + `cta_<lang>.wav`):
```
ffmpeg -i cta_en.mov -i cta_en.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le Rabet_Subscribe_EN_4K.mov
ffmpeg -i cta_en.mov -i cta_en.wav -map 0:v -map 1:a -vf scale=1000:220 -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -c:a pcm_s16le Rabet_Subscribe_EN_1080p.mov
ffmpeg -i cta_en.mov -i cta_en.wav -map 0:v -map 1:a -vf scale=1000:220,format=yuva420p -c:v libvpx-vp9 -b:v 0 -crf 24 -auto-alt-ref 0 -c:a libopus Rabet_Subscribe_EN_1080p.webm
```
Ship them with `add_subscribe.py`, a `README.txt`, and an `Add Subscribe.bat` drag-and-drop wrapper
(`python "%~dp0add_subscribe.py" "%~1" %TIMES% %OPTS%` after two `set /p` prompts).
