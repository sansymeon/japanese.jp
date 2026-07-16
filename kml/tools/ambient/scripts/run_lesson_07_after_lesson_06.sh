#!/usr/bin/env bash
# Wait for Lesson 6 Playwright batch, then record Lesson 7 stages.
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
mkdir -p extended_exhibitions
LOG=extended_exhibitions/lesson_07_recordings.log

exec > >(tee -a "$LOG") 2>&1
echo "=== Lesson 7 waiter started $(date -Iseconds) ==="

# Wait until the Lesson 6 batch shell (and its vocabulary child) are gone.
while pgrep -af "record_lesson_vocabulary.py --lesson 6|lesson_06_recordings\.log" >/dev/null 2>&1; do
  if ! pgrep -f "record_lesson_vocabulary.py --lesson 6" >/dev/null 2>&1 \
     && [[ -f collections/lesson_06/vocabulary_lesson_06.mp4 ]]; then
    # Vocabulary process finished and output exists; also wait for the parent batch tee to exit.
    if ! pgrep -f "record_lesson_(strokes|gallery|compounds|vocabulary).*--lesson 6" >/dev/null 2>&1; then
      break
    fi
  fi
  echo "waiting for Lesson 6 recordings… $(date -Iseconds)"
  sleep 60
done

echo "=== Lesson 6 complete; starting Lesson 7 Playwright recordings $(date -Iseconds) ==="
.venv/bin/python scripts/record_lesson_reading.py --lesson 7 --rebuild --port 8782
.venv/bin/python scripts/record_lesson_strokes.py --lesson 7 --rebuild --port 8779
.venv/bin/python scripts/record_lesson_gallery.py --lesson 7 --rebuild --port 8780
.venv/bin/python scripts/record_lesson_compounds.py --lesson 7 --rebuild --port 8780
.venv/bin/python scripts/record_lesson_vocabulary.py --lesson 7 --rebuild --port 8781
echo "=== Lesson 7 Playwright recordings finished $(date -Iseconds) ==="
