#!/usr/bin/env bash
# Fetch self-hosted Yuji Syuku — the protected KML hero / target-kanji face.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p fonts/yuji-syuku
out="fonts/yuji-syuku/YujiSyuku-Regular.ttf"
if [[ -f "$out" && -s "$out" ]]; then
  echo "ok $out ($(wc -c <"$out") bytes)"
  exit 0
fi
# Prefer google/fonts OFL source (same file Google Fonts CSS serves).
URL='https://raw.githubusercontent.com/google/fonts/main/ofl/yujisyuku/YujiSyuku-Regular.ttf'
echo "fetch Yuji Syuku…"
curl -fsSL -L --retry 3 -o "$out" "$URL"
ls -lh "$out"
file "$out"
