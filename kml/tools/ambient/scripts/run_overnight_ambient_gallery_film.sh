#!/usr/bin/env bash
# Overnight: wait for predecessor recordings to finish, then produce the
# 137-minute Ambient Gallery Film (v2).
#
# Log: collections/ambient_gallery_film/recordings.log
#
# Usage:
#   scripts/run_overnight_ambient_gallery_film.sh
#   scripts/run_overnight_ambient_gallery_film.sh --no-wait
#   scripts/run_overnight_ambient_gallery_film.sh --wait-pid 50543
#   scripts/run_overnight_ambient_gallery_film.sh --wait-gallery-33-37
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/playwright-browsers"
if [[ -d "$(pwd)/.playwright-browsers" ]]; then
  export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
fi

WAIT=1
WAIT_PID=""
WAIT_GALLERY_33_37=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-wait) WAIT=0; shift ;;
    --wait-pid) WAIT_PID="$2"; shift 2 ;;
    --wait-gallery-33-37) WAIT_GALLERY_33_37=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

mkdir -p collections/ambient_gallery_film
LOG=collections/ambient_gallery_film/recordings.log

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install playwright -q
  .venv/bin/playwright install chromium
fi
if ! compgen -G "${PLAYWRIGHT_BROWSERS_PATH}/chromium_headless_shell-*" >/dev/null \
   && ! compgen -G "${PLAYWRIGHT_BROWSERS_PATH}/chromium-*" >/dev/null; then
  .venv/bin/playwright install chromium
fi

exec > >(tee -a "$LOG") 2>&1
echo "=== Ambient Gallery Film overnight started $(date -Iseconds) ==="

wait_for_pid() {
  local pid="$1"
  echo "Tracking explicit PID $pid"
  while kill -0 "$pid" 2>/dev/null; do
    sleep 30
  done
  echo "PID $pid exited $(date -Iseconds)"
}

wait_for_gallery_33_37() {
  echo "Waiting for Heisig gallery lessons 33–37 recordings to finish…"
  # Auto-detect the sequential gallery runner if no PID was supplied.
  if [[ -z "$WAIT_PID" ]]; then
    WAIT_PID="$(pgrep -f 'run_gallery_record_33_37\.sh' | head -1 || true)"
  fi
  if [[ -n "$WAIT_PID" ]] && kill -0 "$WAIT_PID" 2>/dev/null; then
    wait_for_pid "$WAIT_PID"
    WAIT_PID=""
  fi

  while true; do
    if pgrep -f 'run_gallery_record_33_37\.sh' >/dev/null 2>&1 \
       || pgrep -f 'record_lesson_gallery\.py --lesson 3[3-7]' >/dev/null 2>&1; then
      echo "  gallery 33–37 still recording… $(date -Iseconds)"
      sleep 60
      continue
    fi
    sleep 15
    if pgrep -f 'run_gallery_record_33_37\.sh' >/dev/null 2>&1 \
       || pgrep -f 'record_lesson_gallery\.py --lesson 3[3-7]' >/dev/null 2>&1; then
      continue
    fi
    break
  done
  echo "Gallery lessons 33–37 idle $(date -Iseconds)"
  sleep 15
}

wait_for_beyond_joyo() {
  echo "Waiting for Beyond Jōyō overnight recordings to finish…"
  if [[ -n "$WAIT_PID" ]]; then
    wait_for_pid "$WAIT_PID"
    WAIT_PID=""
  fi

  # Prefer the overnight shell; also wait out any leftover record/ffmpeg children.
  while true; do
    if pgrep -f 'run_overnight_beyond_joyo_compounds\.sh' >/dev/null 2>&1 \
       || pgrep -f 'record_beyond_joyo_compounds\.py' >/dev/null 2>&1 \
       || pgrep -f 'run_queued_beyond_joyo_rerecord\.sh' >/dev/null 2>&1; then
      echo "  still recording… $(date -Iseconds)"
      sleep 60
      continue
    fi
    # Brief settle so a part-to-part handoff is not mistaken for completion.
    sleep 20
    if pgrep -f 'run_overnight_beyond_joyo_compounds\.sh' >/dev/null 2>&1 \
       || pgrep -f 'record_beyond_joyo_compounds\.py' >/dev/null 2>&1 \
       || pgrep -f 'run_queued_beyond_joyo_rerecord\.sh' >/dev/null 2>&1; then
      continue
    fi
    break
  done

  # Also require all 19 part MP4s (handles paused / stopped overnight runs).
  local missing=1
  while [[ "$missing" -eq 1 ]]; do
    missing=0
    for n in $(seq -w 1 19); do
      if [[ ! -f "collections/beyond_joyo/beyond_joyo_compounds_${n}.mp4" ]]; then
        missing=1
        echo "  waiting for beyond_joyo_compounds_${n}.mp4 … $(date -Iseconds)"
        break
      fi
    done
    if [[ "$missing" -eq 1 ]]; then
      sleep 60
    fi
  done
  echo "Beyond Jōyō parts 01–19 present $(date -Iseconds)"
}

if [[ "$WAIT" -eq 1 ]]; then
  # If gallery 33–37 is already running (or explicitly requested), wait for it first.
  if [[ "$WAIT_GALLERY_33_37" -eq 1 ]] \
     || pgrep -f 'run_gallery_record_33_37\.sh' >/dev/null 2>&1 \
     || pgrep -f 'record_lesson_gallery\.py --lesson 3[3-7]' >/dev/null 2>&1; then
    wait_for_gallery_33_37
  fi
  wait_for_beyond_joyo
else
  if [[ "$WAIT_GALLERY_33_37" -eq 1 ]]; then
    wait_for_gallery_33_37
  elif [[ -n "$WAIT_PID" ]]; then
    wait_for_pid "$WAIT_PID"
    sleep 15
  else
    echo "Skipping predecessor wait (--no-wait)"
  fi
fi

echo "=== Building ambient_gallery_film collection === $(date -Iseconds) ==="
"$VENV_PYTHON" -u scripts/build_ambient_gallery_film.py

echo "=== Recording ambient_gallery_film (~137 min) === $(date -Iseconds) ==="
if ! "$VENV_PYTHON" -u scripts/record_ambient_gallery_film.py --port 9080; then
  echo "=== FAILED ambient gallery film === $(date -Iseconds) ==="
  exit 1
fi

ls -lh collections/ambient_gallery_film/ambient_gallery_film_v2.mp4 \
  || ls -lh collections/ambient_gallery_film/ambient_gallery_film.mp4 \
  || true
echo "=== Ambient Gallery Film overnight finished $(date -Iseconds) ==="
