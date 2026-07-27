#!/usr/bin/env bash
# After the L11/12 + L34–37 lesson queue finishes, rebuild and record Heart v5
# (Digital Art Exhibition — Gallery Guardian, mobile-refine typography) with the
# same font safeguards used for lesson text stages.
#
# Output: heart_exhibitions/heart_v5.mp4 (~98 min soundtrack)
# Log:    heart_exhibitions/record_heart_v5_after_queue.log
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

QUEUE_LOG=collections/record_queue_l11_12_l34_37.log
LOG=heart_exhibitions/record_heart_v5_after_queue.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p heart_exhibitions

{
  echo "START $(date -Iseconds)"
  echo "Waiting for lesson queue DONE in $QUEUE_LOG …"

  # Poll until the lesson queue marks DONE (or the wrapper process exits).
  while true; do
    if [[ -f "$QUEUE_LOG" ]] && rg -q '^DONE ' "$QUEUE_LOG"; then
      echo "Lesson queue DONE at $(date -Iseconds)"
      break
    fi
    if ! pgrep -f 'run_record_queue_l11_12_l34_37\.sh' >/dev/null 2>&1; then
      # Queue process gone — accept DONE if present, else proceed cautiously.
      if [[ -f "$QUEUE_LOG" ]] && rg -q '^DONE ' "$QUEUE_LOG"; then
        echo "Lesson queue DONE (process exited) at $(date -Iseconds)"
        break
      fi
      echo "WARN: lesson queue process gone without DONE — continuing to Heart anyway"
      break
    fi
    sleep 60
  done

  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  echo "==== Rebuild heart chain v2→v3→v4→v5 $(date -Iseconds) ===="
  "$PY" scripts/build_heart_collection.py
  "$PY" scripts/build_heart_v3_exhibition.py
  "$PY" scripts/build_heart_v4_exhibition.py
  "$PY" scripts/build_heart_v5_exhibition.py

  echo "==== Record heart_v5 $(date -Iseconds) ===="
  # --rebuild would rebuild again; we already rebuilt above with fresh imageRev.
  if "$PY" scripts/record_heart_exhibition.py --port 8766; then
    ls -lh heart_exhibitions/heart_v5.mp4
    echo "DONE $(date -Iseconds)"
  else
    echo "FAIL heart_v5 (exit $?) $(date -Iseconds)"
    exit 1
  fi
} 2>&1 | tee "$LOG"
