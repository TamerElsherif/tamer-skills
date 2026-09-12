# tamer-skills

Reusable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) by Tamer ElSherif. One folder per skill; every folder has its own `README.md` with install and usage instructions.

| Skill | What it does |
|---|---|
| [delivery-orchestrator](./delivery-orchestrator) | Interview-driven kickoff and end-to-end orchestration for software work |
| [product-naming](product-naming/) | Find and clear a unique, trademark-friendly product name: tiered generation, live domain checks (RDAP), exact-word web search, competitor-collision and cross-language checks, ranked shortlist, name critiques |
| [push-to-tamer-skills](./push-to-tamer-skills) | Publish a skill to Tamer's personal skills repository github.com/TamerElsherif/tamer-skills |

## Install all skills at once

```sh
git clone git@github.com:TamerElsherif/tamer-skills.git ~/tamer-skills
mkdir -p ~/.claude/skills
for d in ~/tamer-skills/*/; do [ -f "$d/SKILL.md" ] && ln -sfn "$d" ~/.claude/skills/$(basename "$d"); done
```

`git pull` in `~/tamer-skills` updates every linked skill. To install a single skill, or into one project only, see that skill's README.

## Publishing convention (for every new skill)

1. Author the skill in its own folder: `SKILL.md` (frontmatter `name` + `description`, under 100 lines), `REFERENCE.md` / `EXAMPLES.md` when needed, `scripts/` for deterministic steps.
2. Add a `README.md` inside the folder: one-paragraph purpose, **Install** (personal and project-only), **Use** (three example prompts), **Files**.
3. Add a row to the table above.
4. Commit as `feat: <skill-name> skill` and push to `main`.
5. Link it into `~/.claude/skills/` on every machine that should have it.
