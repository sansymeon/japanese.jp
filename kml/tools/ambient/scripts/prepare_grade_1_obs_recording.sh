#!/usr/bin/env bash
# Build both Grade 1 parts (40 kanji each) for OBS recording.
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/prepare_grade_1_obs_recording_part1.sh "$@"
./scripts/prepare_grade_1_obs_recording_part2.sh "$@"
