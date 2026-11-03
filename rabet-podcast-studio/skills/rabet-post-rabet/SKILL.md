---
name: rabet-post-rabet
description: Schedule Rabet (رابط) Podcast videos (reels, mini episodes, full episodes) on the Rabet Podcast channels ONLY (Facebook, Instagram, YouTube via Postiz; LinkedIn page and TikTok via Zernio), at the best day and time for Rabet's audience. Never touches Tamer ElSherif's personal channels. Use when the user says /rabet-post-rabet, "post on Rabet channels only", "schedule on the Rabet pages". Sub-skill of rabet-studio (step 6); siblings: rabet-tamer-draft, rabet-tamer.
---

# Rabet channels only

**Targets:** the **Rabet** group in rabet-social "Channel groups": fb_brand, ig_brand, yt_brand (Postiz),
linkedin_brand, tiktok_brand (Zernio). **Never** a Tamer channel (li_host, fb_host, ig_host, tiktok, yt_host) and
never COGI. If a request would need a Tamer channel, stop and point to /rabet-tamer-draft or /rabet-tamer.

Follow rabet-social for post text (humanizer, RTL, link in first comment), uploads (100 MB rule) and the tools.

## Steps
1. **Inputs**: which videos (paths or reel numbers), episode number, kind (reel or long), start date (default:
   tomorrow), platform subset if the user named one. Posts text: reuse the episode's captions files when they exist.
2. **Best times**: read `references/timing.md` (rabet-social) and Zernio `analytics_get_best_time_to_post`; use measured
   slots only with 5+ posts behind them.
3. **Busy days**: list the target channels' upcoming posts (Zernio `posts_list_posts` from today; Postiz posts list
   for fb_brand/ig_brand/yt_brand) and write them as `busy.json` (Cairo time).
4. **Calendar**: `python ~/.claude/skills/rabet-social/scripts/plan_slots.py --group rabet --items … --start …
   --kind reel|long --busy busy.json --out <episode campaign folder>/calendar_rabet.csv`. Show it as a table
   (date, day, time, channel, video) with one line on why those times. **Wait for the user's OK**; apply edits.
5. **Create** (only after the OK), status **scheduled**:
   - Postiz channels: rabet-social Postiz flow with `schedule`, tags EP + people.
   - Zernio channels: `posts_create` with `scheduled_for`, `queued_from_profile` + the episode `queue_id`, `tags`,
     LinkedIn mentions, first comment with the YouTube link (`platformSpecificData.firstComment`). `validate_post`
     first.
6. **Report**: table of post ids, channel, date/time, and the CSV log path (append ids to the episode's
   `postiz_*.csv` / `zernio_*.csv`). Say what is scheduled and that no Tamer channel was touched.
