# Rabet posting times (audience rules)

Audience: Egyptian and Gulf B2B tech people (developers, PMs, engineering managers, founders). All times are Cairo
time (Africa/Cairo). Egypt works **Sunday to Thursday**; Friday and Saturday are the weekend. Thursday night and
Friday are the strongest leisure-scrolling times.

| Platform | Days (best first) | Times (best first) | Why |
|---|---|---|---|
| LinkedIn | Sun, Mon, Tue, Wed, Thu (never Fri/Sat) | 09:30, 17:30, 13:00 | Start of the work day, end-of-day commute, lunch |
| Facebook | Thu, Fri, Sat, then the rest | 20:30, 21:30, 14:00 | Evening home time; Friday after prayer |
| Instagram | Thu, Fri, Sat, then the rest | 20:00, 21:00, 13:00 | Evening peak |
| TikTok | Thu, Fri, Sat, then the rest | 21:30, 22:30, 20:00 | Late evening peak |
| YouTube (long, Shorts) | Thu, Fri, Sat, then the rest | 17:00, 18:00, 19:00 | 2 to 3 hours before the evening peak, so the video is indexed when people watch |

House rules:
- One post per channel per day. Alternate guests so a feed doesn't show the same person twice in a row.
- The full episode goes first (day 0). Reels and mini episodes start the next day.
- When Rabet and Tamer channels both post the same video, the Tamer post comes **one day later** at the second-best
  time, so the two feeds don't compete and Tamer's post can point people to the Rabet one.
- Avoid big local moments (Ramadan iftar 17:00–19:30 → move evening posts to 21:30+; Eid days; national matches).
- Never put two posts in the same hour on the same channel. Keep at least 30 minutes between channels of one group.

## Use real data when there is enough
Before planning, read the measured best times:
- Zernio: `call_tool` `analytics_get_best_time_to_post` (optionally `{"account_id": ...}` per channel). Rows give
  `day_of_week` (0 = Sunday … 6 = Saturday) and `hour` (UTC), with `post_count`.
- Use a measured slot instead of the table only when its `post_count` is **5 or more** and it beats the table's slot
  for that platform. Say which times came from data and which from the table.
- On 2026-11-03 every slot had `post_count` 1, so the table above is in use.
