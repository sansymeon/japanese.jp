#!/usr/bin/env bash
# Overnight chain:
#   1) Lesson 25 remaining stage videos (components already present → skipped)
#   2) Component videos for Lessons 31–50
#
# Start with:
#   nohup bash scripts/run_overnight_l25_then_components_l31_50.sh \
#     > /tmp/overnight_l25_l31_50.nohup.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.playwright-browsers"
export PYTHONUNBUFFERED=1

LOG=collections/record_overnight_l25_then_components_l31_50.log

{
  echo "OVERNIGHT START $(date -Iseconds)"
  echo "Chain: L25 remaining stages → components L31–50"

  bash scripts/run_record_queue_l25.sh
  bash scripts/run_kanji_components_l31_50.sh

  echo "OVERNIGHT DONE $(date -Iseconds)"
} 2>&1 | tee -a "$LOG"
