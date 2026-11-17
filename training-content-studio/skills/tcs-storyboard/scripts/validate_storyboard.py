#!/usr/bin/env python3
"""Validate <lesson>.storyboard.json: JSON Schema + production lint.

Usage: validate_storyboard.py <lesson>.storyboard.json [--stage script|final] [--quiz <lesson>.quiz.json]
                              [--target-min 3] [--personas a,b] [--strict] [--json]
Errors: schema; duplicate scene ids; scene without claims; `^` cues fewer than props reference; >6 items on a board;
        generated image prompt without the no-text clause; unknown image/b-roll/quiz/branch refs; narration speaker
        without a voice; unknown persona ids; Arabic without rtl; script-stage placeholders at --stage final.
Warnings: fewer cues than revealed items; unused cues; scene 5–35 s; total vs target; long titles/bullets;
        on_screen_text out of date; lesson/course ids unsafe for Remotion composition ids.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sbtools as T  # noqa: E402

MAX_BOARD = 6


def lint(sb: dict, stage: str = "final", quiz: dict | None = None, target_min: float | None = None,
         extra_personas: list[str] | None = None) -> tuple[list[str], list[str], dict]:
    errs, warns = [], []
    v = Draft202012Validator(T.load_schema())
    for e in sorted(v.iter_errors(sb), key=lambda e: list(e.absolute_path)):
        path = "/".join(map(str, e.absolute_path)) or "<root>"
        errs.append(f"schema: {path}: {e.message[:180]}")
    if errs:
        return errs, warns, {}
    lang = sb["language"]
    if lang.startswith("ar") and sb.get("direction") != "rtl":
        errs.append("Arabic storyboard must set direction: rtl")
    if not lang.startswith("ar") and sb.get("direction") == "rtl":
        errs.append("direction rtl on a non-Arabic storyboard")
    fonts = sb.get("theme", {}).get("fonts")
    if lang.startswith("ar") and fonts and not fonts.get("arabic"):
        warns.append("theme.fonts has no arabic font (Cairo / IBM Plex Sans Arabic / Noto Kufi Arabic)")
    for k in ("course_id", "lesson_id"):
        if not re.match(r"^[A-Za-z0-9-]+$", sb[k]):
            warns.append(f"{k} {sb[k]!r} has chars outside [A-Za-z0-9-] (renderers sanitise composition ids)")
    if sb.get("theme", {}).get("logo"):
        warns.append("theme.logo is set — logo slot is optional and empty by default; confirm the user wants it")

    voices = set(sb["voices"].keys())
    personas = T.known_personas(extra_personas)
    for p in sb.get("cast", []):
        if p not in personas:
            errs.append(f"cast: unknown persona id {p!r} (known: base personas + assets/characters + domain packs)")
    images = {g["id"]: g for g in sb.get("generated_images", [])}
    shots = {b["id"] for b in sb.get("broll_shots", [])}
    for g in images.values():
        if not T.ends_with_no_text(g["prompt"]):
            errs.append(f"generated_images {g['id']}: prompt must end with '{T.NO_TEXT_CLAUSE}'")
        if re.search(r"\b(saying|that says|reads|caption|headline|label(?:ed|led)?|sign that|written|logo of)\b",
                     g["prompt"].split(T.NO_TEXT_CLAUSE)[0], re.I):
            warns.append(f"generated_images {g['id']}: prompt seems to ask for text — move text to template props")
        if g.get("character_ref") and g["character_ref"] not in personas:
            errs.append(f"generated_images {g['id']}: unknown character_ref {g['character_ref']}")
    for vk, vv in sb["voices"].items():
        if vv.get("lang") and vv["lang"][:2] != lang[:2]:
            warns.append(f"voices.{vk}.lang {vv['lang']} differs from storyboard language {lang}")
    ids = [s["id"] for s in sb["scenes"]]
    dup = {i for i in ids if ids.count(i) > 1}
    for d in dup:
        errs.append(f"duplicate scene id {d}")
    node_ids = {n["id"] for n in sb.get("branching", {}).get("nodes", [])}
    quiz_ids = {i["id"] for i in (quiz or {}).get("items", [])}
    wpm = T.default_wpm(sb)
    total, per_scene = 0.0, {}
    used_shots, used_images = set(), set()
    for sc in sb["scenes"]:
        sid, t, p = sc["id"], sc["template"], sc["props"]
        if "script-stage" in (sc.get("notes") or ""):
            (errs if stage == "final" else warns).append(f"{sid}: still a script-stage placeholder ({t})")
        if not sc["claims"]:
            errs.append(f"{sid}: no claims (every scene needs ≥1 claim; general_knowledge: true for intros)")
        if not sc["narration"] and t not in ("broll", "image"):
            warns.append(f"{sid}: no narration")
        for n in sc["narration"]:
            if n["who"] not in voices:
                errs.append(f"{sid}: narration speaker {n['who']!r} has no entry in voices")
            if lang.startswith("ar") and not re.search(r"[؀-ۿ]", n["text"]) and stage == "final":
                errs.append(f"{sid}: {lang} storyboard but narration line is not Arabic")
        for ref in T.persona_refs(sc):
            if ref not in personas:
                errs.append(f"{sid}: unknown persona id {ref!r}")
            elif ref not in sb.get("cast", []):
                warns.append(f"{sid}: persona {ref!r} not listed in storyboard cast")
        cues = T.count_cues(sc)
        refs = T.prop_cues(p) + [x["cue"] for x in sc.get("sfx", []) if isinstance(x.get("cue"), int)]
        need = max(refs) + 1 if refs else 0
        if cues < need:
            errs.append(f"{sid}: props reference cue {need - 1} but narration has only {cues} '^' marker(s)")
        items = T.revealed_items(t, p)
        if not refs and items and cues < items:
            warns.append(f"{sid}: {items} revealed items but {cues} '^' markers (items will share cues)")
        if cues > max(need, items) + 1:
            warns.append(f"{sid}: {cues} '^' markers but only {max(need, items)} used")
        # board size
        for key in ("items", "steps", "events", "dont", "do", "rows", "nodes", "tips"):
            lst = p.get(key)
            if t == "whiteboard" and key == "items" and isinstance(lst, list):
                lst = [i for i in lst if isinstance(i, dict) and i.get("text")]  # only text notes count
            lim = 7 if (t == "checklist" and key == "items") else (12 if t in ("mindmap", "process_flow") else MAX_BOARD)
            if isinstance(lst, list) and len(lst) > lim:
                errs.append(f"{sid}: {len(lst)} {key} on one board (max {lim}; split the scene)")
        if t == "do_dont" and len(p.get("dont", [])) + len(p.get("do", [])) > 8:
            warns.append(f"{sid}: do/don't board has > 8 lines in total")
        for side in ("left", "right"):
            if t == "comparison" and len(p.get(side, {}).get("items", [])) > MAX_BOARD:
                errs.append(f"{sid}: comparison {side} has > {MAX_BOARD} items")
        # refs
        for k in ("shot",):
            if p.get(k):
                used_shots.add(p[k])
                if p[k] not in shots:
                    errs.append(f"{sid}: b-roll shot {p[k]!r} not in broll_shots")
        if p.get("side_broll"):
            used_shots.add(p["side_broll"])
            if p["side_broll"] not in shots:
                errs.append(f"{sid}: side_broll {p['side_broll']!r} not in broll_shots")
        if t == "image":
            used_images.add(p["image"])
            if p["image"] not in images:
                errs.append(f"{sid}: image {p['image']!r} not in generated_images")
        if t == "quiz":
            if quiz is not None and p["quiz_item"] not in quiz_ids:
                errs.append(f"{sid}: quiz_item {p['quiz_item']} not in quiz.json")
            if p.get("options") and isinstance(p.get("answer"), int) and not 0 <= p["answer"] < len(p["options"]):
                errs.append(f"{sid}: quiz answer index out of range")
        if t == "decision":
            for ch in p["choices"]:
                if ch["next"] not in ids and ch["next"] not in node_ids:
                    errs.append(f"{sid}: choice {ch['id']} -> unknown scene/node {ch['next']}")
            if not any(c.get("correct") for c in p["choices"]):
                warns.append(f"{sid}: decision without a correct choice")
        # readability
        title = p.get("title") if isinstance(p.get("title"), str) else ""
        if len(title) > 60:
            warns.append(f"{sid}: title {len(title)} chars (> 60; text must stay ≥ 24 px at 1080p)")
        for it in p.get("items", []) if isinstance(p.get("items"), list) else []:
            txt = it if isinstance(it, str) else (it.get("text") or it.get("label") or "") if isinstance(it, dict) else ""
            if len(txt) > 70:
                warns.append(f"{sid}: item text > 70 chars: {txt[:40]}…")
        derived = T.derive_on_screen_text(sc)
        if sc.get("on_screen_text") is not None and sorted(sc["on_screen_text"]) != sorted(derived):
            warns.append(f"{sid}: on_screen_text differs from props (run derive_text.py)")
        secs = T.scene_seconds(sc, wpm)
        per_scene[sid] = secs
        total += secs
        if sc["narration"] and (secs < 5 or secs > 35):
            warns.append(f"{sid}: ~{secs}s (keep scenes 5–35 s)")
    for sh in shots - used_shots:
        warns.append(f"broll_shots {sh} unused")
    for im in set(images) - used_images:
        # images may also be used by renderers as backgrounds; only warn
        warns.append(f"generated_images {im} not used by an image scene")
    for node in sb.get("branching", {}).get("nodes", []):
        for s in node["scenes"]:
            if s not in ids:
                errs.append(f"branching node {node['id']}: unknown scene {s}")
    if sb.get("branching") and sb["branching"]["start"] not in node_ids:
        errs.append(f"branching.start {sb['branching']['start']} is not a node id")
    stats = {"scenes": len(sb["scenes"]), "est_seconds": round(total, 1), "wpm": wpm,
             "cues": sum(T.count_cues(s) for s in sb["scenes"]),
             "claims": sum(len(s["claims"]) for s in sb["scenes"]),
             "general_knowledge_claims": sum(1 for s in sb["scenes"] for c in s["claims"] if c.get("general_knowledge"))}
    if target_min:
        r = total / (target_min * 60)
        stats["vs_target"] = round(r, 2)
        if r < 0.85 or r > 1.15:
            warns.append(f"estimated {total:.0f}s vs target {target_min * 60:.0f}s ({r:.0%})")
    return errs, warns, stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard")
    ap.add_argument("--stage", choices=["script", "final"], default="final")
    ap.add_argument("--quiz")
    ap.add_argument("--target-min", type=float)
    ap.add_argument("--personas", default="")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    sb = json.loads(Path(a.storyboard).read_text(encoding="utf-8"))
    quiz = json.loads(Path(a.quiz).read_text(encoding="utf-8")) if a.quiz else None
    errs, warns, stats = lint(sb, a.stage, quiz, a.target_min, [p for p in a.personas.split(",") if p])
    if a.json:
        print(json.dumps({"errors": errs, "warnings": warns, "stats": stats}, ensure_ascii=False, indent=1))
    else:
        for e in errs:
            print("ERROR", e)
        for w in warns:
            print("WARN ", w)
        print(f"{'FAIL' if errs or (a.strict and warns) else 'OK'}: {stats}")
    return 1 if errs or (a.strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
