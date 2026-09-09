#!/usr/bin/env bash
# Stroke-order overnight: Lessons 1–25 (crest close; content-bounded).
#
# L1–3 were never recorded; L4–25 still have the old full-bed / no-crest endings.
# This queue force-rebuilds all of them via the shared builder.
#
# Safeguards:
#   * Fetch self-hosted fonts, then hard Playwright font preflight (abort on fail)
#   * Per-capture Noto + Yuji gates
#   * Force replace existing MP4s
#   * Non-fatal per lesson after preflight
#
# Outputs: collections/lesson_NN/strokes_lesson_NN.mp4
# Log:     collections/record_lesson_strokes_l01_25.log
#
# Start with:
#   nohup bash scripts/run_lesson_strokes_l01_25.sh \
#     > /tmp/lesson_strokes_l01_25.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_lesson_strokes_l01_25.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=($(seq 1 25))
PORT_BASE=9100
PREFLIGHT_PORT=8773
PREFLIGHT_LESSON=1

{
  echo "START $(date -Iseconds)"
  echo "Stroke-order queue: L1–25 force re-record (crest close; content-bounded)"

  echo "==== Fetch self-hosted fonts $(date -Iseconds) ===="
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  echo "==== Build preflight collection L${PREFLIGHT_LESSON} $(date -Iseconds) ===="
  "$PY" -u scripts/build_lesson_strokes.py --lesson "$PREFLIGHT_LESSON"

  echo "==== Font preflight (abort whole queue on failure) $(date -Iseconds) ===="
  if ! "$PY" -u scripts/preflight_recording_fonts.py \
      --collection "lesson_$(printf '%02d' "$PREFLIGHT_LESSON")_strokes" \
      --port "$PREFLIGHT_PORT"; then
    echo "ABORT: font preflight failed — not starting overnight stroke recordings"
    echo "DONE (aborted) $(date -Iseconds)"
    exit 1
  fi

  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    mkdir -p "collections/lesson_${nn}"
    out="collections/lesson_${nn}/strokes_lesson_${nn}.mp4"
    if [[ -f "$out" ]]; then
      echo "==== FORCE L$n strokes (removing old MP4) $(date -Iseconds) ===="
      rm -f "$out"
    fi
    rm -rf "collections/lesson_${nn}/.tmp_strokes_lesson_${nn}"
    port=$((PORT_BASE + n))
    echo "==== LESSON $n / strokes  port=$port  $(date -Iseconds) ===="
    if "$PY" -u scripts/record_lesson_strokes.py --lesson "$n" --rebuild --port "$port"; then
      ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
      if [[ -f "$out" ]]; then
        dur=$("$PY" - <<PY
import subprocess
print(float(subprocess.check_output([
  'ffprobe','-v','error','-show_entries','format=duration',
  '-of','default=nk=1:nw=1','$out'
], text=True).strip()))
PY
)
        if awk "BEGIN { exit !($dur > 1000) }"; then
          echo "WARN L$n duration ${dur}s looks like full-bed pad — inspect ending"
        else
          echo "OK L$n duration $(printf '%.0f' "$dur")s"
        fi
      fi
    else
      echo "FAIL L$n / strokes (exit $?) — continuing queue"
    fi
  done

  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
