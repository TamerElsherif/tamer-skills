---
name: push-to-tamer-skills
description: Publish a skill to Tamer's personal skills repository github.com/TamerElsherif/tamer-skills — validates the SKILL.md, picks a proper kebab-case folder name, writes or refreshes a full README (what it is, what it's for, when to use, install, use, examples, layout, dependencies), packages the .skill file, upserts the row in the root README catalog, commits and pushes. Use this whenever a skill has just been created or updated, or whenever the user says "push/publish/upload this skill", "add it to my skills repo", "save to tamer-skills", or "/push-to-tamer-skills" — even if they only say "put it in my repo".
---

# Push to tamer-skills

Publishes one skill folder to `https://github.com/TamerElsherif/tamer-skills` as `<skill-name>/` with `SKILL.md`, `README.md`, `<skill-name>.skill`, and a catalog row in the root `README.md`. Deterministic parts run in `scripts/publish.py`; you handle the judgement parts (naming, description quality, README content).

## Procedure

### 1. Locate and validate the skill
- Skill dir = the argument the user gave, else the skill created/edited most recently in this conversation, else ask.
- Read `SKILL.md`. Frontmatter needs `name` (kebab-case, matches the folder) and a `description` that says **what it does and when to trigger** (push the trigger phrases a little — Claude undertriggers). If the description is weak or the name is generic (`helper`, `tool`, `my-skill`), propose a better one and use it unless the user objects. Rename the folder to match `name`.
- Run `python3 scripts/publish.py --skill-dir <dir> --check` to confirm frontmatter, no absolute paths, no secrets/tokens in files, and that `README.md` exists or will be generated.

### 2. Write or refresh `README.md` (in the skill folder)
Use `assets/README.template.md`. Every README must answer, in this order: **What it is** (2–3 lines) · **What it's for** (problem solved) · **When to use it** (trigger situations, incl. when *not* to) · **Install** (npx skills command + manual copy) · **How to use** (invocation, inputs, outputs, options) · **Examples** (2–3 realistic prompts with what happens) · **Layout** (file tree with one-line purpose each) · **Dependencies/prerequisites** · **Changelog** (date + one line). Derive content from SKILL.md and references; never invent capabilities the skill doesn't have. If a README exists, keep user-written prose and add only missing sections.

### 3. Publish — additive only
```
python3 scripts/publish.py --skill-dir <dir> --list            # see what is already in the repo first
python3 scripts/publish.py --skill-dir <dir> [--update] [--message "<why>"] [--dry-run] [--no-push]
```
The script clones/pulls the repo to `~/.cache/tamer-skills` (or `$TAMER_SKILLS_REPO`/`$TAMER_SKILLS_CLONE`), copies the folder (excluding `evals/`, `*-workspace/`, `.DS_Store`), builds `<name>.skill`, adds one row to the **existing** catalog table in the root `README.md` (columns are matched by header name — Name/Skill, Description/What, When, Install — so the repo's own layout is kept; the template README is used only when the repo has no README at all), commits `feat(skills): add|update <name> — <one-liner>`, pushes to the default branch.

**Overwrite protection:** if `<name>/` already exists the script refuses unless you pass `--update`, and `--update` only replaces that one folder after confirming its `SKILL.md` carries the same `name`. Other skill folders, README prose, licence sections, and other catalog rows are never modified; the report lists the skills that were preserved untouched. If the user asks to "update" a skill, confirm the name matches an existing folder before passing `--update`.

### 4. If push fails (no credentials, 403, offline)
Don't retry blindly. Produce `<name>-bundle.zip` (skill folder + `.skill` + `CATALOG_ROW.md` + `GIT_COMMANDS.sh`) via `python3 scripts/publish.py --skill-dir <dir> --bundle <out-dir>` and hand it over with the exact commands. Say plainly that nothing was pushed.

### 5. Report
Three lines: repo path of the folder, the install one-liner (`npx skills add TamerElsherif/tamer-skills --skill <name> --agent claude-code`), and what changed in the catalog.

## Conventions (keep the repo tidy)
- One folder per skill, folder name == `name` frontmatter, lowercase kebab-case, no version suffixes (`-v2`); versions go in the README changelog.
- Additive by default: never delete, rename, or rewrite another skill's folder or its catalog row; never replace the root README; a same-name folder is replaced only with `--update`.
- Root README catalog columns: `Skill | What it does | When to use | Install`. One row per skill, alphabetical.
- Commit messages: `feat(skills): add <name> — …` for new, `feat(skills): update <name> — …` for changes, `docs(skills): …` for README-only.
- Never push secrets, tokens, absolute local paths, or `evals/` workspaces.
