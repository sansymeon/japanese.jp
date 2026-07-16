#!/usr/bin/env bash
# Overnight: Playwright recordings for Lesson 10 (readings → strokes → gallery → compounds → vocabulary).
# foundations_lesson_10.mp4 already exists — skipped.
# Log: extended_exhibitions/lesson_10_recordings.log
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
mkdir -p extended_exhibitions
LOG=extended_exhibitions/lesson_10_recordings.log

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
echo "=== Lesson 10 overnight Playwright recordings started $(date -Iseconds) ==="
echo "Skipping foundations (foundations_lesson_10.mp4 already exists)"

rm -rf collections/lesson_10/.tmp_readings_lesson_10

"$VENV_PYTHON" scripts/record_lesson_reading.py --lesson 10 --rebuild --port 8783
"$VENV_PYTHON" scripts/record_lesson_strokes.py --lesson 10 --rebuild --port 8784
"$VENV_PYTHON" scripts/record_lesson_gallery.py --lesson 10 --rebuild --port 8785
"$VENV_PYTHON" scripts/record_lesson_compounds.py --lesson 10 --rebuild --port 8785
"$VENV_PYTHON" scripts/record_lesson_vocabulary.py --lesson 10 --rebuild --port 8786

echo "=== Lesson 10 overnight Playwright recordings finished $(date -Iseconds) ==="
