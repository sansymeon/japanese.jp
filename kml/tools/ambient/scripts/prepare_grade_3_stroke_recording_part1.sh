#!/usr/bin/env bash
# Grade 3 stroke order part 1 (25 kanji): 悪 → 漢 · ~9:00
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building stroke-order collection (Grade 3 part 1) ──"
python3 scripts/build_grade_3_stroke_order_exhibition.py --part 1

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_3_strokes_01"

echo ""
echo "── OBS recording (Grade 3 stroke order 1) ──"
echo "  Bookend: kml/assets/images/grade_3_stroke_orders_1.png"
echo "  1. ./serve.sh ${PORT}"
echo "  2. ${URL}"
echo "     (wait for page load — handwritten fonts preload before playback)"
echo "  3. Audio: grade_3_kanji_minus3db.mp3"
echo "  Kanji: 25 (悪 → 漢) · joyo order · recognition → strokes → recognition"
echo "  Save as: collections/grade_3/grade_3_strokes_01.mp4"
echo ""
