#!/usr/bin/env python3
"""Publish a skill folder to github.com/TamerElsherif/tamer-skills.

Usage:
  publish.py --skill-dir <dir> --check                 # validate only
  publish.py --skill-dir <dir> [--message MSG] [--dry-run] [--no-push]
  publish.py --skill-dir <dir> --bundle <out-dir>      # offline: zip + commands, no git

Env: TAMER_SKILLS_REPO (default https://github.com/TamerElsherif/tamer-skills.git)
     TAMER_SKILLS_CLONE (default ~/.cache/tamer-skills)
"""
import argparse, os, re, shutil, subprocess, sys, zipfile, datetime, pathlib

REPO = os.environ.get("TAMER_SKILLS_REPO", "https://github.com/TamerElsherif/tamer-skills.git")
CLONE = pathlib.Path(os.environ.get("TAMER_SKILLS_CLONE", "~/.cache/tamer-skills")).expanduser()
EXCLUDE = {"evals", "__pycache__", ".DS_Store", ".git"}
CATALOG_HEADER = "| Skill | What it does | When to use | Install |"
CATALOG_SEP = "|---|---|---|---|"
SECRET_RX = re.compile(r"(ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)")

def die(msg): print(f"ERROR: {msg}"); sys.exit(1)
def run(cmd, cwd=None, check=True):
    print("  $", " ".join(cmd)); r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and r.returncode: print(r.stdout, r.stderr); die(f"command failed: {' '.join(cmd)}")
    return r

def frontmatter(skill_md: pathlib.Path):
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m: die("SKILL.md has no YAML frontmatter")
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1); fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text

def check(skill_dir: pathlib.Path):
    if not (skill_dir / "SKILL.md").exists(): die("SKILL.md missing")
    fm, _ = frontmatter(skill_dir / "SKILL.md")
    name = fm.get("name", ""); desc = fm.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name): die(f"name '{name}' is not kebab-case")
    if name != skill_dir.name: die(f"folder '{skill_dir.name}' != name '{name}' — rename the folder")
    if len(desc) < 60: die("description too short — say what it does AND when to trigger")
    problems = []
    for p in skill_dir.rglob("*"):
        if p.is_file() and not any(x in p.parts for x in EXCLUDE) and p.resolve() != pathlib.Path(__file__).resolve():
            try: t = p.read_text(encoding="utf-8", errors="ignore")
            except Exception: continue
            if SECRET_RX.search(t): problems.append(f"possible secret in {p}")
            if re.search(r"(/Users/|/home/[a-z]+/|C:\\\\Users)", t) and p.suffix in {".md", ".sh", ".py", ".json"}:
                problems.append(f"absolute local path in {p}")
    if problems: die("\n  ".join(["pre-publish check failed:"] + problems))
    if not (skill_dir / "README.md").exists(): print("WARN: README.md missing — write it from assets/README.template.md before publishing")
    print(f"OK: {name} — {desc[:80]}…"); return name, desc

def one_liner(desc: str) -> str:
    s = re.split(r"(?<=[.!?])\s|\s+—\s+|\.\s", desc)[0].strip().rstrip(".")
    return (s[:110] + "…") if len(s) > 110 else s

def when_to_use(desc: str) -> str:
    m = re.search(r"[Uu]se (?:this|it|when|whenever)([^.]*)\.", desc)
    s = ("Use" + m.group(1)).strip() if m else "See README"
    return (s[:110] + "…") if len(s) > 110 else s

def package(skill_dir: pathlib.Path, out: pathlib.Path) -> pathlib.Path:
    dst = out / f"{skill_dir.name}.skill"
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(skill_dir.rglob("*")):
            if p.is_file() and not any(x in p.parts for x in EXCLUDE) and p.suffix != ".skill":
                z.write(p, p.relative_to(skill_dir.parent))
    print(f"  packaged {dst}"); return dst

def existing_skills(root: pathlib.Path):
    return sorted(d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "SKILL.md").exists())

def copy_skill(skill_dir: pathlib.Path, dest_root: pathlib.Path, update: bool = False) -> pathlib.Path:
    dest = dest_root / skill_dir.name
    if dest.exists():
        if not update:
            die(f"'{skill_dir.name}/' already exists in the repo. Re-run with --update to replace ONLY that folder "
                f"(other skills are never touched), or rename this skill.")
        existing_name = frontmatter(dest / "SKILL.md")[0].get("name") if (dest / "SKILL.md").exists() else None
        if existing_name and existing_name != skill_dir.name:
            die(f"refusing --update: existing folder holds skill '{existing_name}', not '{skill_dir.name}'")
        shutil.rmtree(dest)
    shutil.copytree(skill_dir, dest, ignore=shutil.ignore_patterns(*EXCLUDE, "*.skill", "*-workspace"))
    return dest

def _find_table(lines):
    """First markdown table whose header mentions 'skill' or 'name'. Returns (header_idx, end_idx) or None."""
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            if re.search(r"skill|name", lines[i], re.I):
                end = i + 2
                while end < len(lines) and lines[end].lstrip().startswith("|"): end += 1
                return i, end
            i += 1
        i += 1
    return None

def upsert_catalog(readme: pathlib.Path, name, desc, template: pathlib.Path):
    fields = [f"[{name}](./{name})", one_liner(desc), when_to_use(desc),
              f"`npx skills add TamerElsherif/tamer-skills --skill {name} --agent claude-code`"]
    if not readme.exists():
        text = template.read_text(encoding="utf-8")
    else:
        text = readme.read_text(encoding="utf-8")          # existing README is kept verbatim except the one row
    lines = text.splitlines()
    tbl = _find_table(lines)
    if tbl is None:
        lines += ["", "## Catalog", "", CATALOG_HEADER, CATALOG_SEP]
        tbl = (len(lines) - 2, len(lines))
    hi, end = tbl
    headers = [c.strip().lower() for c in lines[hi].strip().strip("|").split("|")]
    by_kind = {"link": fields[0], "what": fields[1], "when": fields[2], "install": fields[3]}
    def kind(h):
        if "install" in h or "command" in h: return "install"
        if "when" in h or "use" in h or "trigger" in h: return "when"
        if "desc" in h or "what" in h or "summary" in h or "purpose" in h: return "what"
        if "skill" in h or "name" in h: return "link"
        return None
    cells, used = [], set()
    for h in headers:
        k = kind(h)
        if k and k not in used: cells.append(by_kind[k]); used.add(k)
        else: cells.append("")
    if "link" not in used: cells[0] = fields[0]
    row = "| " + " | ".join(cells) + " |"
    rows = lines[hi + 2:end]
    kept = [r for r in rows if not re.search(rf"\|\s*\[?{re.escape(name)}\]?[\s(|]", r)]
    replaced = len(kept) != len(rows)
    kept.append(row); kept.sort(key=lambda l: l.lower())
    lines[hi + 2:end] = kept
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  catalog: {'replaced' if replaced else 'added'} row for {name} ({len(kept)-1} other rows untouched)")
    return row

def bundle(skill_dir, name, desc, out_dir: pathlib.Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    stage = out_dir / f"{name}-bundle"; shutil.rmtree(stage, ignore_errors=True); stage.mkdir()
    dest = copy_skill(skill_dir, stage); package(skill_dir, dest)
    tmpl = pathlib.Path(__file__).resolve().parent.parent / "assets" / "ROOT_README.template.md"
    row = upsert_catalog(stage / "README.catalog-preview.md", name, desc, tmpl)
    (stage / "CATALOG_ROW.md").write_text(f"Add/replace this row in the root README catalog:\n\n{row}\n", encoding="utf-8")
    (stage / "GIT_COMMANDS.sh").write_text(f"""# Run on a machine with GitHub credentials
git clone {REPO} tamer-skills 2>/dev/null || (cd tamer-skills && git pull)
[ -d tamer-skills/{name} ] && echo "'{name}/' already exists — remove it only if you intend to UPDATE that same skill" && exit 1
cp -r {name} tamer-skills/{name}
# add the row from CATALOG_ROW.md to the existing catalog table in tamer-skills/README.md (do not replace the README), then:
cd tamer-skills && git add {name} README.md
git commit -m "feat(skills): add {name} — {one_liner(desc)}"
git push origin HEAD
""", encoding="utf-8")
    zip_path = out_dir / f"{name}-bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file(): z.write(p, p.relative_to(stage))
    print(f"BUNDLE: {zip_path}\nNothing was pushed."); return zip_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-dir", required=True); ap.add_argument("--message")
    ap.add_argument("--check", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true"); ap.add_argument("--bundle")
    ap.add_argument("--update", action="store_true", help="replace an existing folder of the SAME skill")
    ap.add_argument("--list", action="store_true", help="list skills already in the repo and exit")
    a = ap.parse_args()
    skill_dir = pathlib.Path(a.skill_dir).resolve()
    name, desc = check(skill_dir)
    if a.check: return
    if a.bundle: bundle(skill_dir, name, desc, pathlib.Path(a.bundle)); return
    if not (skill_dir / "README.md").exists(): die("README.md missing — write it first (see SKILL.md step 2)")
    tmpl = pathlib.Path(__file__).resolve().parent.parent / "assets" / "ROOT_README.template.md"
    try:
        if not (CLONE / ".git").exists():
            CLONE.parent.mkdir(parents=True, exist_ok=True); run(["git", "clone", REPO, str(CLONE)])
        run(["git", "fetch", "origin", "--prune"], cwd=CLONE)
        heads = run(["git", "branch", "-r"], cwd=CLONE).stdout
        default = "main" if "origin/main" in heads else ("master" if "origin/master" in heads else None)
        if default:
            run(["git", "checkout", "-q", "-B", default, f"origin/{default}"], cwd=CLONE)
        else:  # empty repo: start main
            run(["git", "checkout", "-q", "-B", "main"], cwd=CLONE)
    except SystemExit:
        print("Clone/pull failed (credentials or network). Falling back to bundle.")
        bundle(skill_dir, name, desc, skill_dir.parent); return
    before = existing_skills(CLONE)
    if a.list: print("Skills in repo:", ", ".join(before) or "(none)"); return
    ident = run(["git", "config", "user.email"], cwd=CLONE, check=False).stdout.strip()
    if not ident: die("git identity not set — run: git config --global user.name 'Tamer ElSherif' && git config --global user.email '<email>'")
    dest = copy_skill(skill_dir, CLONE, update=a.update); package(skill_dir, dest)
    row = upsert_catalog(CLONE / "README.md", name, desc, tmpl)
    status = run(["git", "status", "--porcelain"], cwd=CLONE).stdout
    if not status.strip(): print("Nothing changed — repo already up to date."); return
    is_new = f"?? {name}/" in status
    msg = a.message or f"feat(skills): {'add' if is_new else 'update'} {name} — {one_liner(desc)}"
    if a.dry_run: print(f"DRY RUN — would commit:\n  {msg}\n  row: {row}"); run(["git", "checkout", "--", "."], cwd=CLONE, check=False); run(["git", "clean", "-fdq"], cwd=CLONE, check=False); return
    run(["git", "add", "-A"], cwd=CLONE); run(["git", "commit", "-m", msg], cwd=CLONE)
    if a.no_push: print("Committed locally, not pushed (--no-push)."); return
    r = run(["git", "push", "origin", "HEAD"], cwd=CLONE, check=False)
    if r.returncode:
        print(r.stderr); print("Push failed. Falling back to bundle."); bundle(skill_dir, name, desc, skill_dir.parent); return
    untouched = [s for s in before if s != name]
    print(f"Preserved untouched: {', '.join(untouched) or '(no other skills)'}")
    print(f"PUSHED: {REPO.rsplit('.git',1)[0]}/tree/HEAD/{name}\nInstall: npx skills add TamerElsherif/tamer-skills --skill {name} --agent claude-code\nCatalog row: {row}")

if __name__ == "__main__": main()
