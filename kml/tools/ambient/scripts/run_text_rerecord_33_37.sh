#!/usr/bin/env bash
# Re-record L33–37 text stages after Noto Serif JP self-host + font gate.
# Stages: foundations, compounds, reading (strokes/gallery already recorded).
# Soundtrack: mux_exhibition_soundtrack (8s afade to silence on last video frame).
# Closing: holdUntilSoundtrackEnds=false — do not pad to the master bed.
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
LOG=collections/text_rerecord_33_37.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

bash scripts/fetch_noto_serif_jp_fonts.sh

STAGES=(foundations compounds reading)
LESSONS=(33 34 35 36 37)

{
  echo "START $(date -Iseconds)"
  for n in "${LESSONS[@]}"; do
    for stage in "${STAGES[@]}"; do
      echo "==== LESSON $n / $stage $(date -Iseconds) ===="
      case "$stage" in
        foundations)
          "$PY" scripts/record_lesson_foundations.py --lesson "$n" --rebuild --port $((9000 + n))
          ls -lh "collections/lesson_${n}/foundations_lesson_${n}.mp4"
          ;;
        compounds)
          "$PY" scripts/record_lesson_compounds.py --lesson "$n" --rebuild --port $((9010 + n))
          ls -lh "collections/lesson_${n}/compounds_lesson_${n}.mp4"
          ;;
        reading)
          "$PY" scripts/record_lesson_reading.py --lesson "$n" --rebuild --port $((9020 + n))
          ls -lh "collections/lesson_${n}/readings_lesson_${n}.mp4"
          ;;
      esac
    done
  done
  echo "DONE $(date -Iseconds)"
} 2>&1 | tee "$LOG"
