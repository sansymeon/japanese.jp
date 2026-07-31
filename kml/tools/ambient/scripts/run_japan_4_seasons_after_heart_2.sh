#!/usr/bin/env bash
# After Heart 2 finishes, record Ambient Gallery Japan — Four Seasons.
#
# Output: collections/ambient_gallery_japan_4_seasons/ambient_gallery_japan_4_seasons.mp4
# Log:    collections/ambient_gallery_japan_4_seasons/record_after_heart_2.log
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

HEART_LOG=heart_exhibitions/record_heart_2_after_queue.log
HEART_MP4=heart_exhibitions/heart_2.mp4
LOG=collections/ambient_gallery_japan_4_seasons/record_after_heart_2.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p collections/ambient_gallery_japan_4_seasons

{
  echo "START $(date -Iseconds)"
  echo "Waiting for Heart 2 DONE …"

  while true; do
    if [[ -f "$HEART_MP4" ]] && rg -q '^DONE ' "$HEART_LOG" 2>/dev/null; then
      echo "Heart 2 DONE spotted $(date -Iseconds)"
      break
    fi
    # Proceed if Heart MP4 exists and no heart recorder is running
    if [[ -f "$HEART_MP4" ]] \
      && ! pgrep -f 'scripts/record_heart_2\.py' >/dev/null 2>&1 \
      && ! pgrep -f 'run_heart_2_after_lesson_queue\.sh' >/dev/null 2>&1; then
      echo "Heart 2 MP4 present and recorder gone — proceeding $(date -Iseconds)"
      break
    fi
    sleep 30
  done

  echo "==== Rebuild Japan 4 Seasons JSON $(date -Iseconds) ===="
  "$PY" -u scripts/build_ambient_gallery_japan_4_seasons.py

  echo "==== Record Ambient Gallery Japan 4 Seasons (~120 min) $(date -Iseconds) ===="
  if "$PY" -u scripts/record_ambient_gallery_japan_4_seasons.py --port 9082; then
    ls -lh collections/ambient_gallery_japan_4_seasons/ambient_gallery_japan_4_seasons.mp4
    echo "DONE $(date -Iseconds)"
  else
    echo "FAIL Japan 4 Seasons record (exit $?) $(date -Iseconds)"
    exit 1
  fi
} 2>&1 | tee -a "$LOG"
