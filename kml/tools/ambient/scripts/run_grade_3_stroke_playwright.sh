#!/usr/bin/env bash
# Grade 3 Stroke Order (8 × 25 kanji): Playwright capture.
set -euo pipefail
cd "$(dirname "$0")/.."

export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"

PYTHON=python3
if [[ -x .venv/bin/python ]]; then
  PYTHON=.venv/bin/python
fi

if ! "$PYTHON" -c "import playwright" 2>/dev/null; then
  echo "Installing playwright …"
  "$PYTHON" -m pip install playwright -q
  "$PYTHON" -m playwright install chromium
fi

if ! compgen -G ".playwright-browsers/chromium_headless_shell-*" >/dev/null; then
  "$PYTHON" -m playwright install chromium
fi

PORT="${1:-8771}"

echo "── Rebuild Grade 3 stroke-order collections ──"
"$PYTHON" scripts/build_grade_3_stroke_order_exhibition.py --all

echo ""
echo "── Playwright recording (parts 1–8) ──"
"$PYTHON" scripts/record_grade_3_stroke_order.py --all --port "$PORT"

echo ""
echo "Done. Outputs:"
for part in 1 2 3 4 5 6 7 8; do
  printf "  %02d" "$part"
  echo ": collections/grade_3/grade_3_strokes_${part}.mp4"
done
