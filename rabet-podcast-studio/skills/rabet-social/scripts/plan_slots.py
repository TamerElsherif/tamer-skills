"""Posting calendar for Rabet videos: picks a day and time per video per channel from the audience timing rules
(references/timing.md), skipping days a channel already has a post. Prints a table and writes a CSV.

Channel groups (ids from ~/.rabet-reels.json):
  rabet  Rabet Podcast pages: Facebook, Instagram, YouTube (Postiz) + LinkedIn page, TikTok (Zernio)
  tamer  Tamer ElSherif channels: LinkedIn, Facebook, Instagram, TikTok, YouTube (Postiz)
The COGI YouTube channel is never in a group.

usage: python plan_slots.py --group rabet|tamer|both --items "Reel 01" "Reel 02" ... --start YYYY-MM-DD
         [--platforms linkedin,tiktok] [--busy busy.json] [--tamer-offset 1] [--gap 1] [--out calendar.csv]
  --busy        JSON {"<channel key>": ["2026-11-04T21:30", ...]} existing posts (Cairo time) to avoid
  --tamer-offset  days the Tamer post of a video comes after its Rabet post (with --group both)
  --kind        reel (default) or long (full / mini episode: YouTube gets it, TikTok and IG skip it)
"""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def _last(year, month, weekday):
    d = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - weekday) % 7)


class _Cairo(dt.tzinfo):
    """Egypt time without tzdata (Windows): UTC+2, summer time UTC+3 from the last Friday of April to the last
    Thursday of October (rule since 2023)."""

    def utcoffset(self, d):
        on = _last(d.year, 4, 4) <= d.date() <= _last(d.year, 10, 3)
        return dt.timedelta(hours=3 if on else 2)

    def dst(self, d):
        return self.utcoffset(d) - dt.timedelta(hours=2)

    def tzname(self, d):
        return "EEST" if self.dst(d) else "EET"


try:
    CAIRO = ZoneInfo("Africa/Cairo")
except ZoneInfoNotFoundError:
    CAIRO = _Cairo()
CFG = json.load(open(Path.home() / ".rabet-reels.json", encoding="utf-8"))
CH, ZN = CFG.get("channels", {}), CFG.get("zernio", {})

# key: (group, platform, tool). Ids come from the config; a channel missing there is left out.
GROUPS = {
    "fb_brand": ("rabet", "facebook", "postiz"), "ig_brand": ("rabet", "instagram", "postiz"),
    "yt_brand": ("rabet", "youtube", "postiz"), "linkedin_brand": ("rabet", "linkedin", "zernio"),
    "tiktok_brand": ("rabet", "tiktok", "zernio"),
    "li_host": ("tamer", "linkedin", "postiz"), "fb_host": ("tamer", "facebook", "postiz"),
    "ig_host": ("tamer", "instagram", "postiz"), "tiktok": ("tamer", "tiktok", "postiz"),
    "yt_host": ("tamer", "youtube", "postiz"),
}
CHANNELS = {}
for _k, (_g, _p, _t) in GROUPS.items():
    _id = ZN.get(_k) if _t == "zernio" else (CH.get(_k) or {}).get("id")
    if _id and not _id.startswith("<"):
        CHANNELS[_k] = (_g, _p, _t, _id)

# Cairo time. weekday(): Mon=0 .. Sun=6. Egypt works Sun-Thu; Fri/Sat are the weekend.
# days: allowed days, best first. times: best first (the Rabet slot); the Tamer slot takes the second time so the
# two feeds don't publish the same video at the same minute.
RULES = {
    "linkedin": {"days": [6, 0, 1, 2, 3], "times": ["09:30", "17:30", "13:00"]},
    "facebook": {"days": [3, 4, 5, 6, 0, 1, 2], "times": ["20:30", "21:30", "14:00"]},
    "instagram": {"days": [3, 4, 5, 6, 0, 1, 2], "times": ["20:00", "21:00", "13:00"]},
    "tiktok": {"days": [3, 4, 5, 6, 0, 1, 2], "times": ["21:30", "22:30", "20:00"]},
    "youtube": {"days": [3, 4, 5, 6, 0, 1, 2], "times": ["17:00", "18:00", "19:00"]},
}
LONG_SKIP = {"tiktok", "instagram"}


def plan(args):
    busy = json.load(open(args.busy, encoding="utf-8")) if args.busy else {}
    taken = {k: {t[:10] for t in v} for k, v in busy.items()}
    plats = set(args.platforms.split(",")) if args.platforms else None
    start = dt.date.fromisoformat(args.start)
    rows, rabet_day = [], {}
    for key, (group, plat, tool, cid) in CHANNELS.items():  # Rabet channels first, so Tamer can follow them
        if args.group != "both" and group != args.group:
            continue
        if (plats and plat not in plats) or (args.kind == "long" and plat in LONG_SKIP):
            continue
        rule = RULES[plat]
        tamer_second = group == "tamer" and args.group == "both"
        hhmm = rule["times"][1 if tamer_second else 0]
        day = start + dt.timedelta(days=args.tamer_offset if tamer_second else 0)
        used = taken.setdefault(key, set())
        for item in args.items:
            if tamer_second and (plat, item) in rabet_day:  # a day after this video's Rabet post at the earliest
                day = max(day, rabet_day[plat, item] + dt.timedelta(days=args.tamer_offset))
            while day.weekday() not in rule["days"] or day.isoformat() in used:
                day += dt.timedelta(days=1)
            used.add(day.isoformat())
            if group == "rabet":
                rabet_day[plat, item] = day
            local = dt.datetime.combine(day, dt.time.fromisoformat(hhmm), CAIRO)
            rows.append({"item": item, "channel": key, "group": group, "platform": plat, "tool": tool, "id": cid,
                         "date": day.isoformat(), "day": day.strftime("%a"), "time_cairo": hhmm,
                         "utc": local.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            day += dt.timedelta(days=args.gap)
    rows.sort(key=lambda r: (r["utc"], r["channel"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", choices=["rabet", "tamer", "both"], required=True)
    ap.add_argument("--items", nargs="+", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--platforms")
    ap.add_argument("--busy")
    ap.add_argument("--kind", choices=["reel", "long"], default="reel")
    ap.add_argument("--tamer-offset", type=int, default=1)
    ap.add_argument("--gap", type=int, default=1)
    ap.add_argument("--out", default="calendar.csv")
    args = ap.parse_args()
    rows = plan(args)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f'{r["date"]} {r["day"]} {r["time_cairo"]}  {r["channel"]:<15} {r["tool"]:<6} {r["item"]}')
    print(f"{len(rows)} posts -> {args.out}")


if __name__ == "__main__":
    main()
