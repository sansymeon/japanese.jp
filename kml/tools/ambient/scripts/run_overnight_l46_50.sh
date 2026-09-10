#!/usr/bin/env bash
# Overnight queue: Lessons 46–50 films after the new 16:9 study images.
#
#   1. Japanese Reflections 46–50     (~51 min, text)
#   2. Ambient Study foundations 47–50 (~8–9 min each; 46 already recorded)
#   3. Quiet Cinematic 46–50          (~51 min, no text)
#   4. Heisig galleries 47–50         (~8 min each; 46 already recorded)
#
# Sequential so Playwright/Chromium stays stable.
#
# Safeguards:
#   * Self-hosted fonts fetched before any capture
#   * Idempotent + resumable: a stage whose MP4 already exists is skipped
#   * Non-fatal per stage: a failure is logged and the queue moves on
#
# Start with:
#   nohup bash scripts/run_overnight_l46_50.sh \
#     > /tmp/overnight_l46_50.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

REFLECTIONS=ambient-study-japanese-reflections/five-lesson-reflections
INDIVIDUAL=ambient-study-japanese-reflections/individual-lessons
QUIET=ambient-japan-gallery-exhibitions/quiet-cinematic
LOG=extended_exhibitions/record_overnight_l46_50.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

FOUNDATIONS_LESSONS=(47 48 49 50)
GALLERY_LESSONS=(47 48 49 50)

mkdir -p "$REFLECTIONS" "$INDIVIDUAL" "$QUIET" extended_exhibitions collections

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

record_reflections() {
  local id=$1 port=$2
  local exhibition="$REFLECTIONS/${id/_prototype/_exhibition}.mp4"
  if [[ -f "$exhibition" ]]; then
    echo "==== SKIP $id (exists: $exhibition) $(date -Iseconds) ===="
    ls -lh "$exhibition"
    return 0
  fi
  echo "==== Record $id  port=$port  $(date -Iseconds) ===="
  if "$PY" -u scripts/record_japanese_reflections_exhibition.py \
      "$id" --rebuild --port "$port" --output-dir "$REFLECTIONS"; then
    ls -lh "$exhibition" 2>/dev/null || echo "WARN: $exhibition not produced"
    probe_quality "$exhibition" || echo "WARN: qa failed for $exhibition"
  else
    echo "FAIL $id (exit $?) — continuing queue"
  fi
}

record_quiet() {
  local id=$1 script=$2 port=$3
  local out="$QUIET/${id}.mp4"
  if [[ -f "$out" ]]; then
    echo "==== SKIP $id (exists: $out) $(date -Iseconds) ===="
    ls -lh "$out"
    return 0
  fi
  echo "==== Record $id  port=$port  $(date -Iseconds) ===="
  if "$PY" -u "scripts/$script" --rebuild --port "$port"; then
    ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
    probe_quality "$out" || echo "WARN: qa failed for $out"
  else
    echo "FAIL $id (exit $?) — continuing queue"
  fi
}

record_foundations() {
  local n="$1"
  local nn
  nn=$(printf '%02d' "$n")
  local out="$INDIVIDUAL/foundations_lesson_${nn}.mp4"
  if [[ -f "$out" ]]; then
    echo "==== SKIP L$n / foundations (exists: $out) $(date -Iseconds) ===="
    return 0
  fi
  local port=$((9300 + n))
  echo "==== LESSON $n / foundations  port=$port  $(date -Iseconds) ===="
  if "$PY" -u scripts/record_lesson_foundations.py --lesson "$n" --rebuild --port "$port"; then
    ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
    probe_quality "$out" || echo "WARN: qa failed for $out"
  else
    echo "FAIL L$n / foundations (exit $?) — continuing queue"
  fi
}

record_gallery() {
  local n="$1"
  local nn
  nn=$(printf '%02d' "$n")
  mkdir -p "collections/lesson_${nn}"
  local out="collections/lesson_${nn}/gallery_lesson_${nn}.mp4"
  if [[ -f "$out" ]]; then
    echo "==== SKIP L$n / gallery (exists: $out) $(date -Iseconds) ===="
    return 0
  fi
  local port=$((9400 + n))
  echo "==== LESSON $n / gallery  port=$port  $(date -Iseconds) ===="
  if "$PY" -u scripts/record_lesson_gallery.py --lesson "$n" --rebuild --port "$port"; then
    ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
    probe_quality "$out" || echo "WARN: qa failed for $out"
  else
    echo "FAIL L$n / gallery (exit $?) — continuing queue"
  fi
}

{
  echo "START $(date -Iseconds)"
  echo "Overnight: Reflections 46–50, foundations 47–50, Quiet Cinematic 46–50, galleries 47–50"
  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  echo "==== Rebuild collections $(date -Iseconds) ===="
  "$PY" -u scripts/build_lessons_46_50_prototype.py
  "$PY" -u scripts/build_lessons_46_50_quiet_cinematic.py
  for n in "${FOUNDATIONS_LESSONS[@]}"; do
    "$PY" -u scripts/build_lesson_foundations_exhibition.py --lesson "$n"
  done
  for n in "${GALLERY_LESSONS[@]}"; do
    "$PY" -u scripts/build_lesson_gallery.py --lesson "$n"
  done

  record_reflections lessons_46_50_prototype 8786
  for n in "${FOUNDATIONS_LESSONS[@]}"; do
    record_foundations "$n"
  done
  record_quiet lessons_46_50_quiet_cinematic record_lessons_46_50_quiet_cinematic.py 8787
  for n in "${GALLERY_LESSONS[@]}"; do
    record_gallery "$n"
  done

  echo "DONE $(date -Iseconds)"
  echo "---- outputs ----"
  ls -lh "$REFLECTIONS/lessons_46_50_exhibition.mp4" 2>/dev/null || true
  ls -lh "$QUIET/lessons_46_50_quiet_cinematic.mp4" 2>/dev/null || true
  ls -lh "$INDIVIDUAL"/foundations_lesson_{47,48,49,50}.mp4 2>/dev/null || true
  ls -lh collections/lesson_{47,48,49,50}/gallery_lesson_{47,48,49,50}.mp4 2>/dev/null || true
} 2>&1 | tee -a "$LOG"
