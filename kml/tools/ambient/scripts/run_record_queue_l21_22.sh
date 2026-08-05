#!/usr/bin/env bash
# Recording queue: Lessons 21–22 — all 7 stages (foundations through gallery).
#
# Safeguards (match the L19–20 / L15–18 queues):
#   * Self-hosted fonts fetched + asserted before any capture; each recorder
#     runs the Noto Serif JP + Yuji Syuku runtime gates (aborts on fallback).
#   * Idempotent + resumable: a stage whose MP4 already exists is skipped, so
#     re-running continues where it left off.
#   * Non-fatal per stage: a failure is logged and the queue moves on rather
#     than aborting the whole batch.
#   * Unique port per stage/lesson; --rebuild refreshes JSON from the builders.
#
# Start overnight with:
#   nohup bash scripts/run_record_queue_l21_22.sh \
#     > /tmp/record_queue_l21_22.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1
LOG=collections/record_queue_l21_22.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=(21 22)
# stage : recorder script : output-file prefix : port base
STAGES=(
  "foundations:record_lesson_foundations.py:foundations:9100"
  "strokes:record_lesson_strokes.py:strokes:9200"
  "components:record_lesson_components.py:components:9700"
  "compounds:record_lesson_compounds.py:compounds:9300"
  "reading:record_lesson_reading.py:readings:9400"
  "vocabulary:record_lesson_vocabulary.py:vocabulary:9500"
  "gallery:record_lesson_gallery.py:gallery:9600"
)

{
  echo "START $(date -Iseconds)"
  echo "Lessons 21–22 × 7 stages (foundations, strokes, components, compounds, reading, vocabulary, gallery)"
  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    mkdir -p "collections/lesson_${nn}"
    for entry in "${STAGES[@]}"; do
      IFS=":" read -r stage script prefix portbase <<<"$entry"
      out="collections/lesson_${nn}/${prefix}_lesson_${nn}.mp4"
      if [[ -f "$out" ]]; then
        echo "==== SKIP L$n / $stage (exists: $out) $(date -Iseconds) ===="
        continue
      fi
      port=$((portbase + n))
      echo "==== LESSON $n / $stage  port=$port  $(date -Iseconds) ===="
      if "$PY" -u "scripts/$script" --lesson "$n" --rebuild --port "$port"; then
        ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
      else
        echo "FAIL L$n / $stage (exit $?) — continuing queue"
      fi
    done
  done
  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
