#!/usr/bin/env python3
"""
Validate KML V2 lesson metadata packs.

Usage:
  python3 kml_v2/scripts/validate_metadata.py
  python3 kml_v2/scripts/validate_metadata.py --lesson lesson_001

Runs structural checks with no third-party deps.
If jsonschema is installed, also validates against Draft 2020-12 schemas.

  pip install -r kml_v2/scripts/requirements-validate.txt   # optional
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMA_DIR = DATA / "schema"

PACK_FILES = {
    "lesson": "lesson.schema.json",
    "kanji": "kanji.schema.json",
    "vocabulary": "vocabulary.schema.json",
    "phrases": "phrases.schema.json",
    "compounds": "compounds.schema.json",
    "gallery": "lesson_gallery.schema.json",
    "youtube": "lesson_youtube.schema.json",
    "assets": "lesson_assets.schema.json",
}

REQUIRED = tuple(PACK_FILES.keys())


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def structural_check(pack: Path) -> list[str]:
    errs: list[str] = []
    for stem in REQUIRED:
        path = pack / f"{stem}.json"
        if not path.exists():
            errs.append(f"missing required {stem}.json")
            continue
        try:
            data = load(path)
        except json.JSONDecodeError as e:
            errs.append(f"{stem}.json: invalid JSON ({e})")
            continue

        if not isinstance(data, dict):
            errs.append(f"{stem}.json: root must be object")
            continue

        if stem == "lesson":
            for key in ("id", "number", "book_id", "title", "status", "path"):
                if key not in data:
                    errs.append(f"lesson.json: missing {key}")
            if data.get("id") != pack.name:
                errs.append(
                    f"lesson.json id ({data.get('id')!r}) != folder ({pack.name!r})"
                )
        elif stem == "kanji":
            if data.get("lesson_id") != pack.name:
                errs.append("kanji.json lesson_id mismatch")
            items = data.get("items")
            if not isinstance(items, list) or not items:
                errs.append("kanji.json: items must be a non-empty array")
            else:
                for i, item in enumerate(items):
                    for key in ("id", "ord", "character", "slug", "keyword"):
                        if key not in item:
                            errs.append(f"kanji.items[{i}]: missing {key}")
                if data.get("count") is not None and data["count"] != len(items):
                    errs.append(
                        f"kanji.count ({data['count']}) != len(items) ({len(items)})"
                    )
        elif stem in ("vocabulary", "phrases", "compounds"):
            if data.get("lesson_id") != pack.name:
                errs.append(f"{stem}.json lesson_id mismatch")
            items = data.get("items")
            if not isinstance(items, list):
                errs.append(f"{stem}.json: items must be an array")
            elif data.get("count") is not None and data["count"] != len(items):
                errs.append(
                    f"{stem}.count ({data['count']}) != len(items) ({len(items)})"
                )
        elif stem in ("gallery", "youtube", "assets"):
            if data.get("lesson_id") != pack.name:
                errs.append(f"{stem}.json lesson_id mismatch")

    return errs


def schema_check(pack: Path) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return []  # optional

    errs: list[str] = []
    for stem, schema_name in PACK_FILES.items():
        path = pack / f"{stem}.json"
        schema_path = SCHEMA_DIR / schema_name
        if not path.exists() or not schema_path.exists():
            continue
        validator = Draft202012Validator(load(schema_path))
        for e in sorted(validator.iter_errors(load(path)), key=lambda x: list(x.path)):
            loc = ".".join(str(p) for p in e.path) or "(root)"
            errs.append(f"{stem}.json {loc}: {e.message}")
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", help="Validate only this pack id")
    args = parser.parse_args()

    packs = sorted(
        p
        for p in (DATA / "lessons").iterdir()
        if p.is_dir() and p.name.startswith("lesson_")
    )
    if args.lesson:
        packs = [p for p in packs if p.name == args.lesson]
        if not packs:
            print(f"ERROR: pack not found: {args.lesson}", file=sys.stderr)
            return 2

    try:
        import jsonschema  # noqa: F401

        schema_mode = "on"
    except ImportError:
        schema_mode = "off (install jsonschema for Draft 2020-12 checks)"

    print(f"JSON Schema validation: {schema_mode}")
    errors = 0

    for pack in packs:
        print(f"Validating {pack.name}/")
        problems = structural_check(pack) + schema_check(pack)
        if problems:
            for msg in problems:
                print(f"  FAIL  {msg}")
            errors += len(problems)
        else:
            print("  ok    structural" + (" + schema" if schema_mode == "on" else ""))

    for rel in (
        "books/index.json",
        "lessons/index.json",
        "playlists/index.json",
        "site/sitemap.json",
        "site/navigation.json",
    ):
        path = DATA / rel
        if path.exists():
            try:
                load(path)
                print(f"ok      data/{rel}")
            except json.JSONDecodeError as e:
                print(f"FAIL    data/{rel}: {e}")
                errors += 1

    if errors:
        print(f"\n{errors} validation problem(s).")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
