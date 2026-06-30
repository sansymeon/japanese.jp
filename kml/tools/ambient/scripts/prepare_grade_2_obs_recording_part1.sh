#!/usr/bin/env bash
# Grade 2 part 1 (40 kanji): soundtrack grade2_3_number_1_minus3db.mp3
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building 40-kanji collection (Grade 2 part 1) ──"
python3 scripts/build_grade_2_soundtrack.py --part 1

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_2_01"

echo ""
echo "── OBS recording (Grade 2 video 1) ──"
echo "  Bookend: kml/assets/images/grade_2_part_1.png"
echo "  1. ./serve.sh ${PORT}"
echo "  2. ${URL}"
echo "  3. Audio: grade2_3_number_1_minus3db.mp3"
echo "  Kanji: 40 (引 → 原) · joyo order · confetti every 10 kanji"
echo "  Save as: collections/grade_2/grade_2_kanji_1.mp4"
echo ""
