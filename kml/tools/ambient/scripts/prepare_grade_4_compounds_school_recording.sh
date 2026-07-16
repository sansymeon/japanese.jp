#!/usr/bin/env bash
# Grade 4 熟語 (10 parts from jukugo list): Playwright capture + loudness normalize.
set -euo pipefail
cd "$(dirname "$0")/.."

export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"

PYTHON=python3
if [[ -x .venv/bin/python ]]; then
  PYTHON=.venv/bin/python
fi

PORT="${1:-8772}"
IMAGES_DIR="$(readlink -f assets/images)"

echo "── Bookend images (grade_4_jukugo_1–10.png, one per part) ──"
for part in $(seq 1 10); do
  dest="${IMAGES_DIR}/grade_4_jukugo_${part}.png"
  if [[ -f "$dest" ]]; then
    echo "  grade_4_jukugo_${part}.png ✓"
  else
    echo "  warning: missing grade_4_jukugo_${part}.png" >&2
  fi
done

echo ""
echo "── Rebuild Grade 4 compounds collections ──"
"$PYTHON" scripts/build_grade_4_compounds_school.py --all --full

echo ""
echo "── Playwright recording (parts 1–10) ──"
"$PYTHON" scripts/record_grade_4_compounds_school.py --all --port "$PORT"

echo ""
echo "── Loudness normalize (−17 LUFS) ──"
"$PYTHON" scripts/normalize_collection_audio.py collections/grade_4/grade_4_jukugo_*.mp4

echo ""
echo "Done. Outputs:"
for part in $(seq 1 10); do
  echo "  collections/grade_4/grade_4_jukugo_${part}.mp4"
done
