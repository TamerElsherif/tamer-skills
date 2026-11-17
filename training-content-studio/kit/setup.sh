#!/usr/bin/env bash
# Install the render kit's Node dependencies (Remotion 4, fonts, icons). Idempotent.
set -euo pipefail
cd "$(dirname "$0")"
command -v node >/dev/null || { echo "Node.js >= 18 is required (https://nodejs.org)"; exit 1; }
command -v ffmpeg >/dev/null || echo "warning: ffmpeg not found — prepare/render scripts need ffmpeg + ffprobe"
if [ -d node_modules/remotion ] && [ "${1:-}" != "--force" ]; then echo "kit deps already installed"; exit 0; fi
npm install --no-audit --no-fund
echo "kit ready: $(pwd)"
