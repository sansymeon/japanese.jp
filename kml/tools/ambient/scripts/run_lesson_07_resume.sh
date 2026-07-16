#!/usr/bin/env bash
# Resume Lesson 7 Playwright recordings (strokes → gallery → compounds → vocabulary).
# foundations + readings already done.
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
mkdir -p extended_exhibitions
LOG=extended_exhibitions/lesson_07_recordings.log

exec > >(tee -a "$LOG") 2>&1
echo "=== Lesson 7 resume started $(date -Iseconds) ==="
echo "Skipping foundations + readings (already recorded)"

.venv/bin/python scripts/record_lesson_strokes.py --lesson 7 --rebuild --port 8779
.venv/bin/python scripts/record_lesson_gallery.py --lesson 7 --rebuild --port 8780
.venv/bin/python scripts/record_lesson_compounds.py --lesson 7 --rebuild --port 8780
.venv/bin/python scripts/record_lesson_vocabulary.py --lesson 7 --rebuild --port 8781

echo "=== Lesson 7 resume finished $(date -Iseconds) ==="
