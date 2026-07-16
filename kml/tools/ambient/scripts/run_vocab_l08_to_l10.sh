#!/usr/bin/env bash
# Re-record lesson vocabulary L8–L10 (short crest, no meta labels, under-30 fades).
set -euo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1
mkdir -p extended_exhibitions
LOG=extended_exhibitions/vocab_l08_to_l10.log

exec > >(tee -a "$LOG") 2>&1
echo "=== Vocabulary L8–L10 started $(date -Iseconds) ==="

for L in 8 9 10; do
  echo "--- Lesson $L vocabulary $(date -Iseconds) ---"
  rm -rf "collections/lesson_$(printf '%02d' "$L")/.tmp_vocabulary_lesson_$(printf '%02d' "$L")"
  .venv/bin/python scripts/record_lesson_vocabulary.py --lesson "$L" --rebuild --port "$((8775 + L))"
  echo "=== Lesson $L vocabulary done $(date -Iseconds) ==="
done

echo "=== All L8–L10 vocabulary finished $(date -Iseconds) ==="
