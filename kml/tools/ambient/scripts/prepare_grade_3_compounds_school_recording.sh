#!/usr/bin/env bash
# Grade 3 熟語 (10 × 20 kanji): Playwright capture + loudness normalize.
set -euo pipefail
cd "$(dirname "$0")/.."

export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"

PYTHON=python3
if [[ -x .venv/bin/python ]]; then
  PYTHON=.venv/bin/python
fi

PORT="${1:-8770}"
IMAGES_DIR="$(readlink -f assets/images)"

echo "── Bookend images (grade_3_jukugo_*.png, one per part) ──"
THUMBS_DIR="$(readlink -f ../../assets/youtube_thumbnails)"
install_bookend() {
  local part="$1"
  local dest="${IMAGES_DIR}/grade_3_jukugo_${part}.png"
  local src=""
  if [[ "$part" == "1" && -f "${THUMBS_DIR}/grade_３_jukugo_1.png" ]]; then
    src="${THUMBS_DIR}/grade_３_jukugo_1.png"
  elif [[ -f "${THUMBS_DIR}/grade_3_jukugo_${part}.png" ]]; then
    src="${THUMBS_DIR}/grade_3_jukugo_${part}.png"
  elif [[ -f "$dest" && ! -L "$dest" ]]; then
    echo "  grade_3_jukugo_${part}.png (existing)"
    return
  fi
  if [[ -n "$src" ]]; then
    rm -f "$dest"
    cp -f "$src" "$dest"
    echo "  grade_3_jukugo_${part}.png ← $(basename "$src")"
  elif [[ -f "$dest" ]]; then
    echo "  grade_3_jukugo_${part}.png (symlink kept)"
  else
    echo "  warning: missing grade_3_jukugo_${part}.png" >&2
  fi
}
for part in $(seq 1 10); do
  install_bookend "$part"
done

echo ""
echo "── Rebuild Grade 3 compounds collections ──"
"$PYTHON" scripts/build_grade_3_compounds_school.py --all

echo ""
echo "── Playwright recording (parts 1–10) ──"
"$PYTHON" scripts/record_grade_3_compounds_school.py --all --port "$PORT"

echo ""
echo "── Loudness normalize (−17 LUFS) ──"
"$PYTHON" scripts/normalize_collection_audio.py collections/grade_3/grade_3_jukugo_*.mp4

echo ""
echo "Done. Outputs:"
for part in 1 2 3 4 5 6 7 8 9 10; do
  echo "  collections/grade_3/grade_3_jukugo_${part}.mp4"
done
