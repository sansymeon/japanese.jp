#!/usr/bin/env bash
# Serve the KML Curriculum Dashboard.
# ./data → ../output (symlink) so the UI never path-traverses.
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -L data && ! -d data ]]; then
  ln -sfn ../output data
  echo "Linked data → ../output"
fi
PORT="${1:-8787}"
echo "KML Curriculum Dashboard v1.0"
echo "  http://localhost:${PORT}/"
echo "  Data: ./data/kml_channel_learning.json → ../output/"
echo "  Regenerate analytics to refresh (dashboard polls every 30s)."
echo ""
python3 -m http.server "$PORT"
