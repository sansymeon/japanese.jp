#!/usr/bin/env bash
# Serve the ambient player from this directory.
# Requires ./assets -> ../../assets (symlink) so /assets/studies/*.png resolves.
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -e assets/studies ]]; then
  echo "Missing assets link. Run: ln -s ../../assets assets" >&2
  exit 1
fi
if [[ ! -e bookends/lesson_32.png ]]; then
  echo "Missing bookend artwork. Run: ln -s ../../../assets/covers/lesson_32.png bookends/lesson_32.png" >&2
  exit 1
fi
PORT="${1:-8765}"
echo "Study L38:   http://localhost:${PORT}/index.html?collection=lesson_38_study"
echo "Study L39:   http://localhost:${PORT}/index.html?collection=lesson_39_study"
echo "Study L40:   http://localhost:${PORT}/index.html?collection=lesson_40_study"
echo "Study L41:   http://localhost:${PORT}/index.html?collection=lesson_41_study"
echo "Heart Expo:  http://localhost:${PORT}/exhibition.html?collection=heart_v5"
python3 -m http.server "$PORT"
