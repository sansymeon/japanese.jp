#!/usr/bin/env bash
# Re-record lesson vocabulary L6–L10:
# - no "target kanji" / "verse line" meta labels
# - short crest (no pad to full ~83 min vocabulary bed)
# - end-fade trim: all under 30 min (L10 under 25)
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
mkdir -p extended_exhibitions
LOG=extended_exhibitions/vocab_relabel_l06_to_l10.log

exec > >(tee -a "$LOG") 2>&1
echo "=== Vocabulary short re-record L6–L10 started $(date -Iseconds) ==="

export PYTHONUNBUFFERED=1
for L in 6 7 8 9 10; do
  echo "--- Lesson $L vocabulary $(date -Iseconds) ---"
  rm -rf "collections/lesson_$(printf '%02d' "$L")/.tmp_vocabulary_lesson_$(printf '%02d' "$L")"
  .venv/bin/python scripts/record_lesson_vocabulary.py --lesson "$L" --rebuild --port "$((8775 + L))"
  echo "=== Lesson $L vocabulary done $(date -Iseconds) ==="
done

echo "=== All L6–L10 vocabulary finished $(date -Iseconds) ==="
