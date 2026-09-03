#!/usr/bin/env python3
"""Build Digital Art Exhibition collections.

Prototype format — separate from Ambient Kanji, Quiet Exhibition, and
Lesson Art Gallery. Later exhibitions only need title, artworks, soundtrack,
and an optional opening crest.

  python3 scripts/build_digital_art_exhibition.py
  python3 scripts/build_digital_art_exhibition.py --id moon
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "collections" / "digital_art"

DEFAULT_TIMING = {
    "openingBlackBeforeMs": 1000,
    "openingRevealMs": 4500,
    "openingHoldMs": 4500,
    "openingDissolveMs": 9000,
    "titleDelayMs": 200,
    "titleRevealMs": 2200,
    "dissolveMs": 10000,
    "endingFadeMs": 12000,
    "endingBlackAfterMs": 1600,
}


def soundtrack_duration_ms(path: Path) -> int:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return int(round(float(raw) * 1000))


def fit_holds(
    artworks: list[dict],
    duration_ms: int,
    timing: dict,
) -> list[int]:
    n = len(artworks)
    if n == 0:
        return []
    opening = (
        timing["openingBlackBeforeMs"]
        + timing["openingRevealMs"]
        + timing["openingHoldMs"]
        + timing["openingDissolveMs"]
    )
    mid = 0
    for i, art in enumerate(artworks[:-1]):
        mid += int(art.get("dissolveMs") or timing["dissolveMs"])
    ending = timing["endingFadeMs"]
    budget = duration_ms - opening - mid - ending
    if budget < n * 8000:
        budget = n * 8000

    if all(art.get("holdMs") is not None for art in artworks):
        raw = [int(art["holdMs"]) for art in artworks]
        total = sum(raw) or 1
        scaled = [int(round(budget * h / total)) for h in raw]
        scaled[-1] += budget - sum(scaled)
        return scaled

    weights = []
    for i, art in enumerate(artworks):
        if art.get("weight") is not None:
            weights.append(float(art["weight"]))
        else:
            weights.append(0.92 + i * 0.06 + (0.28 if i == n - 1 else 0))
    wsum = sum(weights) or 1
    holds = [int(round(budget * w / wsum)) for w in weights]
    holds[-1] += budget - sum(holds)
    return holds


MOON = {
    "id": "moon",
    "title": "MOON",
    "notes": (
        "Digital Art Exhibition prototype. Gold-leaf Lesson 1 moon crest, "
        "then six nocturnal paintings. No kanji, verse, captions, or Ken Burns. "
        "Soundtrack is the master duration."
    ),
    "soundtrack": "audio/digital_art_moon.mp3",
    "opening": {
        "image": "covers/lesson_01.jpg",
        "title": "MOON",
        "titleMode": "label",
        "blackBeforeMs": 1000,
        "revealMs": 4500,
        "holdMs": 4500,
        "dissolveMs": 9000,
        "titleDelayMs": 200,
        "titleRevealMs": 2200,
    },
    "room": {
        "motion": "still",
    },
    "ending": {
        "fadeMs": 12000,
        "blackAfterMs": 1600,
    },
    "artworks": [
        {
            "id": "moonlight",
            "image": "digital_art_gallery/moon/1_moon.png",
            "holdMs": 14000,
            "dissolveMs": 10000,
        },
        {
            "id": "interior",
            "image": "digital_art_gallery/moon/2_interior.png",
            "holdMs": 15000,
            "dissolveMs": 10000,
        },
        {
            "id": "tree",
            "image": "digital_art_gallery/moon/3_tree.png",
            "holdMs": 13000,
            "dissolveMs": 10000,
        },
        {
            "id": "horizon",
            "image": "digital_art_gallery/moon/4_horizon.png",
            "holdMs": 15000,
            "dissolveMs": 10000,
        },
        {
            "id": "ripples",
            "image": "digital_art_gallery/moon/5_ripples.png",
            "holdMs": 12000,
            "dissolveMs": 12000,
        },
        {
            "id": "mist",
            "image": "digital_art_gallery/moon/6_mist.png",
            "holdMs": 17200,
        },
    ],
}

LESSON_2 = {
    "id": "lesson_2",
    "title": "BRIGHT",
    "notes": (
        "Digital Art Exhibition prototype. Gold-leaf Lesson 2 明 crest "
        "(日 over 月), then six studies of light. No kanji, verse, captions, "
        "or Ken Burns. Soundtrack is the master duration."
    ),
    "soundtrack": "audio/digital_art_2.mp3",
    "opening": {
        "image": "covers/lesson_02.jpg",
        "title": "BRIGHT",
        "titleMode": "label",
        "blackBeforeMs": 1000,
        "revealMs": 4500,
        "holdMs": 4500,
        "dissolveMs": 9000,
        "titleDelayMs": 200,
        "titleRevealMs": 2200,
    },
    "room": {
        "motion": "still",
    },
    "ending": {
        "fadeMs": 12000,
        "blackAfterMs": 1600,
    },
    "artworks": [
        {
            "id": "two_lights",
            "image": "digital_art_gallery/lesson_2/1_two_lights.png",
            "dissolveMs": 10000,
        },
        {
            "id": "refraction",
            "image": "digital_art_gallery/lesson_2/2_refraction.png",
            "dissolveMs": 10000,
        },
        {
            "id": "first_light",
            "image": "digital_art_gallery/lesson_2/3_first_light.png",
            "dissolveMs": 10000,
        },
        {
            "id": "old_light",
            "image": "digital_art_gallery/lesson_2/4_old_light.png",
            "dissolveMs": 10000,
        },
        {
            "id": "center",
            "image": "digital_art_gallery/lesson_2/5_center.png",
            "dissolveMs": 12000,
        },
        {
            "id": "thousand",
            "image": "digital_art_gallery/lesson_2/6_thousand.png",
        },
    ],
}

LESSON_3 = {
    "id": "lesson_3",
    "title": "RISE",
    "notes": (
        "Digital Art Exhibition prototype. Gold-leaf Lesson 3 昇 crest, "
        "then six works in numbered order. No kanji, verse, captions, "
        "or Ken Burns. Soundtrack is the master duration."
    ),
    "soundtrack": "audio/digital_art_3.mp3",
    "opening": {
        "image": "covers/lesson_03.jpg",
        "title": "RISE",
        "titleMode": "label",
        "blackBeforeMs": 1000,
        "revealMs": 4500,
        "holdMs": 4500,
        "dissolveMs": 9000,
        "titleDelayMs": 200,
        "titleRevealMs": 2200,
    },
    "room": {
        "motion": "still",
    },
    "ending": {
        "fadeMs": 12000,
        "blackAfterMs": 1600,
    },
    "artworks": [
        {
            "id": "tongue",
            "image": "digital_art_gallery/lesson_3/1_tongue.png",
            "dissolveMs": 10000,
        },
        {
            "id": "measure",
            "image": "digital_art_gallery/lesson_3/2_measure.png",
            "dissolveMs": 10000,
        },
        {
            "id": "above_below",
            "image": "digital_art_gallery/lesson_3/3_above_below.png",
            "dissolveMs": 10000,
        },
        {
            "id": "divination",
            "image": "digital_art_gallery/lesson_3/4_divination.png",
            "dissolveMs": 10000,
        },
        {
            "id": "rising",
            "image": "digital_art_gallery/lesson_3/5_rising.png",
            "dissolveMs": 12000,
        },
        {
            "id": "morning",
            "image": "digital_art_gallery/lesson_3/6_morning.png",
        },
    ],
}

EXHIBITIONS = {
    "moon": MOON,
    "lesson_2": LESSON_2,
    "lesson_3": LESSON_3,
}


def build_one(spec: dict) -> dict:
    timing = {**DEFAULT_TIMING}
    opening = spec.get("opening") or {}
    ending = spec.get("ending") or {}
    for key, field in (
        ("openingBlackBeforeMs", "blackBeforeMs"),
        ("openingRevealMs", "revealMs"),
        ("openingHoldMs", "holdMs"),
        ("openingDissolveMs", "dissolveMs"),
        ("titleDelayMs", "titleDelayMs"),
        ("titleRevealMs", "titleRevealMs"),
    ):
        if opening.get(field) is not None:
            timing[key] = int(opening[field])
    if ending.get("fadeMs") is not None:
        timing["endingFadeMs"] = int(ending["fadeMs"])
    if ending.get("blackAfterMs") is not None:
        timing["endingBlackAfterMs"] = int(ending["blackAfterMs"])

    soundtrack_rel = spec["soundtrack"]
    duration_ms = soundtrack_duration_ms(ROOT / soundtrack_rel)
    artworks_in = spec["artworks"]
    holds = fit_holds(artworks_in, duration_ms, timing)

    artworks = []
    for art, hold in zip(artworks_in, holds):
        item = {
            "id": art["id"],
            "image": art["image"],
            "holdMs": hold,
        }
        if art.get("dissolveMs") is not None:
            item["dissolveMs"] = int(art["dissolveMs"])
        if art.get("motion"):
            item["motion"] = art["motion"]
        artworks.append(item)

    collection = {
        "format": "digitalArtExhibition",
        "id": spec["id"],
        "title": spec["title"],
        "notes": spec.get("notes", ""),
        "assetsBase": "../../assets",
        "soundtrack": {
            "src": soundtrack_rel,
            "durationMs": duration_ms,
        },
        "opening": {
            "image": opening.get("image"),
            "title": opening.get("title") or spec["title"],
            "titleMode": opening.get("titleMode") or "label",
            "blackBeforeMs": timing["openingBlackBeforeMs"],
            "revealMs": timing["openingRevealMs"],
            "holdMs": timing["openingHoldMs"],
            "dissolveMs": timing["openingDissolveMs"],
            "titleDelayMs": timing["titleDelayMs"],
            "titleRevealMs": timing["titleRevealMs"],
        },
        "room": spec.get("room") or {"motion": "still"},
        "timing": {
            "dissolveMs": timing["dissolveMs"],
            "endingFadeMs": timing["endingFadeMs"],
            "endingBlackAfterMs": timing["endingBlackAfterMs"],
        },
        "ending": {
            "fadeMs": timing["endingFadeMs"],
            "blackAfterMs": timing["endingBlackAfterMs"],
        },
        "artworks": artworks,
        "meta": {
            "family": "digitalArtExhibition",
            "prototype": True,
            "sceneCount": len(artworks),
            "soundtrackDurationMs": duration_ms,
        },
    }
    if ending.get("brand"):
        collection["ending"]["brand"] = ending["brand"]
    return collection


def write_collection(collection: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{collection['id']}.json"
    path.write_text(json.dumps(collection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Digital Art Exhibition JSON")
    parser.add_argument("--id", help="Build a single exhibition id (default: all)")
    args = parser.parse_args()

    ids = [args.id] if args.id else list(EXHIBITIONS)
    for eid in ids:
        spec = EXHIBITIONS.get(eid)
        if not spec:
            print(f"Unknown exhibition id: {eid}", file=sys.stderr)
            return 1
        collection = build_one(spec)
        path = write_collection(collection)
        dur = collection["soundtrack"]["durationMs"]
        print(f"Wrote {path.relative_to(ROOT)}  soundtrack {dur / 1000:.2f}s  works {len(collection['artworks'])}")
        print(f"  Preview: digital-art-exhibition.html?collection={collection['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
