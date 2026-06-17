#!/usr/bin/env bash
# Record Heart v5 exhibition MP4 (Gallery Guardian). Output: heart_exhibitions/heart_v5.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p heart_exhibitions
if ! command -v ffmpeg >/dev/null; then
  echo "ffmpeg is required." >&2
  exit 1
fi
VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  .venv/bin/playwright install chromium
fi
exec "$VENV_PYTHON" scripts/record_heart_exhibition.py --rebuild "$@"
