#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Single elimination ==="
brac7 \
  --title "Single Elimination Demo" \
  --format single_elimination \
  --members-file examples/ai-startups.txt \
  --output-dir output \
  --slug single-elimination \
  --all

echo ""
echo "=== Round robin ==="
brac7 \
  --title "Round Robin Demo" \
  --format round_robin \
  --members-file examples/ai-startups.txt \
  --output-dir output \
  --slug round-robin \
  --all

echo ""
echo "=== Double elimination ==="
brac7 \
  --title "Double Elimination Demo" \
  --format double_elimination \
  --members-file examples/ai-startups.txt \
  --output-dir output \
  --slug double-elimination \
  --all

echo ""
echo "Done — all formats generated in output/"
