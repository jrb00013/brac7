#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

brac7 \
  --title "Round Robin Demo" \
  --format round_robin \
  --seeding seeded \
  --members-file examples/ai-startups.txt \
  --output-dir output \
  --slug round-robin-demo \
  --all
