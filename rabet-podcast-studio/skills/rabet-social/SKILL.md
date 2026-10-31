---
name: rabet-social
description: Write humanized social posts for Rabet (رابط) Podcast reels, mini episodes and full episodes (LinkedIn, Facebook, Instagram, TikTok, YouTube Shorts, X), and plan and schedule them through Postiz and/or Zernio as drafts or scheduled posts with a posting calendar. Use when the user asks for captions, post text, a content calendar, "schedule the reels", "draft the posts", "post this on LinkedIn/Facebook", or best times to post. Part of the rabet-podcast-studio set.
---

# Rabet social posts + scheduling

## Writing posts
- Egyptian Arabic mixed with English terms, B2B tech audience (developers, PMs, engineering managers, founders).
- One post per video per platform, shaped for it: LinkedIn (insight + question, 3–6 short paragraphs), Facebook
  (warmer, shorter), Instagram/TikTok (hook line + 2–3 lines + hashtags), Shorts (title-like line).
- Always run every draft through the **humanizer** skill before showing or saving it. No hype words, no em-dash
  chains, no invented claims (rabet-reels rule 1).
- RTL (rabet-reels rule 8): an RLM (U+200F) at the start of each Arabic line; no line starts with an English word.
- **No YouTube link in Facebook / LinkedIn post text** (rule 17): end with «الحلقة كاملة على YouTube، اللينك في أول
  كومنت 👇» before the hashtags; the link goes in the **first comment** («الحلقة كاملة على YouTube:» + link).
- Tag the guests where the platform allows (LinkedIn profile links above in rabet-youtube).

## Scheduling (Postiz and Zernio)
1. Build one calendar first and show it: date, time, platform, account, video, post. Default rhythm: full episode day 0,
   then one reel or mini episode per day, alternating guests so the feed doesn't repeat; LinkedIn on weekday
   mornings (Cairo time), Facebook/Instagram evenings. Use the tools' best-time data when available
   (Zernio `analytics_get_best_time_to_post`).
2. **Postiz** (already wired, settings in `~/.rabet-reels.json`): `../rabet-reels/scripts/postiz_upload.py` →
   `postiz_payload.py <captions> NN uploads.json <clean> <cover> YYYY-MM-DD payload.json [draft|schedule]` →
   `postiz_drafts.py payload.json NN posts.csv`.
3. **Zernio** (MCP tools `accounts_list`, `media_generate_upload_link`, `posts_create`, `posts_cross_post`,
   `validate_post`): list accounts first; when a platform has more than one account, ask which one — never guess.
   Validate every post (`validate_post`, `validate_media`) before creating it.
4. Which tool posts to which account is the user's choice — ask once and remember it (e.g. in `~/.rabet-reels.json`
   `"social": {"linkedin": "postiz", "tiktok": "zernio"}`).
5. **Nothing goes public without the user's explicit OK**: create drafts by default; schedule only after the user
   approves the calendar; never "publish now" unasked. Report what was created where (post ids, dates).
6. Replacing an existing post: rebuild from the current server text and tags, create the replacement, then delete the
   old one (rule 17) — only with the user's OK.
