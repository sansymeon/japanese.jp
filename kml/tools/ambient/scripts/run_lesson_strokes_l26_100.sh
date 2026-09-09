#!/usr/bin/env bash
# Stroke-order only: Lessons 26–100 (content-bounded crest close).
#
# Safeguards:
#   * Self-hosted fonts fetched, then a hard Playwright font preflight runs
#     before any capture. On load/fallback failure the whole queue aborts.
#   * Each recorder also re-runs Noto Serif JP + Yuji Syuku gates at capture time.
#   * Idempotent + resumable: existing strokes_lesson_NN.mp4 is skipped.
#   * Non-fatal per lesson after preflight: one failure is logged; queue continues.
#   * --rebuild refreshes JSON (crest ending, content-bounded runtime).
#
# Outputs: collections/lesson_NN/strokes_lesson_NN.mp4
# Log:     collections/record_lesson_strokes_l26_100.log
#
# Start overnight with:
#   nohup bash scripts/run_lesson_strokes_l26_100.sh \
#     > /tmp/lesson_strokes_l26_100.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_lesson_strokes_l26_100.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=($(seq 26 100))
PORT_BASE=9226
PREFLIGHT_PORT=8770
PREFLIGHT_LESSON=26

{
  echo "START $(date -Iseconds)"
  echo "Stroke-order queue: L26–100 (crest close; content-bounded; existing MP4s skipped)"

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
      echo "==== SKIP L$n strokes (exists: $out) $(date -Iseconds) ===="
      continue
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
        # Content-bounded strokes ≈ 11–14 min; full bed is ~18:20 (1100s).
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
