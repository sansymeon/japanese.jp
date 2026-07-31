#!/usr/bin/env bash
# After Lessons 11–15 Exhibition finishes, rebuild + record Lessons 16–20
# (same Japanese Reflections image+verse format).
#
# Output: extended_exhibitions/lessons_16_20_prototype.mp4
#         (also copied to extended_exhibitions/lessons_16_20_exhibition.mp4)
# Log:    extended_exhibitions/record_lessons_16_20_after_11_15.log
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

PRIOR_LOG=extended_exhibitions/record_lessons_11_15_after_6_10.log
PRIOR_MP4=extended_exhibitions/lessons_11_15_prototype.mp4
PRIOR_ALT=extended_exhibitions/lessons_11_15_exhibition.mp4
LOG=extended_exhibitions/record_lessons_16_20_after_11_15.log
OUT_PROTOTYPE=extended_exhibitions/lessons_16_20_prototype.mp4
OUT_EXHIBITION=extended_exhibitions/lessons_16_20_exhibition.mp4
PORT=8772
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p extended_exhibitions

real_proc() {
  local pat=$1 line
  while IFS= read -r line; do
    case "$line" in
      *cursorsandbox*|*COMMAND_EXIT_CODE*|*AGENT_LOOP*|*pgrep*) continue ;;
    esac
    return 0
  done < <(pgrep -af "$pat" 2>/dev/null || true)
  return 1
}

prior_mp4_ready() {
  [[ -f "$PRIOR_MP4" ]] || [[ -f "$PRIOR_ALT" ]]
}

prior_recorders_idle() {
  ! real_proc 'scripts/record_japanese_reflections_exhibition\.py lessons_11_15' \
    && ! real_proc 'scripts/run_lessons_11_15_after_lessons_6_10\.sh'
}

{
  echo "START $(date -Iseconds)"
  echo "Waiting for Lessons 11–15 Exhibition DONE …"

  while true; do
    if prior_mp4_ready && rg -q '^DONE ' "$PRIOR_LOG" 2>/dev/null && prior_recorders_idle; then
      echo "Lessons 11–15 DONE spotted $(date -Iseconds)"
      break
    fi
    echo "waiting for Lessons 11–15… $(date -Iseconds)"
    sleep 60
  done

  echo "==== Rebuild Lessons 16–20 prototype JSON $(date -Iseconds) ===="
  "$PY" -u scripts/build_lessons_16_20_prototype.py

  echo "==== Record Lessons 16–20 Exhibition (~51 min) $(date -Iseconds) ===="
  if "$PY" -u scripts/record_japanese_reflections_exhibition.py \
      lessons_16_20_prototype --rebuild --port "$PORT"; then
    ls -lh "$OUT_PROTOTYPE"
    cp -f "$OUT_PROTOTYPE" "$OUT_EXHIBITION"
    ls -lh "$OUT_EXHIBITION"
    echo "DONE $(date -Iseconds)"
  else
    echo "FAIL Lessons 16–20 record (exit $?) $(date -Iseconds)"
    exit 1
  fi
} 2>&1 | tee -a "$LOG"
