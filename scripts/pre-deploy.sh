#!/usr/bin/env bash
# Pre-deploy: regenerate KML channel-learning analytics before the site goes live.
#
# Intended flow (automated on main):
#   create lesson → git push to main → GitHub Action runs this script →
#   commit fresh JSON under kml/analytics/output/ → Netlify deploy
#
# Reads lesson/collection inputs read-only.
# Writes only under kml/analytics/output/ (dashboard ./data is a symlink to that).
#
# Usage (from repo root):
#   ./scripts/pre-deploy.sh
#   SKIP_ANALYTICS=1 ./scripts/pre-deploy.sh   # no-op escape hatch
#
# Also invoked by .github/workflows/pre-deploy-analytics.yml on every push to
# main (except output-only commits). Not a cron / Netlify scheduled function.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${SKIP_ANALYTICS:-}" == "1" ]]; then
  echo "[pre-deploy] SKIP_ANALYTICS=1 — skipping analyze_channel_learning.py"
  exit 0
fi

PYTHON=""
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="$(command -v python3)"
else
  echo "[pre-deploy] error: no Python interpreter found (.venv/bin/python or python3)" >&2
  exit 1
fi

SCRIPT="$ROOT/kml/analytics/scripts/analyze_channel_learning.py"
if [[ ! -f "$SCRIPT" ]]; then
  echo "[pre-deploy] error: missing $SCRIPT" >&2
  exit 1
fi

echo "[pre-deploy] Using: $PYTHON"
echo "[pre-deploy] Running analyze_channel_learning.py …"
"$PYTHON" "$SCRIPT"

OUT_JSON="$ROOT/kml/analytics/output/kml_channel_learning.json"
if [[ ! -f "$OUT_JSON" ]]; then
  echo "[pre-deploy] error: expected output missing: $OUT_JSON" >&2
  exit 1
fi

echo "[pre-deploy] Analytics ready: $OUT_JSON"
echo "[pre-deploy] Homepage + dashboard will read this JSON on the next deploy."
