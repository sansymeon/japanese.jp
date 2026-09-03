#!/usr/bin/env python3
"""Build initial Lesson Art Gallery prototypes (short-form, separate from Ambient Movies).

Uses art_exhibit_N.mp3 at natural duration — no loop/stretch.
Ordinary 16:9 scenes are still; one prototype includes a Miyajima panorama walk.
Silent gold crest reserved at the end, fading with the soundtrack.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402

# Gentle dissolve — artwork fades into the next (not a video cut).
TRANSITION_MS = 3_750
ARRIVAL_FADE_MS = 3_750
CLOSING_REVEAL_MS = 2_500
CLOSING_HOLD_MS = 1_500
CLOSING_EXHALE_MS = 4_000
CLOSING_BLACK_AFTER_MS = 800

# Crest occupies the final portion of the music (music + crest end together).
CREST_MS = (
    CLOSING_REVEAL_MS + CLOSING_HOLD_MS + CLOSING_EXHALE_MS + CLOSING_BLACK_AFTER_MS
)

BOOKENDS = {
    "mode": "silentCrest",
    "closing": {
        "image": "images/gold_closing.png",
        "bookendSize": "small",
        "holdUntilSoundtrackEnds": False,
        "fadeWithSoundtrackEnd": True,
        "silentAfterSoundtrack": False,
    },
}

# Editorial shortlists for first prototypes only — not a template for all lessons.
PROTOTYPES = [
    {
        "id": "proto_lesson_art_gallery_34",
        "lesson": 34,
        "title": "Lesson Art Gallery — Lesson 34 (prototype)",
        "soundtrack": "audio/art_exhibit_1.mp3",
        "notes": (
            "Short-form Lesson Art Gallery prototype. Still 16:9 holds, "
            "restrained dissolves, chamber music at natural length, gold crest ending."
        ),
        "scenes": [
            {"slug": "fear", "image": "studies/fear.jpg"},
            {"slug": "beguile", "image": "studies/beguile.jpg"},
            {"slug": "melancholy", "image": "studies/melancholy.jpg"},
            {"slug": "enlightenment", "image": "studies/enlightenment.jpg"},
            {"slug": "humility", "image": "studies/humility.jpg"},
            {"slug": "ecstasy", "image": "studies/ecstasy.jpg"},
            {"slug": "remorse", "image": "studies/remorse.jpg"},
            {"slug": "recollection", "image": "studies/recollection.jpg"},
        ],
    },
    {
        "id": "proto_lesson_art_gallery_32",
        "lesson": 32,
        "title": "Lesson Art Gallery — Lesson 32 (prototype)",
        "soundtrack": "audio/art_exhibit_2.mp3",
        "notes": (
            "Short-form Lesson Art Gallery prototype. Village, garden, and street "
            "atmosphere; still frames; chamber music at natural length."
        ),
        "scenes": [
            {"slug": "sayeth", "image": "studies/sayeth.jpg"},
            {"slug": "country", "image": "studies/country.jpg"},
            {"slug": "garden", "image": "studies/garden.jpg"},
            {"slug": "courtyard", "image": "studies/courtyard.jpg"},
            {"slug": "store", "image": "studies/store.jpg"},
            {"slug": "government_office", "image": "studies/government_office.jpg"},
            {"slug": "heart", "image": "studies/heart.jpg"},
            {"slug": "podium", "image": "studies/podium.jpg"},
        ],
    },
    {
        "id": "proto_lesson_art_gallery_31_panorama",
        "lesson": 31,
        "title": "Lesson Art Gallery — Lesson 31 + Miyajima panorama (prototype)",
        "soundtrack": "audio/art_exhibit_3.mp3",
        "notes": (
            "Short-form Lesson Art Gallery prototype with one ultra-wide Miyajima "
            "panorama walk (shrine → water → great torii). Other scenes remain still."
        ),
        "scenes": [
            {"slug": "reef", "image": "studies/reef.jpg"},
            {"slug": "gather", "image": "studies/gather.jpg"},
            {"slug": "noon", "image": "studies/noon.jpg"},
            {
                "slug": "miyajima_panorama",
                "image": "lesson_art_gallery/miyajima_panorama.png",
                "motion": "panorama-walk",
                "direction": "ltr",
                "holdBiasMs": 42_000,
                "keyword": "Miyajima",
            },
            {"slug": "observe", "image": "studies/observe.jpg"},
            {"slug": "feathers", "image": "studies/feathers.jpg"},
            {"slug": "assurance", "image": "studies/assurance.jpg"},
        ],
    },
]


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
    return int(round(float(out) * 1000))


def image_rev(relative: str) -> int | None:
    path = ASSETS / relative
    if path.is_file():
        return int(path.stat().st_mtime)
    return None


def distribute_holds(
    n: int,
    budget_ms: int,
    *,
    hold_bias: dict[int, int] | None = None,
) -> list[int]:
    """Even holds with optional longer bias for panorama (or other anchors)."""
    hold_bias = hold_bias or {}
    if n <= 0:
        return []
    reserved = sum(hold_bias.values())
    free_n = n - len(hold_bias)
    if free_n < 0:
        raise SystemExit("hold bias covers more scenes than exist")
    remaining = budget_ms - reserved
    if remaining < free_n * 8_000:
        raise SystemExit(
            f"Soundtrack too short for holds (budget {budget_ms}ms, "
            f"reserved {reserved}ms, free scenes {free_n})"
        )
    base = remaining // free_n if free_n else 0
    holds = []
    free_idxs = [i for i in range(n) if i not in hold_bias]
    for i in range(n):
        if i in hold_bias:
            holds.append(hold_bias[i])
        else:
            holds.append(base)
    drift = budget_ms - sum(holds)
    # Nudge free scenes to absorb rounding.
    j = 0
    while drift != 0 and free_idxs:
        idx = free_idxs[j % len(free_idxs)]
        step = 1 if drift > 0 else -1
        if drift < 0 and holds[idx] <= 8_000:
            j += 1
            if j > n * 50:
                break
            continue
        holds[idx] += step
        drift -= step
        j += 1
    return holds


def build_one(spec: dict) -> dict:
    soundtrack = spec["soundtrack"]
    soundtrack_ms = soundtrack_duration_ms(soundtrack)
    items = spec["scenes"]
    n = len(items)
    # Engine galleryExhibitDurationMs includes exhibitTransitionMs on every scene,
    # including the last (handoff into crest). Budget n transitions, not n-1.
    transitions = n * TRANSITION_MS
    scene_budget = soundtrack_ms - CREST_MS - transitions
    if scene_budget < n * 8_000:
        raise SystemExit(
            f"{spec['id']}: soundtrack {soundtrack_ms}ms too short for {n} scenes "
            f"(need crest {CREST_MS}ms + transitions {transitions}ms)"
        )

    hold_bias = {}
    for i, item in enumerate(items):
        if item.get("holdBiasMs"):
            hold_bias[i] = int(item["holdBiasMs"])

    holds = distribute_holds(n, scene_budget, hold_bias=hold_bias)
    scenes = []
    for item, hold in zip(items, holds):
        motion = item.get("motion") or "still"
        camera = {"motion": motion}
        if motion == "panorama-walk":
            camera["direction"] = item.get("direction") or "ltr"
            if "edgeInset" in item:
                camera["edgeInset"] = item["edgeInset"]
        scene = {
            "id": f"L{spec['lesson']}_{item['slug']}",
            "kanji": "",
            "keyword": item.get("keyword") or item["slug"].replace("_", " "),
            "image": item["image"],
            "galleryCamera": camera,
            "artworkAloneMs": hold,
            "verse": {"jpHtml": "", "en": ""},
            "meta": {
                "lesson": spec["lesson"],
                "slug": item["slug"],
                "lessonArtGallery": True,
                "camera": motion,
            },
        }
        rev = image_rev(item["image"])
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)

    avg_hold = sum(holds) / n
    panorama = next((s for s in scenes if s["galleryCamera"]["motion"] == "panorama-walk"), None)

    collection = {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": spec["id"],
        "title": spec["title"],
        "notes": (
            f"{spec['notes']} "
            f"~{avg_hold / 1000:.1f}s avg hold · {TRANSITION_MS}ms dissolve · "
            f"crest {CREST_MS / 1000:.1f}s within soundtrack "
            f"({soundtrack_ms / 1000:.1f}s). Prototype only — do not propagate yet."
        ),
        "soundtrack": {"main": soundtrack},
        "bookends": dict(BOOKENDS),
        "exhibition": {
            "artworkArrivalMs": 0,
            "artworkArrivalFadeMs": ARRIVAL_FADE_MS,
            "exhibitionBlackBeforeMs": 0,
            "artworkAloneMs": int(round(avg_hold)),
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
            "kenBurnsDurationMs": int(round(avg_hold)) + TRANSITION_MS,
            "closingBlackBeforeMs": 0,
            "closingRevealMs": CLOSING_REVEAL_MS,
            "closingHoldMs": CLOSING_HOLD_MS,
            "closingExhaleMs": CLOSING_EXHALE_MS,
            "closingFadeToBlackMs": CLOSING_EXHALE_MS,
            "closingBlackAfterMs": CLOSING_BLACK_AFTER_MS,
            "closingSilenceHoldMs": 0,
            "blackHoldMs": 0,
            "seamlessExhibitHandoff": True,
        },
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "lessonArtGallery",
            "showKeyword": False,
            "showKanji": False,
            "exhibitProfile": "gallery",
            "verseMode": "sequential",
            "bookendStyle": "galleryCrest",
            "typography": "mobile-refine",
        },
        "meta": {
            "family": "lessonArtGallery",
            "prototype": True,
            "lesson": spec["lesson"],
            "sceneCount": n,
            "soundtrackDurationMs": soundtrack_ms,
            "crestDurationMs": CREST_MS,
            "transitionMs": TRANSITION_MS,
            "avgHoldMs": int(round(avg_hold)),
            "selectedImages": [s["meta"]["slug"] for s in scenes],
            "panorama": bool(panorama),
            "estimatedContentRuntimeMs": ARRIVAL_FADE_MS + soundtrack_ms,
        },
        "scenes": scenes,
    }
    return collection


def main() -> int:
    report = []
    for spec in PROTOTYPES:
        for item in spec["scenes"]:
            path = ASSETS / item["image"]
            if not path.is_file():
                raise SystemExit(f"Missing artwork: {path}")
        collection = build_one(spec)
        out = write_collection_path(ROOT, spec["id"])
        out.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        holds = [s["artworkAloneMs"] for s in collection["scenes"]]
        print(f"Wrote {out.relative_to(ROOT)}")
        print(
            f"  soundtrack {collection['meta']['soundtrackDurationMs']/1000:.1f}s · "
            f"{len(holds)} images · avg hold {sum(holds)/len(holds)/1000:.1f}s · "
            f"transition {TRANSITION_MS}ms · crest {CREST_MS/1000:.1f}s"
        )
        report.append(
            {
                "id": spec["id"],
                "path": str(out.relative_to(ROOT)),
                "soundtrack": spec["soundtrack"],
                "soundtrackDurationMs": collection["meta"]["soundtrackDurationMs"],
                "imageCount": len(holds),
                "avgHoldMs": int(round(sum(holds) / len(holds))),
                "holdsMs": holds,
                "selected": collection["meta"]["selectedImages"],
                "panorama": collection["meta"]["panorama"],
            }
        )

    report_path = ROOT / "collections" / "prototypes" / "lesson_art_gallery_prototypes_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Report → {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
