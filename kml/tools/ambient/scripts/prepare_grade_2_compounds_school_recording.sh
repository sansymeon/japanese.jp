#!/usr/bin/env bash
# Grade 2 熟語 (8 × 20 kanji): Playwright capture + loudness normalize.
set -euo pipefail
cd "$(dirname "$0")/.."

export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"

PYTHON=python3
if [[ -x .venv/bin/python ]]; then
  PYTHON=.venv/bin/python
fi

PORT="${1:-8770}"
IMAGES_DIR="$(readlink -f assets/images)"

echo "── Bookend placeholders (replace with grade_2_jukugo_*.png art when ready) ──"
link_bookend() {
  local part="$1" target="$2"
  local link="${IMAGES_DIR}/grade_2_jukugo_${part}.png"
  if [[ -f "${IMAGES_DIR}/${target}" ]]; then
    ln -sfn "${target}" "${link}"
    echo "  grade_2_jukugo_${part}.png → ${target}"
  else
    echo "  warning: missing ${target} for part ${part}" >&2
  fi
}
link_bookend 1 grade_2_stroke_orders_1.png
link_bookend 2 grade_2_kakijun_2.png
link_bookend 3 grade_2_stroke_orders_3.png
link_bookend 4 grade_2_stroke_orders_4.png
link_bookend 5 grade_2_stroke_orders_5.png
link_bookend 6 grade_2_stroke_orders_6.png
link_bookend 7 grade_2_stroke_orders_7.png
link_bookend 8 grade_2_stroke_orders_8.png

echo ""
echo "── Rebuild Grade 2 compounds collections ──"
"$PYTHON" scripts/build_grade_2_compounds_school.py --all

echo ""
echo "── Playwright recording (parts 1–8) ──"
"$PYTHON" scripts/record_grade_2_compounds_school.py --all --port "$PORT"

echo ""
echo "── Loudness normalize (−17 LUFS) ──"
"$PYTHON" scripts/normalize_collection_audio.py collections/grade_2/grade_2_jukugo_*.mp4

echo ""
echo "Done. Outputs:"
for part in 1 2 3 4 5 6 7 8; do
  echo "  collections/grade_2/grade_2_jukugo_${part}.mp4"
done
