#!/usr/bin/env python3
"""Build Lesson 5 Gallery — image and music only (final learning stage)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"
LESSON = 5
COLLECTION_ID = "lesson_05_gallery"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402

OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)

# ~8 min Foundations bed (Lesson 5 → Study Version 2).
FOUNDATIONS_SOUNDTRACK = "audio/study_version_2_minus3db.mp3"

SILENT_CREST_BOOKENDS = {
    "mode": "silentCrest",
    "closing": {
        "image": "images/gold_closing.png",
        "bookendSize": "small",
        "fadeWithSoundtrackEnd": True,
    },
}

IMAGE_OVERRIDES: dict[str, dict] = {}

GALLERY_CAMERA_BY_SLUG: dict[str, dict] = {
    "craft": {"motion": "push-in"},
    "left": {"motion": "drift-x"},
    "right": {"motion": "drift-x"},
    "possess": {"motion": "drift-y", "focus": "50% 48%"},
    "bribe": {"motion": "drift-diagonal"},
    "tribute": {"motion": "push-in"},
    "paragraph": {"motion": "drift-x"},
    "sword": {"motion": "push-in", "focus": "50% 42%"},
    "blade": {"motion": "rise"},
    "cut": {"motion": "drift-diagonal"},
    "seduce": {"motion": "drift-y"},
    "shining": {"motion": "rise", "focus": "50% 38%"},
    "rule": {"motion": "push-in"},
    "vice": {"motion": "drift-x"},
    "separate": {"motion": "drift-y"},
    "street": {"motion": "drift-diagonal"},
    "town": {"motion": "push-in", "focus": "50% 45%"},
    "possible": {"motion": "rise"},
    "top": {"motion": "push-in", "focus": "50% 40%"},
    "child": {"motion": "drift-x"},
}

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)

RECORDING_BLACK_BEFORE_MS = 3000
ARTWORK_ARRIVAL_FADE_MS = 2000

CLOSING_TIMING_MS = {
    "closingBlackBeforeMs": 800,
    "closingRevealMs": 2500,
    "closingHoldMs": 1500,
    "closingExhaleMs": 4000,
    "closingBlackAfterMs": 1200,
    "closingSilenceHoldMs": 0,
    "closingFadeToBlackMs": 0,
    "blackHoldMs": 0,
}


def soundtrack_duration_ms(relative_path: str) -> int:
    audio_path = ROOT / relative_path
    if not audio_path.is_file():
        return 489_672
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
                str(audio_path),
            ],
            text=True,
        ).strip()
        return int(float(out) * 1000)
    except (subprocess.CalledProcessError, OSError, ValueError):
        return 489_672


def gallery_exhibition_timing(scene_count: int, soundtrack_ms: int) -> dict:
    transition_ms = 3500
    closing_lead_ms = sum(
        CLOSING_TIMING_MS[k]
        for k in (
            "closingBlackBeforeMs",
            "closingRevealMs",
            "closingHoldMs",
            "closingExhaleMs",
        )
    )
    transition_total = max(0, scene_count - 1) * transition_ms
    content_per_exhibit = (
        soundtrack_ms
        - closing_lead_ms
        - transition_total
        - RECORDING_BLACK_BEFORE_MS
        - ARTWORK_ARRIVAL_FADE_MS
    ) // max(1, scene_count)

    artwork_alone_ms = int(content_per_exhibit * 0.485)
    kanji_reveal_ms = 400
    kanji_hold_ms = 800
    kanji_fade_ms = 400
    verse_reveal_ms = 300
    verse_fade_ms = 300
    verse_hold_ms = max(
        1200,
        (
            content_per_exhibit
            - artwork_alone_ms
            - kanji_reveal_ms
            - kanji_hold_ms
            - kanji_fade_ms
            - 2 * (verse_reveal_ms + verse_fade_ms)
        )
        // 2,
    )

    return {
        "artworkArrivalMs": 0,
        "artworkArrivalFadeMs": ARTWORK_ARRIVAL_FADE_MS,
        "exhibitionBlackBeforeMs": RECORDING_BLACK_BEFORE_MS,
        "artworkAloneMs": artwork_alone_ms,
        "kanjiRevealMs": kanji_reveal_ms,
        "imageVerseKanjiHoldMs": kanji_hold_ms,
        "imageVerseKanjiFadeMs": kanji_fade_ms,
        "titleFadeMs": kanji_fade_ms,
        "verseJpRevealMs": verse_reveal_ms,
        "verseJpHoldMs": verse_hold_ms,
        "verseJpFadeMs": verse_fade_ms,
        "verseEnRevealMs": verse_reveal_ms,
        "verseEnHoldMs": verse_hold_ms,
        "verseEnFadeMs": verse_fade_ms,
        "exhibitTransitionMs": transition_ms,
        "exhibitBlackHoldMs": 0,
        "kenBurnsDurationMs": content_per_exhibit,
        **CLOSING_TIMING_MS,
    }


def exhibit_runtime_ms(timing: dict, scene_count: int) -> int:
    content = (
        timing["artworkAloneMs"]
        + timing["kanjiRevealMs"]
        + timing["imageVerseKanjiHoldMs"]
        + timing["imageVerseKanjiFadeMs"]
        + timing["verseJpRevealMs"]
        + timing["verseJpHoldMs"]
        + timing["verseJpFadeMs"]
        + timing["verseEnRevealMs"]
        + timing["verseEnHoldMs"]
        + timing["verseEnFadeMs"]
    )
    transitions = max(0, scene_count - 1) * timing["exhibitTransitionMs"]
    closing = sum(
        CLOSING_TIMING_MS[k]
        for k in (
            "closingBlackBeforeMs",
            "closingRevealMs",
            "closingHoldMs",
            "closingExhaleMs",
            "closingBlackAfterMs",
        )
    )
    lead = timing.get("exhibitionBlackBeforeMs", 0) + timing.get("artworkArrivalFadeMs", 0)
    return lead + scene_count * content + transitions + closing


def image_rev(relative: str) -> int | None:
    path = ASSETS / relative
    if path.is_file():
        return int(path.stat().st_mtime)
    return None


def gallery_camera(slug: str) -> dict:
    return dict(GALLERY_CAMERA_BY_SLUG.get(slug, {"motion": "push-in"}))


def parse_lesson_scenes(lesson: int) -> list[dict]:
    html_path = REPO / "contents/books/book_01/lessons" / f"lesson_{lesson:02d}.html"
    html = html_path.read_text(encoding="utf-8")
    scenes: list[dict] = []
    for block in SECTION_RE.findall(html):
        kanji_m = re.search(r'data-kanji="([^"]+)"', block)
        slug_m = re.search(r'data-slug="([^"]+)"', block)
        keyword_m = re.search(r'<span class="kanji-keyword">([^<]+)</span>', block)
        img_m = re.search(r"assets/studies/([^\"']+\.png)", block)
        jp_m = re.search(r'<p class="jp-verse[^"]*">(.*?)</p>', block, re.DOTALL)
        en_m = re.search(r'<p class="en-verse">(.*?)</p>', block, re.DOTALL)
        if not (kanji_m and slug_m and jp_m and en_m):
            continue

        slug = slug_m.group(1)
        keyword = keyword_m.group(1).strip() if keyword_m else slug.replace("_", " ")
        image = f"studies/{img_m.group(1)}" if img_m else f"studies/{slug}.png"
        en = re.sub(r"<br\s*/?>", "\n", en_m.group(1), flags=re.IGNORECASE).strip()
        cam = gallery_camera(slug)
        scene = {
            "id": f"L{lesson:02d}_{slug}",
            "kanji": kanji_m.group(1),
            "keyword": keyword,
            "image": image,
            "galleryCamera": cam,
            "verse": {
                "jpHtml": jp_m.group(1).strip(),
                "en": en,
            },
            "meta": {"lesson": lesson, "slug": slug},
        }
        if cam.get("focus"):
            scene["imageFocus"] = cam["focus"]
        if slug in IMAGE_OVERRIDES:
            scene.update(IMAGE_OVERRIDES[slug])
        rev = image_rev(image)
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)
    return scenes


def build() -> dict:
    scenes = parse_lesson_scenes(LESSON)
    soundtrack_ms = soundtrack_duration_ms(FOUNDATIONS_SOUNDTRACK)
    exhibition = gallery_exhibition_timing(len(scenes), soundtrack_ms)
    runtime_ms = exhibit_runtime_ms(exhibition, len(scenes))
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "KML Gallery — Lesson 5 (Foundations)",
        "notes": (
            "Final learning stage: artwork and Foundations music only (~8 min). "
            f"Exhibit pacing fits the soundtrack ({runtime_ms // 1000}s runtime, "
            f"{exhibition['artworkAloneMs'] // 1000}s image hold per scene); "
            "composition-aware camera drift (~3–5% per exhibit)."
        ),
        "soundtrack": {"main": FOUNDATIONS_SOUNDTRACK},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": exhibition,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "gallery",
            "showKeyword": False,
            "showKanji": False,
            "exhibitProfile": "gallery",
            "verseMode": "sequential",
            "bookendStyle": "galleryCrest",
        },
        "meta": {
            "family": "gallery",
            "lesson": LESSON,
            "stage": "gallery",
            "foundationsTrack": "study_version_2",
            "sceneCount": len(scenes),
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    timing = config["exhibition"]
    runtime_s = exhibit_runtime_ms(timing, len(config["scenes"])) / 1000
    print(
        f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH} "
        f"({runtime_s:.0f}s runtime, {timing['artworkAloneMs'] / 1000:.1f}s image hold)"
    )

    from framing_policy import run_fill_safety_audit

    return run_fill_safety_audit(COLLECTION_ID)


if __name__ == "__main__":
    raise SystemExit(main())
