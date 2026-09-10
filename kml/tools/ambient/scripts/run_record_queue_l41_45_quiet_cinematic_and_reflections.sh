#!/usr/bin/env bash
# Recording queue: Lessons 41–45, after Ambient Japan 4h finishes.
#
#   0. Wait until ambient_japan_4h.mp4 exists and its recorder/mux has exited
#   1. Quiet Cinematic 41–45          (~51 min, no text)
#   2. Japanese Reflections 41–45     (~51 min, text)
#
# Sequential so Playwright/Chromium stays stable. Do not start while the
# 4h mux is still running (CPU contention).
#
# Safeguards:
#   * Self-hosted fonts fetched + asserted before any capture.
#   * Idempotent + resumable: a stage whose MP4 already exists is skipped.
#   * Non-fatal per stage: a failure is logged and the queue moves on.
#
# Start with:
#   nohup bash scripts/run_record_queue_l41_45_quiet_cinematic_and_reflections.sh \
#     > /tmp/record_queue_l41_45.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

REFLECTIONS=ambient-study-japanese-reflections/five-lesson-reflections
QUIET=ambient-japan-gallery-exhibitions/quiet-cinematic
FOUR_H=collections/ambient_japan_4h_scenery/ambient_japan_4h.mp4
LOG=extended_exhibitions/record_queue_l41_45_quiet_cinematic_and_reflections.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p "$REFLECTIONS" "$QUIET" extended_exhibitions

recorder_alive() {
  ps -C python,python3 -o args= 2>/dev/null | grep -q 'record_ambient_japan_4h.py'
}

mux_alive() {
  ps -C ffmpeg -o args= 2>/dev/null | grep -q 'tmp_ambient_japan_4h/muxed.mp4'
}

wait_for_four_hour() {
  echo "==== WAIT Ambient Japan 4h  $(date -Iseconds) ===="
  while true; do
    if [[ -f "$FOUR_H" ]] && ! recorder_alive && ! mux_alive; then
      echo "4h ready: $(ls -lh "$FOUR_H")"
      return 0
    fi
    if [[ -f "$FOUR_H" ]]; then
      echo "  4h MP4 present; waiting for recorder/mux to exit  $(date -Iseconds)"
    else
      echo "  waiting for $FOUR_H  $(date -Iseconds)"
    fi
    sleep 30
  done
}

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
  echo "Lessons 41–45 × Quiet Cinematic then Japanese Reflections"
  wait_for_four_hour
  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  record_quiet lessons_41_45_quiet_cinematic record_lessons_41_45_quiet_cinematic.py 8785
  record_reflections lessons_41_45_prototype 8786

  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
