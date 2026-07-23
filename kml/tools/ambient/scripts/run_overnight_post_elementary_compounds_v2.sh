#!/usr/bin/env bash
# Overnight: Playwright recordings for Post-Elementary Compounds Volume 2 (parts 1–22).
# Log: collections/post_elementary/volume2_recordings.log
#
# Usage:
#   scripts/run_overnight_post_elementary_compounds_v2.sh
#   scripts/run_overnight_post_elementary_compounds_v2.sh --from 5 --to 22
#   scripts/run_overnight_post_elementary_compounds_v2.sh --skip-existing
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/playwright-browsers"
# Prefer local .playwright-browsers (Vol1 pattern)
if [[ -d "$(pwd)/.playwright-browsers" ]]; then
  export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
fi

FROM=1
TO=22
SKIP_EXISTING=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --from) FROM="$2"; shift 2 ;;
    --to) TO="$2"; shift 2 ;;
    --skip-existing) SKIP_EXISTING=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

mkdir -p collections/post_elementary
LOG=collections/post_elementary/volume2_recordings.log

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  .venv/bin/playwright install chromium
fi
if ! compgen -G "${PLAYWRIGHT_BROWSERS_PATH}/chromium_headless_shell-*" >/dev/null \
   && ! compgen -G "${PLAYWRIGHT_BROWSERS_PATH}/chromium-*" >/dev/null; then
  .venv/bin/playwright install chromium
fi

exec > >(tee -a "$LOG") 2>&1
echo "=== PE Compounds Vol. 2 overnight recordings started $(date -Iseconds) ==="
echo "Parts ${FROM}–${TO}  skip_existing=${SKIP_EXISTING}  browsers=${PLAYWRIGHT_BROWSERS_PATH}"

failed=0
for n in $(seq "$FROM" "$TO"); do
  nn=$(printf '%02d' "$n")
  out="collections/post_elementary/post_elementary_compounds_v2_${nn}.mp4"
  if [[ "$SKIP_EXISTING" -eq 1 && -f "$out" ]]; then
    echo "=== SKIP PART $n (exists: $out) === $(date -Iseconds) ==="
    continue
  fi
  echo "=== RECORDING PART $n === $(date -Iseconds) ==="
  if ! "$VENV_PYTHON" -u scripts/record_post_elementary_compounds_v2.py --part "$n" --port $((8910 + n)); then
    echo "=== FAILED PART $n === $(date -Iseconds) ==="
    failed=$((failed + 1))
  else
    ls -lh "$out" || true
  fi
done

echo "=== PE Compounds Vol. 2 overnight recordings finished $(date -Iseconds) ==="
echo "Failed parts: $failed"
exit "$failed"
