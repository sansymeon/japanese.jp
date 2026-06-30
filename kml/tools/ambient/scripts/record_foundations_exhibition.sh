#!/usr/bin/env bash
# Record Study Exhibition MP4s (Presentation Mode / capture=1).
# Output: foundations_exhibitions/lesson_XX_foundations.mp4 (gitignored)
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null; then
  echo "ffmpeg is required." >&2
  exit 1
fi

if ! python3 -c "import playwright" 2>/dev/null; then
  echo "Installing playwright …"
  pip install playwright
  playwright install chromium
fi

python3 scripts/record_foundations_exhibition.py "$@"
