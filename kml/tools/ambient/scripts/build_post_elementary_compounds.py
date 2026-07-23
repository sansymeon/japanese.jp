#!/usr/bin/env python3
"""Build Jr High / post-elementary compounds collections (groups of 50).

Source: collections/post_elementary/post_elementary_jukugo_list.json
Order: post_elementary_01 … _11 scene lists (Heisig / PE series order).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from collection_paths import write_collection_path  # noqa: E402

COLLECTIONS = ROOT / "collections" / "post_elementary"
JUKUGO = COLLECTIONS / "post_elementary_jukugo_list.json"
MANIFEST = ROOT / "collections" / "manifest.json"

PART_SIZE = 50
SOUNDTRACK_CYCLE = 3  # rotate jr_high_compounds_soundtrack_1..3.mp3
SOUNDTRACK_FALLBACK = "audio/jr_high_compounds_soundtrack_1.mp3"

STEP = 19400
LAST_BODY = STEP - 1400
OPEN = 800 + 1200 + 3200
REVIEW = 22000
FADE = 4000
BLACK = 600


def soundtrack_for_part(part: int) -> tuple[str, int]:
    """Rotate jr_high_compounds_soundtrack_1..3.mp3 by part number."""
    import subprocess

    slot = ((part - 1) % SOUNDTRACK_CYCLE) + 1
    rel = f"audio/jr_high_compounds_soundtrack_{slot}.mp3"
    path = ROOT / rel
    if not path.is_file():
        rel = SOUNDTRACK_FALLBACK
        path = ROOT / rel
    duration_ms = 1005035
    try:
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
        if out:
            duration_ms = int(float(out) * 1000)
    except Exception:
        pass
    return rel, duration_ms


def content_runtime_ms(n: int) -> int:
    if n < 1:
        return OPEN + REVIEW + FADE + BLACK
    if n == 1:
        return OPEN + LAST_BODY + REVIEW + FADE + BLACK
    return OPEN + (n - 1) * STEP + LAST_BODY + REVIEW + FADE + BLACK


def exhibition() -> dict:
    return {
        "artworkArrivalMs": 0,
        "artworkArrivalFadeMs": 1200,
        "artworkAloneMs": 0,
        "exhibitionBlackBeforeMs": 800,
        "compoundsPauseBeforeMs": 3200,
        "compoundsStepRevealMs": 1400,
        "compoundsFuriganaEnterDelayMs": 900,
        "compoundsFuriganaEnterMs": 2200,
        "compoundsFuriganaHoldMs": 3000,
        "compoundsFuriganaFadeMs": 2200,
        "compoundsNativeHoldMs": 2200,
        "compoundsReadingRevealMs": 1200,
        "compoundsReadingHoldMs": 1800,
        "compoundsEnRevealMs": 1200,
        "compoundsEnHoldMs": 3500,
        "compoundsEnFadeMs": 1400,
        "compoundsStepFadeMs": 1400,
        "compoundsFinalReviewHoldMs": 22000,
        "compoundsFinalFadeToBlackMs": 4000,
        "vocabArtworkExhaleMs": 2800,
        "exhibitTransitionMs": 0,
        "kenBurnsDurationMs": 1200000,
        "closingBlackAfterMs": 600,
    }


def display() -> dict:
    return {
        "loop": False,
        "hideChrome": True,
        "family": "japaneseVocabulary",
        "showKeyword": False,
        "showKanji": False,
        "showEnglish": True,
        "exhibitProfile": "japaneseVocabulary",
        "verseMode": "sequential",
        "typography": "mobile-refine",
        "typographyStyle": "foundations",
        "cameraMotionScale": 1.0,
    }


def build_part(part: int, batch: list[dict], part_count: int) -> dict:
    n = len(batch)
    first, last = batch[0], batch[-1]
    runtime = content_runtime_ms(n)
    soundtrack, soundtrack_ms = soundtrack_for_part(part)
    steps = [
        {
            "jp": e["anchor"],
            "reading": e["reading"],
            "en": e["en"],
            "jpHtml": e["jpHtml"],
            "meta": {
                "kanji": e["kanji"],
                "heisigNumber": e["heisigNumber"],
                "slug": e.get("slug"),
                "displayOrder": e["displayOrder"],
            },
        }
        for e in batch
    ]
    cid = f"post_elementary_compounds_{part:02d}"
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": cid,
        "title": f"Jr High Compounds — Part {part}",
        "notes": (
            f"Post-elementary compounds Part {part}/{part_count}: "
            f"{n} kanji ({first['kanji']}→{last['kanji']}), post_elementary series order. "
            "One anchor each — first compound that comes to mind. "
            "No individual kanji, no scenic images. Vocabulary typography. "
            "Ending: final compound review ~22s → 4s fade to black. "
            f"Soundtrack: {soundtrack} (~{soundtrack_ms // 1000}s)."
        ),
        "soundtrack": {"main": soundtrack},
        "exhibition": exhibition(),
        "display": display(),
        "meta": {
            "series": "post_elementary_compounds",
            "curriculum": "post_elementary",
            "scope": "post_elementary_through_joyo",
            "part": part,
            "partCount": part_count,
            "stage": "compounds",
            "format": "anchorCompoundsGrouped",
            "sceneCount": 1,
            "compoundCount": n,
            "kanjiRange": [first["kanji"], last["kanji"]],
            "heisigRange": [first["heisigNumber"], last["heisigNumber"]],
            "sourceOrder": "post_elementary_01..11",
            "soundtrackDurationMs": soundtrack_ms if n >= 50 else min(soundtrack_ms, runtime + 5000),
            "estimatedContentRuntimeMs": runtime,
            "timingNote": (
                f"{n} compounds ≈ {runtime / 1000:.0f}s "
                f"({int(runtime // 60000)}:{int(runtime % 60000) // 1000:02d}) "
                "including review+fade."
            ),
            "ending": "finalCompoundReview",
            "anchorRule": "firstCompoundThatComesToMind",
            "jukugoList": "post_elementary_jukugo_list.json",
        },
        "scenes": [
            {
                "id": f"PE_compounds_{part:02d}",
                "image": "images/black.png",
                "galleryCamera": {
                    "motion": "still",
                    "focus": "50% 50%",
                    "motionScale": 1.0,
                },
                "compounds": {"steps": steps},
            }
        ],
    }


def update_manifest(part_count: int) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    key = "collections"
    items = list(manifest[key])

    keep = [
        item
        for item in items
        if not (
            str(item.get("id", "")).startswith("post_elementary_compounds_")
            and item.get("id") != "post_elementary_compounds_prototype"
        )
    ]

    new_entries = [
        {
            "id": f"post_elementary_compounds_{part:02d}",
            "title": f"Jr High Compounds — Part {part}",
            "url": (
                f"./exhibition.html?collection=post_elementary_compounds_{part:02d}"
                "&typography=mobile-refine&verseMode=sequential"
            ),
            "sceneCount": 1,
            "family": "japaneseVocabulary",
            "presentation": "exhibition",
            "notes": (
                f"Jr high compounds part {part}/{part_count}. "
                f"Soundtrack: {soundtrack_for_part(part)[0]}."
            ),
        }
        for part in range(1, part_count + 1)
    ]

    ids = [x.get("id") for x in keep]
    if "post_elementary_compounds_prototype" in ids:
        idx = ids.index("post_elementary_compounds_prototype") + 1
    elif "post_elementary_01" in ids:
        idx = ids.index("post_elementary_01")
    else:
        idx = len(keep)
    keep[idx:idx] = new_entries
    manifest[key] = keep
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"manifest: inserted {part_count} compounds entries at index {idx}")


def main() -> int:
    if not JUKUGO.is_file():
        raise SystemExit(f"Missing jukugo list: {JUKUGO}")
    doc = json.loads(JUKUGO.read_text(encoding="utf-8"))
    entries = doc["entries"]
    part_count = (len(entries) + PART_SIZE - 1) // PART_SIZE

    for part in range(1, part_count + 1):
        start = (part - 1) * PART_SIZE
        batch = entries[start : start + PART_SIZE]
        collection = build_part(part, batch, part_count)
        path = write_collection_path(ROOT, collection["id"])
        path.write_text(
            json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            f"wrote {path.name}: {len(batch)} "
            f"{batch[0]['kanji']}→{batch[-1]['kanji']}  "
            f"~{collection['meta']['estimatedContentRuntimeMs'] / 1000:.0f}s"
        )

    update_manifest(part_count)
    print(f"done: {part_count} parts, {len(entries)} kanji")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
