"""Shared helpers for tcs-storyboard scripts (import, not CLI)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "schemas" / "storyboard.schema.json"
ENUMS = json.loads((ROOT / "schemas" / "enums.json").read_text())
BASE_PERSONAS = {"host", "learner", "manager", "mentor", "customer", "rookie", "colleague", "exec", "support"}
NO_TEXT_CLAUSE = "no text, no letters, no numbers, no signage, no logos"
LEVEL_WPM = {"en": 140, "ar": 126}
LEAD, HOLD, PAUSE = 0.35, 0.75, 0.28

# keys whose string values are visible text
TEXT_KEYS = {"title", "kicker", "sub", "text", "label", "def", "term", "note", "caption", "line", "evidence_line", "q",
             "why", "prompt", "front", "back", "root", "heading", "brand", "url", "cta", "body", "subject", "from",
             "from_addr", "to", "attachment", "button", "signature", "lines", "chips", "tips", "items", "options",
             "columns", "rows", "dont", "do", "dont_head", "do_head", "head", "when", "place", "app", "filename",
             "value", "part", "n", "sfx_word", "events", "steps", "nodes", "messages", "bubbles", "panels", "left",
             "right", "fields", "actions", "callouts", "highlight", "choices", "email", "overlay", "props", "beats"}
NON_TEXT = {"icon", "shot", "image", "set", "cast", "pose", "expr", "tone", "id", "next", "parent", "target", "kind",
            "quiz_item", "cue", "out_cue", "x", "y", "s", "w", "h", "layout", "side", "device", "page", "color", "flip",
            "night", "desk", "holding", "focus", "move_to", "camera", "sfx", "answer", "correct", "bad", "me", "warn",
            "dim", "cols", "danger", "light", "dark", "external", "think", "lowerHidden", "video_choice", "count_to",
            "screenshot", "who", "template", "side_broll", "accent", "edges", "to_node"}


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def strip_cues(t: str) -> str:
    return re.sub(r"\s*\^\s*", " ", t).strip()


def count_cues(scene: dict) -> int:
    return sum(n.get("text", "").count("^") for n in scene.get("narration", []))


def prop_cues(obj) -> list[int]:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("cue", "out_cue") and isinstance(v, int):
                out.append(v)
            else:
                out += prop_cues(v)
    elif isinstance(obj, list):
        for v in obj:
            out += prop_cues(v)
    return out


def revealed_items(template: str, props: dict) -> int:
    """Items a list-style template reveals one per cue (if no explicit cues)."""
    if template in ("bullets", "icon_grid", "broll_panel", "checklist"):
        return len(props.get("items", []))
    if template == "steps":
        return len(props.get("steps", []))
    if template == "do_dont":
        return len(props.get("dont", [])) + len(props.get("do", []))
    if template == "timeline":
        return len(props.get("events", []))
    if template in ("process_flow", "mindmap"):
        return len(props.get("nodes", []))  # kit reveals nodes in order on cues
    if template == "comparison":
        return len(props.get("left", {}).get("items", [])) + len(props.get("right", {}).get("items", []))
    if template in ("quiz", "flashcard"):
        return 1
    if template == "definition":
        return 1 + (1 if props.get("note") else 0)
    return 0


def _walk_text(obj, template: str, key: str = "") -> list[str]:
    out: list[str] = []
    if isinstance(obj, str):
        if key in TEXT_KEYS or key == "":
            if obj.strip():
                out.append(obj.strip())
        return out
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if key in ("n",):
            out.append(str(obj))
        return out
    if isinstance(obj, list):
        for v in obj:
            out += _walk_text(v, template, key)
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in NON_TEXT:
                continue
            if template == "screencast" and k == "do":
                continue
            if k == "overlay" and isinstance(v, dict):
                out += _walk_text(v.get("props", {}), v.get("template", ""), "")
                continue
            if k not in TEXT_KEYS:
                continue
            out += _walk_text(v, template, k)
    return out


def derive_on_screen_text(scene: dict) -> list[str]:
    t, p = scene["template"], scene.get("props", {})
    texts: list[str] = []
    if t == "process_flow":
        texts = [x for x in [p.get("title", "")] + [n.get("label", "") for n in p.get("nodes", [])]
                 + [e.get("label", "") for e in p.get("edges", [])] if x]
    elif t == "stat":
        val = p.get("value")
        if val is not None:
            v = f"{val:,}" if isinstance(val, (int, float)) and abs(val) >= 1000 else (
                str(int(val)) if isinstance(val, float) and val.is_integer() else str(val))
            texts.append(f"{p.get('prefix', '')}{v}{p.get('suffix', '')}")
        rest = {k: v for k, v in p.items() if k not in ("value", "prefix", "suffix")}
        texts += _walk_text(rest, t)
    else:
        texts = _walk_text(p, t)
    seen, out = set(), []
    for s in texts:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _persona_ids_from(d) -> set[str]:
    ps = d.get("personas", {}) if isinstance(d, dict) else d
    if isinstance(ps, dict):
        return set(ps.keys())
    if isinstance(ps, list):
        return {x if isinstance(x, str) else x.get("id") for x in ps if isinstance(x, (str, dict))} - {None}
    return set()


def known_personas(extra: list[str] | None = None) -> set[str]:
    """Base personas + assets/characters (personas.yaml keys, sub-folders) + domains/*/personas.yaml + extra."""
    ids = set(BASE_PERSONAS)
    chars = ROOT / "assets" / "characters"
    if chars.exists():
        ids |= {f.name for f in chars.iterdir() if f.is_dir() and not f.name.startswith(("_", "."))}
        reg = chars / "personas.yaml"
        if reg.exists():
            ids |= _persona_ids_from(yaml.safe_load(reg.read_text(encoding="utf-8")))
    for f in sorted((ROOT / "domains").glob("*/personas.y*ml")) if (ROOT / "domains").exists() else []:
        if f.parent.name.startswith("_"):
            continue
        try:
            ids |= _persona_ids_from(yaml.safe_load(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return ids | set(extra or [])


def persona_refs(scene: dict) -> list[str]:
    refs = []

    def walk(o, k=""):
        if isinstance(o, dict):
            for kk, v in o.items():
                if kk == "cast" and isinstance(v, str):
                    refs.append(v)
                elif kk == "who" and isinstance(v, str) and k in ("bubbles",):
                    refs.append(v)
                else:
                    walk(v, kk)
        elif isinstance(o, list):
            for v in o:
                walk(v, k)
    walk(scene.get("props", {}))
    return refs


def default_wpm(sb: dict) -> int:
    return sb.get("wpm") or (LEVEL_WPM["ar"] if sb.get("language", "").startswith("ar") else LEVEL_WPM["en"])


def scene_seconds(scene: dict, wpm: int) -> float:
    words = sum(len([w for w in strip_cues(n["text"]).split() if re.search(r"\w", w)]) for n in scene.get("narration", []))
    pauses = sum(n.get("pause", PAUSE) + n.get("pre", 0) for n in scene.get("narration", []))
    est = scene.get("lead", LEAD) + words * 60 / wpm + pauses + scene.get("hold", HOLD)
    return round(max(est, scene.get("min_s", 0) or 0), 1)


def ends_with_no_text(prompt: str) -> bool:
    norm = re.sub(r"[\s.;]+$", "", prompt.strip().lower())
    norm = re.sub(r"\s+", " ", norm)
    return norm.endswith(NO_TEXT_CLAUSE)
