---
name: rabet-tamer
description: Schedule Rabet (رابط) Podcast videos on Tamer ElSherif's personal channels ONLY (LinkedIn, Facebook, Instagram, TikTok, YouTube via Postiz) at the best day and time for the audience. Never touches any Rabet Podcast channel. Use when the user says /rabet-tamer, "post on my channels only", "schedule on Tamer's accounts". Sub-skill of rabet-studio (step 6); siblings: rabet-post-rabet, rabet-tamer-draft.
---

# Tamer channels only

**Targets:** the **Tamer** group in rabet-social "Channel groups", all in Postiz: li_host, fb_host, ig_host,
tiktok, yt_host. **Never** a Rabet channel (fb_brand, ig_brand, yt_brand, linkedin_brand, tiktok_brand; nothing in
Zernio) and never COGI. If a request needs a Rabet channel, stop and point to /rabet-post-rabet or /rabet-tamer-draft.

Follow rabet-social for post text (humanizer, RTL, link in first comment), uploads (100 MB rule) and the Postiz flow.
Write in Tamer's own voice (first person), mention the Rabet page where the platform allows it
(TikTok: `‏🎙️ @rabetpodcast` before the hashtags), tag the featured guests on LinkedIn.

## Steps
1. **Inputs**: videos, episode number, kind (reel or long), start date (default: tomorrow), platform subset.
2. **Best times**: rabet-social `references/timing.md` + Zernio `analytics_get_best_time_to_post` (5+ posts rule).
   If the Rabet channels already carry the same video, start Tamer's posts the day after the Rabet post.
3. **Busy days**: Postiz posts (scheduled and drafts) on the five Tamer channels → `busy.json`.
4. **Calendar**: `plan_slots.py --group tamer --items … --start … --kind … --busy busy.json --out <campaign
   folder>/calendar_tamer.csv`. Show the table and **wait for the user's OK**; apply edits.
5. **Create** after the OK: Postiz flow with `schedule`, tags EP + people.
6. **Report**: post ids, channel, date/time, CSV log; say that no Rabet channel was touched.
