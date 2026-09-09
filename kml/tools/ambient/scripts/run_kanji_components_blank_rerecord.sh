#!/usr/bin/env bash
# Re-record blank components MP4s from the L31–50 overnight batch.
# Cause: collection-paths.js omitted nest paths for L31–32, 39–40, 42–50
# (404 → empty player → near-black timeout captures).
#
# Lessons: 31 32 39 40 42 43 44 45 46 47 48 49 50
# Outputs: collections/lesson_NN/components_lesson_NN.mp4
# Log:     collections/record_kanji_components_blank_rerecord.log
#
# Start with:
#   nohup bash scripts/run_kanji_components_blank_rerecord.sh \
#     > /tmp/kanji_components_blank_rerecord.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_kanji_components_blank_rerecord.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

LESSONS=(31 32 39 40 42 43 44 45 46 47 48 49 50)
PORT_BASE=9900
ARCHIVE=collections/_archive_components_blank_rerecord
STAMP=$(date +%Y%m%d_%H%M)

{
  echo "START $(date -Iseconds)"
  echo "Blank-set rerecord after collection-paths nest fix (L1–50)"
  echo "Lessons: ${LESSONS[*]}"

  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  mkdir -p "$ARCHIVE"

  for n in "${LESSONS[@]}"; do
    nn=$(printf '%02d' "$n")
    mkdir -p "collections/lesson_${nn}"
    out="collections/lesson_${nn}/components_lesson_${nn}.mp4"
    rm -rf "collections/lesson_${nn}/.tmp_components_lesson_${nn}"
    if [[ -f "$out" ]]; then
      mv "$out" "${ARCHIVE}/components_lesson_${nn}_${STAMP}.mp4"
      echo "archived $out → ${ARCHIVE}/components_lesson_${nn}_${STAMP}.mp4"
    fi
    port=$((PORT_BASE + n))
    echo "==== LESSON $n / components  port=$port  $(date -Iseconds) ===="
    if "$PY" -u scripts/record_lesson_components.py --lesson "$n" --port "$port"; then
      ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
      # Quick sanity: reject near-blank encodes (~20 kbps video)
      if [[ -f "$out" ]]; then
        vbr=$("$PY" - <<PY
import json, subprocess
d=json.loads(subprocess.check_output([
  'ffprobe','-v','error','-select_streams','v:0',
  '-show_entries','stream=bit_rate','-of','json','$out'
], text=True))
print(int(d['streams'][0].get('bit_rate') or 0)//1000)
PY
)
        if [[ "$vbr" -lt 50 ]]; then
          echo "WARN L$n looks blank (vbr=${vbr} kbps) — leaving file for inspection"
        else
          echo "OK L$n vbr=${vbr} kbps"
        fi
      fi
    else
      echo "FAIL L$n / components (exit $?) — continuing queue"
    fi
  done

  echo "DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
