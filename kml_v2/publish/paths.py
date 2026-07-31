"""Path helpers for the KML V2 tree."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
MEDIA = ROOT / "media"
OUT_ROOT = ROOT  # generated HTML lives in the site tree


def lesson_pack_dir(lesson_id: str) -> Path:
    return DATA / "lessons" / lesson_id


def site_root_for(output_relpath: str) -> str:
    """Relative path from an output HTML file back to kml_v2/."""
    depth = Path(output_relpath).parent.as_posix().count("/")
    if Path(output_relpath).parent.as_posix() in (".", ""):
        return "."
    return "/".join([".."] * (depth + 1)) if depth >= 0 else "."
