#!/usr/bin/env bash
# Overnight: Playwright recordings for Lesson 9 (readings → strokes → gallery → compounds → vocabulary).
# foundations_lesson_09.mp4 already exists — skipped.
# Log: extended_exhibitions/lesson_09_recordings.log
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
mkdir -p extended_exhibitions
LOG=extended_exhibitions/lesson_09_recordings.log

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  .venv/bin/playwright install chromium
fi
if ! compgen -G ".playwright-browsers/chromium_headless_shell-*" >/dev/null; then
  .venv/bin/playwright install chromium
fi

exec > >(tee -a "$LOG") 2>&1
echo "=== Lesson 9 overnight Playwright recordings started $(date -Iseconds) ==="
echo "Skipping foundations (foundations_lesson_09.mp4 already exists)"

rm -rf collections/lesson_09/.tmp_readings_lesson_09

"$VENV_PYTHON" scripts/record_lesson_reading.py --lesson 9 --rebuild --port 8782
"$VENV_PYTHON" scripts/record_lesson_strokes.py --lesson 9 --rebuild --port 8779
"$VENV_PYTHON" scripts/record_lesson_gallery.py --lesson 9 --rebuild --port 8780
"$VENV_PYTHON" scripts/record_lesson_compounds.py --lesson 9 --rebuild --port 8780
"$VENV_PYTHON" scripts/record_lesson_vocabulary.py --lesson 9 --rebuild --port 8781

echo "=== Lesson 9 overnight Playwright recordings finished $(date -Iseconds) ==="
