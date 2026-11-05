#!/usr/bin/env bash
# Serve the shougaku kanji exhibition player.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8770}"
echo "Grade 1:  http://localhost:${PORT}/index.html?collection=grade_1"
echo "Grade 2:  http://localhost:${PORT}/index.html?collection=grade_2"
echo "Capture:  http://localhost:${PORT}/index.html?collection=grade_2&capture=1"
echo "Rebuild:  python3 scripts/build_grade_collections.py"
python3 -m http.server "$PORT"
