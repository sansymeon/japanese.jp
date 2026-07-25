#!/usr/bin/env bash
# Rebuild + record Heisig lessons 33–37 stages (Lesson 5 standard).
# Stages: foundations, strokes, compounds, readings. (Vocabulary deferred.)
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
LOG=collections/stages_record_33_37.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

STAGES=(foundations strokes compounds reading)
LESSONS=(33 34 35 36 37)

{
  echo "START $(date -Iseconds)"
  for n in "${LESSONS[@]}"; do
    for stage in "${STAGES[@]}"; do
      echo "==== LESSON $n / $stage $(date -Iseconds) ===="
      case "$stage" in
        foundations)
          "$PY" scripts/record_lesson_foundations.py --lesson "$n" --rebuild --port $((8900 + n))
          ls -lh "collections/lesson_${n}/foundations_lesson_${n}.mp4"
          ;;
        strokes)
          "$PY" scripts/record_lesson_strokes.py --lesson "$n" --rebuild --port $((8910 + n))
          ls -lh "collections/lesson_${n}/strokes_lesson_${n}.mp4"
          ;;
        compounds)
          "$PY" scripts/record_lesson_compounds.py --lesson "$n" --rebuild --port $((8920 + n))
          ls -lh "collections/lesson_${n}/compounds_lesson_${n}.mp4"
          ;;
        reading)
          "$PY" scripts/record_lesson_reading.py --lesson "$n" --rebuild --port $((8930 + n))
          ls -lh "collections/lesson_${n}/readings_lesson_${n}.mp4"
          ;;
      esac
    done
  done
  echo "DONE $(date -Iseconds)"
} 2>&1 | tee "$LOG"
