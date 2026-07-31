"""CLI for the KML Publishing Engine.

  python -m publish build lesson lesson_001
  python -m publish build book book_01
  python -m publish build all
  python -m publish validate lesson_001
  python -m publish status
  python -m publish create lesson_003
  python -m publish report missing
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import paths
from .engine import build_all, build_book, build_lesson, build_site
from .validate import ValidationError, project_status, validate_pack_files


def _cmd_build(args: argparse.Namespace) -> int:
    target = args.target
    name = args.name
    try:
        if target == "lesson":
            if not name:
                print("error: build lesson requires an id (e.g. lesson_001)", file=sys.stderr)
                return 2
            out = build_lesson(name)
            print(f"Built {out.relative_to(paths.ROOT)}")
            return 0
        if target == "book":
            if not name:
                print("error: build book requires an id (e.g. book_01)", file=sys.stderr)
                return 2
            out = build_book(name)
            print(f"Built {out.relative_to(paths.ROOT)}")
            return 0
        if target == "site":
            outs = build_site()
            for out in outs:
                print(f"Built {out.relative_to(paths.ROOT)}")
            return 0
        if target == "all":
            results = build_all()
            for rel in results["lessons"]:
                print(f"Built lesson {rel}")
            for rel in results["books"]:
                print(f"Built book   {rel}")
            for rel in results["site"]:
                print(f"Built site   {rel}")
            if results["errors"]:
                print("\nErrors:", file=sys.stderr)
                for err in results["errors"]:
                    for key, msgs in err.items():
                        print(f"  {key}:", file=sys.stderr)
                        for m in msgs:
                            print(f"    - {m}", file=sys.stderr)
                return 1
            print("\nAll builds succeeded.")
            return 0
        print(f"Unknown build target: {target}", file=sys.stderr)
        return 2
    except ValidationError as e:
        print(f"Validation failed for {name or target}:", file=sys.stderr)
        for m in e.messages:
            print(f"  - {m}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _cmd_validate(args: argparse.Namespace) -> int:
    lesson_id = args.lesson_id
    errs = validate_pack_files(lesson_id)
    if errs:
        print(f"FAIL {lesson_id}")
        for m in errs:
            print(f"  - {m}")
        return 1
    print(f"OK   {lesson_id}")
    return 0


def _cmd_status(_args: argparse.Namespace) -> int:
    status = project_status()
    print(f"Lessons: {status['count']}")
    for row in status["lessons"]:
        mark = "✔" if not row["warnings"] else "⚠"
        warn = f"  ({', '.join(row['warnings'])})" if row["warnings"] else ""
        print(f"  {mark} {row['id']:12} {row['status']:10} {row['title']}{warn}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    status = project_status()
    kind = args.kind
    for row in status["lessons"]:
        warns = row["warnings"]
        if kind == "missing":
            if warns:
                print(f"{row['id']}: {', '.join(warns)}")
        elif kind == "drafts":
            if row["status"] == "draft":
                print(row["id"])
        elif kind == "youtube":
            if "missing YouTube id" in warns:
                print(row["id"])
        elif kind == "heroes":
            if "missing hero path" in warns:
                print(row["id"])
    return 0


def _cmd_create(args: argparse.Namespace) -> int:
    """Scaffold an empty pack from lesson_001 template shape."""
    lesson_id = args.lesson_id
    if not lesson_id.startswith("lesson_"):
        print("error: id must look like lesson_003", file=sys.stderr)
        return 2
    dest = paths.DATA / "lessons" / lesson_id
    if dest.exists():
        print(f"error: pack already exists: {dest}", file=sys.stderr)
        return 1
    src = paths.DATA / "lessons" / "lesson_001"
    dest.mkdir(parents=True)
    # Minimal stubs — copy schemas structure with empty items
    number = int(lesson_id.replace("lesson_", ""))
    stubs = {
        "lesson.json": {
            "$schema": "../../schema/lesson.schema.json",
            "id": lesson_id,
            "number": number,
            "book_id": "book_01",
            "book_number": 1,
            "title": f"Lesson {number}",
            "subtitle": None,
            "summary": None,
            "status": "planned",
            "pack": {
                "kanji": "kanji.json",
                "vocabulary": "vocabulary.json",
                "phrases": "phrases.json",
                "compounds": "compounds.json",
                "gallery": "gallery.json",
                "youtube": "youtube.json",
                "assets": "assets.json",
            },
            "focus": {"kanji_count": 0},
            "navigation": {},
            "relationships": {
                "ambient_ids": [],
                "playlist_ids": [],
                "beyond_joyo_ids": [],
                "vocabulary_section_ids": [],
            },
            "publication": {
                "website": False,
                "youtube": False,
                "recorded": False,
                "edited": False,
                "ambient_exhibitions": False,
            },
            "path": f"books/book_01/lessons/lesson_{number:02d}.html",
            "tags": [],
            "notes": "Scaffolded by `python -m publish create`.",
        },
        "kanji.json": {
            "$schema": "../../schema/kanji.schema.json",
            "lesson_id": lesson_id,
            "count": 0,
            "items": [],
        },
        "vocabulary.json": {
            "$schema": "../../schema/vocabulary.schema.json",
            "lesson_id": lesson_id,
            "count": 0,
            "items": [],
        },
        "phrases.json": {
            "$schema": "../../schema/phrases.schema.json",
            "lesson_id": lesson_id,
            "count": 0,
            "items": [],
        },
        "compounds.json": {
            "$schema": "../../schema/compounds.schema.json",
            "lesson_id": lesson_id,
            "count": 0,
            "items": [],
        },
        "gallery.json": {
            "$schema": "../../schema/lesson_gallery.schema.json",
            "lesson_id": lesson_id,
            "collections": [],
            "related_gallery_ids": [],
            "pieces": [],
        },
        "youtube.json": {
            "$schema": "../../schema/lesson_youtube.schema.json",
            "lesson_id": lesson_id,
            "id": None,
            "status": "unpublished",
            "playlist_ids": [],
            "chapters": [],
        },
        "assets.json": {
            "$schema": "../../schema/lesson_assets.schema.json",
            "lesson_id": lesson_id,
            "paths": {
                "hero": f"media/lessons/{lesson_id}/cover.png",
                "thumbnail": f"media/lessons/{lesson_id}/thumb.jpg",
                "study_image": None,
                "audio": None,
                "video": None,
            },
        },
    }
    for name, data in stubs.items():
        (dest / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Created pack {dest.relative_to(paths.ROOT)}")
    print("Next: fill kanji.json / lesson.json, then: python -m publish validate", lesson_id)
    print("      python -m publish build lesson", lesson_id)
    # silence unused
    _ = shutil, src
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m publish",
        description="KML V2 Publishing Engine",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Render HTML from metadata")
    p_build.add_argument(
        "target",
        choices=["lesson", "book", "site", "all"],
        help="What to build",
    )
    p_build.add_argument("name", nargs="?", help="lesson_001 / book_01")
    p_build.set_defaults(func=_cmd_build)

    p_val = sub.add_parser("validate", help="Validate a lesson pack")
    p_val.add_argument("lesson_id")
    p_val.set_defaults(func=_cmd_validate)

    p_status = sub.add_parser("status", help="Project lesson status")
    p_status.set_defaults(func=_cmd_status)

    p_report = sub.add_parser("report", help="Missing-asset style reports")
    p_report.add_argument(
        "kind",
        choices=["missing", "drafts", "youtube", "heroes"],
    )
    p_report.set_defaults(func=_cmd_report)

    p_create = sub.add_parser("create", help="Scaffold a new lesson pack")
    p_create.add_argument("lesson_id")
    p_create.set_defaults(func=_cmd_create)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
