"""Scene -> HTML renderers shared by html_lesson.py, deck.py (deck.html) and jobaid.py.

Every visible string comes from storyboard props / quiz data. UI chrome labels (Next, Check answer…)
come from _common.UI. Icons are inline SVG. Interactivity is wired by templates/lesson.js via data-* hooks.
"""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import icons
from _common import display_name, esc, find_scene_audio, strip_cues, ui, is_rtl
from figures import persona, set_svg

TONE = {"warn": "warn", "safe": "safe", "info": "info", "bad": "warn", None: "info"}


class Ctx:
    """Render context: doc, language, quiz items, media copying, interactivity mode."""

    def __init__(self, doc: dict, base_dir: Path, out_dir: Path | None, quiz: dict | None = None,
                 interactive: bool = True, media_prefix: str = "media"):
        self.doc = doc
        self.rtl = is_rtl(doc)
        self.t = ui(doc)
        self.base = base_dir
        self.out = out_dir
        self.interactive = interactive
        self.media_prefix = media_prefix
        self.quiz = quiz
        self.items = {i["id"]: i for i in (quiz or {}).get("items", [])}
        self.broll = {b["id"]: b for b in doc.get("broll_shots", [])}
        self.images = {g["id"]: g for g in doc.get("generated_images", [])}
        self.scene_ids = [s["id"] for s in doc["scenes"]]
        self.missing: list[str] = []

    def media(self, rel: str | None) -> str | None:
        """Copy a media file (path relative to the storyboard) into out/media; return its relative URL."""
        if not rel:
            return None
        src = Path(rel)
        if not src.is_absolute():
            src = (self.base / rel).resolve()
        if not src.exists():
            self.missing.append(rel)
            return None
        if self.out is None:
            return src.as_uri()
        dst_dir = self.out / self.media_prefix
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src.name
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
        return f"{self.media_prefix}/{src.name}"

    def txt(self, obj: dict, key: str) -> str:
        if self.rtl and obj.get(f"{key}_ar"):
            return obj[f"{key}_ar"]
        return obj.get(key, "") or ""


def ico(name, size=24, cls="ico"):
    return icons.svg(name or "dot", size=size, cls=cls)


def head(p: dict, tag="h2", key="title"):
    out = ""
    if p.get("kicker"):
        out += f'<p class="kicker">{esc(p["kicker"])}</p>'
    if p.get(key):
        out += f'<{tag} class="scene-title" tabindex="-1">{esc(p[key])}</{tag}>'
    return out


def items_list(items, cls="bul"):
    li = []
    for it in items:
        tone = TONE.get(it.get("tone"), "info")
        icon = ico(it.get("icon") or ("alert-triangle" if tone == "warn" else "check" if tone == "safe" else "dot"))
        sub = f'<span class="sub">{esc(it["sub"])}</span>' if it.get("sub") else ""
        li.append(f'<li class="tone-{tone}"><span class="bi">{icon}</span><span><strong>{esc(it["text"])}</strong>{sub}</span></li>')
    return f'<ul class="{cls}">{"".join(li)}</ul>'


def media_block(ctx: Ctx, shot_id: str | None = None, image_id: str | None = None, scene=None, chips=None, cls="media"):
    url, kind = None, "img"
    if shot_id and shot_id in ctx.broll:
        url = ctx.media(ctx.broll[shot_id].get("path"))
        if url and url.lower().endswith((".mp4", ".webm", ".mov", ".m4v")):
            kind = "video"
    elif image_id and image_id in ctx.images:
        url = ctx.media(ctx.images[image_id].get("path"))
    chip_html = "".join(f'<span class="chip">{esc(c)}</span>' for c in (chips or []))
    chip_html = f'<div class="chips">{chip_html}</div>' if chip_html else ""
    alt = esc((scene or {}).get("visual", ""))
    if url and kind == "video":
        inner = (f'<video src="{esc(url)}" muted loop autoplay playsinline preload="metadata" aria-label="{alt}"></video>')
    elif url:
        inner = f'<img src="{esc(url)}" alt="{alt}" loading="lazy">'
    else:
        inner = (f'<div class="ph" role="img" aria-label="{alt or esc(ctx.t["image_missing"])}">{ico("eye", 40)}'
                 f'<span>{alt}</span></div>')
    return f'<figure class="{cls}">{inner}{chip_html}</figure>'

# ------------------------------------------------------------------------------------------- templates

def t_title(p, s, ctx):
    part = f'<p class="part">{esc(p["part"])}</p>' if p.get("part") else ""
    icon = f'<div class="hero-ico">{ico(p["icon"], 56)}</div>' if p.get("icon") else ""
    sub = f'<p class="lead">{esc(p["sub"])}</p>' if p.get("sub") else ""
    kick = f'<p class="kicker">{esc(p["kicker"])}</p>' if p.get("kicker") else ""
    return f'<div class="hero">{icon}{kick}<h1 class="scene-title" tabindex="-1">{esc(p["title"])}</h1>{sub}{part}</div>'


def t_section(p, s, ctx):
    n = f'<span class="sec-n">{esc(p["n"])}</span>' if p.get("n") not in (None, "") else ""
    icon = f'<div class="hero-ico">{ico(p["icon"], 48)}</div>' if p.get("icon") else ""
    sub = f'<p class="lead">{esc(p["sub"])}</p>' if p.get("sub") else ""
    return f'<div class="hero sec">{icon}{n}<h2 class="scene-title" tabindex="-1">{esc(p["title"])}</h2>{sub}</div>'


def t_bullets(p, s, ctx):
    body = items_list(p.get("items", []))
    if p.get("side_broll"):
        return head(p) + f'<div class="split">{body}{media_block(ctx, shot_id=p["side_broll"], scene=s)}</div>'
    return head(p) + body


def t_icon_grid(p, s, ctx):
    cards = []
    for it in p.get("items", []):
        tone = TONE.get(it.get("tone"), "info")
        sub = f'<p class="sub">{esc(it["sub"])}</p>' if it.get("sub") else ""
        cards.append(f'<li class="card tone-{tone}"><span class="gi">{ico(it["icon"], 36)}</span>'
                     f'<strong>{esc(it["label"])}</strong>{sub}</li>')
    cols = int(p.get("cols") or min(3, max(1, len(cards))))
    return head(p) + f'<ul class="grid" style="--cols:{cols}">{"".join(cards)}</ul>'


def t_steps(p, s, ctx):
    li = []
    for i, st in enumerate(p.get("steps", []), 1):
        icon = f'<span class="st-ico">{ico(st["icon"], 22)}</span>' if st.get("icon") else ""
        sub = f'<span class="sub">{esc(st["sub"])}</span>' if st.get("sub") else ""
        li.append(f'<li><span class="st-n" aria-hidden="true">{i}</span><div class="st-b">{icon}<strong>{esc(st["label"])}</strong>{sub}</div></li>')
    return head(p) + f'<ol class="steps{" danger" if p.get("danger") else ""}">{"".join(li)}</ol>'


def flow_layers(nodes, edges):
    ids = [n["id"] for n in nodes]
    incoming = {i: 0 for i in ids}
    for e in edges:
        if e["to"] in incoming:
            incoming[e["to"]] += 1
    depth = {}
    starts = [n["id"] for n in nodes if n.get("kind") == "start"] or [i for i in ids if incoming[i] == 0] or ids[:1]
    frontier = [(i, 0) for i in starts]
    while frontier:
        nid, d = frontier.pop(0)
        if nid in depth and depth[nid] >= d or d > len(ids):
            continue
        depth[nid] = d
        for e in edges:
            if e["from"] == nid:
                frontier.append((e["to"], d + 1))
    for i in ids:
        depth.setdefault(i, max(depth.values(), default=-1) + 1)
    return depth


def t_process_flow(p, s, ctx):
    nodes, edges = p.get("nodes", []), p.get("edges", [])
    depth = flow_layers(nodes, edges)
    cols = max(depth.values(), default=0) + 1
    rowc = {}
    boxes = []
    for n in nodes:
        d = depth[n["id"]]
        rowc[d] = rowc.get(d, 0) + 1
        kind = n.get("kind", "step")
        boxes.append(f'<div class="fnode k-{kind}" data-node="{esc(n["id"])}" style="grid-column:{d+1};grid-row:{rowc[d]}">'
                     f'<span>{esc(n["label"])}</span></div>')
    edata = esc(json.dumps([{"from": e["from"], "to": e["to"], "label": e.get("label", "")} for e in edges], ensure_ascii=False))
    labels = "".join(f'<span class="elabel" data-e="{i}">{esc(e["label"])}</span>' for i, e in enumerate(edges) if e.get("label"))
    return head(p) + (f'<div class="flow" data-edges="{edata}" style="--cols:{cols}">'
                      f'<svg class="flow-svg" aria-hidden="true"></svg>{"".join(boxes)}{labels}</div>')


def t_timeline(p, s, ctx):
    li = []
    for ev in p.get("events", []):
        when = f'<span class="when">{esc(ev["when"])}</span>' if ev.get("when") else ""
        sub = f'<span class="sub">{esc(ev["sub"])}</span>' if ev.get("sub") else ""
        li.append(f'<li><span class="dot" aria-hidden="true"></span>{when}<strong>{esc(ev["label"])}</strong>{sub}</li>')
    return head(p) + f'<ol class="timeline">{"".join(li)}</ol>'


def t_do_dont(p, s, ctx):
    t = ctx.t
    dont = "".join(f'<li>{ico("x", 22)}<span>{esc(x)}</span></li>' for x in p.get("dont", []))
    do = "".join(f'<li>{ico("check", 22)}<span>{esc(x)}</span></li>' for x in p.get("do", []))
    return head(p) + (f'<div class="dd"><div class="dd-col dont"><h3>{ico("x-circle", 26)}{esc(p.get("dont_head") or t["dont"])}</h3><ul>{dont}</ul></div>'
                      f'<div class="dd-col do"><h3>{ico("check-circle", 26)}{esc(p.get("do_head") or t["do"])}</h3><ul>{do}</ul></div></div>')


def t_comparison(p, s, ctx):
    def col(c, cls):
        return f'<div class="cmp-col {cls}"><h3>{esc(c["head"])}</h3><ul>{"".join(f"<li>{esc(x)}</li>" for x in c.get("items", []))}</ul></div>'
    return head(p) + f'<div class="cmp">{col(p["left"], "l")}<span class="vs" aria-hidden="true">{ico("arrow-right", 28)}</span>{col(p["right"], "r")}</div>'


def t_stat(p, s, ctx):
    v = p.get("value", 0)
    shown = f"{v:,}" if isinstance(v, int) or float(v).is_integer() else f"{v}"
    icon = f'<div class="hero-ico">{ico(p["icon"], 48)}</div>' if p.get("icon") else ""
    src = f'<p class="src">{esc(p["source"])}</p>' if p.get("source") else ""
    return (f'<div class="hero stat">{icon}<p class="num" data-count="{esc(v)}"><span>{esc(p.get("prefix", ""))}</span>'
            f'<span class="n">{esc(shown)}</span><span>{esc(p.get("suffix", ""))}</span></p>'
            f'<h2 class="scene-title" tabindex="-1">{esc(p["label"])}</h2>{src}</div>')


def t_definition(p, s, ctx):
    icon = f'<span class="def-ico">{ico(p["icon"], 40)}</span>' if p.get("icon") else ""
    note = f'<p class="note">{ico("info", 20)}<span>{esc(p["note"])}</span></p>' if p.get("note") else ""
    return f'<div class="def card">{icon}<h2 class="scene-title term" tabindex="-1">{esc(p["term"])}</h2><p class="def-t">{esc(p["def"])}</p>{note}</div>'


def t_statement(p, s, ctx):
    text = esc(p["text"])
    if p.get("accent") and esc(p["accent"]) in text:
        a = esc(p["accent"])
        text = text.replace(a, f'<mark>{a}</mark>', 1)
    icon = f'<div class="hero-ico">{ico(p["icon"], 48)}</div>' if p.get("icon") else ""
    sub = f'<p class="lead">{esc(p["sub"])}</p>' if p.get("sub") else ""
    return f'<div class="hero statement{" light" if p.get("light") else ""}">{icon}<p class="big scene-title" tabindex="-1">{text}</p>{sub}</div>'


def t_table(p, s, ctx):
    th = "".join(f'<th scope="col">{esc(c)}</th>' for c in p.get("columns", []))
    rows = "".join("<tr>" + "".join((f'<th scope="row">{esc(c)}</th>' if j == 0 else f"<td>{esc(c)}</td>")
                                    for j, c in enumerate(r)) + "</tr>" for r in p.get("rows", []))
    cap = f'<caption class="scene-title" tabindex="-1">{esc(p["title"])}</caption>' if p.get("title") else ""
    return f'<div class="tbl-wrap"><table class="tbl">{cap}<thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'


def t_checklist(p, s, ctx):
    li = []
    for i, x in enumerate(p.get("items", [])):
        cid = f'{s["id"]}-c{i}'
        if ctx.interactive:
            li.append(f'<li><input type="checkbox" id="{cid}" data-check="{cid}"><label for="{cid}">{esc(x)}</label></li>')
        else:
            li.append(f'<li><span class="box" aria-hidden="true"></span><span>{esc(x)}</span></li>')
    return head(p) + f'<ul class="checklist">{"".join(li)}</ul>'


def quiz_item_from_props(p):
    opts = p.get("options") or []
    return {"id": p.get("quiz_item", "Qx"), "type": "mcq", "stem": p.get("q", ""), "explanation": p.get("why", ""),
            "options": [{"id": f"o{i}", "text": o, "correct": i == p.get("answer")} for i, o in enumerate(opts)]}


def quiz_item_html(item: dict, ctx: Ctx, scope: str) -> str:
    t = ctx.t
    qid = item["id"]
    typ = item.get("type", "mcq")
    stem = ctx.txt(item, "stem")
    scen = f'<p class="q-scen">{esc(item["scenario"])}</p>' if item.get("scenario") else ""
    opts = item.get("options") or []
    name = f"{scope}-{qid}"
    pts = int(item.get("points", 1))
    fb = {o["id"]: o.get("feedback", "") for o in opts}
    expl = esc(item.get("explanation", ""))
    if typ == "flashcard":
        return (f'<div class="flash" data-flash><button class="flash-card" aria-pressed="false" data-flip>'
                f'<span class="f-front"><small>{esc(t["front"])}</small>{esc(stem)}</span>'
                f'<span class="f-back"><small>{esc(t["back_side"])}</small>{esc(item.get("back", ""))}</span></button></div>')
    if not ctx.interactive:
        lis = "".join(f'<li class="{"ok" if o.get("correct") else ""}">{esc(ctx.txt(o, "text"))}</li>' for o in opts)
        return f'<div class="qstatic"><p class="q-stem">{esc(stem)}</p>{scen}<ol type="A">{lis}</ol></div>'
    if typ == "true_false" and not opts:
        opts = [{"id": "true", "text": t["true"]}, {"id": "false", "text": t["false"]}]
    if typ in ("ordering", "matching"):
        rows = []
        if typ == "ordering":
            n = len(opts)
            for o in opts:
                sel = "".join(f'<option value="{k}">{k}</option>' for k in range(1, n + 1))
                rows.append(f'<li><label><span>{esc(ctx.txt(o, "text"))}</span><select data-opt="{esc(o["id"])}" data-key="{o.get("order", 0)}">'
                            f'<option value="">{esc(t["position"])}</option>{sel}</select></label></li>')
            hint = t["order_hint"]
        else:
            matches = sorted({o.get("match", "") for o in opts})
            for o in opts:
                sel = "".join(f'<option value="{esc(m)}">{esc(m)}</option>' for m in matches)
                rows.append(f'<li><label><span>{esc(ctx.txt(o, "text"))}</span><select data-opt="{esc(o["id"])}" data-key="{esc(o.get("match", ""))}">'
                            f'<option value="">{esc(t["select"])}</option>{sel}</select></label></li>')
            hint = t["match_hint"]
        body = f'<p class="hint">{esc(hint)}</p><ol class="q-rows">{"".join(rows)}</ol>'
    else:
        kind = "checkbox" if typ == "multi" else "radio"
        lis = []
        for o in opts:
            oid = f"{name}-{o['id']}"
            lis.append(f'<li><input type="{kind}" name="{esc(name)}" id="{esc(oid)}" value="{esc(o["id"])}" data-correct="{1 if o.get("correct") else 0}">'
                       f'<label for="{esc(oid)}">{esc(ctx.txt(o, "text"))}</label></li>')
        body = f'<ul class="q-opts">{"".join(lis)}</ul>'
    return (f'<form class="qitem" data-q="{esc(qid)}" data-type="{esc(typ)}" data-points="{pts}" data-fb="{esc(json.dumps(fb, ensure_ascii=False))}" '
            f'data-expl="{expl}" novalidate><fieldset><legend class="q-stem">{esc(stem)}</legend>{scen}{body}</fieldset>'
            f'<div class="q-actions"><button type="submit" class="btn primary">{esc(t["check"])}</button></div>'
            f'<div class="q-fb" role="status" aria-live="polite"></div></form>')


def t_quiz(p, s, ctx):
    item = ctx.items.get(p.get("quiz_item")) or quiz_item_from_props(p)
    return f'<p class="kicker">{ico("help-circle", 18)} {esc(ctx.t["final_check"])}</p>' + quiz_item_html(item, ctx, s["id"])


def t_outro(p, s, ctx):
    tips = "".join(f'<li>{ico("check", 20)}<span>{esc(x)}</span></li>' for x in p.get("tips", []))
    tips = f'<ul class="tips">{tips}</ul>' if tips else ""
    ev = p.get("evidence_line") or ""
    ev = f'<p class="evidence">{esc(ev)}</p>' if ev else ""
    title = f'<h2 class="scene-title" tabindex="-1">{esc(p["title"])}</h2>' if p.get("title") else ""
    return f'<div class="hero outro">{title}<p class="big">{esc(p["line"])}</p>{tips}{ev}</div>'


def t_broll(p, s, ctx):
    return media_block(ctx, shot_id=p.get("shot"), scene=s, chips=p.get("chips"), cls="media full")


def t_broll_panel(p, s, ctx):
    side = "rev" if p.get("side") == "left" else ""
    return f'<div class="split {side}"><div>{head(p)}{items_list(p.get("items", []))}</div>{media_block(ctx, shot_id=p.get("shot"), scene=s)}</div>'


def t_image(p, s, ctx):
    cap = f'<p class="caption">{esc(p["caption"])}</p>' if p.get("caption") else ""
    return media_block(ctx, image_id=p.get("image"), scene=s, chips=p.get("chips"), cls="media full") + cap


def callout_list(callouts, ctx):
    if not callouts:
        return ""
    li = "".join(f'<li class="co tone-{TONE.get(c.get("tone"), "warn")}" data-co="{i}"><span class="pin">{i+1}</span>{esc(c["label"])}</li>'
                 for i, c in enumerate(sorted(callouts, key=lambda c: c.get("cue", 0))))
    btn = (f'<button class="btn ghost" data-reveal-co>{ico("flag", 18)} {esc(ctx.t["red_flags"])}</button>' if ctx.interactive else "")
    return f'<div class="callouts{" js-hide" if ctx.interactive else ""}">{btn}<ol>{li}</ol></div>'


def pin(callouts, target):
    srt = sorted(callouts or [], key=lambda c: c.get("cue", 0))
    return "".join(f'<span class="pin tone-{TONE.get(c.get("tone"), "warn")}" data-co="{i}" aria-hidden="true">{i+1}</span>'
                   for i, c in enumerate(srt) if c.get("target") == target)


def t_email_mock(p, s, ctx):
    e, co = p["email"], p.get("callouts", [])
    ext = f'<span class="badge warn">{ico("alert-triangle", 14)}</span>' if e.get("external") else ""
    addr = f'<span class="addr">&lt;{esc(e["from_addr"])}&gt;{pin(co, "addr")}</span>' if e.get("from_addr") else ""
    to = f'<div class="em-to">{ico("user", 16)} {esc(e["to"])}</div>' if e.get("to") else ""
    body = "".join(f'<p>{esc(b)}{pin(co, f"b{i}")}</p>' for i, b in enumerate(e.get("body", [])))
    att = f'<div class="em-att">{ico("paperclip", 18)} {esc(e["attachment"])}{pin(co, "attachment")}</div>' if e.get("attachment") else ""
    btn = f'<div><span class="em-btn">{esc(e["button"])}</span>{pin(co, "button")}</div>' if e.get("button") else ""
    sig = "".join(f"<span>{esc(x)}</span>" for x in e.get("signature", []))
    sig = f'<div class="em-sig">{sig}{pin(co, "signature")}</div>' if sig else ""
    return (f'<div class="mock email" role="group" aria-label="{esc(e["subject"])}"><div class="mock-bar"><i></i><i></i><i></i>{ico("mail", 18)}</div>'
            f'<div class="em-head"><h3 class="em-subj scene-title" tabindex="-1">{esc(e["subject"])}{pin(co, "subject")}</h3>'
            f'<div class="em-from">{ico("user", 18)}<strong>{esc(e["from"])}</strong>{pin(co, "from")} {addr} {ext}</div>{to}</div>'
            f'<div class="em-body">{body}{att}{btn}{sig}</div></div>') + callout_list(co, ctx)


def t_chat_mock(p, s, ctx):
    msgs = "".join(f'<li class="msg{" me" if m.get("me") else ""}{" warn" if m.get("warn") else ""}">{esc(m["text"])}</li>' for m in p.get("messages", []))
    title = f'<div class="chat-title">{ico("user", 18)}<strong>{esc(p["title"])}</strong></div>' if p.get("title") else ""
    dev = p.get("device", "phone")
    return f'<div class="mock chat {dev}">{title}<ul class="msgs">{msgs}</ul></div>' + callout_list(p.get("callouts", []), ctx)


def t_browser_mock(p, s, ctx):
    co = p.get("callouts", [])
    bad = p.get("bad")
    lock = ico("alert-triangle", 16) if bad else ico("lock", 16)
    page = p.get("page", "blank")
    inner = ""
    if p.get("brand"):
        inner += f'<div class="br-brand">{ico("globe", 22)} {esc(p["brand"])}</div>'
    if p.get("heading"):
        inner += f'<h3 class="br-h">{esc(p["heading"])}{pin(co, "heading")}</h3>'
    inner += "".join(f"<p>{esc(x)}</p>" for x in p.get("lines", []))
    if page == "login":
        inner += (f'<div class="br-form">{pin(co, "form")}<div class="fld">{ico("user", 18)}</div><div class="fld">{ico("key", 18)}</div>'
                  f'<div class="fld btnf">{ico("arrow-right", 18)}</div></div>')
    elif page == "checkout":
        inner += f'<div class="br-form">{pin(co, "form")}<div class="fld">{ico("credit-card", 18)}</div><div class="fld btnf">{ico("lock", 18)}</div></div>'
    elif page == "error":
        inner = f'<div class="br-err">{ico("alert-circle", 48)}</div>' + inner
    return (f'<div class="mock browser{" bad" if bad else ""}"><div class="br-bar"><i></i><i></i><i></i>'
            f'<div class="url" dir="ltr">{lock}<span>{esc(p["url"])}</span>{pin(co, "url")}</div></div>'
            f'<div class="br-page">{inner}{pin(co, "body")}</div></div>') + callout_list(co, ctx)


def t_mfa_prompt(p, s, ctx):
    n = int(p.get("count_to") or 1)
    stack = "".join(f'<div class="mfa-card" style="--i:{i}"><div class="mfa-app">{ico("shield", 18)} {esc(p.get("app", ""))}</div>'
                    f'<div class="mfa-place">{ico("globe", 16)} {esc(p.get("place", ""))}</div>'
                    f'<div class="mfa-btns"><span class="deny">{ico("x", 18)}</span><span class="ok">{ico("check", 18)}</span></div></div>'
                    for i in range(min(n, 4)))
    badge = f'<span class="mfa-count" aria-hidden="true">{n}</span>' if n > 1 else ""
    cap = f'<p class="caption">{esc(p["caption"])}</p>' if p.get("caption") else ""
    return f'<div class="mock phone mfa">{badge}<div class="mfa-stack">{stack}</div></div>{cap}'


def t_popup(p, s, ctx):
    tone = p.get("tone", "warn")
    cta = f'<span class="pop-cta">{esc(p["cta"])}</span>' if p.get("cta") else ""
    return (f'<div class="popup-bg"><div class="popup tone-{tone}" role="group" aria-label="{esc(p["title"])}">'
            f'<div class="pop-ico">{ico(p.get("icon") or ("alert-triangle" if tone != "info" else "info"), 34)}</div>'
            f'<h3 class="scene-title" tabindex="-1">{esc(p["title"])}</h3><p>{esc(p["body"])}</p>{cta}</div></div>')


def t_code_mock(p, s, ctx):
    hl = {h["line"]: h for h in p.get("highlight", [])}
    rows = []
    for i, ln in enumerate(p.get("lines", []), 1):
        h = hl.get(i)
        cls = f' class="hl tone-{TONE.get(h.get("tone"), "warn")}"' if h else ""
        lab = f'<span class="hl-l">{esc(h["label"])}</span>' if h and h.get("label") else ""
        rows.append(f'<li{cls}><code>{esc(ln) or " "}</code>{lab}</li>')
    fn = f'<span class="fn">{ico("file", 16)} {esc(p["filename"])}</span>' if p.get("filename") else ""
    title = head(p)
    return title + f'<div class="mock code" dir="ltr"><div class="mock-bar"><i></i><i></i><i></i>{fn}</div><ol class="code-lines">{"".join(rows)}</ol></div>'


SIM_MODES = ("guided", "practice", "assess")


def sim_id(s) -> str:
    sim = (s.get("props") or {}).get("sim") or {}
    return sim.get("quiz_item") or f"SIM_{s['id']}"


def t_sim(p, s, ctx):
    """Interactive screencast simulation (props.sim.mode guided|practice|assess): the learner operates real inputs;
    lesson.js validates them against sim.expect in order, gives hints, counts attempts, applies on_fail."""
    app, sim = p["app"], p["sim"]
    t = ctx.t
    vals = {}
    for e in sim.get("expect", []) + p.get("actions", []):
        if e.get("value") not in (None, "", "*"):
            vals.setdefault(e.get("target"), []).append(e["value"])
    flds = []
    for f in app.get("fields", []):
        k, fid, lab = f.get("kind", "text"), esc(f["id"]), esc(f["label"])
        iid = f'{s["id"]}-{f["id"]}'
        if k == "button":
            flds.append(f'<div class="sc-f" data-target="{fid}"><button type="button" class="sc-btn" data-sim-field="{fid}">{lab}</button></div>')
            continue
        if k == "checkbox":
            flds.append(f'<div class="sc-f" data-target="{fid}"><label><input type="checkbox" id="{iid}" data-sim-field="{fid}"> {lab}</label></div>')
            continue
        if k == "select":
            opts = "".join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in dict.fromkeys(vals.get(f["id"], [])))
            ctl = f'<select id="{iid}" data-sim-field="{fid}"><option value="">{esc(t["select"])}</option>{opts}</select>'
        elif k == "file":
            ctl = f'<button type="button" class="btn ghost" id="{iid}" data-sim-field="{fid}" data-file>{ico("paperclip", 16)} {lab}</button>'
        else:
            typ = "date" if k == "date" else "text"
            mode = ' inputmode="decimal"' if k == "amount" else ""
            ctl = f'<input type="{typ}" id="{iid}" data-sim-field="{fid}"{mode} autocomplete="off">'
        flds.append(f'<div class="sc-f" data-target="{fid}"><label class="sc-l" for="{iid}">{lab}</label>{ctl}</div>')
    cfg = {"mode": sim.get("mode"), "expect": sim.get("expect", []), "hints": sim.get("hints") or {},
           "max": int(sim.get("max_attempts") or 3), "on_fail": sim.get("on_fail", "show_hint"), "item": sim_id(s),
           "demo": [{"target": a.get("target"), "value": a.get("value"), "do": a["do"]} for a in p.get("actions", [])]}
    task = f'<p class="sim-task">{ico("target", 18)}<span>{esc(sim.get("task", ""))}</span></p>' if sim.get("task") else ""
    return (f'<div class="screencast sim" data-sim="{esc(json.dumps(cfg, ensure_ascii=False))}">'
            f'<div class="mock app"><div class="app-title">{ico("monitor", 18)} {esc(app.get("title", ""))}</div>'
            f'<div class="app-body"><div class="sc-fields">{"".join(flds)}</div><div class="toast" hidden></div></div></div>'
            f'<div class="sc-side"><p class="sim-mode">{esc(sim.get("mode", ""))}</p>{task}'
            f'<p class="sim-msg" role="status" aria-live="polite"></p>'
            f'<p><button class="btn ghost" data-sim-reset>{ico("refresh", 16)} {esc(t["restart"])}</button></p></div></div>')


def t_screencast(p, s, ctx):
    if ctx.interactive and (p.get("sim") or {}).get("mode") in SIM_MODES:
        return t_sim(p, s, ctx)
    app = p["app"]
    acts = sorted(p.get("actions", []), key=lambda a: a.get("cue", 0))
    title = f'<div class="app-title">{ico("monitor", 18)} {esc(app.get("title", ""))}</div>'
    if app.get("kind") == "screenshot" and app.get("screenshot"):
        url = ctx.media(app["screenshot"])
        body = f'<img src="{esc(url)}" alt="{esc(s.get("visual", ""))}">' if url else f'<div class="ph">{ico("monitor", 40)}</div>'
    else:
        flds = []
        for f in app.get("fields", []):
            k = f.get("kind", "text")
            fid = esc(f["id"])
            if k == "button":
                flds.append(f'<div class="sc-f" data-target="{fid}"><span class="sc-btn">{esc(f["label"])}</span></div>')
            elif k == "checkbox":
                flds.append(f'<div class="sc-f" data-target="{fid}"><span class="sc-cb" data-val></span><span>{esc(f["label"])}</span></div>')
            else:
                ic = {"date": "calendar", "amount": "wallet", "file": "paperclip", "select": "menu"}.get(k, "")
                flds.append(f'<div class="sc-f" data-target="{fid}"><span class="sc-l">{esc(f["label"])}</span>'
                            f'<span class="sc-in" data-val>{esc(f.get("value", ""))}{ico(ic, 16) if ic else ""}</span></div>')
        body = f'<div class="sc-fields kind-{esc(app.get("kind"))}">{"".join(flds)}</div>'
    steps = []
    for i, a in enumerate(acts):
        flabel = next((f["label"] for f in app.get("fields", []) if f["id"] == a.get("target")), "")
        label = a.get("label") or a.get("value") or flabel
        steps.append(f'<li data-act="{i}" data-do="{esc(a["do"])}" data-target="{esc(a.get("target", ""))}" data-value="{esc(a.get("value", ""))}">'
                     f'<span class="pin">{i+1}</span><span>{esc(label)}</span></li>')
    ctrl = ""
    if ctx.interactive:
        ctrl = (f'<div class="sc-ctrl"><button class="btn primary" data-sc-next>{ico("play", 16)} {esc(ctx.t["next_step"])}</button>'
                f'<button class="btn ghost" data-sc-reset>{ico("refresh", 16)} {esc(ctx.t["restart"])}</button>'
                f'<span class="sc-status" role="status" aria-live="polite"></span></div>')
    return (f'<div class="screencast" data-screencast><div class="mock app">{title}<div class="app-body">{body}'
            f'<button class="hotspot" hidden aria-label="{esc(ctx.t["next_step"])}"></button><div class="toast" hidden></div></div></div>'
            f'<div class="sc-side">{ctrl}<ol class="sc-steps">{"".join(steps)}</ol></div></div>')


def _xy(v, full):
    """Coordinates may be fractions (0-1), percents (1-100) or kit pixels (1920x1080)."""
    if v is None:
        return None
    v = float(v)
    if v <= 1:
        return v * 100
    if v <= 100:
        return v
    return v / full * 100


def people_html(people, ctx):
    out = []
    n = len(people)
    for i, pp in enumerate(people):
        x = _xy(pp.get("x"), 1920)
        x = (100 * (i + 1) / (n + 1)) if x is None else x
        flip = pp.get("flip", False)
        if ctx.rtl:  # mirror stage blocking for RTL
            x, flip = 100 - x, not flip
        sc = float(pp.get("s") or 1)
        out.append(f'<div class="ppl" style="--x:{x:.1f}%;--s:{sc}" data-cast="{esc(pp["cast"])}">'
                   f'{persona(pp["cast"], pp.get("pose", "idle"), pp.get("expr", "neutral"), flip, pp.get("lowerHidden", False), pp.get("holding"))}</div>')
    return "".join(out)


def t_cartoon(p, s, ctx):
    bubbles = sorted(p.get("bubbles", []), key=lambda b: b.get("cue", 0))
    bl = "".join(f'<li class="bub{" think" if b.get("think") else ""} tone-{esc(b.get("tone", "plain"))}" data-reveal="{b.get("cue", 0)}">'
                 f'<span class="who">{esc(display_name(b["who"], ctx.rtl))}</span>{esc(b["text"])}</li>' for b in bubbles)
    overlay = ""
    ov = p.get("overlay")
    if isinstance(ov, dict) and ov.get("template") in RENDER and ov.get("template") not in ("cartoon", "comic"):
        overlay = f'<div class="overlay">{RENDER[ov["template"]](ov.get("props", {}), s, ctx)}</div>'
    rev = reveal_ctrl(ctx) if bubbles else ""
    return (f'<div class="cartoon" data-reveal-scope><div class="panel">{set_svg(p.get("set", "plain"), p.get("night"), p.get("desk"))}'
            f'{people_html(p.get("people", []), ctx)}</div>{overlay}<ol class="bubbles">{bl}</ol>{rev}</div>')


def t_comic(p, s, ctx):
    panels = []
    for i, pn in enumerate(p.get("panels", [])):
        bl = "".join(f'<li class="bub{" think" if b.get("think") else ""}"><span class="who">{esc(display_name(b["who"], ctx.rtl))}</span>{esc(b["text"])}</li>' for b in pn.get("bubbles", []))
        sfx = f'<span class="sfx-word" aria-hidden="true">{esc(pn["sfx_word"])}</span>' if pn.get("sfx_word") else ""
        cap = f'<figcaption>{esc(pn["caption"])}</figcaption>' if pn.get("caption") else ""
        panels.append(f'<figure class="cpanel"><div class="panel">{set_svg(pn.get("set", "plain"))}{people_html(pn.get("people", []), ctx)}{sfx}</div>'
                      f'<ol class="bubbles">{bl}</ol>{cap}</figure>')
    layout = p.get("layout") or {1: "1", 2: "2", 3: "3", 4: "2x2"}.get(len(panels), "2x2")
    return f'<div class="comic l-{esc(layout).replace("+", "p")}">{"".join(panels)}</div>'


def reveal_ctrl(ctx):
    if not ctx.interactive:
        return ""
    return (f'<div class="reveal-ctrl"><button class="btn primary" data-reveal-next>{ico("eye", 16)} {esc(ctx.t["reveal"])}</button>'
            f'<button class="btn ghost" data-reveal-all>{esc(ctx.t["reveal_all"])}</button></div>')


def t_whiteboard(p, s, ctx):
    items = sorted(p.get("items", []), key=lambda it: it.get("cue", 0))
    svg_parts, html_parts = [], []
    col = {"ink": "var(--ink)", "attention": "var(--attention)", "safe": "var(--safe)"}
    H = 0.5625  # board viewBox is 100 x 56.25 (16:9); y percents are scaled by H
    for it in items:
        k = it["kind"]
        c = col.get(it.get("color", "ink"), "var(--ink)")
        x, y = _xy(it.get("x", 0.5), 1920), _xy(it.get("y", 0.5), 1080)
        if ctx.rtl:
            x = 100 - x
        w, h = _xy(it.get("w", 0.15), 1920), _xy(it.get("h", 0.12), 1080)
        rv = f'data-reveal="{it.get("cue", 0)}"'
        if k == "arrow":
            to = it.get("to") or {}
            tx, ty = _xy(to.get("x", 0.6), 1920), _xy(to.get("y", 0.5), 1080)
            if ctx.rtl:
                tx = 100 - tx
            svg_parts.append(f'<line {rv} x1="{x:.2f}" y1="{y*H:.2f}" x2="{tx:.2f}" y2="{ty*H:.2f}" style="stroke:{c};color:{c}" '
                             f'stroke-width=".5" marker-end="url(#ah-{s["id"]})" class="wb-stroke"/>')
        elif k == "circle":
            svg_parts.append(f'<ellipse {rv} cx="{x:.2f}" cy="{y*H:.2f}" rx="{w/2:.2f}" ry="{h*H/2:.2f}" fill="none" style="stroke:{c}" stroke-width=".5" class="wb-stroke"/>')
        elif k == "box":
            svg_parts.append(f'<rect {rv} x="{x-w/2:.2f}" y="{(y-h/2)*H:.2f}" width="{w:.2f}" height="{h*H:.2f}" rx="1" fill="none" style="stroke:{c}" stroke-width=".5" class="wb-stroke"/>')
        elif k == "underline":
            svg_parts.append(f'<path {rv} d="M{x-w/2:.2f} {y*H:.2f} q{w/4:.2f} 1 {w/2:.2f} 0 t{w/2:.2f} 0" fill="none" style="stroke:{c}" stroke-width=".6" class="wb-stroke"/>')
        else:
            if k == "person":
                inner = persona(it.get("cast", "host"), it.get("pose", "idle"), it.get("expr", "neutral"))
            elif k in ("icon", "cross", "check"):
                inner = ico({"cross": "x", "check": "check"}.get(k, it.get("icon")), 64, "ico wb-ico")
            else:
                inner = ""
            txt = f'<span class="wb-t">{esc(it["text"])}</span>' if it.get("text") else ""
            html_parts.append(f'<div class="wb-i k-{k}" {rv} style="--x:{x:.1f}%;--y:{y:.1f}%;color:{c}" data-tone="{it.get('color', 'ink')}">{inner}{txt}</div>')
    title = f'<h2 class="scene-title wb-title" tabindex="-1">{esc(p["title"])}</h2>' if p.get("title") else ""
    svg = (f'<svg class="wb-svg" viewBox="0 0 100 56.25" aria-hidden="true">'
           f'<defs><marker id="ah-{s["id"]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
           f'<path d="M0 0L10 5L0 10z" fill="context-stroke"/></marker></defs>{"".join(svg_parts)}</svg>')
    return f'<div class="wb" data-reveal-scope>{title}<div class="board">{svg}{"".join(html_parts)}</div>{reveal_ctrl(ctx)}</div>'


def mindmap_layout(root_label, nodes):
    kids = {}
    for n in nodes:
        kids.setdefault(n.get("parent") or "root", []).append(n)
    pos = {"root": (50.0, 50.0)}
    first = kids.get("root", [])
    # nodes whose parent equals the root label/id also attach to root
    first += [n for n in nodes if n.get("parent") not in pos and n.get("parent") not in {m["id"] for m in nodes} and n not in first]
    m = max(1, len(first))
    angle = {}
    for i, n in enumerate(first):
        a = -math.pi / 2 + 2 * math.pi * i / m
        angle[n["id"]] = (a, 2 * math.pi / m)
        pos[n["id"]] = (50 + 27 * math.cos(a), 50 + 30 * math.sin(a))

    def place(pid, depth):
        ch = kids.get(pid, [])
        if not ch:
            return
        a0, span = angle[pid]
        span = min(span * 0.8, math.pi / 2)
        for j, c in enumerate(ch):
            a = a0 + (j - (len(ch) - 1) / 2) * (span / max(1, len(ch)))
            angle[c["id"]] = (a, span / max(1, len(ch)))
            r = 26 + 16 * depth
            pos[c["id"]] = (max(7, min(93, 50 + r * 1.25 * math.cos(a))), max(6, min(94, 50 + (r + 4) * math.sin(a))))
            place(c["id"], depth + 1)
    for n in first:
        place(n["id"], 1)
    for n in nodes:
        pos.setdefault(n["id"], (50, 90))
    return pos


def t_mindmap(p, s, ctx):
    nodes = p.get("nodes", [])
    pos = mindmap_layout(p["root"], nodes)
    if ctx.rtl:  # mirror the map for RTL reading order
        pos = {k: (100 - x, y) for k, (x, y) in pos.items()}
    ids = {n["id"] for n in nodes}
    lines, labels = [], []
    for n in nodes:
        par = n.get("parent") if n.get("parent") in ids else "root"
        x1, y1 = pos[par]
        x2, y2 = pos[n["id"]]
        lines.append(f'<line data-reveal="{n["cue"]}" x1="{x1:.1f}" y1="{y1*0.6:.1f}" x2="{x2:.1f}" y2="{y2*0.6:.1f}" class="mm-l"/>')
        tone = TONE.get(n.get("tone"), "info")
        icon = ico(n["icon"], 18) if n.get("icon") else ""
        labels.append(f'<li class="mm-n tone-{tone}" data-reveal="{n["cue"]}" data-node="{esc(n["id"])}" style="--x:{x2:.1f}%;--y:{y2:.1f}%">{icon}<span>{esc(n["label"])}</span></li>')
    focus = esc(json.dumps(p.get("focus", [])))
    return (f'<div class="mindmap" data-reveal-scope data-focus="{focus}"><div class="mm-board">'
            f'<svg viewBox="0 0 100 60" preserveAspectRatio="none" aria-hidden="true">{"".join(lines)}</svg>'
            f'<h2 class="mm-root scene-title" tabindex="-1">{esc(p["root"])}</h2><ul class="mm-list">{"".join(labels)}</ul></div>{reveal_ctrl(ctx)}</div>')


def t_decision(p, s, ctx):
    ch = []
    for c in p.get("choices", []):
        if ctx.interactive:
            ch.append(f'<li><button class="choice" data-choice="{esc(c["id"])}" data-next="{esc(c["next"])}" data-correct="{1 if c.get("correct") else 0}">'
                      f'{ico("arrow-right", 18, "ico flip-rtl")}<span>{esc(c["label"])}</span></button></li>')
        else:
            ch.append(f'<li class="choice static{" ok" if c.get("correct") else ""}">{ico("arrow-right", 18, "ico flip-rtl")}<span>{esc(c["label"])}</span></li>')
    return (f'<div class="decision"><p class="kicker">{ico("help-circle", 18)} {esc(ctx.t["choose"])}</p>'
            f'<h2 class="scene-title" tabindex="-1">{esc(p["prompt"])}</h2><ul class="choices">{"".join(ch)}</ul>'
            f'<div class="dec-fb" role="status" aria-live="polite"></div></div>')


def t_flashcard(p, s, ctx):
    icon = ico(p["icon"], 36) if p.get("icon") else ""
    return (f'<div class="flash" data-flash><button class="flash-card" aria-pressed="false" data-flip>'
            f'<span class="f-front">{icon}<strong class="scene-title">{esc(p["front"])}</strong><small>{esc(ctx.t["flip"])}</small></span>'
            f'<span class="f-back">{esc(p["back"])}</span></button></div>')


RENDER = {
    "title": t_title, "section": t_section, "bullets": t_bullets, "icon_grid": t_icon_grid, "steps": t_steps,
    "process_flow": t_process_flow, "timeline": t_timeline, "do_dont": t_do_dont, "comparison": t_comparison,
    "stat": t_stat, "definition": t_definition, "statement": t_statement, "table": t_table, "checklist": t_checklist,
    "quiz": t_quiz, "outro": t_outro, "broll": t_broll, "broll_panel": t_broll_panel, "image": t_image,
    "email_mock": t_email_mock, "chat_mock": t_chat_mock, "browser_mock": t_browser_mock, "mfa_prompt": t_mfa_prompt,
    "popup": t_popup, "code_mock": t_code_mock, "screencast": t_screencast, "cartoon": t_cartoon,
    "whiteboard": t_whiteboard, "comic": t_comic, "mindmap": t_mindmap, "decision": t_decision, "flashcard": t_flashcard,
}


def scene_body(scene: dict, ctx: Ctx) -> str:
    fn = RENDER.get(scene["template"])
    if not fn:
        return f'<p>{esc(scene.get("visual", ""))}</p>'
    return fn(scene.get("props") or {}, scene, ctx)


def transcript_html(scene: dict, ctx: Ctx, open_=False) -> str:
    lines = scene.get("narration") or []
    if not lines:
        return ""
    li = "".join(f'<p><span class="who">{esc(display_name(l.get("who", ""), ctx.rtl))}</span> {esc(strip_cues(ctx.txt(l, "text")))}</p>' for l in lines)
    return (f'<details class="transcript"{" open" if open_ else ""}><summary>{icons.svg("file-text", 16)} {esc(ctx.t["transcript"])}</summary>'
            f'<div class="tx">{li}</div></details>')
