"""Build portable/attachments/ (knowledge files for a ChatGPT custom GPT / Gemini Gem) and run consistency checks.

Usage:
  .venv/bin/python portable/build_portable.py           # check, then (re)build attachments
  .venv/bin/python portable/build_portable.py --check   # checks only (format examples, packs, personas, contrast)

Attachments are generated from the repo (schemas, format skills, domain packs, assets, QUALITY.md) so the portable
version never drifts from the plugin. Do not edit portable/attachments/ by hand.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "portable" / "attachments"
NO_TEXT = "no text, no letters, no numbers, no signage, no logos"
FORMATS = ["explainer", "doodle", "cartoon", "comic", "narrated-deck", "mindmap", "branching", "screencast-sim",
           "job-aid", "series"]
PIPELINE = ["tcs-orchestrator", "tcs-autopilot", "tcs-curriculum", "tcs-source-ingest", "tcs-scriptwriter",
            "tcs-storyboard", "tcs-assessment", "tcs-grounding-check", "tcs-localize"]


def load_schema(name):
    return json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text())


def lint_storyboard(d, validator):
    """Schema errors + semantic checks shared by examples and mock-up presets."""
    probs = [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:140]}" for e in validator.iter_errors(d)]
    for s in d.get("scenes", []):
        carets = sum(l.get("text", "").count("^") for l in s.get("narration", []))
        cues = [int(x) for x in re.findall(r'"(?:cue|out_cue)": (\d+)', json.dumps(s.get("props", {})))]
        if cues and max(cues) + 1 > carets and s.get("narration"):
            probs.append(f"{s['id']}: props use cue {max(cues)} but only {carets} '^' markers")
    if "branching" in d:
        nodes = {n["id"] for n in d["branching"]["nodes"]}
        sids = {s["id"] for s in d["scenes"]}
        if d["branching"]["start"] not in nodes:
            probs.append("branching.start is not a node")
        for n in d["branching"]["nodes"]:
            probs += [f"node {n['id']}: unknown scene {x}" for x in n["scenes"] if x not in sids]
        for s in d["scenes"]:
            if s["template"] == "decision":
                probs += [f"{s['id']}: choice -> unknown node {c['next']}" for c in s["props"]["choices"] if c["next"] not in nodes]
    for g in d.get("generated_images", []):
        if not g["prompt"].rstrip(" .").endswith(NO_TEXT):
            probs.append(f"generated_images {g['id']}: prompt must end with '{NO_TEXT}'")
    shots = {b["id"] for b in d.get("broll_shots", [])}
    for s in d.get("scenes", []):
        sh = s.get("props", {}).get("shot")
        if sh and sh not in shots:
            probs.append(f"{s['id']}: shot '{sh}' not in broll_shots")
    return probs


def check():
    ok = True
    sb_schema = load_schema("storyboard")
    V = jsonschema.Draft202012Validator(sb_schema)

    def report(label, probs):
        nonlocal ok
        ok &= not probs
        print(f"{'OK  ' if not probs else 'FAIL'} {label}")
        for p in probs:
            print(f"       - {p}")

    # 1. format example fragments
    for fmt in FORMATS:
        for p in sorted((ROOT / "skills" / f"tcs-format-{fmt}" / "templates").glob("*.storyboard.json")):
            report(str(p.relative_to(ROOT)), lint_storyboard(json.loads(p.read_text()), V))
    # 2. series plan + calendar
    sp = ROOT / "skills/tcs-format-series/templates"
    if (sp / "series_plan.schema.json").exists():
        S = jsonschema.Draft202012Validator(json.loads((sp / "series_plan.schema.json").read_text()))
        for f in ("series_plan.yaml", "nudge_calendar.yaml"):
            report(f"series {f}", [e.message[:140] for e in S.iter_errors(yaml.safe_load((sp / f).read_text()))])
    # 3. domain packs: YAML parses; mock-up presets validate as scenes
    for pack in sorted((ROOT / "domains").iterdir()):
        if not pack.is_dir():
            continue
        probs = []
        for y in sorted(pack.glob("*.yaml")):
            try:
                yaml.safe_load(y.read_text())
            except yaml.YAMLError as e:
                probs.append(f"{y.name}: {e}")
        mk = pack / "mockups.yaml"
        if mk.exists() and not probs:
            presets = (yaml.safe_load(mk.read_text()) or {}).get("presets") or {}
            for pid, pr in presets.items():
                n = max([int(x) for x in re.findall(r"'cue': (\d+)", str(pr["props"]))] or [-1]) + 1
                doc = {"schema_version": "1.0", "course_id": "check", "lesson_id": "X", "title": "x", "language": "en-US",
                       "aspect": "16:9", "formats": ["explainer"], "voices": {"narrator": {"provider": "placeholder", "voice": "x"}},
                       "scenes": [{"id": "s1", "template": pr["template"], "props": pr["props"],
                                   "narration": [{"who": "narrator", "text": "^ " * n + "x"}], "claims": [{"text": "x", "general_knowledge": True}]}]}
                probs += [f"mockup {pid}: {p}" for p in lint_storyboard(doc, V)]
        per = pack / "personas.yaml"
        if per.exists() and not probs:
            for pid, p in ((yaml.safe_load(per.read_text()) or {}).get("personas") or {}).items():
                if "prompt" in p and not p["prompt"].rstrip(" .").endswith(NO_TEXT):
                    probs.append(f"persona {pid}: prompt missing no-text suffix")
        report(f"domain pack {pack.name}", probs)
    # 4. core personas
    enums = json.loads((ROOT / "schemas/enums.json").read_text())
    probs = []
    reg = yaml.safe_load((ROOT / "assets/characters/personas.yaml").read_text())["personas"]
    for pid, p in reg.items():
        for x in p.get("poses", []):
            if x not in enums["poses"]:
                probs.append(f"{pid}: pose {x} not in enums")
        for x in p.get("expressions", []):
            if x not in enums["expressions"]:
                probs.append(f"{pid}: expression {x} not in enums")
        pr = ROOT / p.get("prompt", "-")
        if p.get("prompt") and not pr.read_text().rstrip(" .\n").endswith(NO_TEXT):
            probs.append(f"{pid}: prompt.txt missing no-text suffix")
    report("assets/characters personas", probs)
    # 5. theme contrast
    r = subprocess.run([sys.executable, str(ROOT / "assets/scripts/check_contrast.py")], capture_output=True, text=True)
    report("assets/theme_presets contrast", [] if r.returncode == 0 else [l for l in r.stdout.splitlines() if "LOW" in l])
    return ok


def fence(lang, text):
    return f"```{lang}\n{text.rstrip()}\n```\n"


def strip_frontmatter(md):
    return re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "schemas").mkdir(parents=True)
    # raw schemas (for code-execution validation)
    for p in sorted((ROOT / "schemas").glob("*.json")):
        shutil.copy2(p, OUT / "schemas" / p.name)
    # SCHEMAS.md
    parts = ["# SCHEMAS — contract for every file (JSON Schema Draft 2020-12). YAML files validate after parsing.\n"]
    for p in sorted((ROOT / "schemas").glob("*.json")):
        parts += [f"\n## {p.name}\n", fence("json", json.dumps(json.loads(p.read_text()), ensure_ascii=False, separators=(",", ":")))]
    (OUT / "SCHEMAS.md").write_text("".join(parts))
    # FORMATS.md + EXAMPLES.md
    fp, ex = ["# FORMATS — the 10 format skills (SKILL + playbook + templates)\n"], ["# EXAMPLES — valid storyboard fragments per format\n"]
    for fmt in FORMATS:
        d = ROOT / "skills" / f"tcs-format-{fmt}"
        if not d.exists():
            continue
        fp.append(f"\n\n# FORMAT: {fmt}\n\n" + strip_frontmatter((d / "SKILL.md").read_text()))
        pb = d / "references" / "playbook.md"
        if pb.exists():
            fp.append("\n" + pb.read_text())
        for t in sorted((d / "templates").iterdir()):
            if t.name.endswith(".storyboard.json"):
                ex += [f"\n## {fmt} — {t.name}\n", fence("json", json.dumps(json.loads(t.read_text()), ensure_ascii=False, indent=1))]
            elif t.suffix in (".md", ".yaml", ".json"):
                fp += [f"\n### template: {t.name}\n", fence({".md": "markdown", ".yaml": "yaml", ".json": "json"}[t.suffix], t.read_text())]
    (OUT / "FORMATS.md").write_text("".join(fp))
    (OUT / "EXAMPLES.md").write_text("".join(ex))
    # DOMAIN_<pack>.md
    for pack in sorted((ROOT / "domains").iterdir()):
        if not pack.is_dir():
            continue
        name = "TEMPLATE" if pack.name == "_template" else pack.name
        parts = [f"# DOMAIN PACK: {pack.name}\n"]
        for f in sorted(pack.iterdir()):
            if f.suffix in (".yaml", ".md"):
                parts += [f"\n## {f.name}\n", fence("yaml", f.read_text()) if f.suffix == ".yaml" else f.read_text() + "\n"]
        (OUT / f"DOMAIN_{name}.md").write_text("".join(parts))
    # ASSETS.md
    parts = ["# ASSETS — themes, layouts, captions, voices, audio, brand, personas\n"]
    for rel in ["assets/MANIFEST.md", "assets/theme_presets.yaml", "assets/layout_presets.yaml", "assets/caption_styles.yaml",
                "assets/voices.yaml", "assets/audio.yaml", "assets/brand.yaml", "assets/characters/personas.yaml"]:
        p = ROOT / rel
        if p.exists():
            parts += [f"\n## {rel}\n", fence("yaml", p.read_text()) if p.suffix == ".yaml" else p.read_text() + "\n"]
    for sheet in sorted((ROOT / "assets/characters").glob("*/character_sheet.md")):
        parts += [f"\n## {sheet.relative_to(ROOT)}\n", sheet.read_text(), "\nLocked prompt:\n",
                  fence("text", (sheet.parent / "prompt.txt").read_text())]
    (OUT / "ASSETS.md").write_text("".join(parts))
    shutil.copy2(ROOT / "QUALITY.md", OUT / "QUALITY.md")
    # PIPELINE_SKILLS.md (other stages, if present)
    parts = ["# PIPELINE SKILLS — stage instructions (curriculum, ingest, script, storyboard, assessment, grounding, localize)\n"]
    found = 0
    for sk in PIPELINE:
        p = ROOT / "skills" / sk / "SKILL.md"
        if p.exists():
            found += 1
            parts.append(f"\n\n# SKILL: {sk}\n\n" + strip_frontmatter(p.read_text()))
    if found:
        (OUT / "PIPELINE_SKILLS.md").write_text("".join(parts))
    files = sorted(p.relative_to(OUT) for p in OUT.rglob("*") if p.is_file())
    (OUT / "INDEX.txt").write_text("Generated by portable/build_portable.py — do not edit.\n" + "\n".join(map(str, files)) + "\n")
    for f in files:
        print(f"  {str(f):40} {(OUT / f).stat().st_size:>8} bytes")
    print(f"pipeline skills bundled: {found}/{len(PIPELINE)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="run checks only")
    a = ap.parse_args()
    ok = check()
    if not a.check:
        build()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
