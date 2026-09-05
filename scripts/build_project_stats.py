#!/usr/bin/env python3
"""Build public project statistics JSON for the Statistics page.

Writes: statistics/data/project_stats.json

Layers (do not mix meanings):
  - Permanent library — designed KML resources. One-per-kanji items are
    3,094 (kanji, verses, stroke-order pages). Vocabulary, compounds, and
    components are counted from the full production collections, not assumed
    to be 3,094.
  - Published curriculum — completed lesson sequence (currently 1–50)
  - Curriculum coverage — JLPT / Jōyō / school grades vs Lessons 1–50 only
  - Learning resources — curriculum totals plus separately labeled ecosystem
    materials (Start Here, vocabulary series, kana)
  - Media — the published KML media ecosystem, including the YouTube channel

Completed lessons are the published curriculum range, not an asset-audit of
study filenames. Production HTML is the authority for which kanji a lesson
contains. Do not infer completion from `data-slug` matching a study file —
that produced a Lesson 37 false negative (slug `suppose`, live image
`remain.jpg`). Production study artwork is JPG.
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

# Permanent library scope — designed KML collection (not progress).
# One-per-kanji resources follow this total even when a checkout has fewer
# generated HTML/study files.
KANJI_COLLECTION_TOTAL = 3094
PLANNED_LESSONS = 153
YOUTUBE_CHANNEL_VIDEOS = 551
YOUTUBE_COUNT_AS_OF = "2026-09-05"
YOUTUBE_CHANNEL_HANDLE = "@ambientkanji"
# Public Statistics: published Book 1 curriculum currently complete through here.
# Raise this when the next lesson is released. Do not gate it on study-file globs.
COMPLETED_THROUGH_LESSON = 50
START_HERE_ROOMS = 43  # Rooms 0–42
CHANNEL_LEARNING_JSON = KML / "analytics/output/kml_channel_learning.json"
CHANNEL_STATS_JSON = KML / "analytics/output/kml_channel_statistics.json"

PUBLISHED_EXHIBITIONS = [
    {"id": "lessons_1_5_exhibition", "title": "Japanese Reflections — Lessons 1–5"},
    {"id": "lessons_6_10_exhibition", "title": "Japanese Reflections — Lessons 6–10"},
    {"id": "lessons_11_15_exhibition", "title": "Japanese Reflections — Lessons 11–15"},
    {"id": "lessons_16_20_exhibition", "title": "Japanese Reflections — Lessons 16–20"},
    {"id": "lessons_21_25_quiet_cinematic", "title": "Quiet Cinematic Japan — Lessons 21–25"},
]
PUBLISHED_AMBIENT = [
    {"id": "ambient_gallery_film", "title": "Ambient Movie — Lessons 1–20"},
    {"id": "ambient_gallery_japan_4_seasons", "title": "Ambient Gallery Japan — Four Seasons"},
    {"id": "heart_2", "title": "Heart 2 — Ambient Gallery"},
    {"id": "hearts_collection", "title": "Hearts Collection"},
]

LESSONS_DIR = KML / "contents/books/book_01/lessons"
COMPOUNDS_HTML_DIR = KML / "contents/books/book_01/compounds"
COLLECTIONS_DIR = KML / "tools/ambient/collections"
STUDIES_DIR = KML / "assets/studies"
COVERS_DIR = KML / "assets/covers"
JOYO_CSV = KML / "analytics/reference/joyo_kanji.csv"
KANJI_MASTER_CSV = KML / "data/kanji/kanji_master.csv"
STUDY_EXTS = (".jpg", ".jpeg", ".png")


def study_stems() -> set[str]:
    stems: set[str] = set()
    for ext in STUDY_EXTS:
        stems.update(p.stem for p in STUDIES_DIR.glob(f"*{ext}"))
    return stems


def study_exists(slug: str) -> bool:
    return any((STUDIES_DIR / f"{slug}{ext}").is_file() for ext in STUDY_EXTS)


def lesson_number(path: Path) -> int:
    m = re.search(r"lesson_(\d+)", path.name)
    return int(m.group(1)) if m else 0


def lesson_pad(n: int) -> str:
    return f"{n:02d}"


def count_completed_lessons() -> dict:
    """Lessons in the published curriculum range that have production HTML.

    Study-file presence is not a completion test. Lesson 37's 存 is
    `data-slug="suppose"` but the page serves `assets/studies/remain.jpg`.
    """
    completed: list[int] = []
    for n in range(1, COMPLETED_THROUGH_LESSON + 1):
        path = LESSONS_DIR / f"lesson_{lesson_pad(n)}.html"
        if path.is_file():
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
        img_m = re.search(r"assets/studies/([A-Za-z0-9_]+)\.(?:png|jpe?g)", chunk, re.I)
        study_stem = img_m.group(1) if img_m else (slug_m.group(1) if slug_m else "")
        entries.append(
            {
                "kanji": kanji_m.group(1) if kanji_m else "",
                "slug": slug_m.group(1) if slug_m else "",
                "studyStem": study_stem,
                "verses": verses,
                "components": [p.strip() for p in parts if p.strip()],
                "hasStudy": study_exists(study_stem) if study_stem else False,
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
                    "studyStem": s,
                    "verses": 1,
                    "components": [],
                    "hasStudy": study_exists(s),
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
    """Published exhibition titles — not whether a local .mp4 is checked out."""
    return [dict(item) for item in PUBLISHED_EXHIBITIONS]


def ambient_collections() -> list[dict]:
    """Published ambient collection titles — not local file presence."""
    return [dict(item) for item in PUBLISHED_AMBIENT]


def youtube_library() -> dict:
    """Published YouTube library — channel total, not local .mp4 files.

    The repository has no complete upload inventory. The public figure is the
    live @ambientkanji channel count. Learning-path analytics remain a
    narrower subset and must not be shown as the channel total.
    """
    data = load_json(CHANNEL_LEARNING_JSON) or {}
    summary = data.get("summary") or {}
    return {
        "value": YOUTUBE_CHANNEL_VIDEOS,
        "label": "YouTube Videos",
        "detail": f"Published on {YOUTUBE_CHANNEL_HANDLE}",
        "note": (
            f"Channel total as of {YOUTUBE_COUNT_AS_OF}. "
            "Not counted from local .mp4 files."
        ),
        "source": "YouTube channel page",
        "asOf": YOUTUBE_COUNT_AS_OF,
        "learningPathVideos": summary.get("global_videos"),
        "learningPathSource": "kml/analytics/output/kml_channel_learning.json",
        "independentPaths": summary.get("independent_paths"),
    }


def count_published_audio() -> dict:
    """Website audio — ambient/lesson soundtracks plus Start Here rooms."""
    ambient = KML / "tools/ambient/audio"
    start_here = ROOT / "start-here/audio"
    ambient_n = len(list(ambient.glob("*.mp3"))) if ambient.is_dir() else 0
    start_n = len(list(start_here.glob("*.mp3"))) if start_here.is_dir() else 0
    return {
        "value": ambient_n + start_n,
        "ambientSoundtracks": ambient_n,
        "startHereTracks": start_n,
        "detail": "Lesson, ambient, and Start Here soundtracks",
    }


def count_stroke_html_files() -> int:
    pages = KML / "tools/strokes/pages"
    if not pages.is_dir():
        return 0
    return len(list(pages.glob("*.html")))


def count_kana_row_pages() -> int:
    hira = KML / "kana/hiragana"
    kata = KML / "kana/katakana"
    rows = 0
    for base in (hira, kata):
        if not base.is_dir():
            continue
        for child in base.iterdir():
            if child.is_dir() and (child / "index.html").is_file():
                rows += 1
    return rows


def spoken_vocabulary_unique() -> int | None:
    """Unique words in the Japanese Vocabulary YouTube/learning path.

    That path is Foundation F1–F6 plus Everyday Vocabulary 1–22. It is not
    the same pool as lesson-page vocabulary in Lessons 1–50.
    """
    data = load_json(CHANNEL_LEARNING_JSON) or {}
    path = (data.get("paths") or {}).get("japanese_vocabulary") or {}
    value = (path.get("final") or {}).get("unique_vocabulary")
    if isinstance(value, int):
        return value
    fallback = load_json(CHANNEL_STATS_JSON) or {}
    old = fallback.get("unique_vocabulary")
    return int(old) if isinstance(old, int) else None


def count_vocabulary_series() -> tuple[int, int]:
    vocab_dir = COLLECTIONS_DIR / "vocabulary"
    if not vocab_dir.is_dir():
        return 0, 0
    foundation = len(list(vocab_dir.glob("vocabulary_f*.json")))
    everyday = 0
    for path in vocab_dir.glob("vocabulary_*.json"):
        if re.fullmatch(r"vocabulary_\d+", path.stem):
            everyday += 1
    return foundation, everyday


def count_start_here_rooms() -> int:
    rooms = list((ROOT / "start-here").glob("lesson-*/index.html"))
    return len(rooms) if rooms else START_HERE_ROOMS


def _skip_collection_json(path: Path) -> bool:
    if "prototypes" in path.parts:
        return True
    return "prototype" in path.name.lower()


def _compound_words(data: dict) -> list[str]:
    words: list[str] = []
    for scene in data.get("scenes") or []:
        compounds = scene.get("compounds")
        if isinstance(compounds, dict):
            for step in compounds.get("steps") or []:
                jp = (step.get("jp") or step.get("word") or "").strip()
                if jp:
                    words.append(jp)
        anchor = scene.get("anchor") or {}
        word = (anchor.get("word") or "").strip()
        if word:
            words.append(word)
    return words


def count_library_compounds() -> dict:
    """Unique compounds across published compound series — not one-per-kanji."""
    words: list[str] = []
    files = 0
    for path in COLLECTIONS_DIR.rglob("*compounds*.json"):
        if _skip_collection_json(path):
            continue
        data = load_json(path)
        if not data:
            continue
        files += 1
        words.extend(_compound_words(data))
    return {
        "presentations": len(words),
        "unique": len(set(words)),
        "files": files,
    }


def count_library_components() -> int:
    """Component teaching marks in the full planned lesson library (1–153)."""
    total = 0
    for n in range(1, PLANNED_LESSONS + 1):
        parsed = parse_lesson_html(n)
        for entry in parsed["entries"]:
            total += len(entry["components"])
    return total


def learning_path_unique_vocabulary() -> int | None:
    data = load_json(CHANNEL_LEARNING_JSON) or {}
    value = (data.get("summary") or {}).get("global_unique_vocabulary")
    return int(value) if isinstance(value, int) else None


def count_video_collections() -> int:
    path = ROOT / "collections/index.html"
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8", errors="ignore")
    return len(re.findall(r"class=\"collection-entry", text))


def build_permanent(library_compounds: dict, library_components: int) -> dict:
    unique_vocab = learning_path_unique_vocabulary()
    stroke_html = count_stroke_html_files()
    cards = {
        "kanjiCollection": {
            "value": KANJI_COLLECTION_TOTAL,
            "label": "Kanji",
            "detail": "Complete master collection",
            "note": "Designed one-per-kanji library total.",
        },
        "verses": {
            "value": KANJI_COLLECTION_TOTAL,
            "label": "Verses",
            "detail": "One verse per kanji",
            "note": "Designed one-per-kanji library total.",
        },
        "strokeOrderPages": {
            "value": KANJI_COLLECTION_TOTAL,
            "label": "Stroke-Order Pages",
            "detail": "One page per kanji",
            "note": (
                "Designed one-per-kanji library total. "
                f"This checkout currently has {stroke_html:,} generated HTML files."
            ),
            "checkoutHtmlFiles": stroke_html,
        },
        "plannedLessons": {
            "value": PLANNED_LESSONS,
            "label": "Planned Lessons",
            "detail": "Designed lesson curriculum",
        },
        "vocabularyUnique": {
            "value": unique_vocab,
            "label": "Unique Vocabulary",
            "detail": "YouTube learning-path words",
        },
        "compoundsUnique": {
            "value": library_compounds["unique"],
            "label": "Unique Compounds",
            "detail": "Published compound series",
            "presentations": library_compounds["presentations"],
        },
        "components": {
            "value": library_components,
            "label": "Components",
            "detail": "Full lesson library (1–153)",
        },
    }
    order = [
        "kanjiCollection",
        "verses",
        "strokeOrderPages",
        "plannedLessons",
        "vocabularyUnique",
        "compoundsUnique",
        "components",
    ]
    return {"order": order, **cards}


def build_ecosystem_resources() -> dict:
    spoken_unique = spoken_vocabulary_unique()
    foundation, everyday = count_vocabulary_series()
    return {
        "startHereRooms": {
            "value": count_start_here_rooms(),
            "label": "Start Here Rooms",
            "detail": "Rooms 0–42 on the website",
        },
        "foundationVocabularyLessons": {
            "value": foundation,
            "label": "Foundation Vocabulary",
            "detail": "F1–F6 published series",
        },
        "vocabularyLessons": {
            "value": everyday,
            "label": "Everyday Vocabulary Lessons",
            "detail": "Vocabulary series 1–22",
        },
        "spokenVocabularyUnique": {
            "value": spoken_unique,
            "label": "Unique Spoken Vocabulary",
            "detail": "F1–F6 and Vocabulary 1–22 path",
        },
        "kanaRowPages": {
            "value": count_kana_row_pages(),
            "label": "Kana Chart Pages",
            "detail": "Hiragana and katakana rows",
        },
    }


def build_published(completed_info: dict) -> dict:
    studies = study_stems()
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
            art = entry.get("studyStem") or entry["slug"]
            if art and art in studies:
                hero_illustrations += 1
            if entry["verses"] and art and art in studies:
                verse_illustrations += entry["verses"]
        verses += lesson_verses
        component_boxes += len(re.findall(r'class="component-box"', parsed["html"]))
        vocab += count_vocab_steps(n)
        compounds += count_compound_entries(n)
        readings += count_reading_entries(n, lesson_verses)
        jk, jn = count_component_json(n)
        component_json_kanji += jk
        component_json_new += jn
        if (COVERS_DIR / f"lesson_{lesson_pad(n)}.jpg").is_file():
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
        "curriculumScope": f"Lessons 1–{completed_info['highest']}"
        if completed_info.get("highest")
        else "Completed lessons",
        "completionRule": (
            "Production HTML exists for each lesson in the published "
            "curriculum range. Study-image presence is not a completion test."
        ),
        "coverage": coverage,
    }


def build() -> dict:
    completed = count_completed_lessons()
    published = build_published(completed)
    gallery = gallery_exhibitions()
    ambient = ambient_collections()
    youtube = youtube_library()
    ecosystem = build_ecosystem_resources()
    audio = count_published_audio()
    library_compounds = count_library_compounds()
    library_components = count_library_components()
    permanent = build_permanent(library_compounds, library_components)
    scope_label = published.get("curriculumScope") or "completed lessons"
    video_collections = count_video_collections()

    latest = None
    if completed["highest"]:
        latest = {
            "id": f"lesson_{lesson_pad(completed['highest'])}",
            "title": f"Lesson {completed['highest']}",
            "kind": "lesson",
        }
    published["latestCurriculumLesson"] = latest["title"] if latest else None

    return {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scopeNote": (
            "Statistics include published KML materials across the website "
            "and KML YouTube collections unless otherwise noted. Curriculum "
            "coverage refers specifically to the KML lesson sequence."
        ),
        "permanent": permanent,
        "hero": {
            "kanjiCollection": permanent["kanjiCollection"],
            "verses": permanent["verses"],
            "plannedLessons": permanent["plannedLessons"],
            "lessonsCompleted": {
                "value": published["completedLessons"],
                "label": "Lessons Completed",
                "detail": f"Curriculum through lesson {published['highestCompletedLesson']}"
                if published["highestCompletedLesson"]
                else "Completed curriculum lessons",
            },
            "kanjiPublished": {
                "value": published["kanjiPublished"],
                "label": "Lesson Kanji Published",
                "detail": f"In {scope_label}",
            },
            "youtubeVideos": {
                "value": youtube["value"],
                "label": youtube["label"],
                "detail": youtube["detail"],
                "note": youtube.get("note") or "",
            },
        },
        "published": published,
        "resources": {
            "curriculum": [
                {
                    "value": published["vocabularyPublished"],
                    "label": "Lesson Vocabulary",
                    "detail": scope_label,
                },
                {
                    "value": published["compoundEntries"],
                    "label": "Lesson Compounds",
                    "detail": scope_label,
                },
                {
                    "value": published["readingEntries"],
                    "label": "Lesson Readings",
                    "detail": scope_label,
                },
                {
                    "value": published["componentsPublished"],
                    "label": "Lesson Components",
                    "detail": scope_label,
                },
                {
                    "value": published["strokeOrderPages"],
                    "label": "Lesson Stroke Pages",
                    "detail": f"Linked from {scope_label}",
                },
                {
                    "value": published["lessonCovers"],
                    "label": "Lesson Covers",
                    "detail": scope_label,
                },
            ],
            "ecosystem": [
                item
                for item in ecosystem.values()
                if item.get("value") is not None
            ],
        },
        "media": {
            "galleryExhibitions": [
                {"id": g["id"], "title": g["title"]} for g in gallery
            ],
            "ambientCollections": [
                {"id": a["id"], "title": a["title"]} for a in ambient
            ],
            "galleryExhibitionCount": len(gallery),
            "ambientCollectionCount": len(ambient),
            "videoCollectionCount": video_collections,
            "videoCollectionDetail": "Website playlist galleries",
            "youtube": youtube,
            "audioTracks": audio["value"],
            "audioDetail": audio["detail"],
            "galleryDetail": "Published exhibition films",
            "ambientDetail": "Published ambient collections",
        },
    }


def main() -> int:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hero = data["hero"]
    pub = data["published"]
    perm = data["permanent"]
    cov = pub["coverage"]
    media = data["media"]
    yt = media.get("youtube") or {}
    print(f"Wrote {OUT}")
    print(f"  Permanent kanji/verses/strokes: {perm['kanjiCollection']['value']}")
    print(f"  Permanent unique vocabulary: {perm['vocabularyUnique']['value']}")
    print(f"  Permanent unique compounds: {perm['compoundsUnique']['value']}")
    print(f"  Permanent components: {perm['components']['value']}")
    print(f"  Planned Lessons: {perm['plannedLessons']['value']}")
    print(f"  Lessons Completed: {hero['lessonsCompleted']['value']}")
    print(f"  Lesson kanji published: {pub['kanjiPublished']}")
    print(f"  Lesson verses published: {pub['versesPublished']}")
    print(f"  Lesson vocabulary: {pub['vocabularyPublished']}")
    print(f"  Lesson compounds: {pub['compoundEntries']}")
    print(f"  Lesson components: {pub['componentsPublished']}")
    print(f"  Lesson readings: {pub['readingEntries']}")
    print(f"  Lesson stroke pages: {pub['strokeOrderPages']}")
    print(f"  N5: {cov['jlpt']['N5']['covered']}/{cov['jlpt']['N5']['total']}")
    print(f"  N4: {cov['jlpt']['N4']['covered']}/{cov['jlpt']['N4']['total']}")
    print(f"  N3: {cov['jlpt']['N3']['covered']}/{cov['jlpt']['N3']['total']}")
    print(f"  N2: {cov['jlpt']['N2']['covered']}/{cov['jlpt']['N2']['total']}")
    print(f"  N1: {cov['jlpt']['N1']['covered']}/{cov['jlpt']['N1']['total']}")
    print(f"  Jōyō: {cov['joyo']['covered']}/{cov['joyo']['total']} ({cov['joyo']['percent']}%)")
    print(f"  YouTube: {yt.get('value')}")
    print(f"  Audio: {media['audioTracks']}")
    print(f"  Video collections: {media['videoCollectionCount']}")
    print(f"  Exhibitions: {media['galleryExhibitionCount']}")
    print(f"  Ambient: {media['ambientCollectionCount']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
