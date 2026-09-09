#!/usr/bin/env bash
# Overnight: Heisig gallery (artwork + Foundations music only) for Lessons 25–46.
#
# YouTube / Playwright uses PNG production masters (studies_png/), not website JPEGs.
# Sequential so Chromium stays stable. ~22 × 8 min ≈ 3 hours of finished video.
#
# Idempotent: an MP4 that already exists is skipped (resume after a partial run).
#
# Start with:
#   nohup bash scripts/run_overnight_gallery_l25_46.sh \
#     > /tmp/overnight_gallery_l25_46.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_overnight_gallery_l25_46.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=($(seq 25 46))
PREFLIGHT_PORT=8776

{
  echo "START $(date -Iseconds)"
  echo "Overnight: Gallery Lessons 25–46 (PNG masters, images + music only)"

  echo "==== Fetch self-hosted fonts $(date -Iseconds) ===="
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  echo "==== Rebuild gallery collections 25–46 $(date -Iseconds) ===="
  png_ok=1
  for n in "${LESSONS[@]}"; do
    if ! "$PY" -u scripts/build_lesson_gallery.py --lesson "$n"; then
      echo "FAIL rebuild L$n"
      png_ok=0
    fi
  done
  if [[ "$png_ok" -ne 1 ]]; then
    echo "ABORT: gallery rebuild failed — not starting overnight recordings"
    echo "DONE (aborted) $(date -Iseconds)"
    exit 1
  fi

  echo "==== Font + PNG pipeline preflight $(date -Iseconds) ===="
  if ! "$PY" -u scripts/preflight_recording_fonts.py \
        --collection lesson_25_gallery \
        --port "$PREFLIGHT_PORT" \
        --png-pipeline; then
    echo "ABORT: font/PNG preflight failed — not starting overnight recordings"
    echo "DONE (aborted) $(date -Iseconds)"
    exit 1
  fi

  failed=0
  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    mkdir -p "collections/lesson_${nn}"
    out="collections/lesson_${nn}/gallery_lesson_${nn}.mp4"
    if [[ -f "$out" ]]; then
      echo "==== SKIP L$n gallery (exists: $out) $(date -Iseconds) ===="
      ls -lh "$out"
      continue
    fi
    port=$((8800 + n))
    echo "==== LESSON $n gallery  port=$port  $(date -Iseconds) ===="
    if "$PY" -u scripts/record_lesson_gallery.py --lesson "$n" --rebuild --port "$port"; then
      ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
      if [[ ! -f "$out" ]]; then
        echo "FAIL L$n — MP4 missing after record $(date -Iseconds)"
        failed=1
      fi
    else
      echo "FAIL L$n gallery (exit $?) $(date -Iseconds)"
      failed=1
    fi
  done

  if [[ "$failed" -eq 1 ]]; then
    echo "DONE $(date -Iseconds) (with failures)"
    exit 1
  fi
  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
