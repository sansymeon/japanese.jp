#!/usr/bin/env bash
# Overnight: re-record lesson videos with broken typography (font/CSS not ready).
# Waits for Grade 3 jukugo (grade_3_jukugo_*.mp4) to finish, then records:
#   L3 readings
#   L6 readings, vocabulary, compounds, gallery, strokes
#   L7 readings, strokes, compounds, gallery, vocabulary
# Log: extended_exhibitions/lesson_typography_rerecord.log
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
mkdir -p extended_exhibitions
LOG=extended_exhibitions/lesson_typography_rerecord.log

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  .venv/bin/playwright install chromium
fi
if ! compgen -G ".playwright-browsers/chromium_headless_shell-*" >/dev/null; then
  .venv/bin/playwright install chromium
fi

exec > >(tee -a "$LOG") 2>&1

wait_for_grade_3_jukugo() {
  echo "=== Waiting for Grade 3 jukugo recordings $(date -Iseconds) ==="
  while pgrep -f "[p]ython.*scripts/record_grade_3_compounds_school.py" >/dev/null 2>&1 \
    || pgrep -f "[p]repare_grade_3_compounds_school_recording.sh" >/dev/null 2>&1; do
    done_count=$(ls collections/grade_3/grade_3_jukugo_[0-9]*.mp4 2>/dev/null | wc -l)
    echo "  grade 3 jukugo still running… ${done_count}/10 parts done $(date -Iseconds)"
    sleep 60
  done
  echo "=== Grade 3 jukugo finished $(date -Iseconds) ==="
}

probe_quality() {
  local path="$1"
  python3 - "$path" <<'PY'
import json, subprocess, sys
path = sys.argv[1]
out = subprocess.check_output(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", path],
    text=True,
)
v = next(s for s in json.loads(out)["streams"] if s["codec_type"] == "video")
fps = v.get("r_frame_rate")
cs = v.get("color_space")
ok = fps == "60/1" and cs == "bt709"
print(f"  qa {path}: fps={fps} cs={cs} {'OK' if ok else 'CHECK'}")
PY
}

echo "=== Lesson typography re-record queue started $(date -Iseconds) ==="
wait_for_grade_3_jukugo

# Clear stale partial captures.
rm -rf collections/lesson_03/.tmp_readings_lesson_03
rm -rf collections/lesson_06/.tmp_{readings,vocabulary,compounds,gallery,strokes}_lesson_06
rm -rf collections/lesson_07/.tmp_{readings,vocabulary,compounds,gallery,strokes}_lesson_07

echo "── Lesson 3 readings ──"
"$VENV_PYTHON" scripts/record_lesson_reading.py --lesson 3 --rebuild --port 8782
probe_quality collections/lesson_03/readings_lesson_03.mp4

echo "── Lesson 6 (readings → vocabulary → compounds → gallery → strokes) ──"
"$VENV_PYTHON" scripts/record_lesson_reading.py --lesson 6 --rebuild --port 8782
probe_quality collections/lesson_06/readings_lesson_06.mp4
"$VENV_PYTHON" scripts/record_lesson_vocabulary.py --lesson 6 --rebuild --port 8781
probe_quality collections/lesson_06/vocabulary_lesson_06.mp4
"$VENV_PYTHON" scripts/record_lesson_compounds.py --lesson 6 --rebuild --port 8780
probe_quality collections/lesson_06/compounds_lesson_06.mp4
"$VENV_PYTHON" scripts/record_lesson_gallery.py --lesson 6 --rebuild --port 8780
probe_quality collections/lesson_06/gallery_lesson_06.mp4
"$VENV_PYTHON" scripts/record_lesson_strokes.py --lesson 6 --rebuild --port 8779
probe_quality collections/lesson_06/strokes_lesson_06.mp4

echo "── Lesson 7 (readings → strokes → compounds → gallery → vocabulary) ──"
"$VENV_PYTHON" scripts/record_lesson_reading.py --lesson 7 --rebuild --port 8782
probe_quality collections/lesson_07/readings_lesson_07.mp4
"$VENV_PYTHON" scripts/record_lesson_strokes.py --lesson 7 --rebuild --port 8779
probe_quality collections/lesson_07/strokes_lesson_07.mp4
"$VENV_PYTHON" scripts/record_lesson_compounds.py --lesson 7 --rebuild --port 8780
probe_quality collections/lesson_07/compounds_lesson_07.mp4
"$VENV_PYTHON" scripts/record_lesson_gallery.py --lesson 7 --rebuild --port 8780
probe_quality collections/lesson_07/gallery_lesson_07.mp4
"$VENV_PYTHON" scripts/record_lesson_vocabulary.py --lesson 7 --rebuild --port 8781
probe_quality collections/lesson_07/vocabulary_lesson_07.mp4

echo "=== Lesson typography re-record queue finished $(date -Iseconds) ==="
