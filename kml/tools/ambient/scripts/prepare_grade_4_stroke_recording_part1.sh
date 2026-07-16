#!/usr/bin/env bash
# Grade 4 stroke order part 1 (25 kanji): 愛 → …
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building stroke-order collection (Grade 4 part 1) ──"
python3 scripts/build_grade_4_stroke_order_exhibition.py --part 1

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_4_strokes_01"

echo ""
echo "── OBS / Playwright recording (Grade 4 stroke order 1) ──"
echo "  Bookend: assets/images/grade_4_stroke_orders_1.png"
echo "  1. ./serve.sh ${PORT}"
echo "  2. ${URL}"
echo "     (wait for page load — handwritten fonts preload before playback)"
echo "  3. Audio: grade_4_parts_1_3_minus3db.mp3"
echo "  Save as: collections/grade_4/grade_4_strokes_01.mp4"
echo "  Or: python3 scripts/record_grade_4_stroke_order.py --part 1 --port ${PORT}"
echo ""
