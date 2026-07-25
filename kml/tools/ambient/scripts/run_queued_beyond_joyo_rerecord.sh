#!/usr/bin/env bash
# Queue: wait for ambient gallery film recorder (if running), then redo Beyond Jōyō
# compounds with updated soundtracks + gold crest. Part 19 first (biáng finale),
# then parts 1–18.
#
# Usage:
#   scripts/run_queued_beyond_joyo_rerecord.sh
#   scripts/run_queued_beyond_joyo_rerecord.sh --wait-pid 310351
#   scripts/run_queued_beyond_joyo_rerecord.sh --no-wait
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/playwright-browsers"
if [[ -d "$(pwd)/.playwright-browsers" ]]; then
  export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
fi

WAIT_PID=""
NO_WAIT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --wait-pid) WAIT_PID="$2"; shift 2 ;;
    --no-wait) NO_WAIT=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

mkdir -p collections/beyond_joyo
LOG=collections/beyond_joyo/recordings.log
VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  .venv/bin/playwright install chromium
fi

exec > >(tee -a "$LOG") 2>&1
echo "=== Beyond Jōyō queued re-record started $(date -Iseconds) ==="

if [[ "$NO_WAIT" -eq 0 ]]; then
  if [[ -z "$WAIT_PID" ]]; then
    WAIT_PID="$(pgrep -f '[.]venv/bin/python -u scripts/record_ambient_gallery_film.py' | head -1 || true)"
  fi
  if [[ -z "$WAIT_PID" ]]; then
    WAIT_PID="$(pgrep -f 'python -u scripts/record_ambient_gallery_film.py' | head -1 || true)"
  fi
  if [[ -n "$WAIT_PID" ]] && kill -0 "$WAIT_PID" 2>/dev/null; then
    echo "Waiting for ambient gallery film recorder pid=$WAIT_PID …"
    while kill -0 "$WAIT_PID" 2>/dev/null; do
      sleep 30
    done
    echo "Ambient recorder finished $(date -Iseconds)"
    # Brief settle so Playwright/ffmpeg release ports & GPU
    sleep 15
  else
    echo "No ambient recorder to wait for (or --no-wait)."
  fi
fi

# Order: 19 first (biáng), then 1–18 full redo
PARTS=(19 $(seq 1 18))
failed=0
for n in "${PARTS[@]}"; do
  nn=$(printf '%02d' "$n")
  out="collections/beyond_joyo/beyond_joyo_compounds_${nn}.mp4"
  echo "=== RECORDING PART $n → $out === $(date -Iseconds) ==="
  if ! "$VENV_PYTHON" -u scripts/record_beyond_joyo_compounds.py --part "$n" --port $((9010 + n)); then
    echo "=== FAILED PART $n === $(date -Iseconds) ==="
    failed=$((failed + 1))
  else
    ls -lh "$out" || true
  fi
done

echo "=== Beyond Jōyō queued re-record finished $(date -Iseconds) ==="
echo "Failed parts: $failed"
exit "$failed"
