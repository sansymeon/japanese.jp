#!/usr/bin/env bash
# Fetch self-hosted Ambient recording fonts:
#   - Noto Serif CJK JP OTFs → "Noto Serif JP" (supporting body)
#   - Yuji Syuku TTF         → hero / target kanji (protected identity)
set -euo pipefail
cd "$(dirname "$0")"
bash ./fetch_yuji_syuku_font.sh
cd ..
mkdir -p fonts/noto-serif-jp
BASE='https://github.com/notofonts/noto-cjk/raw/main/Serif/OTF/Japanese'
for w in Regular Medium SemiBold Bold; do
  out="fonts/noto-serif-jp/NotoSerifCJKjp-${w}.otf"
  if [[ -f "$out" && -s "$out" ]]; then
    echo "ok $out"
    continue
  fi
  echo "fetch $w…"
  curl -fsSL -L --retry 3 -o "$out" "$BASE/NotoSerifCJKjp-${w}.otf"
  ls -lh "$out"
done
