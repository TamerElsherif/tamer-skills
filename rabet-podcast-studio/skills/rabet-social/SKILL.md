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
   **Files over 100 MB** (most mini and full episodes): Postiz sits behind Cloudflare, which rejects any upload
   request over 100 MB (HTTP 413). Check every file's size first. Under 100 MB → normal upload. Over 100 MB → never
   send it to the upload API; use a **temporary public URL** instead (tested 2026-11-01, 384 MB–4 GB):
   1. Tell the user first, in one line: which files, their sizes, and that a temporary Cloudflare tunnel will expose
      only those files for the duration of the upload and be closed straight after.
   2. `python scripts/tunnel_upload.py start <file> …` → one `https://….trycloudflare.com/fNN.ext` URL per file.
      It hard-links the files into `<drive>:\rabet_tunnel_tmp` (no extra disk space, originals untouched).
   3. Per file, one at a time: Postiz `uploadFromUrlTool` with the URL. The call reports "server isn't responding"
      after ~60 s, but Postiz keeps downloading (and retries once). Run `tunnel_upload.py wait`, then find the new item
      in `mediaListTool` and check its `Content-Length` equals the local file size before using it. Thumbnails can go
      the same way.
      **Postiz's own URL-upload cap is ~1 GB** ("File is too large": 829 MB passed, 1,046 MB failed). For a file a bit
      over it, make a temporary smaller copy in the tunnel folder (ffmpeg `h264_nvenc -rc vbr -b:v` sized to ≈ 900 MB,
      `-c:a copy`; ~6 Mbps is fine for 1080p since YouTube re-encodes anyway) and delete it on `stop`. A full episode
      (3–4 GB) can't go through Postiz: upload it in YouTube Studio, or via Zernio if YouTube is connected there.
   4. Create the posts (YouTube: `type` private unless told otherwise) **one at a time**: wait until each is
      PUBLISHED in `postsListTool` before creating the next. Four at once failed with "The media storage did not
      return the requested byte range"; the same post sent alone went through. A failed post stays in Postiz as ERROR
      (Postiz tools can't delete it; tell the user to remove it in the app). If one file keeps failing alone with the
      byte-range error, pull a fresh copy into Postiz (new `uploadFromUrlTool`) and post with the new path: that fixed
      EP1 Sub-04 after 3 failures. Large posts can sit in QUEUE for ~10 min before PUBLISHED. Then **always** `tunnel_upload.py stop` (also
      after any error): it closes the tunnel and server and deletes the temp folder (links only, never the originals).
      Confirm nothing is left: no `rabet_tunnel_tmp` folder, no cloudflared process.
5. **Nothing goes public without the user's explicit OK**: create drafts by default; schedule only after the user
   approves the calendar; never "publish now" unasked. Report what was created where (post ids, dates).
6. Replacing an existing post: rebuild from the current server text and tags, create the replacement, then delete the
   old one (rule 17) — only with the user's OK.
