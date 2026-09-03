"""Load Quiet Cinematic drafts from the Lessons 21–40 keeper shortlist."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEEPERS_PATH = (
    ROOT.parent
    / "tmp"
    / "lessons_21_40_extended_exhibition_review"
    / "candidates.json"
)
ASSETS = ROOT.parents[1] / "assets"


def keeper_items(start: int, end: int) -> list[dict]:
    if not KEEPERS_PATH.is_file():
        raise SystemExit(f"Missing keeper shortlist: {KEEPERS_PATH}")
    data = json.loads(KEEPERS_PATH.read_text(encoding="utf-8"))
    items = [
        item
        for item in (data.get("items") or [])
        if start <= int(item["lesson"]) <= end
    ]
    if not items:
        raise SystemExit(f"No keepers for lessons {start}–{end}")
    missing = [
        item["image"]
        for item in items
        if not (ASSETS / item["image"]).is_file()
    ]
    if missing:
        preview = ", ".join(missing[:8])
        raise SystemExit(f"Missing {len(missing)} keeper images (e.g. {preview})")
    return items


def write_draft(
    path: Path,
    *,
    collection_id: str,
    title: str,
    start: int,
    end: int,
    items: list[dict],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "id": collection_id,
                "title": title,
                "lessons": list(range(start, end + 1)),
                "source": str(KEEPERS_PATH.relative_to(ROOT.parent.parent)),
                "itemCount": len(items),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
