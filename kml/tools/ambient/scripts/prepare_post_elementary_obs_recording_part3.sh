#!/usr/bin/env bash
# Build 100-kanji OBS take (part 3): jr_high_03 + jr_high_4 looped A-B-A-B (2 cycles).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building soundtrack (A→B×2) + 100-kanji collection (part 3) ──"
python3 scripts/build_post_elementary_soundtrack.py \
  --part 3 \
  --offset 200 \
  --cycles 2 \
  --render-soundtrack \
  --kanji-per-part 100

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=post_elementary_03"

echo ""
echo "── OBS recording (Video 3) ──"
echo "  1. ./serve.sh ${PORT}   (separate terminal)"
echo "  2. Browser: fullscreen 1920×1080"
echo "     ${URL}"
echo "  3. Click once if autoplay gate appears (or Space after load)"
echo "  4. OBS: Display Capture or Window Capture (browser), 1920×1080"
echo "  5. Audio: capture browser/desktop audio OR mux audio/jr_high_soundtrack_03.mp3 in post"
echo "  6. Record ~10 min (soundtrack → audio/jr_high_soundtrack_03.mp3 is ~9:46)"
echo ""
echo "  Kanji: 100 (韻 → 拐) @ 4.0s each · content ~6:40 · A-B×2 loop"
echo "  Save as: collections/post_elementary/jr_high_kanji_3.mp4 (suggested)"
echo ""
