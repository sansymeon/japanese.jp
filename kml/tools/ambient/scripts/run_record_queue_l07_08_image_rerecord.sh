#!/usr/bin/env bash
# Overnight image-stage re-record for Lessons 7–8 (updated study images).
# Stages: foundations → reading → gallery → compounds → vocabulary
# Skipping: strokes, components, expanded exhibitions
#
# Foundations use the lesson-specific builders (preserve soundtracks:
#   L7 study_version_1, L8 study_version_3) then record_lesson_foundations.
#
# Start with:
#   nohup bash scripts/run_record_queue_l07_08_image_rerecord.sh \
#     > /tmp/record_queue_l07_08_image.nohup.out 2>&1 &
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1
mkdir -p extended_exhibitions collections/lesson_07 collections/lesson_08
LOG=extended_exhibitions/lesson_07_08_image_rerecord.log

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers" .venv/bin/playwright install chromium
fi
if ! compgen -G ".playwright-browsers/chromium_headless_shell-*" >/dev/null; then
  PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers" .venv/bin/playwright install chromium
fi

exec > >(tee -a "$LOG") 2>&1

probe_quality() {
  local path="$1"
  python3 - "$path" <<'PY'
import json, subprocess, sys
from pathlib import Path
path = Path(sys.argv[1])
if not path.is_file():
    print(f"  qa MISSING {path}")
    sys.exit(1)
out = subprocess.check_output(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-show_format", str(path)],
    text=True,
)
data = json.loads(out)
v = next(s for s in data["streams"] if s["codec_type"] == "video")
fps = v.get("r_frame_rate")
cs = v.get("color_space")
dur = float(data["format"].get("duration") or 0)
mb = path.stat().st_size / 1e6
ok = fps == "60/1" and cs == "bt709"
print(f"  qa {path.name}: {mb:.0f}MB {dur/60:.1f}min fps={fps} cs={cs} {'OK' if ok else 'CHECK'}")
PY
}

record_lesson() {
  local n="$1"
  local nn
  nn=$(printf '%02d' "$n")
  local port_f=$((9100 + n))
  local port_r=$((9400 + n))
  local port_g=$((9600 + n))
  local port_c=$((9300 + n))
  local port_v=$((9500 + n))

  echo "######## LESSON $n image re-record $(date -Iseconds) ########"
  echo "Stages: foundations → reading → gallery → compounds → vocabulary"
  echo "Skipping: strokes, components, expanded exhibitions"
  echo "Updated images since prior recordings: L7 jealousy/exquisite; L8 gland/swim/marsh/soup/extinguish"

  rm -f "collections/lesson_${nn}"/{foundations,readings,gallery,compounds,vocabulary}_lesson_${nn}.mp4
  rm -rf "collections/lesson_${nn}"/.tmp_{foundations,readings,gallery,compounds,vocabulary}_lesson_${nn}

  echo "── L$n Foundations ──"
  "$VENV_PYTHON" "scripts/build_lesson_${nn}_exhibition.py"
  "$VENV_PYTHON" scripts/record_lesson_foundations.py --lesson "$n" --port "$port_f"
  probe_quality "ambient-study-japanese-reflections/individual-lessons/foundations_lesson_${nn}.mp4"

  echo "── L$n Reading ──"
  "$VENV_PYTHON" scripts/record_lesson_reading.py --lesson "$n" --rebuild --port "$port_r"
  probe_quality "collections/lesson_${nn}/readings_lesson_${nn}.mp4"

  echo "── L$n Gallery ──"
  "$VENV_PYTHON" scripts/record_lesson_gallery.py --lesson "$n" --rebuild --port "$port_g"
  probe_quality "collections/lesson_${nn}/gallery_lesson_${nn}.mp4"

  echo "── L$n Compounds ──"
  "$VENV_PYTHON" scripts/record_lesson_compounds.py --lesson "$n" --rebuild --port "$port_c"
  probe_quality "collections/lesson_${nn}/compounds_lesson_${nn}.mp4"

  echo "── L$n Vocabulary ──"
  "$VENV_PYTHON" scripts/record_lesson_vocabulary.py --lesson "$n" --rebuild --port "$port_v"
  probe_quality "collections/lesson_${nn}/vocabulary_lesson_${nn}.mp4"

  echo "######## LESSON $n finished $(date -Iseconds) ########"
  ls -lh "collections/lesson_${nn}"/{foundations,readings,gallery,compounds,vocabulary}_lesson_${nn}.mp4
}

echo "=== Lessons 7–8 image re-record started $(date -Iseconds) ==="
bash scripts/fetch_noto_serif_jp_fonts.sh
bash scripts/fetch_yuji_syuku_font.sh

record_lesson 7
record_lesson 8

echo "=== Lessons 7–8 image re-record finished $(date -Iseconds) ==="
