"""Validation for the publishing engine (blocks incomplete renders)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from . import paths
from .models import Lesson


class ValidationError(Exception):
    def __init__(self, messages: list[str]):
        self.messages = messages
        super().__init__("\n".join(messages))


def validate_pack_files(lesson_id: str) -> list[str]:
    """Run structural validator; return error strings (empty = ok)."""
    script = paths.ROOT / "scripts" / "validate_metadata.py"
    py = sys.executable
    result = subprocess.run(
        [py, str(script), "--lesson", lesson_id],
        cwd=str(paths.ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return []
    lines = [
        line.strip()
        for line in (result.stdout + result.stderr).splitlines()
        if "FAIL" in line or "ERROR" in line or "missing" in line.lower()
    ]
    if not lines:
        lines = [result.stdout.strip() or result.stderr.strip() or "validation failed"]
    return lines


def validate_lesson_object(lesson: Lesson) -> list[str]:
    """Business-level checks before render."""
    errs: list[str] = []
    if not lesson.title:
        errs.append("lesson.title is required")
    if not lesson.path:
        errs.append("lesson.path is required")
    if not lesson.kanji:
        errs.append("kanji roster is empty — kanji.json must list characters")
    ids = [k.id for k in lesson.kanji]
    if len(ids) != len(set(ids)):
        errs.append("duplicate kanji ids in roster")
    chars = [k.character for k in lesson.kanji]
    if len(chars) != len(set(chars)):
        errs.append("duplicate kanji characters in roster")
    return errs


def ensure_valid_lesson(lesson_id: str, lesson: Lesson) -> None:
    messages = validate_pack_files(lesson_id) + validate_lesson_object(lesson)
    if messages:
        raise ValidationError(messages)


def project_status() -> dict:
    """Summary status for `kml status` / future dashboard."""
    lessons_dir = paths.DATA / "lessons"
    packs = sorted(
        p.name for p in lessons_dir.iterdir() if p.is_dir() and p.name.startswith("lesson_")
    )
    rows = []
    for lid in packs:
        pack = lessons_dir / lid
        lesson = json.loads((pack / "lesson.json").read_text(encoding="utf-8"))
        assets = {}
        assets_path = pack / "assets.json"
        if assets_path.exists():
            assets = json.loads(assets_path.read_text(encoding="utf-8")).get("paths") or {}
        youtube = {}
        yt_path = pack / "youtube.json"
        if yt_path.exists():
            youtube = json.loads(yt_path.read_text(encoding="utf-8"))
        compounds = pack / "compounds.json"
        gallery = pack / "gallery.json"
        warnings = []
        if not assets.get("hero"):
            warnings.append("missing hero path")
        if not youtube.get("id"):
            warnings.append("missing YouTube id")
        if not compounds.exists():
            warnings.append("missing compounds.json")
        if not gallery.exists():
            warnings.append("missing gallery.json")
        rows.append(
            {
                "id": lid,
                "title": lesson.get("title"),
                "status": lesson.get("status"),
                "warnings": warnings,
                "ok": not warnings and lesson.get("status") in ("draft", "ready", "published"),
            }
        )
    return {"lessons": rows, "count": len(rows)}
