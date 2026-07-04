#!/usr/bin/env bash
# Build + serve static map (production preview on VPS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAP="$ROOT/apps/map"
PORT="${MAP_PORT:-4173}"

cd "$MAP"
npm run build
echo ""
echo "Carte statique : $MAP/dist"
du -sh "$MAP/dist" "$MAP/dist/data" 2>/dev/null || du -sh "$MAP/dist"
echo ""
echo "Preview : http://0.0.0.0:$PORT  (tunnel SSH: ssh -L $PORT:localhost:$PORT user@vps)"
exec npm run preview -- --host --port "$PORT"
