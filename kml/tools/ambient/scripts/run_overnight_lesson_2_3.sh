#!/usr/bin/env bash
# Overnight: normalize Lesson 2 audio, then re-record Lesson 3 vocabulary.
# Lesson 3 reading should already be running separately.
set -euo pipefail
cd "$(dirname "$0")/.."
LOG=extended_exhibitions/overnight_lesson_2_3.log
mkdir -p extended_exhibitions
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"

exec > >(tee -a "$LOG") 2>&1
echo "=== overnight lesson 2+3 started $(date -Iseconds) ==="

echo "=== Lesson 2 audio normalization $(date -Iseconds) ==="
python3 scripts/normalize_collection_audio.py collections/lesson_02/

echo "=== Lesson 3 vocabulary re-record $(date -Iseconds) ==="
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  .venv/bin/playwright install chromium
fi
.venv/bin/python scripts/record_lesson_vocabulary.py --lesson 3 --rebuild --port 8781

echo "=== overnight lesson 2+3 finished $(date -Iseconds) ==="
