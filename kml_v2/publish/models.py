"""Typed lesson / book objects for the publishing engine.

Templates receive these objects — never raw JSON.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Readings:
    on: list[str] = field(default_factory=list)
    kun: list[str] = field(default_factory=list)


@dataclass
class Verse:
    jp: str = ""
    en: str = ""


@dataclass
class KanjiAssets:
    study_image: str | None = None
    stroke_page: str | None = None


@dataclass
class Kanji:
    id: str
    ord: int
    character: str
    slug: str
    keyword: str
    heisig_number: int | None = None
    strokes: int | None = None
    grade: str | None = None
    category: str | None = None
    unicode: str | None = None
    readings: Readings = field(default_factory=Readings)
    primitives: list[str] = field(default_factory=list)
    verse: Verse = field(default_factory=Verse)
    assets: KanjiAssets = field(default_factory=KanjiAssets)
    status: str = "draft"

    @property
    def on_display(self) -> str:
        return self.readings.on[0] if self.readings.on else "—"


@dataclass
class VocabularyItem:
    id: str
    surface: str
    reading: str | None = None
    meaning: str | None = None
    from_kanji_slug: str | None = None
    anchor_character: str | None = None


@dataclass
class Phrase:
    id: str
    surface: str
    reading: str | None = None
    meaning: str | None = None
    from_kanji_slug: str | None = None
    anchor_character: str | None = None


@dataclass
class Compound:
    id: str
    surface: str
    reading: str | None = None
    meaning: str | None = None
    kanji_slug: str | None = None
    anchor_character: str | None = None


@dataclass
class GalleryCollection:
    id: str
    kind: str
    title: str
    role: str = ""
    source_ref: str | None = None
    prototype: bool = False
    experimental: bool = False


@dataclass
class Gallery:
    lesson_id: str
    status: str = "draft"
    collections: list[GalleryCollection] = field(default_factory=list)
    related_gallery_ids: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class YouTubeMeta:
    lesson_id: str
    id: str | None = None
    title: str | None = None
    description: str | None = None
    published_at: str | None = None
    playlist_ids: list[str] = field(default_factory=list)
    chapters: list[dict[str, Any]] = field(default_factory=list)
    status: str = "unpublished"
    notes: str = ""

    @property
    def published(self) -> bool:
        return bool(self.id)


@dataclass
class LessonAssets:
    lesson_id: str
    hero: str | None = None
    thumbnail: str | None = None
    study_image: str | None = None
    audio: str | None = None
    video: str | None = None
    logical_layout: dict[str, Any] = field(default_factory=dict)
    source_refs: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class Navigation:
    prev_id: str | None = None
    next_id: str | None = None
    prev_href: str | None = None
    next_href: str | None = None
    prev_label: str = "Previous"
    next_label: str = "Next"


@dataclass
class LessonFocus:
    heisig_start: int | None = None
    heisig_end: int | None = None
    kanji_count: int | None = None
    opening_character: str | None = None
    closing_character: str | None = None
    primary_keyword: str | None = None


@dataclass
class Lesson:
    """Complete render-ready lesson object."""

    id: str
    number: int
    book_id: str
    book_number: int
    title: str
    path: str
    status: str = "draft"
    subtitle: str | None = None
    slug: str | None = None
    summary: str | None = None
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    gallery_url: str | None = None
    focus: LessonFocus = field(default_factory=LessonFocus)
    navigation: Navigation = field(default_factory=Navigation)
    publication: dict[str, Any] = field(default_factory=dict)
    relationships: dict[str, Any] = field(default_factory=dict)

    kanji: list[Kanji] = field(default_factory=list)
    vocabulary: list[VocabularyItem] = field(default_factory=list)
    phrases: list[Phrase] = field(default_factory=list)
    compounds: list[Compound] = field(default_factory=list)
    gallery: Gallery | None = None
    youtube: YouTubeMeta | None = None
    assets: LessonAssets | None = None

    # Computed for templates (filled by loader / engine)
    site_root: str = "../../.."
    book_title: str = "Book"
    book_href: str = "../index.html"
    output_relpath: str = ""

    @property
    def opening_character(self) -> str:
        if self.focus.opening_character:
            return self.focus.opening_character
        if self.kanji:
            return self.kanji[0].character
        return "字"

    @property
    def opening_keyword(self) -> str:
        if self.focus.primary_keyword:
            return self.focus.primary_keyword
        if self.kanji:
            return self.kanji[0].keyword
        return self.title

    @property
    def kanji_count(self) -> int:
        return self.focus.kanji_count or len(self.kanji)

    @property
    def vocabulary_count(self) -> int:
        return len(self.vocabulary)

    @property
    def phrase_count(self) -> int:
        return len(self.phrases)

    @property
    def compound_count(self) -> int:
        return len(self.compounds)

    @property
    def status_line(self) -> str:
        yt = "unpublished"
        if self.youtube and self.youtube.id:
            yt = self.youtube.id
        return (
            f"Status: {self.status} · {self.id} · {self.kanji_count} kanji · "
            f"{self.vocabulary_count} vocab · {self.phrase_count} phrases · "
            f"{self.compound_count} compounds · YouTube: {yt}"
        )


@dataclass
class BookLessonRef:
    id: str
    number: int
    title: str
    path: str
    status: str = "planned"
    subtitle: str | None = None
    opening_character: str | None = None
    kanji_count: int | None = None
    href: str = ""


@dataclass
class Book:
    id: str
    number: int
    title: str
    path: str
    status: str = "draft"
    subtitle: str | None = None
    description: str | None = None
    lesson_start: int | None = None
    lesson_end: int | None = None
    lesson_ids: list[str] = field(default_factory=list)
    cover: str | None = None
    tags: list[str] = field(default_factory=list)
    lessons: list[BookLessonRef] = field(default_factory=list)
    site_root: str = "../.."
    output_relpath: str = ""

    @property
    def lesson_range_label(self) -> str:
        if self.lesson_start and self.lesson_end:
            return (
                f"Lessons {self.lesson_start:02d}–{self.lesson_end:02d}"
            )
        return ""
