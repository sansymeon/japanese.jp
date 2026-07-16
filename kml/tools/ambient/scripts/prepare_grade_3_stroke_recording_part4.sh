#!/usr/bin/env bash
# Grade 3 stroke order part 4 (25 kanji): 守 → 神 · ~8:34
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building stroke-order collection (Grade 3 part 4) ──"
python3 scripts/build_grade_3_stroke_order_exhibition.py --part 4

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_3_strokes_04"

echo ""
echo "── OBS recording (Grade 3 stroke order 4) ──"
echo "  Bookend: kml/assets/images/grade_3_stroke_orders_4.png"
echo "  1. ./serve.sh ${PORT}"
echo "  2. ${URL}"
echo "  3. Audio: grade_3_kanji_minus3db.mp3"
echo "  Kanji: 25 (守 → 神) · joyo order"
echo "  Save as: collections/grade_3/grade_3_strokes_04.mp4"
echo ""
