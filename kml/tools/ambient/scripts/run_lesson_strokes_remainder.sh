#!/usr/bin/env bash
# Stroke-order remainder overnight:
#   * Force re-record L33–37 (skipped last batch; still full-bed / no crest)
#   * Record L101–153 (never recorded)
#
# Same safeguards as L26–100:
#   * Fetch self-hosted fonts, then hard Playwright font preflight (abort on fail)
#   * Per-capture Noto + Yuji gates
#   * Idempotent for L101–153 (existing MP4 skipped); L33–37 always rebuilt
#   * Non-fatal per lesson after preflight
#
# Outputs: collections/lesson_NN/strokes_lesson_NN.mp4
# Log:     collections/record_lesson_strokes_remainder.log
#
# Start with:
#   nohup bash scripts/run_lesson_strokes_remainder.sh \
#     > /tmp/lesson_strokes_remainder.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_lesson_strokes_remainder.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

# Force-rebuild first (old full-bed endings), then forward remainder.
FORCE_LESSONS=(33 34 35 36 37)
NEW_LESSONS=($(seq 101 153))
PORT_BASE=9300
PREFLIGHT_PORT=8771
PREFLIGHT_LESSON=101

record_one() {
  local n=$1
  local force=${2:-0}
  local nn port out
  nn=$(printf '%02d' "$n")
  mkdir -p "collections/lesson_${nn}"
  out="collections/lesson_${nn}/strokes_lesson_${nn}.mp4"

  if [[ "$force" != "1" && -f "$out" ]]; then
    echo "==== SKIP L$n strokes (exists: $out) $(date -Iseconds) ===="
    return 0
  fi
  if [[ "$force" == "1" && -f "$out" ]]; then
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
      # Content-bounded ≈ 11–17 min; full bed is ~18:20 (1100s).
      if awk "BEGIN { exit !($dur > 1000) }"; then
        echo "WARN L$n duration ${dur}s looks like full-bed pad — inspect ending"
      else
        echo "OK L$n duration $(printf '%.0f' "$dur")s"
      fi
    fi
  else
    echo "FAIL L$n / strokes (exit $?) — continuing queue"
  fi
}

{
  echo "START $(date -Iseconds)"
  echo "Stroke remainder: force L33–37 + new L101–153 (crest close; content-bounded)"

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

  echo "==== Phase 1: force re-record L33–37 $(date -Iseconds) ===="
  for n in "${FORCE_LESSONS[@]}"; do
    record_one "$n" 1
  done

  echo "==== Phase 2: L101–153 $(date -Iseconds) ===="
  for n in "${NEW_LESSONS[@]}"; do
    record_one "$n" 0
  done

  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
