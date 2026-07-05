#!/usr/bin/env bash
# Grade 3 part 3 (50 kanji): soundtrack grade_3_kanji_minus3db.mp3
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building 50-kanji collection (Grade 3 part 3) ──"
python3 scripts/build_grade_3_soundtrack.py --part 3

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_3_03"

echo ""
echo "── OBS recording (Grade 3 video 3) ──"
echo "  Bookend: kml/assets/images/grade_3_part_3.png"
echo "  1. ./serve.sh ${PORT}"
echo "  2. ${URL}"
echo "  3. Audio: grade_3_kanji_minus3db.mp3"
echo "  Kanji: 50 (真 → 箱) · joyo order · confetti every 10 kanji"
echo "  Save as: collections/grade_3/grade_3_kanji_3.mp4"
echo ""
