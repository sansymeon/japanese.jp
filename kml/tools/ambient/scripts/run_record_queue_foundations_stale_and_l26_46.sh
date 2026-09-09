#!/usr/bin/env bash
# Overnight Ambient Study (foundations) queue:
#   1. Re-record stale image films: 3, 11–15
#   2. First-time films through Lesson 46: 26–30, 41–46
#
# Existing current films (1–2, 4–10, 16–25, 31–40) are left untouched.
# Stale MP4s are deleted before capture so skip-if-exists cannot keep the old cut.
#
# Safeguards (match the L31–40 foundations queue):
#   * Self-hosted fonts fetched + asserted before any capture
#   * New lessons skip if the MP4 already exists (resumable)
#   * Non-fatal per lesson: a failure is logged and the queue moves on
#   * Unique port per lesson; --rebuild refreshes exhibition JSON
#
# Start with:
#   nohup bash scripts/run_record_queue_foundations_stale_and_l26_46.sh \
#     > /tmp/record_queue_foundations_stale_and_l26_46.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1
LOG=collections/record_queue_foundations_stale_and_l26_46.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

FORCE_LESSONS=(3 11 12 13 14 15)
NEW_LESSONS=(26 27 28 29 30 41 42 43 44 45 46)

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

record_one() {
  local n="$1"
  local force="$2"
  local nn
  nn=$(printf '%02d' "$n")
  mkdir -p "collections/lesson_${nn}" ambient-study-japanese-reflections/individual-lessons
  local out="ambient-study-japanese-reflections/individual-lessons/foundations_lesson_${nn}.mp4"
  if [[ "$force" == "1" ]]; then
    rm -f "$out"
    rm -rf "ambient-study-japanese-reflections/individual-lessons/.tmp_foundations_lesson_${nn}"
  elif [[ -f "$out" ]]; then
    echo "==== SKIP L$n / foundations (exists: $out) $(date -Iseconds) ===="
    return 0
  fi
  local port=$((9200 + n))
  echo "==== LESSON $n / foundations  port=$port  force=$force  $(date -Iseconds) ===="
  if "$PY" -u scripts/record_lesson_foundations.py --lesson "$n" --rebuild --port "$port"; then
    ls -lh "$out" 2>/dev/null || echo "WARN: $out not produced"
    probe_quality "$out" || echo "WARN: qa failed for $out"
  else
    echo "FAIL L$n / foundations (exit $?) — continuing queue"
  fi
}

{
  echo "START $(date -Iseconds)"
  echo "Stale re-record: ${FORCE_LESSONS[*]}"
  echo "First-time through 46: ${NEW_LESSONS[*]}"
  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  echo "######## STALE IMAGE RE-RECORDS ########"
  for n in "${FORCE_LESSONS[@]}"; do
    record_one "$n" 1
  done

  echo "######## FIRST-TIME LESSONS 26–30, 41–46 ########"
  for n in "${NEW_LESSONS[@]}"; do
    record_one "$n" 0
  done

  echo "DONE $(date -Iseconds)"
  echo "---- outputs ----"
  ls -lh ambient-study-japanese-reflections/individual-lessons/foundations_lesson_{03,11,12,13,14,15,26,27,28,29,30,41,42,43,44,45,46}.mp4 2>/dev/null || true
} 2>&1 | tee -a "$LOG"
