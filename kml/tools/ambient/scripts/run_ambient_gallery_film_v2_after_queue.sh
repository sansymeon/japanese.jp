#!/usr/bin/env bash
# After the L11/12 + L34–37 lesson queue finishes, rebuild and record the
# Ambient Gallery Film (Ambient Move V2 — ~137 min scenic Ken Burns).
#
# This is the ~2-hour film (Heart + Lessons 1–10 galleries, scenic-filtered)
# with updated study art (incl. love.png) and the shared soundtrack end-fade
# protocol (8s afade to silence on the final video frame).
#
# Output: collections/ambient_gallery_film/ambient_gallery_film_v2.mp4
# Log:    collections/ambient_gallery_film/record_v2_after_queue.log
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

QUEUE_LOG=collections/record_queue_l11_12_l34_37.log
LOG=collections/ambient_gallery_film/record_v2_after_queue.log
PY="$(pwd)/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

mkdir -p collections/ambient_gallery_film

{
  echo "START $(date -Iseconds)"
  echo "Waiting for lesson queue DONE in $QUEUE_LOG …"

  while true; do
    if [[ -f "$QUEUE_LOG" ]] && rg -q '^DONE ' "$QUEUE_LOG"; then
      echo "Lesson queue DONE at $(date -Iseconds)"
      break
    fi
    if ! pgrep -f 'run_record_queue_l11_12_l34_37\.sh' >/dev/null 2>&1; then
      if [[ -f "$QUEUE_LOG" ]] && rg -q '^DONE ' "$QUEUE_LOG"; then
        echo "Lesson queue DONE (process exited) at $(date -Iseconds)"
        break
      fi
      echo "WARN: lesson queue process gone without DONE — continuing to Ambient Film anyway"
      break
    fi
    sleep 60
  done

  echo "Ensuring self-hosted fonts…"
  bash scripts/fetch_noto_serif_jp_fonts.sh
  bash scripts/fetch_yuji_syuku_font.sh

  SND=audio/137_minute_ambient.mp3
  if [[ ! -f "$SND" ]]; then
    echo "FAIL: missing soundtrack $SND"
    exit 1
  fi
  echo "Soundtrack present: $SND ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SND")s)"

  echo "==== Validate curated ambient_gallery_film JSON $(date -Iseconds) ===="
  # Do not rebuild here: the approved gallery order is curated and must remain
  # unchanged after removing gallbladder, convex, and concave.
  "$PY" - <<'PY'
import json
from pathlib import Path
love = Path("../../assets/studies/love.png")
d = json.loads(Path("collections/ambient_gallery_film/ambient_gallery_film.json").read_text())
removed = {"gallbladder", "convex", "concave"}
slugs = {(s.get("meta") or {}).get("slug") or Path(s.get("image", "")).stem for s in d["scenes"]}
assert len(d["scenes"]) == 184, len(d["scenes"])
assert not (slugs & removed), sorted(slugs & removed)
scene = next(s for s in d["scenes"] if s.get("id") == "L40_love")
mtime = int(love.stat().st_mtime)
print(f"  love.png mtime={mtime} imageRev={scene.get('imageRev')} match={scene.get('imageRev')==mtime}")
print(f"  scenes={len(d['scenes'])} soundtrack={d.get('soundtrack')}")
print(f"  closing={((d.get('bookends') or {}).get('closing'))}")
PY

  echo "==== Record ambient_gallery_film_v2 (~137 min) $(date -Iseconds) ===="
  # record_ambient_gallery_film already muxes with mux_exhibition_soundtrack
  # (8s end fade). Capture also runs Noto/Yuji font gates.
  if "$PY" scripts/record_ambient_gallery_film.py --port 9080; then
    ls -lh collections/ambient_gallery_film/ambient_gallery_film_v2.mp4
    echo "DONE $(date -Iseconds)"
  else
    echo "FAIL ambient_gallery_film_v2 (exit $?) $(date -Iseconds)"
    exit 1
  fi
} 2>&1 | tee "$LOG"
