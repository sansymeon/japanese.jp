#!/usr/bin/env bash
# Serve the review gallery from this directory.
# Creates symlinks to test images + site assets if missing.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -e images ]]; then
  ln -sfn ../../../assets/images/lesson_01_kml_v1_test images
  echo "Linked images → assets/images/lesson_01_kml_v1_test"
fi

if [[ ! -e site_assets ]]; then
  ln -sfn ../../assets/site site_assets
  echo "Linked site_assets → kml/assets/site"
fi

if [[ ! -f images/one.png ]]; then
  echo "ERROR: Test images not found. Expected: assets/images/lesson_01_kml_v1_test/*.png" >&2
  exit 1
fi

PORT="${1:-8770}"
echo "Lesson 01 review:  http://localhost:${PORT}/index.html"
python3 -m http.server "$PORT"
