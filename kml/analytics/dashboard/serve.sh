#!/usr/bin/env bash
# Serve the KML Curriculum Dashboard from kml/analytics/ so the UI can fetch
# ../output/... (same relative layout as production on Netlify).
# dashboard/data → ../output remains as a local convenience symlink only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ ! -L dashboard/data && ! -d dashboard/data ]]; then
  ln -sfn ../output dashboard/data
  echo "Linked dashboard/data → ../output"
fi
PORT="${1:-8787}"
echo "KML Curriculum Dashboard v1.0"
echo "  http://localhost:${PORT}/dashboard/"
echo "  Data: ../output/kml_channel_learning.json"
echo "  Regenerate analytics to refresh (dashboard polls every 30s)."
echo ""
python3 -m http.server "$PORT"
