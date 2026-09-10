#!/usr/bin/env bash
# After run_kanji_components_l24_30.sh writes DONE, retry any missing L24–30 MP4s.
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_kanji_components_l24_30.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

{
  echo "RETRY_WAITER START $(date -Iseconds)"

  while ! rg -q '^DONE ' "$LOG" 2>/dev/null; do
    sleep 30
  done

  # Wait until the main queue's recorder process is gone (match argv, not this script).
  while true; do
    if pgrep -f '[r]ecord_lesson_components\.py --lesson' >/dev/null 2>&1; then
      sleep 10
    else
      break
    fi
  done

  echo "==== Retry missing L24–30 components $(date -Iseconds) ===="
  for n in 24 25 26 27 28 29 30; do
    nn=$(printf '%02d' "$n")
    out="collections/lesson_${nn}/components_lesson_${nn}.mp4"
    if [[ -f "$out" ]]; then
      echo "==== RETRY SKIP L$n (exists) $(date -Iseconds) ===="
      continue
    fi
    port=$((9900 + n))
    echo "==== RETRY LESSON $n / components  port=$port  $(date -Iseconds) ===="
    rm -rf "collections/lesson_${nn}/.tmp_components_lesson_${nn}"
    if "$PY" -u scripts/record_lesson_components.py --lesson "$n" --port "$port"; then
      ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
      continue
    fi
    echo "RETRY FAIL L$n (exit $?) — trying once more"
    sleep 5
    rm -rf "collections/lesson_${nn}/.tmp_components_lesson_${nn}"
    if "$PY" -u scripts/record_lesson_components.py --lesson "$n" --port "$((port + 50))"; then
      ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
    else
      echo "RETRY FAIL2 L$n (exit $?)"
    fi
  done

  echo "RETRY_WAITER DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
