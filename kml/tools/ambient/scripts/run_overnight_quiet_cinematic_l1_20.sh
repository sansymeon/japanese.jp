#!/usr/bin/env bash
# Overnight: Quiet Cinematic Japan for Lessons 1–20 (the missing five-lesson films).
#
#   1. Lessons 1–5   (~51 min)
#   2. Lessons 6–10  (~51 min)
#   3. Lessons 11–15 (~51 min)
#   4. Lessons 16–20 (~51 min)
#
# ~3.5 hours of finished video. Sequential so Playwright/Chromium stays stable.
#
# Start with:
#   nohup bash scripts/run_overnight_quiet_cinematic_l1_20.sh \
#     > /tmp/overnight_quiet_cinematic_l1_20.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

QUIET=ambient-japan-gallery-exhibitions/quiet-cinematic
LOG=extended_exhibitions/record_overnight_quiet_cinematic_l1_20.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

PREFLIGHT_PORT=8775
BLOCKS=(
  "lessons_1_5_quiet_cinematic:8791"
  "lessons_6_10_quiet_cinematic:8792"
  "lessons_11_15_quiet_cinematic:8793"
  "lessons_16_20_quiet_cinematic:8794"
)

mkdir -p "$QUIET" extended_exhibitions

record_block() {
  local id=$1 port=$2
  local out="$QUIET/${id}.mp4"
  if [[ -f "$out" ]]; then
    echo "==== SKIP $id (exists: $out) $(date -Iseconds) ===="
    ls -lh "$out"
    return 0
  fi
  echo "==== Record $id  port=$port  $(date -Iseconds) ===="
  if "$PY" -u scripts/record_quiet_cinematic.py "$id" --rebuild --port "$port"; then
    ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
    if [[ ! -f "$out" ]]; then
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
  echo "Overnight: Quiet Cinematic Lessons 1–5, 6–10, 11–15, 16–20 (~3.5 hours)"

  echo "==== Fetch self-hosted fonts $(date -Iseconds) ===="
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  echo "==== Rebuild Quiet Cinematic 1–20 collections $(date -Iseconds) ===="
  "$PY" -u scripts/build_lessons_1_20_quiet_cinematic.py

  echo "==== Font preflight (abort whole queue on failure) $(date -Iseconds) ===="
  if ! "$PY" -u scripts/preflight_recording_fonts.py \
      --collection lessons_1_5_quiet_cinematic \
      --port "$PREFLIGHT_PORT"; then
    echo "ABORT: font preflight failed — not starting overnight recordings"
    echo "DONE (aborted) $(date -Iseconds)"
    exit 1
  fi

  failed=0
  for spec in "${BLOCKS[@]}"; do
    id=${spec%%:*}
    port=${spec##*:}
    if ! record_block "$id" "$port"; then
      failed=1
      echo "Continuing queue after $id failure"
    fi
  done

  if [[ "$failed" -eq 1 ]]; then
    echo "DONE $(date -Iseconds) (with failures)"
    exit 1
  fi
  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
