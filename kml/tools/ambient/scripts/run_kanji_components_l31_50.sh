#!/usr/bin/env bash
# Components-only: Lessons 31–50.
#
# Outputs: collections/lesson_NN/components_lesson_NN.mp4
# Log:     collections/record_kanji_components_l31_50.log
#
# Start with:
#   nohup bash scripts/run_kanji_components_l31_50.sh \
#     > /tmp/kanji_components_l31_50.nohup.out 2>&1 &
#
# Or after the L25 full-stage queue:
#   nohup bash scripts/run_overnight_l25_then_components_l31_50.sh \
#     > /tmp/overnight_l25_l31_50.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_kanji_components_l31_50.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=($(seq 31 50))
PORT_BASE=9831

{
  echo "START $(date -Iseconds)"
  echo "Components-only queue: L31–50"

  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  # Clear any stale tmp dirs for this range
  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    rm -rf "collections/lesson_${nn}/.tmp_components_lesson_${nn}"
  done

  echo "==== Rebuild Kanji Components JSON from HTML (through L50) $(date -Iseconds) ===="
  "$PY" -u scripts/build_kanji_components.py --rebuild-html-db --max-lesson 50

  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    mkdir -p "collections/lesson_${nn}"
    out="collections/lesson_${nn}/components_lesson_${nn}.mp4"
    if [[ -f "$out" ]]; then
      echo "==== SKIP L$n components (exists: $out) $(date -Iseconds) ===="
      continue
    fi
    port=$((PORT_BASE + n))
    echo "==== LESSON $n / components  port=$port  $(date -Iseconds) ===="
    if "$PY" -u scripts/record_lesson_components.py --lesson "$n" --port "$port"; then
      ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
    else
      echo "FAIL L$n / components (exit $?) — continuing queue"
    fi
  done

  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
