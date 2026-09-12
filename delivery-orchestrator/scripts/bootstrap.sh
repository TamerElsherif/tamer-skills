#!/usr/bin/env bash
# Bootstrap a repo for the delivery-orchestrator workflow. Idempotent: skips what exists.
# Usage: bash <skill-dir>/scripts/bootstrap.sh [repo-root]
set -euo pipefail
REPO="${1:-$(pwd)}"; SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
echo "== delivery-orchestrator bootstrap in $REPO"

# 1. Skills
if command -v claude >/dev/null 2>&1; then
  claude plugins install mattpocock-skills 2>/dev/null || echo "   (install mattpocock-skills manually: /plugin install mattpocock-skills)"
fi
if command -v npx >/dev/null 2>&1; then
  for s in clean-code-guard test-guard docs-guard; do
    npx -y skills add amElnagdy/guard-skills --skill "$s" --agent claude-code -y 2>/dev/null || echo "   (guard $s: install manually)"
  done
  npx -y skills add amElnagdy/review-skills --agent claude-code -y 2>/dev/null || echo "   (review-skills: install manually)"
  if command -v codex >/dev/null 2>&1; then
    npx -y skills add amElnagdy/delegate-skills --skill codex-delegate --agent claude-code -y 2>/dev/null || true
  fi
fi

# 2. Files
mkdir -p .claude/agents docs/ai docs/research docs/adr
for f in "$SKILL_DIR"/assets/agents/*.md; do
  b=$(basename "$f"); [ -e ".claude/agents/$b" ] || cp "$f" ".claude/agents/$b"
done
[ -e .claude/settings.json ] || cp "$SKILL_DIR/assets/settings.json" .claude/settings.json
for f in STATE.md DECISIONS.md BRIEF.md; do [ -e "docs/ai/$f" ] || cp "$SKILL_DIR/assets/$f" "docs/ai/$f"; done
if ! grep -q "Orchestrator Operating Rules" CLAUDE.md 2>/dev/null; then
  cat "$SKILL_DIR/assets/CLAUDE.orchestrator.md" >> CLAUDE.md
fi

# 3. Facts for STATE.md
DEF=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#origin/##' || echo main)
sed -i.bak "s#Default branch: main#Default branch: ${DEF:-main}#" docs/ai/STATE.md && rm -f docs/ai/STATE.md.bak
command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1 && echo "   gh: authenticated" || echo "   gh: NOT authenticated — PR creation will fail"

# 4. Validate
command -v claude >/dev/null 2>&1 && claude plugin validate .claude/agents || true
echo "== Next: run /setup-matt-pocock-skills, then patch the 'skills:' IDs in .claude/agents/*.md to the exact installed IDs (plugin skills may be scoped, e.g. mattpocock-skills:tdd)."
