"""Shared bits for the YouTube thumbnail styles (one style per file in this folder, see yt_thumbs.py).
Every style module defines:
  NAME    style id used on the command line and in output names (lowercase, no spaces)
  LOOK    one line describing the look (shown by `yt_thumbs.py --list` and in the skill's style table)
  GUESTS  (min, max) number of guests the layout supports
  TEXT    spec fields it reads, for the --list output
  LEGACY  optional old spec block it also reads ("a"/"b"/"c" from make_episode_thumbs specs)
  render(s) -> (css, body)   s = the merged spec for this style (see yt_thumbs.merge)
Assets available in the page: assets/fonts/*, assets/logo.png, assets/logo-mark.png, assets/cut/<guest id>.png,
assets/bg/<file> (everything in rabet-reels/assets/thumb_bg), assets/pins/<i>.<ext> (spec "pins").
"""

HEAD = """
      @font-face { font-family: "LalezarLocal"; src: url("assets/fonts/Lalezar-Regular.ttf") format("truetype"); font-display: block; }
      @font-face { font-family: "AlexandriaFull"; src: url("assets/fonts/Alexandria.ttf") format("truetype"); font-weight: 100 900; font-display: block; }
      :root { --navy: #10335a; --deep: #0b2340; --teal: #1aaac1; --aqua: #07c3be; --teal-ink: #0e7487; --orange: #ff6600; --cream: #fdf9f5; --ink: #0b0d10; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1280px; height: 720px; overflow: hidden; background: var(--deep); }
      #root { position: relative; width: 1280px; height: 720px; overflow: hidden; }
"""

# cut-out styles (collage, dark, giant, stage ...): absolutely placed cut-outs with a bottom fade
CUT = """
      .abs { position: absolute; }
      .cut { position: absolute; --vm: linear-gradient(180deg, #000 58%, transparent 90%); -webkit-mask-image: var(--vm); mask-image: var(--vm); }
      .cut.fr { -webkit-mask-image: linear-gradient(90deg, #000 74%, transparent 88%), var(--vm); mask-image: linear-gradient(90deg, #000 74%, transparent 88%), var(--vm); -webkit-mask-composite: source-in; mask-composite: intersect; }
      .logo { position: absolute; width: 96px; height: 96px; object-fit: contain; }
      .ar { direction: rtl; white-space: nowrap; }
      .tag { position: absolute; font-family: "AlexandriaFull"; font-weight: 800; font-size: 20px; padding: 3px 12px 7px; direction: rtl; white-space: nowrap; box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.35); background: var(--cream); color: var(--ink); }
      .tag.t { background: var(--aqua); }
"""


def place(s, i, g, default):
    """[left, top, width] for guest g (index i): spec pos override > style default list."""
    return s.get("pos", {}).get(s["style"], {}).get(g["id"]) or default[i]


def cut(s, i, defaults, cls=""):
    g = s["guests"][i]
    left, top, width = place(s, i, g, defaults)
    fr = " fr" if g.get("fade_right") else ""
    return (f'<img class="cut {cls}{fr}" src="assets/cut/{g["id"]}.png" alt="" '
            f'style="left: {left}px; top: {top}px; width: {width}px" />')


def tags(s, places):
    """Name tags; the host (`"host": true`) gets the aqua tag."""
    return "".join(f'<div class="tag{" t" if g.get("host") else ""}" style="{p}">{g["name"]}</div>'
                   for g, p in zip(s["guests"], places))


def page(name, css, body):
    return f"""<!doctype html>
<html lang="ar">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1280, height=720" />
    <title>Rabet Thumbnail {name}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{HEAD}{css}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1280" data-height="720" data-duration="1">{body}
    </div>
    <script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""
