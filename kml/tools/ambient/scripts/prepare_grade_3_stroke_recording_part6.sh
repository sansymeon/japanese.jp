#!/usr/bin/env bash
# Grade 3 stroke order part 6 (25 kanji): 柱 → 箱 · ~8:59
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building stroke-order collection (Grade 3 part 6) ──"
python3 scripts/build_grade_3_stroke_order_exhibition.py --part 6

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_3_strokes_06"

echo ""
echo "── OBS recording (Grade 3 stroke order 6) ──"
echo "  Bookend: kml/assets/images/grade_3_stroke_orders_6.png"
echo "  1. ./serve.sh ${PORT}"
echo "  2. ${URL}"
echo "  3. Audio: grade_3_kanji_minus3db.mp3"
echo "  Kanji: 25 (柱 → 箱) · joyo order"
echo "  Save as: collections/grade_3/grade_3_strokes_06.mp4"
echo ""
