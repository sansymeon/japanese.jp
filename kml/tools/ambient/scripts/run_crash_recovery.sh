#!/usr/bin/env bash
# Post-crash recovery: resume Lessons 15–18 queue, then Ambient Revised film.
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
if [[ -d "$(pwd)/.playwright-browsers" ]]; then
  export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
fi
LOG=collections/crash_recovery.log
PY=.venv/bin/python
[[ -x "$PY" ]] || PY="$(command -v python3)"

exec > >(tee -a "$LOG") 2>&1
echo "=== Crash recovery started $(date -Iseconds) ==="

if [[ -f collections/lesson_16/vocabulary_lesson_16.mp4 ]]; then
  echo "L16 vocabulary present: $(ls -lh collections/lesson_16/vocabulary_lesson_16.mp4 | awk '{print $5,$9}')"
else
  echo "WARN: L16 vocabulary still missing — queue will re-record it"
fi

# Clean Ambient tmp so recorder starts fresh.
rm -rf collections/ambient_gallery_film/.tmp_ambient_gallery_film_v2
mkdir -p collections/ambient_gallery_film

echo "=== Resume Lessons 15–18 queue $(date -Iseconds) ==="
bash scripts/run_record_queue_l15_18.sh

echo "=== Rebuild + record Ambient Revised $(date -Iseconds) ==="
"$PY" -u scripts/build_ambient_gallery_film.py
if ! "$PY" -u scripts/record_ambient_gallery_film.py --port 9080; then
  echo "=== FAILED ambient revised === $(date -Iseconds) ==="
  exit 1
fi
ls -lh collections/ambient_gallery_film/ambient_gallery_film_v2.mp4 \
  || ls -lh collections/ambient_gallery_film/ambient_gallery_film.mp4 \
  || true
echo "=== Crash recovery finished $(date -Iseconds) ==="
