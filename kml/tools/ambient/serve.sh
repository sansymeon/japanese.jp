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
echo "Exhibit L01:  http://localhost:${PORT}/index.html?collection=lesson_1_study&capture=1"
echo "Exhibit L02:  http://localhost:${PORT}/index.html?collection=lesson_2_study&capture=1"
echo "Exhibit L03:  http://localhost:${PORT}/index.html?collection=lesson_3_study&capture=1"
echo "YouTube L36:  http://localhost:${PORT}/index.html?collection=lesson_36_study"
echo "YouTube L37:  http://localhost:${PORT}/index.html?collection=lesson_37_study"
echo "YouTube L38:  http://localhost:${PORT}/index.html?collection=lesson_38_study"
echo "YouTube L39:  http://localhost:${PORT}/index.html?collection=lesson_39_study"
echo "YouTube L40:  http://localhost:${PORT}/index.html?collection=lesson_40_study"
echo "Exhibit L36:  http://localhost:${PORT}/index.html?collection=lesson_36_study&capture=1"
echo "Exhibit L37:  http://localhost:${PORT}/index.html?collection=lesson_37_study&capture=1"
echo "Exhibit L38:  http://localhost:${PORT}/index.html?collection=lesson_38_study&capture=1"
echo "Exhibit L39:  http://localhost:${PORT}/index.html?collection=lesson_39_study&capture=1"
echo "Exhibit L40:  http://localhost:${PORT}/index.html?collection=lesson_40_study&capture=1"
echo "Exhibit L41:  http://localhost:${PORT}/index.html?collection=lesson_41_study&capture=1"
echo "Exhibit L42:  http://localhost:${PORT}/index.html?collection=lesson_42_study&capture=1"
echo "Record MP4s:  ./scripts/record_study_exhibition.sh   (lessons 40–42)"
echo "Study L41:    http://localhost:${PORT}/index.html?collection=lesson_41_study"
echo "Heart Expo:   http://localhost:${PORT}/exhibition.html?collection=heart_v5"
echo "Record Heart: ./scripts/record_heart_exhibition.sh  → heart_exhibitions/heart_v5.mp4"
python3 -m http.server "$PORT"
