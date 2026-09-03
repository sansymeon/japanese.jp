#!/usr/bin/env python3
"""Move existing ambient MP4s into the two YouTube family folders.

Does not rebuild video. Leaves relative symlinks at old paths so skip-if-exists
checks and older scripts keep working.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_video_paths import (  # noqa: E402
    AMBIENT_MOVIES,
    FIVE_LESSON_REFLECTIONS,
    INDIVIDUAL_LESSONS,
    QUIET_CINEMATIC,
    ROOT,
    ensure_compat_symlink,
    foundations_legacy_mp4,
    foundations_mp4,
)

MOVES: list[tuple[Path, Path]] = []


def plan_move(src: Path, dest: Path) -> None:
    MOVES.append((src, dest))


def relink(legacy: Path, canonical: Path) -> None:
    ensure_compat_symlink(legacy, canonical)


def apply() -> None:
    for folder in (INDIVIDUAL_LESSONS, FIVE_LESSON_REFLECTIONS, QUIET_CINEMATIC, AMBIENT_MOVIES):
        folder.mkdir(parents=True, exist_ok=True)

    # Individual Ambient Study (canonical current files only)
    for lesson in range(1, 154):
        src = foundations_legacy_mp4(lesson)
        if src.is_file() and not src.is_symlink():
            plan_move(src, foundations_mp4(lesson))

    # Japanese Reflections (published exhibition names)
    extended = ROOT / "extended_exhibitions"
    for name in (
        "lessons_1_5_exhibition.mp4",
        "lessons_6_10_exhibition.mp4",
        "lessons_11_15_exhibition.mp4",
        "lessons_16_20_exhibition.mp4",
    ):
        src = extended / name
        if src.is_file() and not src.is_symlink():
            plan_move(src, FIVE_LESSON_REFLECTIONS / name)

    # Quiet Cinematic currently saved as *_exhibition.mp4; canonical recorder name is *_quiet_cinematic.mp4
    qc_renames = (
        ("lessons_21_25_exhibition.mp4", "lessons_21_25_quiet_cinematic.mp4"),
        ("lessons_26_30_exhibition.mp4", "lessons_26_30_quiet_cinematic.mp4"),
    )
    for old_name, new_name in qc_renames:
        src = extended / old_name
        if src.is_file() and not src.is_symlink():
            plan_move(src, QUIET_CINEMATIC / new_name)

    # Ambient Movies
    film = ROOT / "collections" / "ambient_gallery_film" / "ambient_gallery_film.mp4"
    if film.is_file() and not film.is_symlink():
        plan_move(film, AMBIENT_MOVIES / "ambient_gallery_film.mp4")
    movie_2140 = extended / "lessons_21_40_ambient_gallery.mp4"
    if movie_2140.is_file() and not movie_2140.is_symlink():
        plan_move(movie_2140, AMBIENT_MOVIES / "lessons_21_40_ambient_gallery.mp4")

    print(f"Planned moves: {len(MOVES)}")
    for src, dest in MOVES:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            print(f"SKIP dest exists: {dest}")
            continue
        print(f"MOVE {src.relative_to(ROOT)} → {dest.relative_to(ROOT)}")
        shutil.move(str(src), str(dest))
        relink(src, dest)

    # Extra aliases for Quiet Cinematic exhibition filenames
    for old_name, new_name in qc_renames:
        canonical = QUIET_CINEMATIC / new_name
        if canonical.is_file():
            relink(QUIET_CINEMATIC / old_name, canonical)
            relink(extended / new_name, canonical)

    # Re-assert foundations legacy links (in case dest already existed)
    for lesson in range(1, 154):
        canonical = foundations_mp4(lesson)
        if canonical.is_file():
            relink(foundations_legacy_mp4(lesson), canonical)


if __name__ == "__main__":
    apply()
    print("Done.")
