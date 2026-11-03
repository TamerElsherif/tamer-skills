---
name: rabet-podcast-studio
description: Skill set for producing and publishing Rabet (رابط) Podcast content — Egyptian Arabic + English, B2B tech — from one recorded episode: full-episode packaging (teaser, intro/outro, name cards, subscribe pop-ups), mini/sub-episodes, 9:16 reels, thumbnails, YouTube titles/descriptions/chapters, humanized posts and Postiz/Zernio scheduling. Use for any Rabet video task; it routes to the right sub-skill (rabet-studio, rabet-teaser, rabet-episodes, rabet-reels, rabet-subscribe, rabet-namecards, rabet-thumbnails, rabet-youtube, rabet-social, and the posting sub-skills rabet-post-rabet, rabet-tamer-draft, rabet-tamer).
---

# Rabet Podcast Studio

This folder is a plugin: the skills live in `skills/`. Pick the one that fits the request and follow its SKILL.md.

| Request | Skill |
|---|---|
| "Process this episode", "full package", new recording end to end | `skills/rabet-studio` |
| Teaser, promo, trailer, highlights, cold open, hook | `skills/rabet-teaser` |
| Mini / sub / topic episodes from a full episode | `skills/rabet-episodes` |
| 9:16 reels from a clip sheet or moments | `skills/rabet-reels` |
| Subscribe button / pop-up / CTA on a video | `skills/rabet-subscribe` |
| Name card / lower third for a guest | `skills/rabet-namecards` |
| YouTube thumbnail, Reels/Shorts/TikTok cover | `skills/rabet-thumbnails` |
| Titles, description, chapters, hashtags | `skills/rabet-youtube` |
| Posts, captions, content calendar, Postiz / Zernio | `skills/rabet-social` |
| Schedule on the Rabet Podcast channels only | `skills/rabet-post-rabet` |
| Schedule on Rabet + drafts on the host's own channels | `skills/rabet-tamer-draft` |
| Schedule on the host's own channels only | `skills/rabet-tamer` |

`skills/rabet-reels` is also the shared engine (fonts, logo, SFX, config loader, `cutsafe.py`, `edge_check.py`,
`tail_check.py`, GPU Whisper, thumbnail templates) and holds the house rules every other skill follows:
never cut inside a word, complete ideas only, faces never covered, RTL-safe Arabic, SFX at 0.6, no public post
without the user's OK. Per-user settings: `~/.rabet-reels.json` (see `skills/rabet-reels/config.example.json`).
