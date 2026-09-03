"""Quiet Cinematic drafts for Lessons 1–20.

Keepers come from the Ambient Revised playlist (already cinematic), mapped
back onto Heisig lessons. Still-life is dropped. Sparse blocks are filled
from remaining landscape-category studies. Dense blocks trim to ~38.
"""

from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"
DRAFT_DIR = ROOT / "quiet_cinematic_review" / "data"
FILM_JSON = ROOT / "collections" / "ambient_gallery_film" / "ambient_gallery_film.json"
EXCLUDE_JSON = ROOT / "collections" / "ambient_gallery_film" / "scenic_exclude.json"

BLOCKS: tuple[tuple[int, int], ...] = ((1, 5), (6, 10), (11, 15), (16, 20))
TARGET_MIN = 30
TARGET_MAX = 38
SEEDS = {
    (1, 5): 20260822,
    (6, 10): 20260823,
    (11, 15): 20260824,
    (16, 20): 20260825,
}

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)

WIDE_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "temples",
        re.compile(
            r"temple|shrine|torii|pagoda|lantern|buddhist|shinto|pavilion|haven",
            re.I,
        ),
    ),
    ("castles", re.compile(r"castle|donjon|fortress|tenshu", re.I)),
    (
        "water",
        re.compile(
            r"river|lake|pond|stream|waterfall|cascade|sea|coast|shore|"
            r"harbor|harbour|canal|tide|spring|creek|ford|shallow|ice|"
            r"whale|fish|swim|open_sea|angling",
            re.I,
        ),
    ),
    (
        "forests",
        re.compile(
            r"forest|woods|bamboo|cedar|pine|grove|tree|oak|leaf|"
            r"overgrown|plantation|treetops",
            re.I,
        ),
    ),
    (
        "mountains",
        re.compile(
            r"mountain|valley|peak|ridge|fuji|highland|cliff|overlook|"
            r"range|horizon|cape|scenery|escape",
            re.I,
        ),
    ),
    (
        "villages",
        re.compile(
            r"village|farm|rice|thatched|rural|hamlet|minka|countryside|"
            r"villa|cottage|meadow|field",
            re.I,
        ),
    ),
    (
        "streets",
        re.compile(
            r"street|alley|machiya|town|kyoto|capital|car|road|"
            r"crossing|guidance|walk",
            re.I,
        ),
    ),
    (
        "season",
        re.compile(
            r"snow|winter|autumn|fall|maple|cherry|blossom|sakura|spring|summer",
            re.I,
        ),
    ),
    (
        "evening",
        re.compile(
            r"evening|dusk|twilight|night|moon|dawn|morning|sunrise|sunset|"
            r"dream|tranquilize",
            re.I,
        ),
    ),
]
WIDE_CATEGORIES = frozenset(name for name, _ in WIDE_RULES)
ENDING_PREFER = re.compile(
    r"evening|dusk|twilight|night|moon|lake|mist|temple|mountain|horizon",
    re.I,
)


def collection_id(start: int, end: int) -> str:
    return f"lessons_{start}_{end}_quiet_cinematic"


def draft_path(start: int, end: int) -> Path:
    return DRAFT_DIR / f"{collection_id(start, end)}.json"


def load_exclude_slugs() -> set[str]:
    if not EXCLUDE_JSON.is_file():
        return set()
    data = json.loads(EXCLUDE_JSON.read_text(encoding="utf-8"))
    return set(data.get("excludeSlugs") or [])


def load_film_stems() -> set[str]:
    data = json.loads(FILM_JSON.read_text(encoding="utf-8"))
    return {Path(scene["image"]).stem for scene in data.get("scenes") or []}


def parse_lesson(lesson: int) -> list[dict]:
    html_path = REPO / "contents/books/book_01/lessons" / f"lesson_{lesson:02d}.html"
    html = html_path.read_text(encoding="utf-8")
    items: list[dict] = []
    for block in SECTION_RE.findall(html):
        kanji_m = re.search(r'data-kanji="([^"]+)"', block)
        slug_m = re.search(r'data-slug="([^"]+)"', block)
        keyword_m = re.search(r'<span class="kanji-keyword">([^<]+)</span>', block)
        img_m = re.search(r"assets/studies/([^\"']+\.jpg)", block)
        if not slug_m:
            continue
        slug = slug_m.group(1)
        keyword = keyword_m.group(1).strip() if keyword_m else slug.replace("_", " ")
        image = f"studies/{img_m.group(1)}" if img_m else f"studies/{slug}.jpg"
        items.append(
            {
                "id": f"L{lesson:02d}_{slug}",
                "lesson": lesson,
                "slug": slug,
                "filename": Path(image).name,
                "keyword": keyword,
                "kanji": kanji_m.group(1) if kanji_m else "",
                "image": image,
                "title": keyword,
                "category": categorize(slug, keyword),
            }
        )
    return items


def categorize(slug: str, keyword: str) -> str:
    try:
        import build_ambient_gallery_film as film

        mapped = film.CATEGORY_BY_SLUG.get(slug)
        if mapped:
            return mapped
    except Exception:
        pass
    blob = f"{slug} {keyword}"
    for name, pat in WIDE_RULES:
        if pat.search(blob):
            return name
    return "other"


def is_wide(item: dict) -> bool:
    return item["category"] in WIDE_CATEGORIES


def image_ok(item: dict) -> bool:
    return (ASSETS / item["image"]).is_file()


def interleave(items: list[dict], rng: random.Random) -> list[dict]:
    ending = [
        item
        for item in items
        if ENDING_PREFER.search(f"{item['slug']} {item['keyword']}")
    ]
    ending = ending[-2:] if ending else []
    ending_ids = {item["id"] for item in ending}
    pool = [item for item in items if item["id"] not in ending_ids]

    by_lesson: dict[int, list[dict]] = defaultdict(list)
    for item in pool:
        by_lesson[int(item["lesson"])].append(item)
    for bucket in by_lesson.values():
        rng.shuffle(bucket)

    cycle = sorted(by_lesson)
    rng.shuffle(cycle)
    ordered: list[dict] = []
    prev: int | None = None
    while any(by_lesson.values()):
        progressed = False
        for lesson in cycle + cycle:
            bucket = by_lesson.get(lesson) or []
            if not bucket:
                continue
            if prev is not None and lesson == prev and any(
                by_lesson[other] for other in by_lesson if other != lesson
            ):
                continue
            ordered.append(bucket.pop(0))
            prev = lesson
            progressed = True
            break
        if not progressed:
            for bucket in by_lesson.values():
                ordered.extend(bucket)
            break
        by_lesson = {k: v for k, v in by_lesson.items() if v}

    ordered.extend(ending)
    for index, item in enumerate(ordered, start=1):
        item["order"] = index
    return ordered


def trim(items: list[dict], *, max_count: int, rng: random.Random) -> list[dict]:
    if len(items) <= max_count:
        return items
    people = [item for item in items if item["category"] == "people"]
    keep = [item for item in items if item["category"] != "people"]
    rng.shuffle(people)
    while len(keep) + len(people) > max_count and people:
        people.pop()
    selected = keep + people
    if len(selected) <= max_count:
        return selected

    by_lesson: dict[int, list[dict]] = defaultdict(list)
    for item in selected:
        by_lesson[int(item["lesson"])].append(item)
    while sum(len(v) for v in by_lesson.values()) > max_count:
        richest = max(by_lesson, key=lambda lesson: len(by_lesson[lesson]))
        if len(by_lesson[richest]) <= 1:
            break
        by_lesson[richest].pop()
    out: list[dict] = []
    for lesson in sorted(by_lesson):
        out.extend(by_lesson[lesson])
    return out


def fill(items: list[dict], extras: list[dict], *, min_count: int) -> list[dict]:
    have = {item["id"] for item in items}
    for extra in extras:
        if len(items) >= min_count:
            break
        if extra["id"] in have:
            continue
        items.append(extra)
        have.add(extra["id"])
    return items


def curator_items(start: int, end: int) -> list[dict]:
    rng = random.Random(SEEDS[(start, end)])
    film_stems = load_film_stems()
    excluded = load_exclude_slugs()
    pool: list[dict] = []
    for lesson in range(start, end + 1):
        pool.extend(parse_lesson(lesson))
    pool = [
        item
        for item in pool
        if image_ok(item) and item["slug"] not in excluded
    ]

    film_items = [item for item in pool if item["slug"] in film_stems]
    scenic = [item for item in film_items if item["category"] != "still_life"]
    wide_fill = [
        item
        for item in pool
        if item["slug"] not in film_stems and is_wide(item)
    ]
    rng.shuffle(wide_fill)

    selected = fill(list(scenic), wide_fill, min_count=TARGET_MIN)
    selected = trim(selected, max_count=TARGET_MAX, rng=rng)
    if not selected:
        raise SystemExit(f"No Quiet Cinematic keepers for lessons {start}–{end}")
    return interleave(selected, rng)


def write_draft(start: int, end: int, items: list[dict]) -> Path:
    cid = collection_id(start, end)
    path = draft_path(start, end)
    unused = []
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "id": cid,
                "title": f"Quiet Cinematic Japan — Lessons {start}–{end} (Draft)",
                "theme": "Quiet Cinematic Japan",
                "status": "draft-review",
                "notes": (
                    "Lessons 1–20 Quiet Cinematic from Ambient Revised keepers "
                    "(still-life dropped; landscape fill where the playlist was thin). "
                    "Landscape and atmosphere first; solitary figures only when they serve mood."
                ),
                "lessons": list(range(start, end + 1)),
                "targetFinalCount": TARGET_MIN,
                "candidateCount": len(items),
                "assetsBase": "../../../assets",
                "source": "collections/ambient_gallery_film/ambient_gallery_film.json",
                "itemCount": len(items),
                "items": items,
                "unusedCandidates": unused,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path
