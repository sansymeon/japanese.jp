#!/usr/bin/env bash
# Recording queue: Lessons 31–40 Ambient Study (foundations exhibition only).
#
# Safeguards (match the L23–25 queues):
#   * Self-hosted fonts fetched + asserted before any capture; each recorder
#     runs the Noto Serif JP + Yuji Syuku runtime gates (aborts on fallback).
#   * Idempotent + resumable: a stage whose MP4 already exists is skipped.
#   * Non-fatal per lesson: a failure is logged and the queue moves on.
#   * Unique port per lesson; --rebuild refreshes exhibition JSON.
#
# Start with:
#   nohup bash scripts/run_record_queue_l31_40_foundations.sh \
#     > /tmp/record_queue_l31_40_foundations.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1
LOG=collections/record_queue_l31_40_foundations.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=(31 32 33 34 35 36 37 38 39 40)

{
  echo "START $(date -Iseconds)"
  echo "Lessons 31–40 × foundations (Ambient Study / Gallery Seal Ending)"
  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    mkdir -p "collections/lesson_${nn}" ambient-study-japanese-reflections/individual-lessons
    out="ambient-study-japanese-reflections/individual-lessons/foundations_lesson_${nn}.mp4"
    if [[ -f "$out" ]]; then
      echo "==== SKIP L$n / foundations (exists: $out) $(date -Iseconds) ===="
      continue
    fi
    port=$((9100 + n))
    echo "==== LESSON $n / foundations  port=$port  $(date -Iseconds) ===="
    if "$PY" -u scripts/record_lesson_foundations.py --lesson "$n" --rebuild --port "$port"; then
      ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
    else
      echo "FAIL L$n / foundations (exit $?) — continuing queue"
    fi
  done
  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
