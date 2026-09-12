# <skill-name>

<!-- One paragraph, 2–3 lines: what this skill is. -->

## What it's for
<!-- The problem it solves and the outcome it produces. -->

## When to use it
- <!-- trigger situation 1 -->
- <!-- trigger situation 2 -->
- **Not for:** <!-- adjacent cases it should not handle -->

## Install
```bash
npx skills add TamerElsherif/tamer-skills --skill <skill-name> --agent claude-code
# manual: copy the folder to .claude/skills/<skill-name>/ (project) or ~/.claude/skills/<skill-name>/ (user)
```
Prerequisites: <!-- tools, CLIs, credentials, other skills -->

## How to use
```
/<skill-name> <arguments>
```
- **Inputs:** <!-- what it needs from the user or repo -->
- **Outputs:** <!-- files, PRs, messages it produces -->
- **Options:** <!-- flags, modes, env vars -->

## Examples
**Example 1 — <situation>**
Prompt: `<what the user types>`
Result: <!-- what happens, what is produced -->

**Example 2 — <situation>**
Prompt: `<what the user types>`
Result: <!-- … -->

## Layout
```
<skill-name>/
├── SKILL.md            # <one line>
├── references/…        # <one line>
├── assets/…            # <one line>
└── scripts/…           # <one line>
```

## Dependencies
- <!-- other skills / external tools with links -->

## Changelog
- YYYY-MM-DD — initial version
