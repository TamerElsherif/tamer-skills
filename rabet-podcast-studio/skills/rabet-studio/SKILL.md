---
name: rabet-studio
description: One-command Rabet (رابط) Podcast production pipeline for a recorded episode — teaser/promo, intro and outro, name cards, subscribe pop-ups, mini-episode and reel suggestions and cuts, thumbnails, YouTube titles/descriptions/chapters, humanized posts, and a Postiz/Zernio posting schedule — in review-first mode (confirm each step) or autopilot (do everything, review after). Use when the user says "process this episode", "do the full package", "run the studio", "prepare episode N for publishing", or hands over a new recording and wants everything done. Part of the rabet-podcast-studio set.
---

# Rabet Studio (orchestrator)

Runs the other skills in this set in order. It doesn't re-implement them: open each skill's SKILL.md when you reach
its step and follow its rules (they carry the lessons from Ep 1–3; rabet-reels holds the shared engine and rules).

## 0. First question (always, one AskUserQuestion)
1. **Mode**: *Review first* (stop at every ◆ gate with suggestions, implement after approval) or *Autopilot* (do
   everything with the house defaults, then hand over one review page).
2. **Episode number + the guests' names/titles** (confirm spelling; new guest → rabet-namecards).
3. **Output folder** (house layout: full episode in the main folder; `Thumbnails/`, `Sub-Episodes/`, `Reels/`,
   `Teaser/` subfolders only when used). Render on a disk with space (never into a Google Drive folder).
Even in autopilot: **nothing is posted or scheduled publicly without an explicit OK** (drafts only).

## 1. Understand the episode
rabet-episodes `prep_episode.py` (GPU Whisper words, shots, transcript). Label who is on each shot.
Write a topic map: minute ranges, speaker, one line each, the strongest claims/numbers/stories.
Check for a teaser already in the master, burned-in name cards, and a burned-in logo (changes pop-up placement).

## 2. Full episode
- rabet-teaser: pick 5–9 moments (◆ teaser lines), build the teaser.
- Assemble: teaser → intro logo → episode → outro logo (`~/.rabet-reels.json` episodes.intro/outro).
- rabet-namecards: one card per speaker on their first solo shot after the intro (◆ card times).
- rabet-subscribe: after the name cards, middle topic change, before the outro during the host's closing (◆ times).
- Spot-check frames at every card, pop-up and joint in the rendered file.

## 3. Mini episodes (rabet-episodes)
Suggest 4–7 consolidated sub-episodes (one idea each, 7–20 min) + optional topic episode (◆ list with source ranges).
Build with cold-open hooks (rabet-teaser), cards, pop-ups (cta in each spec), check_edges → render → qa → briefs.

## 4. Reels (rabet-reels)
Suggest 8–15 reels from the strongest self-contained moments, alternating guests (◆ list). Build with S1 Clean,
cover versions + thumbnails (rabet-thumbnails), tail_check / edge_check every edge.

## 5. Packaging
- rabet-thumbnails: A/B/C for the full episode; one per mini episode; covers for reels (◆ picks).
- rabet-youtube: titles + descriptions + chapters for the full and mini episodes (◆ titles).
- rabet-social: humanized posts (humanizer skill) for every video and platform.

## 6. Schedule (rabet-social)
**Which channels** (ask once, in the first question if posting is in scope): use the matching posting sub-skill.
| Sub-skill | Rabet Podcast channels | Tamer ElSherif channels |
|---|---|---|
| /rabet-post-rabet | scheduled | not touched |
| /rabet-tamer-draft | scheduled | Postiz drafts, one day later |
| /rabet-tamer | not touched | scheduled |
All three pick each post's day and time from rabet-social `references/timing.md` + `scripts/plan_slots.py`
(best reach for Rabet's audience) and show the calendar for approval before creating anything.

Uploads: check each file's size first. Over 100 MB (Cloudflare limit in front of Postiz) → tell the user, then use
rabet-social's temporary-URL route (`scripts/tunnel_upload.py`), and close the tunnel and remove its temp folder
when done. Full episodes go to the playlist «Full Episodes», mini episodes to «Mini Episodes - Topics»
(rabet-youtube "Playlists": Zernio sets it at upload; with Postiz, hand the user a Studio checklist).
Calendar across YouTube, LinkedIn, Facebook, Instagram, TikTok (◆ calendar), then Postiz/Zernio drafts; schedule only
after the user approves the calendar.

## 7. Hand-over
One review page (Artifact or .md in the output folder): every file with its path, each decision (times, titles,
picks) and what to change it with, what was checked and what was **not** watched end to end, what is drafted vs
scheduled. In autopilot this is where the user reviews; offer to redo any item.

## Gates in review-first mode (◆)
Present each as a short table with a recommendation, wait, apply edits, continue. Batch questions where possible
(the user may leave the agent alone after answering).
