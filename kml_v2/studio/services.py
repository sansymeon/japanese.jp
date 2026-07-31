"""Studio services — dashboard model & actions over the publish engine.

No metadata schema changes. Lifecycle display maps existing lesson.status.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from publish import paths
from publish.engine import build_all, build_book, build_lesson, build_site
from publish.loaders import load_book, load_lesson
from publish.validate import ValidationError, project_status, validate_pack_files

# Session activity (process lifetime). Later: .studio/activity.jsonl
_ACTIVITY: list[dict[str, Any]] = []


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def log_activity(action: str, detail: str = "", ok: bool = True) -> None:
    _ACTIVITY.insert(
        0,
        {"time": _now(), "action": action, "detail": detail, "ok": ok},
    )
    del _ACTIVITY[50:]


def activity() -> list[dict[str, Any]]:
    return list(_ACTIVITY)


def workflow_stage(status: str, warnings: list[str], output_exists: bool) -> str:
    """Derive display stage from existing fields (no new schema)."""
    if status == "published":
        return "Publish"
    if status == "ready":
        return "Generate"
    if status == "planned":
        return "Create"
    # draft
    if warnings:
        if any("hero" in w.lower() for w in warnings):
            return "Assets"
        if any("YouTube" in w for w in warnings) and output_exists:
            return "Publish"
        return "Author"
    if output_exists:
        return "Preview"
    return "Author"


@dataclass
class LessonRow:
    id: str
    title: str
    status: str
    stage: str
    warnings: list[str] = field(default_factory=list)
    valid: bool | None = None
    validation_errors: list[str] = field(default_factory=list)
    output_path: str = ""
    output_exists: bool = False
    kanji_count: int | None = None
    book_id: str = ""
    number: int = 0


def enrich_lessons(run_validate: bool = False) -> list[LessonRow]:
    raw = project_status()
    rows: list[LessonRow] = []
    for item in raw["lessons"]:
        lid = item["id"]
        pack = paths.DATA / "lessons" / lid
        lesson = json.loads((pack / "lesson.json").read_text(encoding="utf-8"))
        out_rel = lesson.get("path") or ""
        out_exists = bool(out_rel) and (paths.ROOT / out_rel).exists()
        warns = list(item.get("warnings") or [])
        # Media file existence (logical path under media/)
        assets_path = pack / "assets.json"
        if assets_path.exists():
            hero = (json.loads(assets_path.read_text(encoding="utf-8")).get("paths") or {}).get(
                "hero"
            )
            if hero and not (paths.ROOT / hero).exists():
                if "hero file missing on disk" not in warns:
                    warns.append("hero file missing on disk")

        errs: list[str] = []
        valid: bool | None = None
        if run_validate:
            errs = validate_pack_files(lid)
            valid = not errs

        rows.append(
            LessonRow(
                id=lid,
                title=item.get("title") or lid,
                status=item.get("status") or "planned",
                stage=workflow_stage(item.get("status") or "planned", warns, out_exists),
                warnings=warns,
                valid=valid,
                validation_errors=errs,
                output_path=out_rel,
                output_exists=out_exists,
                kanji_count=lesson.get("focus", {}).get("kanji_count")
                if isinstance(lesson.get("focus"), dict)
                else None,
                book_id=lesson.get("book_id") or "",
                number=int(lesson.get("number") or 0),
            )
        )
    return rows


def dashboard(run_validate: bool = False) -> dict[str, Any]:
    lessons = enrich_lessons(run_validate=run_validate)
    by_status: dict[str, int] = {}
    for row in lessons:
        by_status[row.status] = by_status.get(row.status, 0) + 1

    attention = [
        row
        for row in lessons
        if row.warnings or row.valid is False or row.status in ("planned", "draft")
    ]

    books = []
    books_dir = paths.DATA / "books"
    for path in sorted(books_dir.glob("book_*.json")):
        try:
            book = load_book(path.stem)
            present = sum(
                1
                for lid in book.lesson_ids
                if (paths.DATA / "lessons" / lid / "lesson.json").exists()
            )
            books.append(
                {
                    "id": book.id,
                    "title": book.title,
                    "number": book.number,
                    "status": book.status,
                    "lesson_ids": len(book.lesson_ids),
                    "packs_present": present,
                    "path": book.path,
                    "output_exists": (paths.ROOT / book.path).exists(),
                }
            )
        except Exception as e:  # noqa: BLE001
            books.append({"id": path.stem, "error": str(e)})

    missing_heroes = [r.id for r in lessons if any("hero" in w.lower() for w in r.warnings)]
    missing_youtube = [r.id for r in lessons if any("YouTube" in w for w in r.warnings)]
    missing_gallery = [r.id for r in lessons if any("gallery" in w.lower() for w in r.warnings)]
    unpublished = [r.id for r in lessons if r.status != "published"]

    return {
        "summary": {
            "lesson_count": len(lessons),
            "by_status": by_status,
            "warning_lessons": sum(1 for r in lessons if r.warnings),
            "validation_failures": sum(1 for r in lessons if r.valid is False),
            "generated": sum(1 for r in lessons if r.output_exists),
            "published": by_status.get("published", 0),
        },
        "lessons": lessons,
        "books": books,
        "attention": attention[:12],
        "missing_heroes": missing_heroes,
        "missing_youtube": missing_youtube,
        "missing_gallery": missing_gallery,
        "unpublished": unpublished,
        "activity": activity(),
        "generated_at": _now(),
    }


def lesson_detail(lesson_id: str) -> dict[str, Any]:
    pack = paths.DATA / "lessons" / lesson_id
    if not pack.is_dir():
        raise FileNotFoundError(lesson_id)
    core = json.loads((pack / "lesson.json").read_text(encoding="utf-8"))
    files = sorted(p.name for p in pack.glob("*.json"))
    counts = {}
    for name in ("kanji", "vocabulary", "phrases", "compounds"):
        path = pack / f"{name}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            counts[name] = data.get("count", len(data.get("items") or []))
    errs = validate_pack_files(lesson_id)
    rows = {r.id: r for r in enrich_lessons(run_validate=False)}
    row = rows.get(lesson_id)
    return {
        "lesson": core,
        "row": row,
        "files": files,
        "counts": counts,
        "validation_errors": errs,
        "valid": not errs,
        "pack_rel": str(pack.relative_to(paths.ROOT)),
        "output_path": core.get("path"),
        "output_exists": bool(core.get("path")) and (paths.ROOT / core["path"]).exists(),
    }


def action_create(lesson_id: str) -> dict[str, Any]:
    from publish.cli import _cmd_create
    import argparse

    code = _cmd_create(argparse.Namespace(lesson_id=lesson_id))
    ok = code == 0
    log_activity("create", lesson_id, ok=ok)
    return {"ok": ok, "lesson_id": lesson_id, "code": code}


def action_validate(lesson_id: str) -> dict[str, Any]:
    errs = validate_pack_files(lesson_id)
    ok = not errs
    log_activity("validate", lesson_id if ok else f"{lesson_id}: {len(errs)} issue(s)", ok=ok)
    return {"ok": ok, "lesson_id": lesson_id, "errors": errs}


def action_build_lesson(lesson_id: str) -> dict[str, Any]:
    try:
        out = build_lesson(lesson_id)
        log_activity("build lesson", str(out.relative_to(paths.ROOT)), ok=True)
        return {"ok": True, "path": str(out.relative_to(paths.ROOT))}
    except ValidationError as e:
        log_activity("build lesson", lesson_id, ok=False)
        return {"ok": False, "errors": e.messages}
    except Exception as e:  # noqa: BLE001
        log_activity("build lesson", str(e), ok=False)
        return {"ok": False, "errors": [str(e)]}


def action_build_book(book_id: str) -> dict[str, Any]:
    try:
        out = build_book(book_id)
        log_activity("build book", str(out.relative_to(paths.ROOT)), ok=True)
        return {"ok": True, "path": str(out.relative_to(paths.ROOT))}
    except Exception as e:  # noqa: BLE001
        log_activity("build book", str(e), ok=False)
        return {"ok": False, "errors": [str(e)]}


def action_build_site() -> dict[str, Any]:
    try:
        outs = build_site()
        rels = [str(p.relative_to(paths.ROOT)) for p in outs]
        log_activity("build site", ", ".join(rels), ok=True)
        return {"ok": True, "paths": rels}
    except Exception as e:  # noqa: BLE001
        log_activity("build site", str(e), ok=False)
        return {"ok": False, "errors": [str(e)]}


def action_build_all() -> dict[str, Any]:
    results = build_all()
    ok = not results.get("errors")
    log_activity("build all", "ok" if ok else "with errors", ok=ok)
    return {"ok": ok, "results": results}


def suggest_next_lesson_id() -> str:
    lessons_dir = paths.DATA / "lessons"
    nums = []
    for p in lessons_dir.iterdir():
        if p.is_dir() and p.name.startswith("lesson_"):
            try:
                nums.append(int(p.name.replace("lesson_", "")))
            except ValueError:
                pass
    n = max(nums) + 1 if nums else 1
    return f"lesson_{n:03d}"
