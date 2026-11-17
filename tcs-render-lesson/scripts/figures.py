"""Persona + set SVGs for cartoon/comic/whiteboard scenes.

Prefers real persona art from `assets/characters/<cast>/<pose>.svg` or `assets/characters/<cast>.svg`
(owned by the assets agent). Falls back to a neutral flat-vector placeholder figure (no text, no faces of
real people). Sets fall back to simple geometric backdrops.
"""
from __future__ import annotations

from pathlib import Path

from _common import ASSETS

# skin, hair, shirt — neutral, diverse; 'vex' is the only persona in the attention colour
PALETTE = {
    "host": ("#C68B59", "#2B1B12", "#006AB3"),
    "learner": ("#8D5524", "#1A1A1A", "#6FC7DA"),
    "manager": ("#F1C27D", "#5A3825", "#363E77"),
    "mentor": ("#E0AC69", "#9A9A9A", "#2E7D6B"),
    "customer": ("#FFDBAC", "#B5651D", "#7A5BA6"),
    "rookie": ("#D9A066", "#3B2A1A", "#4F8FD6"),
    "colleague": ("#A86B3C", "#111111", "#5B6385"),
    "exec": ("#EAC086", "#444444", "#1B2140"),
    "support": ("#7D4A2A", "#222222", "#1E9E6A"),
    "vex": ("#B98A64", "#111111", "#FF6700"),
}
EXPR_MOUTH = {
    "neutral": '<path d="M44 58h12" />', "happy": '<path d="M42 56q8 8 16 0" />',
    "worried": '<path d="M42 60q8-6 16 0" />', "shocked": '<ellipse cx="50" cy="59" rx="4" ry="5" fill="#2b1b12"/>',
    "sly": '<path d="M42 58q10 4 16-3" />', "angry": '<path d="M42 61q8-6 16 0" />',
    "sad": '<path d="M42 61q8-7 16 0" />', "think": '<path d="M45 59h9" />',
}
ARMS = {  # (left arm path, right arm path) in a 100x200 figure box; shoulder at (30,95)/(70,95)
    "idle": ("M30 95 L22 150", "M70 95 L78 150"),
    "wave": ("M30 95 L22 150", "M70 95 L92 60"),
    "point": ("M30 95 L22 150", "M70 95 L104 100"),
    "pointUp": ("M30 95 L22 150", "M70 95 L80 45"),
    "shrug": ("M30 95 L10 90 L4 76", "M70 95 L90 90 L96 76"),
    "phone": ("M30 95 L22 150", "M70 95 L74 120 L60 70"),
    "think": ("M30 95 L22 150", "M70 95 L72 125 L56 66"),
    "cheer": ("M30 95 L14 45", "M70 95 L86 45"),
    "facepalm": ("M30 95 L22 150", "M70 95 L70 125 L52 50"),
    "type": ("M30 95 L36 135 L56 130", "M70 95 L64 135 L44 130"),
    "present": ("M30 95 L22 150", "M70 95 L106 92"),
    "stop": ("M30 95 L22 150", "M70 95 L100 88 L100 70"),
    "hold": ("M30 95 L40 130 L60 128", "M70 95 L60 130"),
    "armsOut": ("M30 95 L0 104", "M70 95 L100 104"),
    "handsHips": ("M30 95 L14 120 L30 140", "M70 95 L86 120 L70 140"),
    "rub": ("M30 95 L44 128 L54 124", "M70 95 L56 128 L46 124"),
    "cross": ("M30 95 L62 118", "M70 95 L38 118"),
}


def palette(cast: str):
    """(skin, hair, shirt) from assets/characters/personas.yaml (+ domain packs), else built-in fallback."""
    from _common import personas
    pal = (personas().get(cast) or {}).get("palette") or {}
    base = PALETTE.get(cast, ("#C9A27E", "#333333", "#5B6385"))
    return (pal.get("skin", base[0]), pal.get("hair", base[1]),
            pal.get("jacket") or pal.get("top") or pal.get("outfit") or base[2])


def _asset(cast: str, pose: str) -> str | None:
    base = ASSETS / "characters"
    for p in (base / cast / f"{pose}.svg", base / cast / "idle.svg", base / cast / f"{cast}.svg", base / f"{cast}.svg"):
        if p.exists():
            return p.read_text(encoding="utf-8")
    return None


def persona(cast: str = "host", pose: str = "idle", expr: str = "neutral", flip: bool = False,
            lower_hidden: bool = False, holding: str | None = None) -> str:
    """Return a standalone <svg> (viewBox 0 0 110 200) for a persona."""
    real = _asset(cast or "host", pose or "idle")
    if real:
        return real if not flip else f'<g transform="scale(-1,1) translate(-110,0)">{real}</g>'
    skin, hair, shirt = palette(cast)
    la, ra = ARMS.get(pose or "idle", ARMS["idle"])
    mouth = EXPR_MOUTH.get(expr or "neutral", EXPR_MOUTH["neutral"])
    brows = '<path d="M38 38l8 3M62 38l-8 3" />' if expr == "angry" else (
        '<path d="M38 40l8-3M62 40l-8-3" />' if expr in ("worried", "sad") else "")
    legs = "" if lower_hidden else (
        '<path d="M40 160 L38 196" stroke="#1B2140" stroke-width="10" stroke-linecap="round"/>'
        '<path d="M60 160 L62 196" stroke="#1B2140" stroke-width="10" stroke-linecap="round"/>')
    held = ""
    if holding == "phone" or pose == "phone":
        held = '<rect x="54" y="60" width="9" height="16" rx="2" fill="#1B2140"/>'
    elif holding in ("paper", "card"):
        held = '<rect x="50" y="118" width="18" height="14" rx="2" fill="#fff" stroke="#5B6385"/>'
    elif holding == "cup":
        held = '<rect x="48" y="120" width="10" height="12" rx="2" fill="#fff" stroke="#5B6385"/>'
    elif holding == "laptop":
        held = '<rect x="32" y="122" width="36" height="20" rx="2" fill="#5B6385"/>'
    elif holding == "usb":
        held = '<rect x="54" y="122" width="6" height="12" rx="1" fill="#5B6385"/>'
    flipt = ' transform="scale(-1,1) translate(-110,0)"' if flip else ""
    eyes = '<circle cx="42" cy="46" r="2.6" fill="#1b1b1b"/><circle cx="58" cy="46" r="2.6" fill="#1b1b1b"/>'
    if expr == "sly":
        eyes = '<path d="M38 46h8M54 46h8" stroke="#1b1b1b" stroke-width="2.5"/>'
    return (
        f'<svg viewBox="-10 0 130 200" class="persona" role="img" aria-hidden="true" focusable="false">'
        f'<g{flipt}>'
        f'{legs}'
        f'<path d="M26 96 Q50 84 74 96 L72 164 L28 164 Z" fill="{shirt}"/>'
        f'<g fill="none" stroke="{shirt}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{la}"/><path d="{ra}"/></g>'
        f'<rect x="44" y="70" width="12" height="14" fill="{skin}"/>'
        f'<circle cx="50" cy="48" r="22" fill="{skin}"/>'
        f'<path d="M28 46 Q30 20 50 22 Q72 20 72 46 Q66 32 50 32 Q36 32 28 46z" fill="{hair}"/>'
        f'{eyes}<g fill="none" stroke="#2b1b12" stroke-width="2.5" stroke-linecap="round">{mouth}{brows}</g>'
        f'{held}</g></svg>')


SET_BG = {
    "office": ("#E8EEF7", "#C9D4E5"), "openOffice": ("#EAF1F8", "#C4D3E3"), "home": ("#F3EDE6", "#D9CBB8"),
    "server": ("#1F2547", "#151936"), "meeting": ("#E9EEF6", "#BFCBDD"), "boardroom": ("#E4E7F0", "#B4BCD0"),
    "reception": ("#EDF3F8", "#CBD8E4"), "airport": ("#E6F0F6", "#B9CEDD"), "cafe": ("#F1EBE4", "#D3C2AE"),
    "den": ("#2A2440", "#1B1730"), "street": ("#DCE8F2", "#9FB0C2"), "plain": ("#F4F7FB", "#DDE4EE"),
    "whiteboard": ("#FFFFFF", "#E6EAF0"),
}


def set_svg(name: str = "plain", night: bool = False, desk: bool = False) -> str:
    """Backdrop <svg> viewBox 0 0 1600 900, no text."""
    wall, floor = SET_BG.get(name, SET_BG["plain"])
    if night:
        wall, floor = "#232A4D", "#171C38"
    props = ""
    if name in ("office", "openOffice", "meeting", "boardroom", "reception", "home", "cafe"):
        props += '<rect x="1060" y="120" width="380" height="260" rx="8" fill="#BFE3EE" opacity=".8"/>' \
                 '<path d="M1250 120v260M1060 250h380" stroke="#fff" stroke-width="10"/>'
    if name in ("server",):
        for i in range(5):
            x = 120 + i * 290
            props += f'<rect x="{x}" y="140" width="200" height="520" rx="10" fill="#2E3566"/>'
            for j in range(8):
                props += f'<rect x="{x+20}" y="{170+j*60}" width="160" height="36" rx="4" fill="#3B4380"/>' \
                         f'<circle cx="{x+160}" cy="{188+j*60}" r="5" fill="#6FC7DA"/>'
    if name == "street":
        props += '<rect x="80" y="200" width="300" height="460" fill="#B8C6D6"/><rect x="1180" y="160" width="340" height="500" fill="#AEBDCF"/>'
    if name == "airport":
        props += '<rect x="0" y="140" width="1600" height="260" fill="#CFE6F2"/><path d="M200 300l200-40 40 10-120 40z" fill="#9FB4C8"/>'
    if name == "den":
        props += '<rect x="600" y="300" width="400" height="240" rx="10" fill="#3B3363"/><rect x="630" y="330" width="340" height="180" fill="#6FC7DA" opacity=".35"/>'
    if desk or name in ("office", "openOffice"):
        props += '<rect x="420" y="640" width="760" height="40" rx="6" fill="#8A9BB5"/><rect x="460" y="680" width="24" height="160" fill="#7A8AA3"/>' \
                 '<rect x="1116" y="680" width="24" height="160" fill="#7A8AA3"/>'
    return (f'<svg viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" class="setbg" aria-hidden="true" focusable="false">'
            f'<rect width="1600" height="900" fill="{wall}"/><rect y="680" width="1600" height="220" fill="{floor}"/>{props}</svg>')
