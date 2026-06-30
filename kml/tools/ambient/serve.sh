#!/usr/bin/env bash
# Serve the ambient player from this directory.
# Requires ./assets -> ../../assets (symlink) so /assets/studies/*.png resolves.
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -e assets/studies ]]; then
  echo "Missing assets link. Run: ln -s ../../assets assets" >&2
  exit 1
fi
if [[ ! -e strokes/pages ]]; then
  echo "Missing strokes link. Run: ln -s ../strokes strokes" >&2
  exit 1
fi
if [[ ! -e bookends/lesson_32.png ]]; then
  echo "Missing bookend artwork. Run: ln -s ../../../assets/covers/lesson_32.png bookends/lesson_32.png" >&2
  exit 1
fi
PORT="${1:-8765}"
echo "── Lesson 1 (six stages) ──"
echo "1 Foundations: http://localhost:${PORT}/index.html?collection=lesson_1_foundations&typography=mobile-refine"
echo "2 Reading:     http://localhost:${PORT}/exhibition.html?collection=lesson_01_reading"
echo "3 Vocabulary:  http://localhost:${PORT}/exhibition.html?collection=lesson_01_vocabulary"
echo "4 Strokes:     http://localhost:${PORT}/exhibition.html?collection=lesson_01_strokes"
echo "5 Compounds:   http://localhost:${PORT}/exhibition.html?collection=lesson_01_compounds"
echo "6 Gallery:     http://localhost:${PORT}/exhibition.html?collection=lesson_01_gallery"
echo ""
for n in $(seq 1 10); do
  echo "Foundations L${n}: http://localhost:${PORT}/index.html?collection=lesson_${n}_foundations&typography=mobile-refine"
done
for n in $(seq -w 2 10); do
  echo "Reading L${n}:     http://localhost:${PORT}/exhibition.html?collection=lesson_${n}_reading"
done
echo "YouTube L36:  http://localhost:${PORT}/index.html?collection=lesson_36_foundations"
echo "YouTube L37:  http://localhost:${PORT}/index.html?collection=lesson_37_foundations"
echo "YouTube L38:  http://localhost:${PORT}/index.html?collection=lesson_38_foundations"
echo "YouTube L39:  http://localhost:${PORT}/index.html?collection=lesson_39_foundations"
echo "YouTube L40:  http://localhost:${PORT}/index.html?collection=lesson_40_foundations"
echo "Exhibit L36:  http://localhost:${PORT}/index.html?collection=lesson_36_foundations&capture=1"
echo "Exhibit L37:  http://localhost:${PORT}/index.html?collection=lesson_37_foundations&capture=1"
echo "Exhibit L38:  http://localhost:${PORT}/index.html?collection=lesson_38_foundations&capture=1"
echo "Exhibit L39:  http://localhost:${PORT}/index.html?collection=lesson_39_foundations&capture=1"
echo "Exhibit L40:  http://localhost:${PORT}/index.html?collection=lesson_40_foundations&capture=1"
echo "Exhibit L41:  http://localhost:${PORT}/index.html?collection=lesson_41_foundations&capture=1"
echo "Exhibit L42:  http://localhost:${PORT}/index.html?collection=lesson_42_foundations&capture=1"
echo "Record MP4s:  ./scripts/record_foundations_exhibition.sh   (lessons 40–42)"
echo "Foundations L41: http://localhost:${PORT}/index.html?collection=lesson_41_foundations"
echo "Heart Expo:   http://localhost:${PORT}/exhibition.html?collection=heart_v5"
echo "Heart QA:     http://localhost:${PORT}/exhibition.html?collection=heart_v5&skipBookends=1&exhibit=0&singleExhibit=1"
echo "Heart record: fullscreen browser + OBS (~96 min). Save → heart_exhibitions/heart_v5.mp4"
echo "              Mux audio: audio/exhibition_flute_intro.mp3 @ 2s, then ambient_kanji_exhibition.mp3 after flute ends + 6s exhale"
echo "Party Kanji:  http://localhost:${PORT}/exhibition.html?collection=party_kanji_v1&skipBookends=1&singleExhibit=1"
echo "Party QA:     add &timingScale=0.05"
echo "Jōyō Soundtrack part 1 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_01"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording.sh"
echo "Jōyō Soundtrack part 2 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_02"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part2.sh"
echo "Jōyō Soundtrack part 3 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_03"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part3.sh"
echo "Jōyō Soundtrack part 4 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_04"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part4.sh"
echo "Jōyō Soundtrack part 5 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_05"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part5.sh"
echo "Jōyō Soundtrack part 6 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_06"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part6.sh"
echo "Jōyō Soundtrack part 7 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_07"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part7.sh"
echo "Jōyō Soundtrack part 8 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_08"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part8.sh"
echo "Jōyō Soundtrack part 9 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_09"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part9.sh"
echo "Jōyō Soundtrack part 10 (100): http://localhost:${PORT}/exhibition.html?collection=post_elementary_10"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part10.sh"
echo "Jōyō Soundtrack part 11 (109): http://localhost:${PORT}/exhibition.html?collection=post_elementary_11"
echo "  Build:      ./scripts/prepare_post_elementary_obs_recording_part11.sh"
echo "Grade 1 Soundtrack part 1 (40): http://localhost:${PORT}/exhibition.html?collection=grade_1_01"
echo "  Build:      ./scripts/prepare_grade_1_obs_recording_part1.sh"
echo "Grade 1 Soundtrack part 2 (40): http://localhost:${PORT}/exhibition.html?collection=grade_1_02"
echo "  Build:      ./scripts/prepare_grade_1_obs_recording_part2.sh"
echo "Grade 2 Soundtrack part 1 (40): http://localhost:${PORT}/exhibition.html?collection=grade_2_01"
echo "  Build:      ./scripts/prepare_grade_2_obs_recording_part1.sh"
echo "Grade 2 Soundtrack part 2 (40): http://localhost:${PORT}/exhibition.html?collection=grade_2_02"
echo "  Build:      ./scripts/prepare_grade_2_obs_recording_part2.sh"
echo "Grade 2 Soundtrack part 3 (40): http://localhost:${PORT}/exhibition.html?collection=grade_2_03"
echo "  Build:      ./scripts/prepare_grade_2_obs_recording_part3.sh"
echo "Grade 2 Soundtrack part 4 (41): http://localhost:${PORT}/exhibition.html?collection=grade_2_04"
echo "  Build:      ./scripts/prepare_grade_2_obs_recording_part4.sh"
echo "Playwright Heart (optional): ./scripts/record_heart_exhibition.sh"
python3 -m http.server "$PORT"
