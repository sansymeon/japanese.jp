#!/usr/bin/env python3
"""Build Quiet Cinematic Japan — Lessons 21–25 exhibition.

Source order: quiet_cinematic_review/data/lessons_21_25_draft.json
Textless ambient gallery profile; holds fitted to audio/-3db_fifty_minutes.mp3.
Silent gold crest after soundtrack (Ambient Film style).
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402

COLLECTION_ID = "lessons_21_25_quiet_cinematic"
DRAFT_PATH = (
    ROOT / "quiet_cinematic_review" / "data" / "lessons_21_25_draft.json"
)
OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)
SOUNDTRACK = "audio/-3db_fifty_minutes.mp3"
SEED = 20260805

MOTIONS = (
    "push-in",
    "pull-out",
    "drift-x",
    "drift-y",
    "drift-diagonal",
    "rise",
)

HOLD_MIN_MS = 70_000
HOLD_MAX_MS = 110_000
HOLD_EXCEPTIONAL_MS = 120_000
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
            "default=nw=1:nk=1",
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


def distribute_holds(n: int, budget_ms: int, rng: random.Random) -> list[int]:
    base = budget_ms // n
    holds = [base] * n
    drift = budget_ms - sum(holds)
    # Prefer slightly longer holds for early anchors and the final image.
    preference = list(range(n))
    rng.shuffle(preference)
    preference = [0, 1, 2, n - 1] + [i for i in preference if i not in (0, 1, 2, n - 1)]

    i = 0
    while drift != 0 and i < n * 20:
        idx = preference[i % n]
        if drift > 0 and holds[idx] < HOLD_EXCEPTIONAL_MS:
            step = min(drift, HOLD_EXCEPTIONAL_MS - holds[idx], 500)
            holds[idx] += step
            drift -= step
        elif drift < 0 and holds[idx] > HOLD_MIN_MS:
            step = min(-drift, holds[idx] - HOLD_MIN_MS, 500)
            holds[idx] -= step
            drift += step
        i += 1
    holds[-1] += budget_ms - sum(holds)
    return holds


def assign_motions(n: int, rng: random.Random) -> list[str]:
    motions: list[str] = []
    prev = None
    for _ in range(n):
        choices = [m for m in MOTIONS if m != prev] or list(MOTIONS)
        pick = rng.choice(choices)
        motions.append(pick)
        prev = pick
    return motions


def build() -> dict:
    if not DRAFT_PATH.is_file():
        raise SystemExit(f"Missing draft: {DRAFT_PATH}")

    draft = json.loads(DRAFT_PATH.read_text(encoding="utf-8"))
    items = draft.get("items") or []
    if not items:
        raise SystemExit("Draft has no items")

    rng = random.Random(SEED)
    soundtrack_ms = soundtrack_duration_ms(SOUNDTRACK)
    n = len(items)
    transitions = max(0, n - 1) * TRANSITION_MS
    hold_budget = soundtrack_ms - transitions
    if hold_budget < n * HOLD_MIN_MS:
        raise SystemExit(
            f"Soundtrack too short for {n} scenes at min hold "
            f"({hold_budget}ms budget, need {n * HOLD_MIN_MS}ms)"
        )

    holds = distribute_holds(n, hold_budget, rng)
    motions = assign_motions(n, rng)
    scenes = []
    for item, hold, motion in zip(items, holds, motions):
        image = item["image"]
        scene = {
            "id": item["id"],
            "kanji": item.get("kanji") or "",
            "keyword": item.get("keyword") or item.get("slug") or "",
            "image": image,
            "galleryCamera": {"motion": motion},
            "artworkAloneMs": hold,
            "verse": {"jpHtml": "", "en": ""},
            "meta": {
                "lesson": item["lesson"],
                "slug": item["slug"],
                "source": f"lesson_{item['lesson']}",
                "quietCinematic": True,
            },
        }
        rev = image_rev(image)
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)

    avg_hold = sum(holds) / n
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Quiet Cinematic Japan — Lessons 21–25",
        "notes": (
            "Curated textless journey: Quiet Cinematic Japan from Lessons 21–25. "
            "Landscape and atmosphere first; solitary figures only when they serve mood. "
            f"Ken Burns gallery profile, ~{avg_hold / 1000:.0f}s holds, "
            f"silent gold crest after soundtrack "
            f"(reveal {CLOSING_REVEAL_MS // 1000}s · hold {CLOSING_HOLD_MS // 1000}s · "
            f"fade {CLOSING_FADE_MS // 1000}s). {n} images · soundtrack "
            f"{soundtrack_ms / 60000:.1f} min. Draft: quiet_cinematic_review."
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
            "kenBurnsDurationMs": int(avg_hold) + TRANSITION_MS,
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
            "family": "quietCinematicJapan",
            "showKeyword": False,
            "showKanji": False,
            "exhibitProfile": "gallery",
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "bookendStyle": "galleryCrest",
            "cameraMotionScale": CAMERA_MOTION_SCALE,
        },
        "meta": {
            "family": "quietCinematicJapan",
            "theme": "Quiet Cinematic Japan",
            "edition": "Lessons 21–25",
            "lessons": list(range(21, 26)),
            "sceneCount": n,
            "soundtrackDurationMs": soundtrack_ms,
            "avgHoldMs": int(avg_hold),
            "holdMinMs": min(holds),
            "holdMaxMs": max(holds),
            "cameraMotionScale": CAMERA_MOTION_SCALE,
            "draftPath": str(DRAFT_PATH.relative_to(ROOT)),
            "unusedCandidates": len(draft.get("unusedCandidates") or []),
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH}")
    print(
        f"  avg hold {config['meta']['avgHoldMs'] / 1000:.1f}s · "
        f"soundtrack {config['meta']['soundtrackDurationMs'] / 60000:.1f} min"
    )
    for lesson in range(21, 26):
        n = sum(1 for s in config["scenes"] if s["meta"]["lesson"] == lesson)
        print(f"  Lesson {lesson}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
