"""Check WCAG contrast of theme presets (and optional storyboard theme overrides).

Usage:
  .venv/bin/python assets/scripts/check_contrast.py                 # all presets in assets/theme_presets.yaml
  .venv/bin/python assets/scripts/check_contrast.py X.storyboard.json   # preset + theme.colors overrides of a storyboard
Exit code 1 if any text pair < 4.5:1 or large pair < 3:1.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PRESETS = ROOT / "assets" / "theme_presets.yaml"


def lum(hex_):
    h = hex_.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = out
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check(name, p, overrides=None):
    colors = {**p["colors"], **(overrides or {})}
    ok = True
    for pairs, need in ((p.get("text_pairs", []), 4.5), (p.get("large_pairs", []), 3.0)):
        for fg, bg in pairs:
            r = ratio(colors[fg], colors[bg])
            flag = "ok " if r >= need else "LOW"
            ok &= r >= need
            print(f"  {flag} {name:13} {fg:>14} on {bg:<8} {r:5.2f}:1 (need {need})")
    return ok


def main():
    data = yaml.safe_load(PRESETS.read_text())
    ok = True
    if len(sys.argv) > 1:
        sb = json.loads(Path(sys.argv[1]).read_text())
        theme = sb.get("theme", {})
        name = theme.get("preset", data["default"])
        ok = check(name, data["presets"][name], theme.get("colors"))
    else:
        for name, p in data["presets"].items():
            ok &= check(name, p)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
