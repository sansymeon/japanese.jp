"""Load lesson / book packs into typed objects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import paths
from .models import (
    Book,
    BookLessonRef,
    Compound,
    Gallery,
    GalleryCollection,
    Kanji,
    KanjiAssets,
    Lesson,
    LessonAssets,
    LessonFocus,
    Navigation,
    Phrase,
    Readings,
    Verse,
    VocabularyItem,
    YouTubeMeta,
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def load_lesson(lesson_id: str, root: Path | None = None) -> Lesson:
    """Public API: load a complete Lesson object from its pack."""
    base = (root or paths.ROOT) / "data" / "lessons" / lesson_id
    if not base.is_dir():
        raise FileNotFoundError(f"Lesson pack not found: {base}")

    core = _load_json(base / "lesson.json")
    kanji_doc = _load_json(base / "kanji.json")
    vocab_doc = _optional_json(base / "vocabulary.json") or {"items": []}
    phrases_doc = _optional_json(base / "phrases.json") or {"items": []}
    compounds_doc = _optional_json(base / "compounds.json") or {"items": []}
    gallery_doc = _optional_json(base / "gallery.json")
    youtube_doc = _optional_json(base / "youtube.json")
    assets_doc = _optional_json(base / "assets.json")

    focus_raw = core.get("focus") or {}
    nav_raw = core.get("navigation") or {}

    kanji: list[Kanji] = []
    for item in kanji_doc.get("items") or []:
        readings = item.get("readings") or {}
        verse = item.get("verse") or {}
        assets = item.get("assets") or {}
        kanji.append(
            Kanji(
                id=item["id"],
                ord=int(item["ord"]),
                character=item["character"],
                slug=item["slug"],
                keyword=item["keyword"],
                heisig_number=item.get("heisig_number"),
                strokes=item.get("strokes"),
                grade=item.get("grade"),
                category=item.get("category"),
                unicode=item.get("unicode"),
                readings=Readings(
                    on=list(readings.get("on") or []),
                    kun=list(readings.get("kun") or []),
                ),
                primitives=list(item.get("primitives") or []),
                verse=Verse(jp=verse.get("jp") or "", en=verse.get("en") or ""),
                assets=KanjiAssets(
                    study_image=assets.get("study_image"),
                    stroke_page=assets.get("stroke_page"),
                ),
                status=item.get("status") or "draft",
            )
        )

    vocabulary = [
        VocabularyItem(
            id=i["id"],
            surface=i["surface"],
            reading=i.get("reading"),
            meaning=i.get("meaning"),
            from_kanji_slug=i.get("from_kanji_slug"),
            anchor_character=i.get("anchor_character"),
        )
        for i in vocab_doc.get("items") or []
    ]
    phrases = [
        Phrase(
            id=i["id"],
            surface=i["surface"],
            reading=i.get("reading"),
            meaning=i.get("meaning"),
            from_kanji_slug=i.get("from_kanji_slug"),
            anchor_character=i.get("anchor_character"),
        )
        for i in phrases_doc.get("items") or []
    ]
    compounds = [
        Compound(
            id=i["id"],
            surface=i["surface"],
            reading=i.get("reading"),
            meaning=i.get("meaning"),
            kanji_slug=i.get("kanji_slug"),
            anchor_character=i.get("anchor_character"),
        )
        for i in compounds_doc.get("items") or []
    ]

    gallery = None
    if gallery_doc:
        gallery = Gallery(
            lesson_id=gallery_doc.get("lesson_id") or lesson_id,
            status=gallery_doc.get("status") or "draft",
            collections=[
                GalleryCollection(
                    id=c["id"],
                    kind=c.get("kind") or "",
                    title=c.get("title") or c["id"],
                    role=c.get("role") or "",
                    source_ref=c.get("source_ref"),
                    prototype=bool(c.get("prototype")),
                    experimental=bool(c.get("experimental")),
                )
                for c in gallery_doc.get("collections") or []
            ],
            related_gallery_ids=list(gallery_doc.get("related_gallery_ids") or []),
            notes=gallery_doc.get("notes") or "",
        )

    youtube = None
    if youtube_doc:
        youtube = YouTubeMeta(
            lesson_id=youtube_doc.get("lesson_id") or lesson_id,
            id=youtube_doc.get("id"),
            title=youtube_doc.get("title"),
            description=youtube_doc.get("description"),
            published_at=youtube_doc.get("published_at"),
            playlist_ids=list(youtube_doc.get("playlist_ids") or []),
            chapters=list(youtube_doc.get("chapters") or []),
            status=youtube_doc.get("status") or "unpublished",
            notes=youtube_doc.get("notes") or "",
        )

    assets = None
    if assets_doc:
        p = assets_doc.get("paths") or {}
        assets = LessonAssets(
            lesson_id=assets_doc.get("lesson_id") or lesson_id,
            hero=p.get("hero"),
            thumbnail=p.get("thumbnail"),
            study_image=p.get("study_image"),
            audio=p.get("audio"),
            video=p.get("video"),
            logical_layout=dict(assets_doc.get("logical_layout") or {}),
            source_refs=dict(assets_doc.get("source_refs") or {}),
            notes=assets_doc.get("notes") or "",
        )

    out_path = core.get("path") or f"books/{core.get('book_id')}/lessons/{lesson_id}.html"
    site_root = paths.site_root_for(out_path)

    book_number = int(core.get("book_number") or 1)
    book_title = f"Book {book_number}"

    return Lesson(
        id=core["id"],
        number=int(core["number"]),
        book_id=core["book_id"],
        book_number=book_number,
        title=core["title"],
        path=out_path,
        status=core.get("status") or "draft",
        subtitle=core.get("subtitle"),
        slug=core.get("slug"),
        summary=core.get("summary"),
        tags=list(core.get("tags") or []),
        notes=core.get("notes") or "",
        gallery_url=(core.get("gallery_url") or "").strip() or None,
        focus=LessonFocus(
            heisig_start=focus_raw.get("heisig_start"),
            heisig_end=focus_raw.get("heisig_end"),
            kanji_count=focus_raw.get("kanji_count"),
            opening_character=focus_raw.get("opening_character"),
            closing_character=focus_raw.get("closing_character"),
            primary_keyword=focus_raw.get("primary_keyword"),
        ),
        navigation=Navigation(
            prev_id=nav_raw.get("prev_id"),
            next_id=nav_raw.get("next_id"),
            prev_href=nav_raw.get("prev_href"),
            next_href=nav_raw.get("next_href"),
            prev_label=nav_raw.get("prev_label") or "Previous",
            next_label=nav_raw.get("next_label") or "Next",
        ),
        publication=dict(core.get("publication") or {}),
        relationships=dict(core.get("relationships") or {}),
        kanji=kanji,
        vocabulary=vocabulary,
        phrases=phrases,
        compounds=compounds,
        gallery=gallery,
        youtube=youtube,
        assets=assets,
        site_root=site_root,
        book_title=book_title,
        book_href="../index.html",
        output_relpath=out_path,
    )


def load_book(book_id: str, root: Path | None = None) -> Book:
    """Public API: load a Book with lesson refs from indexes."""
    root = root or paths.ROOT
    book_path = root / "data" / "books" / f"{book_id}.json"
    index_path = root / "data" / "lessons" / "index.json"
    if not book_path.exists():
        raise FileNotFoundError(f"Book metadata not found: {book_path}")

    raw = _load_json(book_path)
    index = _load_json(index_path) if index_path.exists() else {"lessons": []}
    by_id = {row["id"]: row for row in index.get("lessons") or []}

    lessons: list[BookLessonRef] = []
    for lid in raw.get("lesson_ids") or []:
        row = by_id.get(lid)
        if not row:
            # Pack may exist without index entry — soft ref
            lessons.append(
                BookLessonRef(
                    id=lid,
                    number=int(lid.replace("lesson_", "") or 0),
                    title=lid,
                    path="",
                    status="planned",
                    href="",
                )
            )
            continue
        rel = row.get("path") or ""
        # From books/book_01/index.html → lessons/lesson_01.html
        href = ""
        if rel.startswith(f"books/{book_id}/"):
            href = "./" + rel[len(f"books/{book_id}/") :]
        elif rel:
            href = f"{paths.site_root_for(raw.get('path') or f'books/{book_id}/index.html')}/{rel}"
        lessons.append(
            BookLessonRef(
                id=row["id"],
                number=int(row["number"]),
                title=row.get("title") or row["id"],
                path=rel,
                status=row.get("status") or "planned",
                subtitle=row.get("subtitle"),
                opening_character=row.get("opening_character"),
                kanji_count=row.get("kanji_count"),
                href=href,
            )
        )

    out_path = raw.get("path") or f"books/{book_id}/index.html"
    return Book(
        id=raw["id"],
        number=int(raw["number"]),
        title=raw["title"],
        path=out_path,
        status=raw.get("status") or "draft",
        subtitle=raw.get("subtitle"),
        description=raw.get("description"),
        lesson_start=raw.get("lesson_start"),
        lesson_end=raw.get("lesson_end"),
        lesson_ids=list(raw.get("lesson_ids") or []),
        cover=raw.get("cover"),
        tags=list(raw.get("tags") or []),
        lessons=lessons,
        site_root=paths.site_root_for(out_path),
        output_relpath=out_path,
    )
