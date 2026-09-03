"""Canonical folders for KML ambient YouTube families.

Study = text-bearing. Ambient Japan = textless gallery viewing.

JSON collections stay under collections/. These paths are MP4 output only.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STUDY_FAMILY = ROOT / "ambient-study-japanese-reflections"
INDIVIDUAL_LESSONS = STUDY_FAMILY / "individual-lessons"
FIVE_LESSON_REFLECTIONS = STUDY_FAMILY / "five-lesson-reflections"

JAPAN_FAMILY = ROOT / "ambient-japan-gallery-exhibitions"
QUIET_CINEMATIC = JAPAN_FAMILY / "quiet-cinematic"
AMBIENT_MOVIES = JAPAN_FAMILY / "ambient-movies"


def foundations_mp4(lesson: int) -> Path:
    return INDIVIDUAL_LESSONS / f"foundations_lesson_{lesson:02d}.mp4"


def foundations_legacy_mp4(lesson: int) -> Path:
    return ROOT / "collections" / f"lesson_{lesson:02d}" / f"foundations_lesson_{lesson:02d}.mp4"


def ensure_compat_symlink(legacy: Path, canonical: Path) -> None:
    """Point an old path at the canonical file without duplicating video."""
    if not canonical.is_file():
        return
    legacy.parent.mkdir(parents=True, exist_ok=True)
    rel = os.path.relpath(canonical, legacy.parent)
    if legacy.is_symlink():
        if os.readlink(legacy) == rel:
            return
        legacy.unlink()
    elif legacy.exists():
        if legacy.resolve() == canonical.resolve():
            legacy.unlink()
        else:
            return
    legacy.symlink_to(rel)
