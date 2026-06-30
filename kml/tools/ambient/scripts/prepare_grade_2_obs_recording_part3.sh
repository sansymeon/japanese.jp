#!/usr/bin/env bash
# Grade 2 part 3 (40 kanji): soundtrack grade2_3_number_1_minus3db.mp3
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building 40-kanji collection (Grade 2 part 3) ──"
python3 scripts/build_grade_2_soundtrack.py --part 3

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_2_03"

echo ""
echo "── OBS recording (Grade 2 video 3) ──"
echo "  Bookend: kml/assets/images/grade_2_part_3.png (add before recording)"
echo "  1. ./serve.sh ${PORT}"
echo "  2. ${URL}"
echo "  3. Audio: grade2_3_number_1_minus3db.mp3"
echo "  Kanji: 40 (少 → 冬) · joyo order · confetti every 10 kanji"
echo "  Save as: collections/grade_2/grade_2_kanji_3.mp4"
echo ""
