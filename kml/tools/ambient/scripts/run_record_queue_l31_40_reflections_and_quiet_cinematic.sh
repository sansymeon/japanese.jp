#!/usr/bin/env bash
# Recording queue: Lessons 31–35 and 36–40, both YouTube families.
#
#   1. Japanese Reflections 31–35  (~51 min, text)
#   2. Japanese Reflections 36–40  (~51 min, text)
#   3. Quiet Cinematic 31–35       (~51 min, no text)
#   4. Quiet Cinematic 36–40       (~51 min, no text)
#
# ~4 hours of finished video. Sequential so Playwright/Chromium stays stable.
#
# Safeguards:
#   * Self-hosted fonts fetched + asserted before any capture.
#   * Idempotent + resumable: a stage whose MP4 already exists is skipped.
#   * Non-fatal per stage: a failure is logged and the queue moves on.
#
# Start with:
#   nohup bash scripts/run_record_queue_l31_40_reflections_and_quiet_cinematic.sh \
#     > /tmp/record_queue_l31_40_both_families.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

REFLECTIONS=ambient-study-japanese-reflections/five-lesson-reflections
QUIET=ambient-japan-gallery-exhibitions/quiet-cinematic
LOG=extended_exhibitions/record_queue_l31_40_reflections_and_quiet_cinematic.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p "$REFLECTIONS" "$QUIET" extended_exhibitions

record_reflections() {
  local id=$1 port=$2
  local exhibition="$REFLECTIONS/${id/_prototype/_exhibition}.mp4"
  if [[ -f "$exhibition" ]]; then
    echo "==== SKIP $id (exists: $exhibition) $(date -Iseconds) ===="
    ls -lh "$exhibition"
    return 0
  fi
  echo "==== Record $id  port=$port  $(date -Iseconds) ===="
  if "$PY" -u scripts/record_japanese_reflections_exhibition.py \
      "$id" --rebuild --port "$port"; then
    ls -lh "$exhibition" 2>/dev/null || echo "WARN: $exhibition not produced"
  else
    echo "FAIL $id (exit $?) — continuing queue"
  fi
}

record_quiet() {
  local id=$1 script=$2 port=$3
  local out="$QUIET/${id}.mp4"
  if [[ -f "$out" ]]; then
    echo "==== SKIP $id (exists: $out) $(date -Iseconds) ===="
    ls -lh "$out"
    return 0
  fi
  echo "==== Record $id  port=$port  $(date -Iseconds) ===="
  if "$PY" -u "scripts/$script" --rebuild --port "$port"; then
    ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
  else
    echo "FAIL $id (exit $?) — continuing queue"
  fi
}

{
  echo "START $(date -Iseconds)"
  echo "Lessons 31–40 × Japanese Reflections + Quiet Cinematic (~4 hours)"
  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  record_reflections lessons_31_35_prototype 8781
  record_reflections lessons_36_40_prototype 8782
  record_quiet lessons_31_35_quiet_cinematic record_lessons_31_35_quiet_cinematic.py 8783
  record_quiet lessons_36_40_quiet_cinematic record_lessons_36_40_quiet_cinematic.py 8784

  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
