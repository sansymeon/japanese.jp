#!/usr/bin/env bash
# Recording queue: Lessons 15–18 (JSON already built).
#
# Safeguards (match the L13–14 / L11–12 / L34–37 queues):
#   * Self-hosted fonts fetched + asserted before any capture; each recorder
#     runs the Noto Serif JP + Yuji Syuku runtime gates (aborts on fallback).
#   * Idempotent + resumable: a stage whose MP4 already exists is skipped, so
#     re-running continues where it left off.
#   * Non-fatal per stage: a failure is logged and the queue moves on rather
#     than aborting the whole batch.
#   * Unique port per stage/lesson; --rebuild refreshes JSON from the builders.
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
LOG=collections/record_queue_l15_18.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=(15 16 17 18)
# stage : recorder script : output-file prefix : port base
STAGES=(
  "foundations:record_lesson_foundations.py:foundations:9100"
  "strokes:record_lesson_strokes.py:strokes:9200"
  "compounds:record_lesson_compounds.py:compounds:9300"
  "reading:record_lesson_reading.py:readings:9400"
  "vocabulary:record_lesson_vocabulary.py:vocabulary:9500"
  "gallery:record_lesson_gallery.py:gallery:9600"
)

{
  echo "START $(date -Iseconds)"
  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    for entry in "${STAGES[@]}"; do
      IFS=":" read -r stage script prefix portbase <<<"$entry"
      out="collections/lesson_${nn}/${prefix}_lesson_${nn}.mp4"
      if [[ -f "$out" ]]; then
        echo "==== SKIP L$n / $stage (exists: $out) $(date -Iseconds) ===="
        continue
      fi
      port=$((portbase + n))
      echo "==== LESSON $n / $stage  port=$port  $(date -Iseconds) ===="
      if "$PY" "scripts/$script" --lesson "$n" --rebuild --port "$port"; then
        ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
      else
        echo "FAIL L$n / $stage (exit $?) — continuing queue"
      fi
    done
  done
  echo "DONE $(date -Iseconds)"
} 2>&1 | tee "$LOG"
