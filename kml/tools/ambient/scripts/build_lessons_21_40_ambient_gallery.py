#!/usr/bin/env python3
"""Build Ambient Movie — Lessons 21–40 (single long film).

One textless Ken Burns journey from the confirmed keeper shortlist
(tmp/lessons_21_40_extended_exhibition_review/candidates.json), paced to
fill audio/137_minute_ambient.mp3 (~2h 18m) like Lessons 1–20 Ambient Revised.

  35–45s holds (exceptional up to 60s), 2.5s transitions, silent gold crest.
  Category-aware interleaving (not strict lesson order).
"""

from __future__ import annotations

import json
import random
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402

COLLECTION_ID = "lessons_21_40_ambient_gallery"
KEEPERS_PATH = (
    REPO
    / "tools"
    / "tmp"
    / "lessons_21_40_extended_exhibition_review"
    / "candidates.json"
)
SOUNDTRACK = "audio/137_minute_ambient.mp3"
SEED = 20260812

MOTIONS = (
    "push-in",
    "pull-out",
    "drift-x",
    "drift-y",
    "drift-diagonal",
    "rise",
)

HOLD_MIN_MS = 35_000
HOLD_MAX_MS = 45_000
HOLD_EXCEPTIONAL_MS = 60_000
HOLD_FINAL_MS = 55_000
TRANSITION_MS = 2_500
ARRIVAL_FADE_MS = 2_500
CLOSING_REVEAL_MS = 5_000
CLOSING_HOLD_MS = 7_000
CLOSING_FADE_MS = 12_000
CLOSING_BLACK_AFTER_MS = 2_000
CAMERA_MOTION_SCALE = 2.5

SILENT_CREST_BOOKENDS = {
    "mode": "silentCrest",
    "closing": {
        "image": "images/gold_closing.png",
        "bookendSize": "small",
        "silentAfterSoundtrack": True,
        "holdUntilSoundtrackEnds": False,
    },
}

# Note / slug keyword → visual category for interleaving.
_CATEGORY_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "temples",
        re.compile(
            r"temple|shrine|torii|pagoda|lantern|buddhist|shinto|gate.?house",
            re.I,
        ),
    ),
    ("castles", re.compile(r"castle|donjon|fortress|tenshu", re.I)),
    (
        "water",
        re.compile(
            r"river|lake|pond|stream|waterfall|cascade|sea|coast|shore|"
            r"harbor|harbour|canal|bridge.?over.?water|mist.?over.?water",
            re.I,
        ),
    ),
    (
        "forests",
        re.compile(r"forest|woods|bamboo|cedar|pine|grove|tree.?lined|mossy.?path", re.I),
    ),
    (
        "mountains",
        re.compile(r"mountain|valley|peak|ridge|fuji|highland|cliff|overlook", re.I),
    ),
    (
        "villages",
        re.compile(
            r"village|farm|rice.?field|thatched|rural|hamlet|minka|countryside",
            re.I,
        ),
    ),
    (
        "streets",
        re.compile(
            r"street|alley|machiya|town|kyoto|engawa|courtyard|shop.?front|"
            r"wooden.?facade|narrow.?lane",
            re.I,
        ),
    ),
    (
        "season",
        re.compile(
            r"snow|winter|autumn|fall.?color|maple|cherry|blossom|sakura|spring",
            re.I,
        ),
    ),
    (
        "evening",
        re.compile(r"evening|dusk|twilight|night|moon|dawn|morning|sunrise|sunset", re.I),
    ),
    ("still_life", re.compile(r"still.?life|interior|tea|pottery|detail|close", re.I)),
]

ENDING_NOTE_PREFER = re.compile(
    r"evening|dusk|twilight|night|moon|lake|still.?water|mist|temple|mountain|"
    r"horizon|quiet|lantern",
    re.I,
)

WIDE_CATEGORIES = frozenset(
    {
        "mountains",
        "forests",
        "water",
        "temples",
        "castles",
        "villages",
        "streets",
        "season",
        "evening",
    }
)


def soundtrack_duration_ms(rel: str) -> int:
    path = ROOT / rel
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    ).strip()
    return int(float(out) * 1000)


def image_rev(relative: str) -> int | None:
    path = ASSETS / relative
    if path.is_file():
        return int(path.stat().st_mtime)
    return None


def categorize(item: dict) -> str:
    blob = f"{item.get('slug', '')} {item.get('keyword', '')} {item.get('note', '')}"
    for cat, pat in _CATEGORY_RULES:
        if pat.search(blob):
            return cat
    # Soft slug fallbacks
    slug = (item.get("slug") or "").lower()
    for cat, words in (
        ("water", ("water", "river", "lake", "sea", "tide", "stream", "pond")),
        ("forests", ("tree", "forest", "woods", "bamboo", "lumber")),
        ("mountains", ("mountain", "peak", "hill", "slope")),
        ("temples", ("temple", "shrine", "pray", "buddhist")),
        ("villages", ("village", "farm", "rice", "field")),
        ("evening", ("night", "moon", "evening", "dawn")),
        ("season", ("snow", "freeze", "frozen", "blossom")),
    ):
        if any(w in slug for w in words):
            return cat
    return "scenic"


def load_keepers() -> list[dict]:
    if not KEEPERS_PATH.is_file():
        raise SystemExit(f"Missing keeper shortlist: {KEEPERS_PATH}")
    data = json.loads(KEEPERS_PATH.read_text(encoding="utf-8"))
    items = data.get("items") or []
    if not items:
        raise SystemExit("Keeper shortlist has no items")
    return list(items)


def scale_of(cat: str) -> str:
    return "wide" if cat in WIDE_CATEGORIES else "intimate"


def pick_ending(scenes: list[dict], count: int = 10) -> list[dict]:
    scored = []
    for s in scenes:
        note = f"{s.get('note', '')} {s.get('slug', '')}"
        bonus = 20 if ENDING_NOTE_PREFER.search(note) else 0
        cat_bonus = {
            "evening": 15,
            "water": 12,
            "temples": 10,
            "mountains": 10,
            "season": 6,
        }.get(s["category"], 0)
        scored.append((bonus + cat_bonus, s))
    scored.sort(key=lambda t: t[0], reverse=True)
    chosen: list[dict] = []
    used_lessons: list[int] = []
    for _score, s in scored:
        if len(chosen) >= count:
            break
        lesson = int(s["lesson"])
        if used_lessons and lesson == used_lessons[-1] and any(
            int(x["lesson"]) != lesson for _, x in scored if x not in chosen
        ):
            continue
        chosen.append(s)
        used_lessons.append(lesson)
    return chosen


def interleave(scenes: list[dict], rng: random.Random) -> list[dict]:
    """Interleave by lesson so the film doesn't run contiguous lesson blocks.

    Visual note categories are sparse on this shortlist (many 'User keep' stubs),
    so lesson round-robin is the reliable rhythm.
    """
    ending = pick_ending(scenes, count=10)
    ending_ids = {s["id"] for s in ending}
    pool = [s for s in scenes if s["id"] not in ending_ids]

    by_lesson: dict[int, list[dict]] = defaultdict(list)
    for s in pool:
        by_lesson[int(s["lesson"])].append(s)
    for bucket in by_lesson.values():
        rng.shuffle(bucket)

    lessons = sorted(by_lesson.keys())
    rng.shuffle(lessons)  # soft start mix; still round-robin afterward
    # Prefer ascending lesson cycle after an initial shuffle of the cycle order.
    cycle = sorted(by_lesson.keys())
    rng.shuffle(cycle)

    ordered: list[dict] = []
    prev_lesson: int | None = None
    while any(by_lesson.values()):
        progressed = False
        # Prefer a lesson different from the previous one.
        for lesson in cycle + cycle:
            bucket = by_lesson.get(lesson) or []
            if not bucket:
                continue
            if prev_lesson is not None and lesson == prev_lesson and any(
                by_lesson[L] for L in by_lesson if L != lesson
            ):
                continue
            ordered.append(bucket.pop(0))
            prev_lesson = lesson
            progressed = True
            break
        if not progressed:
            # Only one lesson left — drain it.
            for lesson, bucket in list(by_lesson.items()):
                while bucket:
                    ordered.append(bucket.pop(0))
            break
        # Drop empty lessons
        by_lesson = {k: v for k, v in by_lesson.items() if v}

    ordered.extend(ending)
    return ordered


def assign_motions(scenes: list[dict], rng: random.Random) -> None:
    prev = None
    motion_by_cat = {
        "mountains": "pull-out",
        "forests": "drift-diagonal",
        "water": "drift-x",
        "temples": "push-in",
        "castles": "rise",
        "villages": "drift-x",
        "streets": "drift-x",
        "season": "drift-x",
        "evening": "drift-y",
        "still_life": "push-in",
        "scenic": "pull-out",
    }
    for scene in scenes:
        preferred = motion_by_cat.get(scene["category"])
        choices = [m for m in MOTIONS if m != prev]
        if preferred in choices and rng.random() < 0.55:
            motion = preferred
        else:
            motion = rng.choice(choices)
        scene["galleryCamera"] = {"motion": motion}
        prev = motion


def distribute_holds(scenes: list[dict], budget_ms: int, rng: random.Random) -> list[int]:
    n = len(scenes)
    if n <= 0:
        return []
    holds: list[int] = []
    for i, scene in enumerate(scenes):
        roll = rng.random()
        if i == n - 1:
            holds.append(HOLD_FINAL_MS)
        elif scene["category"] in {"evening", "water", "temples", "mountains"} and roll < 0.45:
            holds.append(rng.randint(48_000, HOLD_EXCEPTIONAL_MS))
        elif roll < 0.10:
            holds.append(rng.randint(HOLD_MAX_MS, HOLD_EXCEPTIONAL_MS))
        elif roll < 0.28:
            holds.append(rng.randint(HOLD_MIN_MS, HOLD_MIN_MS + 4_000))
        else:
            holds.append(rng.randint(HOLD_MIN_MS + 4_000, HOLD_MAX_MS))

    total = sum(holds)
    scaled = [
        max(HOLD_MIN_MS, min(HOLD_EXCEPTIONAL_MS, int(h * budget_ms / total)))
        for h in holds
    ]
    if scaled[-1] < HOLD_FINAL_MS:
        need = HOLD_FINAL_MS - scaled[-1]
        for i in range(n - 2, -1, -1):
            if need <= 0:
                break
            give = min(need, scaled[i] - HOLD_MIN_MS)
            if give > 0:
                scaled[i] -= give
                scaled[-1] += give
                need -= give

    drift = budget_ms - sum(scaled)
    i = 0
    while drift != 0 and i < n * 8:
        idx = i % n
        if drift > 0 and scaled[idx] < HOLD_EXCEPTIONAL_MS:
            step = min(drift, HOLD_EXCEPTIONAL_MS - scaled[idx], 250)
            scaled[idx] += step
            drift -= step
        elif drift < 0 and scaled[idx] > HOLD_MIN_MS:
            step = min(-drift, scaled[idx] - HOLD_MIN_MS, 250)
            scaled[idx] -= step
            drift += step
        i += 1
    scaled[-1] += budget_ms - sum(scaled)
    return scaled


def max_same_lesson_run(scenes: list[dict]) -> int:
    if not scenes:
        return 0
    best = 1
    run = 1
    for i in range(1, len(scenes)):
        if scenes[i]["lesson"] == scenes[i - 1]["lesson"]:
            run += 1
            best = max(best, run)
        else:
            run = 1
    return best


def max_same_category_run(scenes: list[dict]) -> tuple[int, str]:
    if not scenes:
        return 0, ""
    best = 1
    best_cat = scenes[0]["category"]
    run = 1
    for i in range(1, len(scenes)):
        if scenes[i]["category"] == scenes[i - 1]["category"]:
            run += 1
            if run > best:
                best = run
                best_cat = scenes[i]["category"]
        else:
            run = 1
    return best, best_cat


def build() -> dict:
    rng = random.Random(SEED)
    soundtrack_ms = soundtrack_duration_ms(SOUNDTRACK)
    keepers = load_keepers()

    raw_scenes: list[dict] = []
    missing: list[str] = []
    for item in keepers:
        image = item.get("image") or f"studies/{item.get('filename')}"
        if not (ASSETS / image).is_file():
            missing.append(image)
            continue
        cat = categorize(item)
        raw_scenes.append(
            {
                "id": item["id"],
                "kanji": item.get("kanji") or "",
                "keyword": item.get("keyword") or item.get("slug") or "",
                "image": image,
                "lesson": int(item["lesson"]),
                "slug": item.get("slug") or Path(image).stem,
                "verse": item.get("verse"),
                "note": item.get("note") or "",
                "category": cat,
            }
        )
    if missing:
        raise SystemExit("Missing assets:\n  " + "\n  ".join(missing[:20]))

    mixed = interleave(raw_scenes, rng)
    assign_motions(mixed, rng)

    n = len(mixed)
    transitions = max(0, n - 1) * TRANSITION_MS
    hold_budget = soundtrack_ms - transitions
    if hold_budget < n * HOLD_MIN_MS:
        max_scenes = max(1, hold_budget // HOLD_MIN_MS)
        ending = mixed[-10:] if n > 10 else []
        body = mixed[:-10] if n > 10 else mixed
        mixed = body[: max(0, max_scenes - len(ending))] + ending
        n = len(mixed)
        transitions = max(0, n - 1) * TRANSITION_MS
        hold_budget = soundtrack_ms - transitions

    holds = distribute_holds(mixed, hold_budget, rng)
    avg_hold = sum(holds) / n
    max_run, max_run_cat = max_same_category_run(mixed)
    max_lesson_run = max_same_lesson_run(mixed)
    cat_counts: dict[str, int] = defaultdict(int)
    for s in mixed:
        cat_counts[s["category"]] += 1

    scenes = []
    for raw, hold in zip(mixed, holds):
        scene = {
            "id": raw["id"],
            "kanji": raw["kanji"],
            "keyword": raw["keyword"],
            "image": raw["image"],
            "galleryCamera": raw["galleryCamera"],
            "artworkAloneMs": hold,
            "verse": {"jpHtml": "", "en": ""},
            "meta": {
                "lesson": raw["lesson"],
                "slug": raw["slug"],
                "verse": raw.get("verse"),
                "category": raw["category"],
                "source": f"lesson_{raw['lesson']}",
                "ambientGalleryFilm": True,
                "ambientMove": "lessons_21_40_long",
            },
        }
        rev = image_rev(raw["image"])
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Ambient Movie — Lessons 21–40",
        "notes": (
            "Single long Ambient Movie from the Lessons 21–40 keeper shortlist. "
            "Textless Ken Burns, lesson-interleaved (not two split films), paced to fill "
            f"{SOUNDTRACK} (~{soundtrack_ms / 60000:.1f} min). Holds 35–45s "
            f"(exceptional up to 60s). Silent gold crest after soundtrack "
            f"(reveal {CLOSING_REVEAL_MS // 1000}s · hold {CLOSING_HOLD_MS // 1000}s · "
            f"fade {CLOSING_FADE_MS // 1000}s). {n} images · avg hold "
            f"{avg_hold / 1000:.1f}s."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": {
            "artworkArrivalMs": 0,
            "artworkArrivalFadeMs": ARRIVAL_FADE_MS,
            "exhibitionBlackBeforeMs": 0,
            "artworkAloneMs": int(avg_hold),
            "kanjiRevealMs": 0,
            "imageVerseKanjiHoldMs": 0,
            "imageVerseKanjiFadeMs": 0,
            "titleFadeMs": 0,
            "verseJpRevealMs": 0,
            "verseJpHoldMs": 0,
            "verseJpFadeMs": 0,
            "verseEnRevealMs": 0,
            "verseEnHoldMs": 0,
            "verseEnFadeMs": 0,
            "exhibitTransitionMs": TRANSITION_MS,
            "exhibitBlackHoldMs": 0,
            "kenBurnsDurationMs": int(avg_hold + TRANSITION_MS),
            "closingBlackBeforeMs": 0,
            "closingRevealMs": CLOSING_REVEAL_MS,
            "closingHoldMs": CLOSING_HOLD_MS,
            "closingExhaleMs": CLOSING_FADE_MS,
            "closingFadeToBlackMs": CLOSING_FADE_MS,
            "closingBlackAfterMs": CLOSING_BLACK_AFTER_MS,
            "closingSilenceHoldMs": 0,
            "blackHoldMs": 0,
            "seamlessExhibitHandoff": True,
        },
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "ambientGalleryFilm",
            "showKeyword": False,
            "showKanji": False,
            "exhibitProfile": "gallery",
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "bookendStyle": "galleryCrest",
            "cameraMotionScale": CAMERA_MOTION_SCALE,
            "ambientMove": "lessons_21_40_long",
        },
        "meta": {
            "family": "ambientGalleryFilm",
            "ambientMove": "lessons_21_40_long",
            "edition": "Lessons 21–40",
            "lessons": list(range(21, 41)),
            "sceneCount": n,
            "soundtrackDurationMs": soundtrack_ms,
            "soundtrackProvisional": False,
            "avgHoldMs": int(avg_hold),
            "holdMinMs": min(holds),
            "holdMaxMs": max(holds),
            "cameraMotionScale": CAMERA_MOTION_SCALE,
            "keepersPath": str(KEEPERS_PATH.relative_to(REPO)),
            "seed": SEED,
            "maxSameCategoryRun": max_run,
            "maxSameCategory": max_run_cat,
            "maxSameLessonRun": max_lesson_run,
            "categoryCounts": dict(sorted(cat_counts.items())),
            "endingSlugs": [s["slug"] for s in mixed[-10:]],
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    out = write_collection_path(ROOT, COLLECTION_ID)
    out.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    meta = config["meta"]
    print(
        f"Wrote {meta['sceneCount']} exhibits → {out}\n"
        f"  edition: {meta['edition']}\n"
        f"  soundtrack {meta['soundtrackDurationMs'] / 60000:.1f} min\n"
        f"  holds {meta['holdMinMs'] / 1000:.1f}–{meta['holdMaxMs'] / 1000:.1f}s "
        f"(avg {meta['avgHoldMs'] / 1000:.1f}s)\n"
        f"  max same-lesson run: {meta['maxSameLessonRun']}\n"
        f"  ending: {' → '.join(meta['endingSlugs'])}\n"
        f"  categories: {meta['categoryCounts']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
