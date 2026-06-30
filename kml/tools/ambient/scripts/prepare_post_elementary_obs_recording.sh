#!/usr/bin/env bash
# Build 100-kanji OBS take: jr_high_1 + jr_high_2 looped A-B-A-B (2 cycles).
# Video 2 will use different tracks — do not overwrite this MP3 when adding jr_high_03/4.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── Building soundtrack (A→B→A→B) + 100-kanji collection ──"
python3 scripts/build_post_elementary_soundtrack.py \
  --part 1 \
  --cycles 2 \
  --render-soundtrack \
  --kanji-per-part 100

PORT="${1:-8765}"
URL="http://localhost:${PORT}/exhibition.html?collection=post_elementary_01"

echo ""
echo "── OBS recording (Video 1) ──"
echo "  1. ./serve.sh ${PORT}   (separate terminal)"
echo "  2. Browser: fullscreen 1920×1080"
echo "     ${URL}"
echo "  3. Click once if autoplay gate appears (or Space after load)"
echo "  4. OBS: Display Capture or Window Capture (browser), 1920×1080"
echo "  5. Audio: capture browser/desktop audio OR mux jr_high_soundtrack.mp3 in post"
echo "  6. Record ~10 min (soundtrack ${URL%%\?*} → audio/jr_high_soundtrack.mp3 is ~9:46)"
echo ""
echo "  Kanji: 100 (冒 → 迫) @ 4.0s each · content ~6:40 · A-B-A-B loop"
echo "  Save as: post_elementary_exhibitions/post_elementary_01_obs.mp4 (suggested)"
echo ""
