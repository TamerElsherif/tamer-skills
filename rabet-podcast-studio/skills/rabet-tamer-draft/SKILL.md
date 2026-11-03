---
name: rabet-tamer-draft
description: Schedule Rabet (رابط) Podcast videos on the Rabet Podcast channels AND create matching DRAFT posts (not scheduled) on Tamer ElSherif's personal channels in Postiz, each at the best day and time for the audience, with the Tamer drafts dated one day after the Rabet post. Use when the user says /rabet-tamer-draft, "post on Rabet and draft on my channels", "schedule Rabet, keep mine as drafts". Sub-skill of rabet-studio (step 6); siblings: rabet-post-rabet, rabet-tamer.
---

# Rabet scheduled + Tamer drafts

**Targets:**
- **Rabet group → scheduled**: fb_brand, ig_brand, yt_brand (Postiz), linkedin_brand, tiktok_brand (Zernio).
- **Tamer group → drafts in Postiz only**: li_host, fb_host, ig_host, tiktok, yt_host. Postiz `type: "draft"`. Never
  schedule or publish a Tamer post in this skill; the user reviews and schedules them in Postiz.
- Never COGI. Channel ids and tag/mention rules: rabet-social "Channel groups".

Follow rabet-social for post text (humanizer, RTL, link in first comment), uploads (100 MB rule) and the tools.
Tamer's posts are written in his own voice (first person, "in this episode we talked about…"), not a copy of the
Rabet page text; his TikTok post carries `‏🎙️ @rabetpodcast` before the hashtags.

## Steps
1. **Inputs**: videos, episode number, kind (reel or long), start date (default: tomorrow), platform subset.
2. **Best times**: rabet-social `references/timing.md` + Zernio `analytics_get_best_time_to_post` (5+ posts rule).
3. **Busy days** for all ten channels (Zernio and Postiz post lists, drafts included for Tamer) → `busy.json`.
4. **Calendar**: `plan_slots.py --group both --tamer-offset 1 --items … --start … --kind … --busy busy.json --out
   <campaign folder>/calendar_rabet_tamer.csv`. Show one table with a Status column (Rabet = scheduled, Tamer =
   draft). The draft dates matter: they are the suggested publish times when the user schedules them later.
   **Wait for the user's OK**; apply edits.
5. **Create** after the OK:
   - Rabet: as /rabet-post-rabet step 5 (scheduled, Zernio posts in the episode queue with explicit time).
   - Tamer: Postiz payload with `draft` (`postiz_payload.py … draft`), date = the planned Tamer slot, tags EP +
     people.
6. **Report**: two tables, Scheduled (Rabet) and Drafts (Tamer), with ids and dates; log the ids in the episode's
   campaign CSVs with "(DRAFT)" on the Tamer rows.
