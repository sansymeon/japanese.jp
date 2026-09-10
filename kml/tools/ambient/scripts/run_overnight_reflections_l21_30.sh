#!/usr/bin/env bash
# Tonight's queue: the missing Japanese Reflections five-lesson films.
#
#   1. Japanese Reflections 21–25  (~51 min, text)
#      → ambient-study-japanese-reflections/five-lesson-reflections/lessons_21_25_exhibition.mp4
#   2. Japanese Reflections 26–30  (~51 min, text)
#      → ambient-study-japanese-reflections/five-lesson-reflections/lessons_26_30_exhibition.mp4
#
# ~2 hours of finished video. Sequential so Playwright/Chromium stays stable.
#
# Safeguards:
#   * Self-hosted fonts fetched + Playwright font preflight (abort on fail)
#   * Per-capture Noto + Yuji gates
#   * Abort on first record failure so a bad 21–25 does not quietly skip 26–30
#     after a partial overnight (resume by re-running; skip-if-exists)
#
# Start with:
#   nohup bash scripts/run_overnight_reflections_l21_30.sh \
#     > /tmp/overnight_reflections_l21_30.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

REFLECTIONS=ambient-study-japanese-reflections/five-lesson-reflections
LOG=extended_exhibitions/record_overnight_reflections_l21_30.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

PREFLIGHT_PORT=8774
PORT_21_25=8785
PORT_26_30=8786

mkdir -p "$REFLECTIONS" extended_exhibitions

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
    if [[ ! -f "$exhibition" ]]; then
      echo "FAIL $id — MP4 missing after record $(date -Iseconds)"
      return 1
    fi
  else
    echo "FAIL $id (exit $?) $(date -Iseconds)"
    return 1
  fi
}

{
  echo "START $(date -Iseconds)"
  echo "Overnight: Japanese Reflections Lessons 21–25 then 26–30 (~2 hours)"

  echo "==== Fetch self-hosted fonts $(date -Iseconds) ===="
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  echo "==== Rebuild Lessons 21–25 prototype JSON $(date -Iseconds) ===="
  "$PY" -u scripts/build_lessons_21_25_prototype.py

  echo "==== Font preflight (abort whole queue on failure) $(date -Iseconds) ===="
  if ! "$PY" -u scripts/preflight_recording_fonts.py \
      --collection lessons_21_25_prototype \
      --port "$PREFLIGHT_PORT"; then
    echo "ABORT: font preflight failed — not starting overnight recordings"
    echo "DONE (aborted) $(date -Iseconds)"
    exit 1
  fi

  if ! record_reflections lessons_21_25_prototype "$PORT_21_25"; then
    echo "Aborting so the 21–25 failure stays visible."
    echo "DONE $(date -Iseconds) (failed at 21–25)"
    exit 1
  fi

  if ! record_reflections lessons_26_30_prototype "$PORT_26_30"; then
    echo "DONE $(date -Iseconds) (failed at 26–30)"
    exit 1
  fi

  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
