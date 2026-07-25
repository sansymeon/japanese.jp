#!/usr/bin/env bash
# Rebuild + record Heisig gallery lessons 33–37 sequentially.
set -euo pipefail
cd "$(dirname "$0")/.."
# Force local Playwright browsers (ignore Cursor sandbox empty cache path).
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
LOG=collections/gallery_record_33_37.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

{
  echo "START $(date -Iseconds)"
  for n in 33 34 35 36 37; do
    echo "==== LESSON $n $(date -Iseconds) ===="
    "$PY" scripts/record_lesson_gallery.py --lesson "$n" --rebuild --port $((8800 + n))
    ls -lh "collections/lesson_${n}/gallery_lesson_${n}.mp4"
  done
  echo "DONE $(date -Iseconds)"
} 2>&1 | tee "$LOG"
