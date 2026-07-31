#!/usr/bin/env bash
# After Kanji Components L1–5 finishes, rebuild + record Lessons 6–10.
#
# Outputs: collections/lesson_0N/components_lesson_0N.mp4
# Log:     collections/record_kanji_components_l06_10_after_l01_05.log
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

PRIOR_LOG=collections/record_kanji_components_l01_05_after_16_20.log
LOG=collections/record_kanji_components_l06_10_after_l01_05.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=(6 7 8 9 10)
PORT_BASE=9790

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

prior_outputs_ready() {
  local n nn
  for n in 1 2 3 4 5; do
    nn=$(printf '%02d' "$n")
    [[ -f "collections/lesson_${nn}/components_lesson_${nn}.mp4" ]] || return 1
  done
  return 0
}

prior_recorders_idle() {
  ! real_proc 'scripts/record_lesson_components\.py --lesson [1-5](\s|$)' \
    && ! real_proc 'scripts/run_kanji_components_l01_05_after_lessons_16_20\.sh'
}

{
  echo "START $(date -Iseconds)"
  echo "Waiting for Kanji Components L1–5 DONE …"

  while true; do
    if prior_outputs_ready && rg -q '^DONE ' "$PRIOR_LOG" 2>/dev/null && prior_recorders_idle; then
      echo "Kanji Components L1–5 DONE spotted $(date -Iseconds)"
      break
    fi
    echo "waiting for Components L1–5… $(date -Iseconds)"
    sleep 60
  done

  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  echo "==== Rebuild Kanji Components JSON (L1–16) $(date -Iseconds) ===="
  "$PY" -u scripts/build_kanji_components.py

  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
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
