# product-naming

A Claude Code skill that finds and clears a unique, trademark-friendly product or company name: tiered candidate generation, live domain checks against the registries (RDAP), exact-word web searches, competitor-collision and cross-language meaning checks, ranked shortlist, and a structured critique when you already have a name in mind.

## Install

Personal (available in every project):

```sh
git clone git@github.com:TamerElsherif/tamer-skills.git ~/tamer-skills
mkdir -p ~/.claude/skills
ln -s ~/tamer-skills/product-naming ~/.claude/skills/product-naming
```

Project-only (checked into one repo):

```sh
mkdir -p .claude/skills
cp -r ~/tamer-skills/product-naming .claude/skills/
```

No dependencies beyond `curl`. Claude Code picks the skill up on the next session; `/product-naming` invokes it directly.

## Use

- "Name this product for MENA security buyers, lighter than Tandrik" → runs the full pipeline and returns a ranked table plus the rejected list.
- "Is Forewiser taken?" → domain check, web search, competitor collision, verdict.
- "Debate Tandrik vs Forewiser" → criteria table and the deciding fact.

Check domains yourself at any time:

```sh
~/.claude/skills/product-naming/scripts/check_domains.sh -t com,io tandrik forewiser kamtira
```

## What it will not do

Trademark registers (WIPO, EUIPO, USPTO, national offices) need a browser session; the skill tells you which classes to search and hands off. Registrar-level availability (premium/reserved names) is only known in the registrar's cart.

## Files

- `SKILL.md` — the workflow Claude follows
- `REFERENCE.md` — registry endpoints, trademark databases, phonetic rules for MENA, a worked example
- `scripts/check_domains.sh` — RDAP availability check, any TLD the bootstrap serves
