#!/usr/bin/env bash
# Grade 4 Stroke Order (8 parts): Playwright capture.
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

PORT="${1:-8773}"
IMAGES_DIR="$(readlink -f assets/images)"

echo "── Bookend images (grade_4_stroke_orders_1–8.png) ──"
for part in $(seq 1 8); do
  dest="${IMAGES_DIR}/grade_4_stroke_orders_${part}.png"
  if [[ -f "$dest" ]]; then
    echo "  grade_4_stroke_orders_${part}.png ✓"
  else
    echo "  warning: missing grade_4_stroke_orders_${part}.png" >&2
  fi
done

echo ""
echo "── Rebuild Grade 4 stroke-order collections ──"
"$PYTHON" scripts/build_grade_4_stroke_order_exhibition.py --all

echo ""
echo "── Playwright recording (parts 1–8) ──"
"$PYTHON" scripts/record_grade_4_stroke_order.py --all --port "$PORT"

echo ""
echo "Done. Outputs:"
for part in 1 2 3 4 5 6 7 8; do
  printf "  %02d" "$part"
  echo ": collections/grade_4/grade_4_strokes_${part}.mp4"
done
