#!/usr/bin/env bash
# Re-record Lesson 18 image stages only (skip strokes, components, expanded exhibitions).
# Log: extended_exhibitions/lesson_18_image_rerecord.log
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1
mkdir -p extended_exhibitions collections/lesson_18
LOG=extended_exhibitions/lesson_18_image_rerecord.log

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

echo "=== Lesson 18 image re-record started $(date -Iseconds) ==="
echo "Stages: foundations → reading → gallery → compounds → vocabulary"
echo "Skipping: strokes, components, expanded exhibitions"

# Remove stale image-stage outputs so recorders rewrite them
rm -f collections/lesson_18/{foundations,gallery,compounds,vocabulary,readings}_lesson_18.mp4
rm -rf collections/lesson_18/.tmp_{foundations,readings,vocabulary,compounds,gallery}_lesson_18

echo "── Foundations ──"
"$VENV_PYTHON" scripts/record_lesson_foundations.py --lesson 18 --rebuild --port 9118
probe_quality collections/lesson_18/foundations_lesson_18.mp4

echo "── Reading ──"
"$VENV_PYTHON" scripts/record_lesson_reading.py --lesson 18 --rebuild --port 9418
probe_quality collections/lesson_18/readings_lesson_18.mp4

echo "── Gallery ──"
"$VENV_PYTHON" scripts/record_lesson_gallery.py --lesson 18 --rebuild --port 9618
probe_quality collections/lesson_18/gallery_lesson_18.mp4

echo "── Compounds ──"
"$VENV_PYTHON" scripts/record_lesson_compounds.py --lesson 18 --rebuild --port 9318
probe_quality collections/lesson_18/compounds_lesson_18.mp4

echo "── Vocabulary ──"
"$VENV_PYTHON" scripts/record_lesson_vocabulary.py --lesson 18 --rebuild --port 9518
probe_quality collections/lesson_18/vocabulary_lesson_18.mp4

echo "=== Lesson 18 image re-record finished $(date -Iseconds) ==="
ls -lh collections/lesson_18/{foundations,readings,gallery,compounds,vocabulary}_lesson_18.mp4
