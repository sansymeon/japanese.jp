#!/usr/bin/env bash
# Record extended exhibitions overnight (~3 h, Playwright).
#   extended_exhibitions/lessons_1_5_prototype.mp4
#   extended_exhibitions/lesson_01-05_verses.mp4
#   extended_exhibitions/lessons_6_10_prototype.mp4
# Heart v5 is recorded manually (see serve.sh) — skipped by default.
# Log: extended_exhibitions/record_overnight.log
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p extended_exhibitions heart_exhibitions
if ! command -v ffmpeg >/dev/null; then
  echo "ffmpeg is required." >&2
  exit 1
fi
VENV_PYTHON=".venv/bin/python"
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  .venv/bin/playwright install chromium
fi
if [[ ! -d .playwright-browsers/chromium_headless_shell-* ]]; then
  .venv/bin/playwright install chromium
fi
exec "$VENV_PYTHON" scripts/record_overnight_exhibitions.py --rebuild --skip-heart "$@"
