#!/usr/bin/env bash
# After Kanji Components L6–8 finishes, record Lessons 9–10.
# HTML for L9–10 was manually reviewed (Phase 1 H/V). Rebuild JSON from HTML,
# archive older MP4s, then record.
#
# Outputs: collections/lesson_NN/components_lesson_NN.mp4
# Log:     collections/record_kanji_components_l09_10_after_l06_08.log
#
# Start with:
#   nohup bash scripts/run_kanji_components_l09_10_after_l06_08.sh \
#     > /tmp/kanji_components_l09_10.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

PRIOR_LOG=collections/record_kanji_components_l06_08_after_l01_05.log
LOG=collections/record_kanji_components_l09_10_after_l06_08.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=(9 10)
PORT_BASE=9780

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
  for n in 6 7 8; do
    nn=$(printf '%02d' "$n")
    [[ -f "collections/lesson_${nn}/components_lesson_${nn}.mp4" ]] || return 1
  done
  return 0
}

prior_recorders_idle() {
  ! real_proc 'scripts/record_lesson_components\.py --lesson [6-8](\s|$)' \
    && ! real_proc 'run_kanji_components_l06_08_after_l01_05'
}

{
  echo "START $(date -Iseconds)"
  echo "Waiting for Kanji Components L6–8 DONE …"

  while true; do
    if prior_outputs_ready && rg -q '^DONE ' "$PRIOR_LOG" 2>/dev/null && prior_recorders_idle; then
      echo "Kanji Components L6–8 DONE spotted $(date -Iseconds)"
      break
    fi
    echo "waiting for Components L6–8… $(date -Iseconds)"
    sleep 60
  done

  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  STAMP=$(date +%Y%m%d_%H%M)
  mkdir -p collections/_archive_components_pre_l09_10_rerecord
  echo "==== Archive prior L9–10 component MP4s $(date -Iseconds) ===="
  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    out="collections/lesson_${nn}/components_lesson_${nn}.mp4"
    if [[ -f "$out" ]]; then
      dest="collections/_archive_components_pre_l09_10_rerecord/components_lesson_${nn}_${STAMP}.mp4"
      mv "$out" "$dest"
      echo "archived $out -> $dest"
    fi
  done

  echo "==== Rebuild Kanji Components JSON from HTML (through L10) $(date -Iseconds) ===="
  "$PY" -u scripts/build_kanji_components.py --rebuild-html-db --max-lesson 10

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
