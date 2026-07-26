"""Resolve collection JSON paths (lesson subfolders for L1–10)."""

from __future__ import annotations

import re
from pathlib import Path

_LESSON_FOLDER_OVERRIDES: dict[str, str] = {
    "lessons_1_5_prototype": "lesson_01",
    "lesson_01-05_verses": "lesson_01",
    "lessons_6_10_prototype": "lesson_06",
}


def lesson_folder(lesson: int) -> str:
    return f"lesson_{lesson:02d}"


def collection_dir_for_id(collection_id: str) -> str | None:
    if collection_id in _LESSON_FOLDER_OVERRIDES:
        return _LESSON_FOLDER_OVERRIDES[collection_id]
    if collection_id.startswith("proto_"):
        return "prototypes"
    if collection_id.startswith("post_elementary"):
        return "post_elementary"
    if collection_id.startswith("beyond_joyo"):
        return "beyond_joyo"
    if collection_id.startswith("ambient_gallery_film"):
        return "ambient_gallery_film"
    if re.match(r"vocabulary_\d+", collection_id):
        return "vocabulary"
    if collection_id.startswith("hiragana_song"):
        return "hiragana_song"
    if collection_id.startswith("hiragana_lesson"):
        return "hiragana_lesson"
    if collection_id.startswith("katakana_lesson"):
        return "katakana_lesson"
    if collection_id.startswith("hiragana_origins"):
        return "hiragana_origins"
    if collection_id.startswith("katakana_origins"):
        return "katakana_origins"
    if collection_id.startswith("katakana_song"):
        return "katakana_song"
    if collection_id.startswith("grade_1"):
        return "grade_1"
    if collection_id.startswith("grade_2"):
        return "grade_2"
    if collection_id.startswith("grade_3"):
        return "grade_3"
    if collection_id.startswith("grade_4"):
        return "grade_4"
    if collection_id.startswith("grade_5"):
        return "grade_5"
    if collection_id.startswith("grade_6"):
        return "grade_6"
    m = re.match(r"lesson_(\d+)", collection_id)
    if not m:
        return None
    n = int(m.group(1))
    # Nest Heisig lesson collections (1–10 shipped; 14 strokes; 33–37 galleries).
    if 1 <= n <= 10 or n == 14 or 33 <= n <= 37:
        return lesson_folder(n)
    return None


def collection_json_path(root: Path, collection_id: str) -> Path:
    sub = collection_dir_for_id(collection_id)
    if sub:
        nested = root / "collections" / sub / f"{collection_id}.json"
        if nested.is_file():
            return nested
    return root / "collections" / f"{collection_id}.json"


def write_collection_path(root: Path, collection_id: str) -> Path:
    sub = collection_dir_for_id(collection_id)
    if sub:
        folder = root / "collections" / sub
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{collection_id}.json"
    path = root / "collections" / f"{collection_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
