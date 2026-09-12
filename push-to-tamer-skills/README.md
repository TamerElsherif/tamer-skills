# push-to-tamer-skills

Publishes a finished skill to `github.com/TamerElsherif/tamer-skills` in one command: validates it, names the folder properly, writes or refreshes a full README, packages the `.skill`, updates the root catalog, commits and pushes. Falls back to a zip + exact git commands when there are no credentials.

## What it's for
Keeping every skill I create in one public, installable, well-documented place without repeating the same packaging and README chores by hand.

## When to use it
- Right after creating or updating any skill (`/skill-creator`, hand-written, or generated in chat)
- When asked "push/publish/upload this skill", "add it to my skills repo", "save to tamer-skills"
- **Not for:** publishing to skills.sh or a marketplace (do that from the repo afterwards), or pushing non-skill code

## Install
```bash
npx skills add TamerElsherif/tamer-skills --skill push-to-tamer-skills --agent claude-code
# manual: copy the folder to ~/.claude/skills/push-to-tamer-skills/
```
Prerequisites: `git`, Python 3.9+, GitHub credentials that can push to the repo (HTTPS credential helper, `gh auth login`, or SSH — set `TAMER_SKILLS_REPO=git@github.com:TamerElsherif/tamer-skills.git` for SSH).

## How to use
```
/push-to-tamer-skills <path-to-skill-folder>
```
- **Inputs:** a skill folder with a valid `SKILL.md` (kebab-case `name` matching the folder, trigger-quality `description`).
- **Outputs:** `tamer-skills/<name>/` (SKILL.md, README.md, `<name>.skill`, references/assets/scripts), an upserted row in the root README catalog, one commit pushed to the default branch.
- **Options** (script): `--list` show skills already in the repo · `--update` replace an existing folder of the same skill (otherwise the script refuses to overwrite) · `--check` validate only · `--dry-run` show commit/row without committing · `--no-push` commit locally · `--bundle <dir>` offline zip + `GIT_COMMANDS.sh` · `--message` custom commit message · env `TAMER_SKILLS_REPO`, `TAMER_SKILLS_CLONE`.

## Examples
**Example 1 — just built a skill in chat**
Prompt: `/push-to-tamer-skills ./invoice-parser`
Result: validates frontmatter, writes `invoice-parser/README.md` from the template (asks you only for things it can't infer), packages `invoice-parser.skill`, adds the catalog row, pushes `feat(skills): add invoice-parser — …`, replies with the folder URL and install one-liner.

**Example 2 — updated an existing skill**
Prompt: `push the updated delivery-orchestrator to my repo`
Result: replaces the folder in place, refreshes README changelog with a dated line, replaces the catalog row, commits `feat(skills): update delivery-orchestrator — …`.

**Example 3 — no credentials on this machine**
Prompt: `/push-to-tamer-skills ./foo-skill`
Result: push fails → produces `foo-skill-bundle.zip` containing the folder, `.skill`, `CATALOG_ROW.md`, `GIT_COMMANDS.sh`, and says clearly that nothing was pushed.

## Layout
```
push-to-tamer-skills/
├── SKILL.md                      # procedure: validate → README → publish → fallback → report
├── scripts/publish.py            # deterministic: check, package, copy, catalog upsert, commit, push, bundle
└── assets/
    ├── README.template.md        # required README sections for every skill
    └── ROOT_README.template.md   # catalog skeleton used when the repo README has none
```

## Safety
Additive only. Existing skill folders, the root README's own prose and sections, and other catalog rows are never touched; the catalog row is inserted into the repo's existing table by matching header names. A same-name folder is replaced only with `--update`, and only if its `SKILL.md` has the same `name`.

## Dependencies
- git, Python 3.9+, optional `gh` CLI for auth
- Repo conventions: one folder per skill, folder == `name`, catalog columns `Skill | What it does | When to use | Install`

## Changelog
- 2026-09-12 — initial version
- 2026-09-12 — overwrite protection (`--update`, `--list`), header-aware catalog insertion into existing README tables
