#!/usr/bin/env bash
# Tonight's queue:
#   1) Rebuild + re-record Japanese Reflections Lessons 1–5 (~51 min)
#      → ambient-study-japanese-reflections/five-lesson-reflections/lessons_1_5_prototype.mp4
#      → also copied to lessons_1_5_exhibition.mp4
#   2) Then record Kanji Components L101–153 (~9 h)
#
# Log: collections/record_overnight_l1_5_then_components_l101_153.log
#
# Start with:
#   nohup bash scripts/run_overnight_l1_5_then_components_l101_153.sh \
#     > /tmp/overnight_l1_5_components_l101_153.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_overnight_l1_5_then_components_l101_153.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

OUT_PROTOTYPE=ambient-study-japanese-reflections/five-lesson-reflections/lessons_1_5_prototype.mp4
OUT_EXHIBITION=ambient-study-japanese-reflections/five-lesson-reflections/lessons_1_5_exhibition.mp4
ARCHIVE_DIR=extended_exhibitions/_archive_lessons_1_5_rerecord
PORT_EXHIBITION=8765

mkdir -p extended_exhibitions collections "$ARCHIVE_DIR" ambient-study-japanese-reflections/five-lesson-reflections

{
  echo "START $(date -Iseconds)"
  echo "Overnight: Lessons 1–5 extended exhibition rerecord, then Components L101–153"

  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  # --- Phase 1: Lessons 1–5 extended exhibition ---
  echo "==== Archive previous Lessons 1–5 exhibition $(date -Iseconds) ===="
  STAMP=$(date +%Y%m%d_%H%M)
  for f in "$OUT_PROTOTYPE" "$OUT_EXHIBITION"; do
    if [[ -f "$f" ]]; then
      base=$(basename "$f")
      dest="$ARCHIVE_DIR/${base%.mp4}_${STAMP}.mp4"
      cp -f "$f" "$dest"
      echo "archived $f → $dest"
    fi
  done
  rm -rf ambient-study-japanese-reflections/five-lesson-reflections/.tmp_lessons_1_5_prototype

  echo "==== Rebuild Lessons 1–5 prototype JSON (fresh imageRev) $(date -Iseconds) ===="
  "$PY" -u scripts/build_lessons_1_5_prototype.py

  echo "==== Record Lessons 1–5 Exhibition (~51 min) port=$PORT_EXHIBITION $(date -Iseconds) ===="
  if "$PY" -u scripts/record_japanese_reflections_exhibition.py \
      lessons_1_5_prototype --rebuild --port "$PORT_EXHIBITION"; then
    ls -lh "$OUT_EXHIBITION"
    echo "OK Lessons 1–5 exhibition $(date -Iseconds)"
  else
    echo "FAIL Lessons 1–5 record (exit $?) $(date -Iseconds)"
    echo "Aborting components queue so the failure stays visible."
    echo "DONE $(date -Iseconds) (failed at exhibition)"
    exit 1
  fi

  # --- Phase 2: Components L101–153 ---
  echo "==== Hand off to Components L101–153 $(date -Iseconds) ===="
  bash scripts/run_kanji_components_l101_153.sh

  echo "OVERNIGHT_DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
