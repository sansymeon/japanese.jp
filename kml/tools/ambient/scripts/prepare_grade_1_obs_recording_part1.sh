#!/usr/bin/env bash
# Build 40-kanji OBS take (Grade 1 part 1): soundtrack grade_1_kanji_minus3db.mp3.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building soundtrack + 40-kanji collection (Grade 1 part 1) ──"
python3 scripts/build_grade_1_soundtrack.py \
  --part 1 \
  --offset 0 \
  --kanji-per-part 40 \
  --render-soundtrack

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=grade_1_01"

echo ""
echo "── OBS recording (Grade 1 video 1) ──"
echo "  1. ./serve.sh ${PORT}   (separate terminal)"
echo "  2. Browser: fullscreen 1920×1080"
echo "     ${URL}"
echo "  3. Click once if autoplay gate appears (or Space after load)"
echo "  4. OBS: Display Capture or Window Capture (browser), 1920×1080"
echo "  5. Audio: capture browser/desktop audio OR mux audio/grade_1_kanji_minus3db.mp3 in post"
echo "  6. Record ~5 min · trim ~18–20s from head after recording"
echo ""
echo "  Kanji: 40 (一 → 森) · confetti every 10 kanji"
echo "  Opening: 3s black lead → grade_1 hero → music ~2.5s after image"
echo "  Closing: grade_1 hero holds through music → fade to black"
echo "  Save as: collections/grade_1/grade_1_kanji_1.mp4 (suggested)"
echo ""
