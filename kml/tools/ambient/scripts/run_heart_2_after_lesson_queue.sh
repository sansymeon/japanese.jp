#!/usr/bin/env bash
# After the Lessons 19–20 queue finishes, record Heart 2 (textless ambient gallery).
#
# Output: heart_exhibitions/heart_2.mp4
# Log:    heart_exhibitions/record_heart_2_after_queue.log
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

QUEUE_LOG=collections/record_queue_l19_20.log
LOG=heart_exhibitions/record_heart_2_after_queue.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p heart_exhibitions

{
  echo "START $(date -Iseconds)"
  echo "Waiting for lesson queue DONE in $QUEUE_LOG …"

  while true; do
    if rg -q '^DONE ' "$QUEUE_LOG" 2>/dev/null; then
      echo "Lesson queue DONE spotted $(date -Iseconds)"
      break
    fi
    # Also proceed if the queue wrapper is gone and L20 gallery exists
    if [[ -f collections/lesson_20/gallery_lesson_20.mp4 ]] \
      && ! pgrep -f 'run_record_queue_l19_20\.sh' >/dev/null 2>&1; then
      echo "L20 gallery present and queue process gone — proceeding $(date -Iseconds)"
      break
    fi
    sleep 30
  done

  echo "==== Record Heart 2 $(date -Iseconds) ===="
  if "$PY" scripts/record_heart_2.py --port 8768; then
    ls -lh heart_exhibitions/heart_2.mp4
    echo "DONE $(date -Iseconds)"
  else
    echo "FAIL Heart 2 record (exit $?) $(date -Iseconds)"
    exit 1
  fi
} 2>&1 | tee -a "$LOG"
