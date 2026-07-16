#!/usr/bin/env bash
# Grade 3 stroke order part 5 (25 kanji): 真 → 注 · ~8:48
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building stroke-order collection (Grade 3 part 5) ──"
python3 scripts/build_grade_3_stroke_order_exhibition.py --part 5

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_3_strokes_05"

echo ""
echo "── OBS recording (Grade 3 stroke order 5) ──"
echo "  Bookend: kml/assets/images/grade_3_stroke_orders_5.png"
echo "  1. ./serve.sh ${PORT}"
echo "  2. ${URL}"
echo "  3. Audio: grade_3_kanji_minus3db.mp3"
echo "  Kanji: 25 (真 → 注) · joyo order"
echo "  Save as: collections/grade_3/grade_3_strokes_05.mp4"
echo ""
