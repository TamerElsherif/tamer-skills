#!/usr/bin/env bash
# Install every Rabet skill into ~/.claude/skills (side by side, so they can find the shared rabet-reels engine).
# usage: bash install.sh            (run from this folder; re-run to update)
set -e
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"
cd "$(dirname "$0")/skills"
for d in */; do
  d="${d%/}"; rm -rf "$DEST/$d"; cp -r "$d" "$DEST/$d"; echo "installed $d"
done
[ -f "$HOME/.rabet-reels.json" ] || { cp rabet-reels/config.example.json "$HOME/.rabet-reels.json"; echo "created ~/.rabet-reels.json: fill in your paths"; }
