#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .venv/bin/activate 2>/dev/null || true

brac7 \
  --title "AI Startup Showdown — Single Elimination" \
  --format single_elimination \
  --seeding seeded \
  --byes \
  --members-file examples/ai-startups.txt \
  --output-dir output \
  --slug ai-startup-bracket \
  --all \
  --no-interactive

echo "Done. Open output/ai-startup-bracket.*"
