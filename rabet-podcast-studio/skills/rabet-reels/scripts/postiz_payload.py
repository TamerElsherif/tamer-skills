"""Build the Postiz payload (socialPost array) for one reel: 8 channel posts (+ first comments) + 4 stories.

Inputs: captions JSON (one entry per reel id), uploads.json (postiz_upload.py cache), the reel's clean + cover
file names, a campaign day (Cairo local date) and the post type (draft | schedule). Channels come from
~/.rabet-reels.json (see config.example.json).

Slots (Cairo): LinkedIn 09:30 · YT brand 17:00 · YT host 18:00 · FB brand 19:30 · FB host 20:00 ·
IG brand 20:30 · IG host 21:00 · TikTok 21:30 · IG/FB stories 22:00. Egypt DST: UTC+3 from the last Friday
of April to the last Thursday of October, UTC+2 otherwise.

Caption fields per reel: linkedin, linkedin_comment, facebook_brand(+_comment), facebook_host(+_comment),
instagram_brand, instagram_host, instagram_comment, tiktok_title, tiktok, youtube_brand_title/desc,
youtube_host_title/desc, story_text. (Older "_rabet"/"_tamer" field names are accepted too.)

usage: python postiz_payload.py <captions.json> <reel id> <uploads.json> <clean.mp4> <cover.mp4> <YYYY-MM-DD> <out.json> [draft|schedule]
"""
import datetime as dt
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

SLOTS = {"li_host": "09:30", "yt_brand": "17:00", "yt_host": "18:00", "fb_brand": "19:30", "fb_host": "20:00",
         "ig_brand": "20:30", "ig_host": "21:00", "tiktok": "21:30", "story": "22:00"}
RLM = "‏"


def cairo_offset(day):
    y = day.year
    last_thu = max(dt.date(y, 10, d) for d in range(25, 32) if dt.date(y, 10, d).weekday() == 3)
    first_fri_dst = max(dt.date(y, 4, d) for d in range(24, 31) if dt.date(y, 4, d).weekday() == 4)
    return 3 if first_fri_dst <= day <= last_thu else 2


def utc(day, hhmm):
    h, m = map(int, hhmm.split(":"))
    t = dt.datetime(day.year, day.month, day.day, h, m) - dt.timedelta(hours=cairo_offset(day))
    return t.strftime("%Y-%m-%dT%H:%M:00.000Z")


def to_html(text):
    """One <p> per line; RLM at the start of every Arabic line so mixed RTL/LTR lines render right-to-left."""
    out = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        lead = "" if line.startswith(("http", ".")) else RLM
        out.append(f"<p>{lead}{html.escape(line, quote=False)}</p>")
    return "".join(out)


def field(c, key):
    """Accept the neutral brand/host names and the older rabet/tamer ones."""
    if key in c:
        return c[key]
    return c[key.replace("_brand", "_rabet").replace("_host", "_tamer")]


def main(cap_p, reel, up_p, clean, cover, day_s, out_p, kind="draft"):
    ch = config.channels(config.load())
    c = json.load(open(cap_p, encoding="utf-8"))[reel]
    up = json.load(open(up_p, encoding="utf-8"))
    # cache keys are "<name>:<size>" — match the file as it is now (a re-rendered reel has a new size and a new upload)
    base = Path(up_p).parent
    path = lambda name: up[f"{name}:{(base / name).stat().st_size}"]["path"]
    clean_u, cover_u = path(clean), path(cover)
    day = dt.date.fromisoformat(day_s)

    def post(key, slot, body, media, comments=(), settings=()):
        items = [{"content": to_html(body), "attachments": [media]}] + [{"content": to_html(x), "attachments": []} for x in comments]
        return {"integrationId": ch[key]["id"], "isPremium": False, "date": utc(day, slot), "shortLink": False, "type": kind,
                "settings": list(settings), "postsAndComments": items}

    yt = lambda title: [{"key": "title", "value": title[:100]}, {"key": "type", "value": "public"}, {"key": "selfDeclaredMadeForKids", "value": "no"}]
    tt = [{"key": "title", "value": c["tiktok_title"][:90]}, {"key": "privacy_level", "value": "PUBLIC_TO_EVERYONE"},
          {"key": "duet", "value": True}, {"key": "stitch", "value": True}, {"key": "comment", "value": True},
          {"key": "autoAddMusic", "value": "no"}, {"key": "brand_content_toggle", "value": False},
          {"key": "brand_organic_toggle", "value": False}, {"key": "video_made_with_ai", "value": False},
          {"key": "content_posting_method", "value": "DIRECT_POST"}]
    pt = lambda k: [{"key": "post_type", "value": k}]
    posts = [
        post("li_host", SLOTS["li_host"], c["linkedin"], cover_u, [c["linkedin_comment"]]),
        post("yt_brand", SLOTS["yt_brand"], field(c, "youtube_brand_desc"), cover_u, settings=yt(field(c, "youtube_brand_title"))),
        post("yt_host", SLOTS["yt_host"], field(c, "youtube_host_desc"), cover_u, settings=yt(field(c, "youtube_host_title"))),
        post("fb_brand", SLOTS["fb_brand"], field(c, "facebook_brand"), cover_u, [field(c, "facebook_brand_comment")], pt("post")),
        post("fb_host", SLOTS["fb_host"], field(c, "facebook_host"), cover_u, [field(c, "facebook_host_comment")], pt("post")),
        post("ig_brand", SLOTS["ig_brand"], field(c, "instagram_brand"), cover_u, [c["instagram_comment"]], pt("post")),
        post("ig_host", SLOTS["ig_host"], field(c, "instagram_host"), cover_u, [c["instagram_comment"]], pt("post")),
        post("tiktok", SLOTS["tiktok"], c["tiktok"], cover_u, settings=tt),
    ] + [post(k, SLOTS["story"], c["story_text"], clean_u, settings=pt("story")) for k in ("ig_brand", "ig_host", "fb_brand", "fb_host")]
    json.dump({"socialPost": posts}, open(out_p, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{out_p}: {len(posts)} {kind} posts on {day_s} (UTC+{cairo_offset(day)})")


if __name__ == "__main__":
    main(*sys.argv[1:9])
