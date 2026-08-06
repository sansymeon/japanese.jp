#!/usr/bin/env python3
"""Build public project statistics JSON for the Statistics page.

Writes: statistics/data/project_stats.json

Two layers:
  - Permanent library — full KML scope (changes only occasionally)
  - Published progress — derived from completed (fully illustrated) lessons

Curriculum coverage and learning-resource counts include only content that
belongs to completed lessons. Internal / future lesson material is excluded.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KML = ROOT / "kml"
OUT = ROOT / "statistics" / "data" / "project_stats.json"

# Permanent library scope — complete KML collection (not progress).
KANJI_COLLECTION_TOTAL = 3094
PLANNED_LESSONS = 153
KANJI_PER_LESSON = 20

LESSONS_DIR = KML / "contents/books/book_01/lessons"
COMPOUNDS_HTML_DIR = KML / "contents/books/book_01/compounds"
COLLECTIONS_DIR = KML / "tools/ambient/collections"
STUDIES_DIR = KML / "assets/studies"
COVERS_DIR = KML / "assets/covers"
JOYO_CSV = KML / "analytics/reference/joyo_kanji.csv"
KANJI_MASTER_CSV = KML / "data/kanji/kanji_master.csv"


def lesson_number(path: Path) -> int:
    m = re.search(r"lesson_(\d+)", path.name)
    return int(m.group(1)) if m else 0


def lesson_pad(n: int) -> str:
    return f"{n:02d}"


def count_completed_lessons() -> dict:
    studies = {p.stem for p in STUDIES_DIR.glob("*.png")}
    completed: list[int] = []
    for path in sorted(LESSONS_DIR.glob("lesson_*.html")):
        n = lesson_number(path)
        html = path.read_text(encoding="utf-8", errors="ignore")
        slugs = re.findall(r'data-slug="([^"]+)"', html)
        if not slugs:
            slugs = re.findall(r"studies/([a-z0-9_]+)\.png", html)
        present = sum(1 for s in slugs if s in studies)
        if len(slugs) >= KANJI_PER_LESSON and present >= KANJI_PER_LESSON:
            completed.append(n)
    return {
        "count": len(completed),
        "lessons": completed,
        "highest": max(completed) if completed else 0,
    }


def parse_lesson_html(n: int) -> dict:
    path = LESSONS_DIR / f"lesson_{lesson_pad(n)}.html"
    html = path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
    entries = []
    for block in re.finditer(
        r'<section\s+class="kanji-entry"[^>]*>(.*?)</section>',
        html,
        re.S | re.I,
    ):
        chunk = block.group(0)
        kanji_m = re.search(r'data-kanji="([^"]+)"', chunk)
        slug_m = re.search(r'data-slug="([^"]+)"', chunk)
        verses = len(re.findall(r'class="jp-verse', chunk))
        parts = re.findall(r'class="kanji-part"[^>]*>([^<]+)<', chunk)
        has_study = bool(re.search(r"assets/studies/[^\"']+\.png", chunk))
        entries.append(
            {
                "kanji": kanji_m.group(1) if kanji_m else "",
                "slug": slug_m.group(1) if slug_m else "",
                "verses": verses,
                "components": [p.strip() for p in parts if p.strip()],
                "hasStudy": has_study,
            }
        )
    # Fallback if section regex misses
    if not entries:
        kanji = re.findall(r'data-kanji="([^"]+)"', html)
        slugs = re.findall(r'data-slug="([^"]+)"', html)
        for k, s in zip(kanji, slugs):
            entries.append(
                {
                    "kanji": k,
                    "slug": s,
                    "verses": 1,
                    "components": [],
                    "hasStudy": (STUDIES_DIR / f"{s}.png").is_file(),
                }
            )
    return {"lesson": n, "entries": entries, "html": html}


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def count_vocab_steps(n: int) -> int:
    data = load_json(
        COLLECTIONS_DIR / f"lesson_{lesson_pad(n)}" / f"lesson_{lesson_pad(n)}_vocabulary.json"
    )
    if not data:
        return 0
    total = 0
    for scene in data.get("scenes") or []:
        steps = (scene.get("vocabulary") or {}).get("steps") or []
        total += len(steps)
    return total


def count_compound_entries(n: int) -> int:
    data = load_json(
        COLLECTIONS_DIR / f"lesson_{lesson_pad(n)}" / f"lesson_{lesson_pad(n)}_compounds.json"
    )
    if data:
        total = 0
        for scene in data.get("scenes") or []:
            total += len((scene.get("compounds") or {}).get("steps") or [])
        return total
    html_path = COMPOUNDS_HTML_DIR / f"lesson_{lesson_pad(n)}.html"
    if not html_path.is_file():
        return 0
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    return len(re.findall(r"<strong>[^<]+</strong>【", text))


def count_reading_entries(n: int, verse_fallback: int) -> int:
    data = load_json(
        COLLECTIONS_DIR / f"lesson_{lesson_pad(n)}" / f"lesson_{lesson_pad(n)}_reading.json"
    )
    if data:
        return len(data.get("scenes") or [])
    # Lesson page verses are the published reading content when no reading film JSON yet.
    return verse_fallback


def count_component_json(n: int) -> tuple[int, int]:
    """Return (kanji_component_scenes, new_component_scenes)."""
    data = load_json(
        COLLECTIONS_DIR / f"lesson_{lesson_pad(n)}" / f"lesson_{lesson_pad(n)}_components.json"
    )
    if not data:
        return 0, 0
    kanji_scenes = 0
    new_scenes = 0
    for scene in data.get("scenes") or []:
        t = scene.get("type")
        if t == "newComponent":
            new_scenes += 1
        elif t == "kanji":
            kanji_scenes += 1
    return kanji_scenes, new_scenes


def coverage_from_kanji(published: set[str]) -> dict:
    joyo_grade: dict[str, str] = {}
    if JOYO_CSV.is_file():
        with JOYO_CSV.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                joyo_grade[row["kanji"]] = row["grade"]

    jlpt_of: dict[str, str] = {}
    if KANJI_MASTER_CSV.is_file():
        with KANJI_MASTER_CSV.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                k = row.get("kanji") or ""
                level = (row.get("jlpt") or "").strip()
                if k and level and k not in jlpt_of:
                    jlpt_of[k] = level

    joyo_total = len(joyo_grade)
    joyo_covered = sum(1 for k in published if k in joyo_grade)
    grade_totals = Counter(joyo_grade.values())
    jlpt_totals = Counter(jlpt_of.values())

    def pct(covered: int, total: int) -> float:
        return round(100.0 * covered / total, 2) if total else 0.0

    grades = {}
    for g, label in [
        ("1", "Grade 1"),
        ("2", "Grade 2"),
        ("3", "Grade 3"),
        ("4", "Grade 4"),
        ("5", "Grade 5"),
        ("6", "Grade 6"),
        ("S", "Secondary School"),
    ]:
        total = grade_totals.get(g, 0)
        covered = sum(1 for k in published if joyo_grade.get(k) == g)
        grades[g] = {
            "label": label,
            "covered": covered,
            "total": total,
            "percent": pct(covered, total),
        }

    jlpt = {}
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        total = jlpt_totals.get(level, 0)
        covered = sum(1 for k in published if jlpt_of.get(k) == level)
        jlpt[level] = {
            "label": f"JLPT {level}",
            "covered": covered,
            "total": total,
            "percent": pct(covered, total),
        }

    return {
        "joyo": {
            "covered": joyo_covered,
            "total": joyo_total,
            "percent": pct(joyo_covered, joyo_total),
        },
        "grades": grades,
        "jlpt": jlpt,
    }


def gallery_exhibitions() -> list[dict]:
    names = [
        ("lessons_1_5_exhibition.mp4", "Japanese Reflections — Lessons 1–5"),
        ("lessons_6_10_exhibition.mp4", "Japanese Reflections — Lessons 6–10"),
        ("lessons_11_15_exhibition.mp4", "Japanese Reflections — Lessons 11–15"),
        ("lessons_16_20_exhibition.mp4", "Japanese Reflections — Lessons 16–20"),
        (
            "lessons_21_25_quiet_cinematic.mp4",
            "Quiet Cinematic Japan — Lessons 21–25",
        ),
    ]
    out = []
    base = KML / "tools/ambient/extended_exhibitions"
    for filename, title in names:
        path = base / filename
        if path.is_file():
            out.append(
                {"id": path.stem, "title": title, "mtime": path.stat().st_mtime}
            )
    return out


def ambient_collections() -> list[dict]:
    candidates = [
        (
            KML / "tools/ambient/collections/ambient_gallery_film/ambient_gallery_film.mp4",
            "Ambient Movie — Lessons 1–20",
        ),
        (
            KML
            / "tools/ambient/collections/ambient_gallery_japan_4_seasons"
            / "ambient_gallery_japan_4_seasons.mp4",
            "Ambient Gallery Japan — Four Seasons",
        ),
        (
            KML / "tools/ambient/heart_exhibitions/heart_2.mp4",
            "Heart 2 — Ambient Gallery",
        ),
        (
            KML / "tools/ambient/heart_exhibitions/hearts_collection.mp4",
            "Hearts Collection",
        ),
    ]
    out = []
    for path, title in candidates:
        if path.is_file():
            out.append({"id": path.stem, "title": title, "mtime": path.stat().st_mtime})
    return out


def count_published_videos(completed: list[int]) -> int:
    total = 0
    for n in completed:
        folder = COLLECTIONS_DIR / f"lesson_{lesson_pad(n)}"
        if folder.is_dir():
            total += len(list(folder.glob("*.mp4")))
    # Plus published exhibition / ambient films
    total += len(gallery_exhibitions())
    total += len(ambient_collections())
    return total


def count_published_audio() -> int:
    audio_dir = KML / "tools/ambient/audio"
    if not audio_dir.is_dir():
        return 0
    return len(list(audio_dir.glob("*.mp3")))


def build_published(completed_info: dict) -> dict:
    studies = {p.stem for p in STUDIES_DIR.glob("*.png")}
    completed = completed_info["lessons"]

    kanji_list: list[str] = []
    slug_list: list[str] = []
    verses = 0
    hero_illustrations = 0
    verse_illustrations = 0
    component_parts = 0
    component_boxes = 0
    vocab = 0
    compounds = 0
    readings = 0
    component_json_kanji = 0
    component_json_new = 0
    covers = 0

    for n in completed:
        parsed = parse_lesson_html(n)
        lesson_verses = 0
        for entry in parsed["entries"]:
            if entry["kanji"]:
                kanji_list.append(entry["kanji"])
            if entry["slug"]:
                slug_list.append(entry["slug"])
            lesson_verses += entry["verses"]
            component_parts += len(entry["components"])
            if entry["slug"] and entry["slug"] in studies:
                hero_illustrations += 1
            if entry["verses"] and entry["slug"] and entry["slug"] in studies:
                verse_illustrations += entry["verses"]
        verses += lesson_verses
        component_boxes += len(re.findall(r'class="component-box"', parsed["html"]))
        vocab += count_vocab_steps(n)
        compounds += count_compound_entries(n)
        readings += count_reading_entries(n, lesson_verses)
        jk, jn = count_component_json(n)
        component_json_kanji += jk
        component_json_new += jn
        if (COVERS_DIR / f"lesson_{lesson_pad(n)}.png").is_file():
            covers += 1

    published_kanji = set(kanji_list)
    coverage = coverage_from_kanji(published_kanji)

    # Prefer HTML component teaching marks; fall back to JSON scene counts.
    components_published = component_parts if component_parts else (
        component_json_kanji + component_json_new
    )

    stroke_pages = sum(
        1
        for s in set(slug_list)
        if (KML / "tools/strokes/pages" / f"{s}.html").is_file()
    )

    return {
        "completedLessons": completed_info["count"],
        "highestCompletedLesson": completed_info["highest"],
        "completedLessonNumbers": completed,
        "kanjiPublished": len(kanji_list),
        "uniqueKanjiPublished": len(published_kanji),
        "versesPublished": verses,
        "heroIllustrations": hero_illustrations,
        "verseIllustrations": verse_illustrations,
        "lessonCovers": covers,
        "componentsPublished": components_published,
        "componentBoxes": component_boxes,
        "vocabularyPublished": vocab,
        "compoundEntries": compounds,
        "readingEntries": readings,
        "strokeOrderPages": stroke_pages,
        "coverage": coverage,
    }


def build() -> dict:
    completed = count_completed_lessons()
    published = build_published(completed)
    gallery = gallery_exhibitions()
    ambient = ambient_collections()

    release_candidates = []
    for item in gallery:
        release_candidates.append({**item, "kind": "exhibition"})
    for item in ambient:
        release_candidates.append({**item, "kind": "ambient"})
    if completed["highest"]:
        lesson_path = LESSONS_DIR / f"lesson_{lesson_pad(completed['highest'])}.html"
        if lesson_path.is_file():
            release_candidates.append(
                {
                    "id": f"lesson_{lesson_pad(completed['highest'])}",
                    "title": f"Lesson {completed['highest']}",
                    "mtime": lesson_path.stat().st_mtime,
                    "kind": "lesson",
                }
            )
    latest = max(release_candidates, key=lambda x: x["mtime"]) if release_candidates else None

    videos = count_published_videos(completed["lessons"])
    audio = count_published_audio()

    return {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "permanent": {
            "kanjiCollection": {
                "value": KANJI_COLLECTION_TOTAL,
                "label": "Kanji Collection",
                "detail": "Total KML library",
                "note": "The complete library scope — including the core curriculum and specialized collections as they are added over time.",
            },
            "plannedLessons": {
                "value": PLANNED_LESSONS,
                "label": "Planned Lessons",
                "detail": "Full lesson curriculum",
            },
        },
        "hero": {
            "kanjiCollection": {
                "value": KANJI_COLLECTION_TOTAL,
                "label": "Kanji Collection",
                "detail": "Total KML library",
                "note": "The complete library scope — including the core curriculum and specialized collections as they are added over time.",
            },
            "plannedLessons": {
                "value": PLANNED_LESSONS,
                "label": "Planned Lessons",
                "detail": "Full lesson curriculum",
            },
            "lessonsCompleted": {
                "value": published["completedLessons"],
                "label": "Lessons Completed",
                "detail": f"Through lesson {published['highestCompletedLesson']}"
                if published["highestCompletedLesson"]
                else "Fully illustrated lessons",
            },
            "kanjiPublished": {
                "value": published["kanjiPublished"],
                "label": "Kanji Published",
                "detail": "In completed lessons",
            },
            "versesPublished": {
                "value": published["versesPublished"],
                "label": "Verses Published",
                "detail": "Poetic verses in completed lessons",
            },
            "latestRelease": {
                "value": latest["title"] if latest else "—",
                "label": "Latest Release",
                "detail": latest["kind"].title() if latest else "",
                "id": latest["id"] if latest else None,
            },
        },
        "published": published,
        "media": {
            "galleryExhibitions": [
                {"id": g["id"], "title": g["title"]} for g in gallery
            ],
            "ambientCollections": [
                {"id": a["id"], "title": a["title"]} for a in ambient
            ],
            "galleryExhibitionCount": len(gallery),
            "ambientCollectionCount": len(ambient),
            "videos": videos,
            "audioTracks": audio,
        },
    }


def main() -> int:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hero = data["hero"]
    pub = data["published"]
    print(f"Wrote {OUT}")
    print(f"  Kanji Collection: {hero['kanjiCollection']['value']}")
    print(f"  Planned Lessons: {hero['plannedLessons']['value']}")
    print(f"  Lessons Completed: {hero['lessonsCompleted']['value']}")
    print(f"  Kanji Published: {pub['kanjiPublished']}")
    print(f"  Verses Published: {pub['versesPublished']}")
    print(f"  Hero Illustrations: {pub['heroIllustrations']}")
    print(f"  Vocabulary: {pub['vocabularyPublished']}")
    print(f"  Compounds: {pub['compoundEntries']}")
    print(f"  Jōyō: {pub['coverage']['joyo']['percent']}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
