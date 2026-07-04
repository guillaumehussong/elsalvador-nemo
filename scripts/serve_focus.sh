#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${FOCUS_PORT:-8080}"
cd "$ROOT"
exec uv run sv-focus-api --host 0.0.0.0 --port "$PORT"
