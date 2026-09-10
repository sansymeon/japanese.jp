#!/usr/bin/env bash
# Queue: wait for Components L101–153 to finish, then record the single
# Ambient Movie — Lessons 21–40 (~137 min).
#
# Log: collections/record_lessons_21_40_ambient_after_components.log
#
# Start with:
#   nohup bash scripts/run_lessons_21_40_ambient_after_components_l101_153.sh \
#     > /tmp/lessons_21_40_ambient_after_components.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_lessons_21_40_ambient_after_components.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p collections extended_exhibitions ambient-japan-gallery-exhibitions/ambient-movies

components_busy() {
  pgrep -f 'scripts/run_kanji_components_l101_153\.sh' >/dev/null 2>&1 && return 0
  pgrep -f 'Hand off to Components L101-153|run_kanji_components_l101_153\.sh' >/dev/null 2>&1 && return 0
  pgrep -af 'record_lesson_components\.py --lesson' 2>/dev/null \
    | grep -v cursorsandbox \
    | grep -v 'run_lessons_21_40_ambient_after' \
    | awk '{
        for (i=1;i<=NF;i++) if ($i=="--lesson") { n=$(i+1)+0; if (n>=101 && n<=153) exit 0 }
        exit 1
      }' && return 0
  return 1
}

{
  echo "START $(date -Iseconds)"
  echo "Queued: Ambient Movie Lessons 21–40 (single film) after Components L101–153"

  while components_busy; do
    echo "  components still running… $(date -Iseconds)"
    sleep 60
  done
  sleep 20
  if components_busy; then
    while components_busy; do
      echo "  components still running… $(date -Iseconds)"
      sleep 60
    done
  fi

  echo "Components L101–153 idle $(date -Iseconds)"
  echo "==== Rebuild + record Lessons 21–40 Ambient Movie $(date -Iseconds) ===="
  if "$PY" -u scripts/record_lessons_21_40_ambient_gallery_overnight.py --rebuild; then
    echo "OK Ambient 21–40 $(date -Iseconds)"
    ls -lh ambient-japan-gallery-exhibitions/ambient-movies/lessons_21_40_ambient_gallery.mp4 2>/dev/null || true
  else
    echo "FAIL Ambient 21–40 (exit $?) $(date -Iseconds)"
    echo "DONE $(date -Iseconds) (failed)"
    exit 1
  fi

  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
