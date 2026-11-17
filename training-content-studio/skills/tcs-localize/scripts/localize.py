#!/usr/bin/env python3
"""Localization skeleton + worklist for a storyboard (EN→AR or AR→EN).

  localize.py skeleton <L>.storyboard.json --lang ar-EG [--glossary templates/glossary.yaml] [--numerals western|eastern]
      → <L>.ar-EG.storyboard.json  (language/direction/fonts/voices switched; every translatable string = "«TR» <source>")
      → <L>.ar-EG.translate.yaml   (worklist: path, src, tr: "", cues, glossary hints)
  localize.py apply <L>.ar-EG.storyboard.json <L>.ar-EG.translate.yaml
      → writes translations into the skeleton, checks `^` counts per string, re-derives on_screen_text.
Claims stay in the source language (grounding matches cited facts); URLs, e-mail addresses, file names and code are not
translated. Adaptation (not literal translation) rules: references/*.md.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "tcs-storyboard" / "scripts"))
import sbtools as T  # noqa: E402

MARK = "«TR» "
LANGS = ["en-US", "en-GB", "ar-EG", "ar-MSA"]
NO_TRANSLATE_KEYS = {"url", "from_addr", "filename"}
LANG_LINE = {"en-US": "Speak American English.", "en-GB": "Speak British English.",
             "ar-EG": "Speak natural Egyptian Arabic (Cairene colloquial).", "ar-MSA": "Speak clear Modern Standard Arabic."}
FALLBACK_NARR = {
    "ar-EG": "Speak natural Egyptian Arabic (Cairene colloquial), warm and friendly like a respected colleague explaining to the team. Clear, relaxed pace; pronounce English technical terms the way Egyptian professionals say them.",
    "ar-MSA": "Speak clear Modern Standard Arabic in a calm, professional training tone. Moderate pace, precise pronunciation.",
    "en-US": "Warm, confident corporate trainer speaking American English to colleagues. Clear, friendly, natural pace. Never robotic.",
    "en-GB": "Warm, confident trainer speaking British English. Clear, friendly, measured pace.",
}
LITERAL = re.compile(r"^(https?://\S+|[\w.+-]+@[\w-]+\.[\w.]+|[\w./-]+\.\w{2,4}|[\d\s.,:%$€£+-]+)$")


def translatable(sb: dict):
    """Yield (path list, string) for every translatable string."""
    yield ["title"], sb["title"]
    for i, sc in enumerate(sb["scenes"]):
        for j, n in enumerate(sc["narration"]):
            yield ["scenes", i, "narration", j, "text"], n["text"]
        t = sc["template"]

        def walk(o, path, key=""):
            if isinstance(o, str):
                if key in T.TEXT_KEYS and key not in NO_TRANSLATE_KEYS and not LITERAL.match(o.strip()):
                    yield path, o
            elif isinstance(o, list):
                if t == "code_mock" and key == "lines":
                    return
                for k, v in enumerate(o):
                    yield from walk(v, path + [k], key)
            elif isinstance(o, dict):
                for k, v in o.items():
                    if k in T.NON_TEXT or (t == "screencast" and k == "do"):
                        continue
                    if k == "overlay" and isinstance(v, dict):
                        yield from walk(v.get("props", {}), path + [k, "props"], "props")
                        continue
                    if k in T.TEXT_KEYS:
                        yield from walk(v, path + [k], k)
        yield from walk(sc["props"], ["scenes", i, "props"], "props")
        if sc.get("visual"):
            yield ["scenes", i, "visual"], sc["visual"]


def get_set(obj, path, value=None):
    for k in path[:-1]:
        obj = obj[k]
    if value is None:
        return obj[path[-1]]
    obj[path[-1]] = value


def load_glossary(p: Path | None) -> list[dict]:
    p = p or Path(__file__).resolve().parents[1] / "templates" / "glossary.yaml"
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return [t for grp in d.get("groups", {}).values() for t in grp]


def hints(text: str, glossary: list[dict], lang: str) -> list[str]:
    out, low = [], text.lower()
    for g in glossary:
        src = g.get("en", "")
        hit = re.search(rf"\b{re.escape(src)}\b", text) if src[:1].isupper() else \
            re.search(rf"\b{re.escape(src.lower())}\b", low)
        if src and hit:
            tgt = g.get("ar_eg" if lang == "ar-EG" else "ar_msa") or g.get("ar_msa") or g.get("ar_eg")
            out.append(f"{src} → {tgt}" + (f" (keep: {g['keep']})" if g.get("keep") else ""))
        for k in ("ar_eg", "ar_msa"):
            if g.get(k) and g[k] in text and lang.startswith("en"):
                out.append(f"{g[k]} → {src}")
    return sorted(set(out))


def voices_for(sb: dict, lang: str) -> dict:
    narr = {}
    vf = ROOT / "assets" / "voices.yaml"
    if vf.exists():
        slots = (yaml.safe_load(vf.read_text(encoding="utf-8")) or {}).get("slots", {})
        narr = ((slots.get("narrator") or {}).get(lang) or {}).get("openai") or {}
    out = {}
    for k, v in sb["voices"].items():
        nv = dict(v, lang=lang)
        if k == "narrator":
            nv["instructions"] = narr.get("instructions", FALLBACK_NARR[lang])
            nv["voice"] = v.get("voice") or narr.get("voice", "marin")
        else:
            acting = re.sub(r"^(Speak [^.]*\.\s*)", "", v.get("instructions", ""))
            nv["instructions"] = f"{LANG_LINE[lang]} {acting}".strip()
        out[k] = nv
    return out


def skeleton(sb: dict, lang: str, glossary: list[dict], numerals: str = "western") -> tuple[dict, list[dict]]:
    loc = copy.deepcopy(sb)
    src_lang = sb["language"]
    loc["language"] = lang
    loc["direction"] = "rtl" if lang.startswith("ar") else "ltr"
    subs = [x for x in sb.get("subtitle_languages", []) if x != lang]
    if src_lang not in subs:
        subs.append(src_lang)
    loc["subtitle_languages"] = subs
    loc["voices"] = voices_for(sb, lang)
    theme = loc.setdefault("theme", {"preset": "neutral", "logo": None})
    fonts = theme.setdefault("fonts", {})
    if lang.startswith("ar"):
        fonts.setdefault("arabic", "Cairo")
    fonts.setdefault("latin", "Poppins")
    if sb.get("wpm"):
        loc["wpm"] = round(sb["wpm"] * (0.9 if lang.startswith("ar") and not src_lang.startswith("ar") else
                                        (1 / 0.9 if src_lang.startswith("ar") and not lang.startswith("ar") else 1)))
    work = []
    for path, text in translatable(sb):
        get_set(loc, path, MARK + text)
        work.append({"path": "/".join(map(str, path)), "src": text, "tr": "", "cues": text.count("^"),
                     **({"hints": h} if (h := hints(text, glossary, lang)) else {}),
                     **({"numerals": "eastern ٠-٩ on screen"} if numerals == "eastern" and re.search(r"\d", text)
                        and path[-1] != "text" else {})})
    for sc in loc["scenes"]:
        sc.pop("on_screen_text", None)
        for n in sc["narration"]:
            n.pop("text_ar", None)
        sc["notes"] = (sc.get("notes", "") + f" · localized from {src_lang}").strip(" ·")
    return loc, work


def apply(loc: dict, work: list[dict]) -> tuple[dict, list[str]]:
    errs = []
    for w in work:
        path = [int(p) if p.isdigit() else p for p in w["path"].split("/")]
        tr = (w.get("tr") or "").strip()
        if not tr:
            errs.append(f"{w['path']}: no translation")
            continue
        if tr.count("^") != w.get("cues", 0):
            errs.append(f"{w['path']}: {tr.count('^')} '^' markers, source has {w.get('cues', 0)}")
        get_set(loc, path, tr)
    for sc in loc["scenes"]:
        sc["on_screen_text"] = T.derive_on_screen_text(sc)
    return loc, errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("skeleton")
    s.add_argument("storyboard")
    s.add_argument("--lang", required=True, choices=LANGS)
    s.add_argument("--glossary")
    s.add_argument("--numerals", choices=["western", "eastern"], default="western")
    s.add_argument("--out-dir")
    a2 = sub.add_parser("apply")
    a2.add_argument("skeleton")
    a2.add_argument("worklist")
    a = ap.parse_args(argv)
    if a.cmd == "skeleton":
        src = Path(a.storyboard)
        sb = json.loads(src.read_text(encoding="utf-8"))
        loc, work = skeleton(sb, a.lang, load_glossary(Path(a.glossary) if a.glossary else None), a.numerals)
        out_dir = Path(a.out_dir) if a.out_dir else src.parent
        stem = sb["lesson_id"]
        sp, wp = out_dir / f"{stem}.{a.lang}.storyboard.json", out_dir / f"{stem}.{a.lang}.translate.yaml"
        sp.write_text(json.dumps(loc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        wp.write_text(yaml.safe_dump(work, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
        print(f"wrote {sp} ({len(work)} strings marked {MARK.strip()}) and {wp}")
        return 0
    sp = Path(a.skeleton)
    loc, errs = apply(json.loads(sp.read_text(encoding="utf-8")),
                      yaml.safe_load(Path(a.worklist).read_text(encoding="utf-8")))
    for e in errs:
        print("ERROR", e)
    sp.write_text(json.dumps(loc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{'FAIL' if errs else 'OK'}: applied to {sp}; next: rtl_lint.py {sp} --source <source storyboard>")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
