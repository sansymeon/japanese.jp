#!/usr/bin/env bash
# After Ambient Gallery Japan — Four Seasons finishes, rebuild + record
# Japanese Reflections Lessons 6–10 (image+verse exhibition).
#
# Output: extended_exhibitions/lessons_6_10_prototype.mp4
#         (also copied to extended_exhibitions/lessons_6_10_exhibitions.mp4)
# Log:    extended_exhibitions/record_lessons_6_10_after_4_seasons.log
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

SEASONS_LOG=collections/ambient_gallery_japan_4_seasons/record_after_heart_2.log
SEASONS_MP4=collections/ambient_gallery_japan_4_seasons/ambient_gallery_japan_4_seasons.mp4
SEASONS_TMP=collections/ambient_gallery_japan_4_seasons/.tmp_ambient_gallery_japan_4_seasons
LOG=extended_exhibitions/record_lessons_6_10_after_4_seasons.log
OUT_PROTOTYPE=extended_exhibitions/lessons_6_10_prototype.mp4
OUT_EXHIBITIONS=extended_exhibitions/lessons_6_10_exhibitions.mp4
PORT=8769
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p extended_exhibitions

# True if a real recorder matches; ignore Cursor agent/sandbox shells whose
# cmdlines mention the same strings and spoof plain `pgrep -f`.
real_proc() {
  local pat=$1 line
  while IFS= read -r line; do
    case "$line" in
      *cursorsandbox*|*COMMAND_EXIT_CODE*|*AGENT_LOOP*|*pgrep*) continue ;;
    esac
    return 0
  done < <(pgrep -af "$pat" 2>/dev/null || true)
  return 1
}

{
  echo "START $(date -Iseconds)"
  echo "Waiting for Ambient Japan 4 Seasons DONE …"

  while true; do
    if [[ -f "$SEASONS_MP4" ]] && rg -q '^DONE ' "$SEASONS_LOG" 2>/dev/null; then
      if ! real_proc 'scripts/record_ambient_gallery_japan_4_seasons\.py' \
        && ! real_proc 'run_japan_4_seasons_after_heart_2\.sh' \
        && [[ ! -d "$SEASONS_TMP" ]]; then
        echo "Japan 4 Seasons DONE spotted $(date -Iseconds)"
        break
      fi
    fi
    # Proceed if final MP4 exists and recorder/ffmpeg for this job are gone
    if [[ -f "$SEASONS_MP4" ]] \
      && ! real_proc 'scripts/record_ambient_gallery_japan_4_seasons\.py' \
      && ! real_proc '\.tmp_ambient_gallery_japan_4_seasons/muxed\.mp4' \
      && [[ ! -d "$SEASONS_TMP" ]]; then
      echo "Japan 4 Seasons MP4 present and recorder gone — proceeding $(date -Iseconds)"
      break
    fi
    echo "waiting for Japan 4 Seasons… $(date -Iseconds)"
    sleep 60
  done

  echo "==== Rebuild Lessons 6–10 prototype JSON $(date -Iseconds) ===="
  "$PY" -u scripts/build_lessons_6_10_prototype.py

  echo "==== Record Lessons 6–10 Exhibitions (~51 min) $(date -Iseconds) ===="
  if "$PY" -u scripts/record_japanese_reflections_exhibition.py \
      lessons_6_10_prototype --rebuild --port "$PORT"; then
    ls -lh "$OUT_PROTOTYPE"
    cp -f "$OUT_PROTOTYPE" "$OUT_EXHIBITIONS"
    ls -lh "$OUT_EXHIBITIONS"
    echo "DONE $(date -Iseconds)"
  else
    echo "FAIL Lessons 6–10 record (exit $?) $(date -Iseconds)"
    exit 1
  fi
} 2>&1 | tee -a "$LOG"
