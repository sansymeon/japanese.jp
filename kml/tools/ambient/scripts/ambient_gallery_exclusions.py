"""Persistent Ambient Gallery Japan exclusion list.

Curatorial only: never delete source assets. Do not apply to lessons,
vocabulary, strokes, or thumbnails.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUSIONS_PATH = ROOT / "collections" / "ambient_gallery_japan" / "exclusions.json"


def exclusions_path() -> Path:
    return EXCLUSIONS_PATH


def load_exclude_slugs() -> set[str]:
    if not EXCLUSIONS_PATH.is_file():
        return set()
    data = json.loads(EXCLUSIONS_PATH.read_text(encoding="utf-8"))
    return {str(slug) for slug in (data.get("excludeSlugs") or [])}
