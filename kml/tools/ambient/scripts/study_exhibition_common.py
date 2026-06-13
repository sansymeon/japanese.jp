"""Shared config for Ambient Study exhibition builds (Gallery Seal Ending)."""

from __future__ import annotations

STUDY_LESSON = "audio/study_lesson.mp3"
INTRO_HOLD_MS = 1000
INTRO_DURATION_MS = 9000

GALLERY_SEAL_IMAGE = "images/gold_closing.png"


def gallery_seal_ending() -> dict:
    return {
        "type": "gallerySeal",
        "sealImage": GALLERY_SEAL_IMAGE,
    }


def gallery_seal_timing() -> dict:
    return {
        "fadeMs": 1800,
        "kanjiLeadMs": 2000,
        "keywordLeadMs": 5000,
        "verseJpLeadMs": 8500,
        "sceneDurationMs": 22000,
        "studyExitFadeMs": 1800,
        "studyEmptyBeatMs": 500,
        "studyKanjiGapMs": 350,
        "introExitFadeMs": 1200,
        "studyLoopConcertFadeMs": 2500,
        "studyLoopFadeMs": 2500,
        "crossfadeMs": 2500,
        "kenBurnsDurationMs": 60000,
        "gallerySealVerseFadeMs": 2200,
        "gallerySealKanjiFadeMs": 2200,
        "gallerySealImageHoldMs": 6000,
        "gallerySealHoldDarkenMs": 4000,
        "gallerySealHoldDarkenDelayMs": 1500,
        "gallerySealFadeToBlackMs": 5000,
        "gallerySealFadeInMs": 4000,
        "gallerySealOverlapMs": 2800,
        "gallerySealHoldMs": 9000,
    }


def youtube_timing() -> dict:
    return {
        "fadeMs": 1800,
        "kanjiLeadMs": 2000,
        "keywordLeadMs": 5000,
        "verseJpLeadMs": 8500,
        "sceneDurationMs": 22000,
        "studyExitFadeMs": 1800,
        "studyEmptyBeatMs": 500,
        "studyKanjiGapMs": 350,
        "introExitFadeMs": 1200,
        "studyLoopConcertFadeMs": 2500,
        "studyLoopFadeMs": 2500,
        "crossfadeMs": 2500,
        "kenBurnsDurationMs": 60000,
    }


def reorder_scenes(
    scenes: list[dict], *, first: str, last: str
) -> list[dict]:
    by_id = {s["id"]: s for s in scenes}
    original = [s["id"] for s in scenes]
    middle = [sid for sid in original if sid not in (first, last)]
    order = [first] + middle + [last]
    missing = [sid for sid in order if sid not in by_id]
    if missing:
        raise ValueError(f"Missing scenes for reorder: {missing}")
    return [by_id[sid] for sid in order]


def exhibition_study_config(
    *,
    lesson: int,
    title: str,
    notes: str,
    scenes: list[dict],
    assets_base: str = "../../assets",
) -> dict:
    return {
        "id": f"lesson_{lesson}_study",
        "title": title,
        "presentation": "study",
        "assetsBase": assets_base,
        "notes": notes,
        "ending": gallery_seal_ending(),
        "intro": {
            "image": f"covers/lesson_{lesson}.png",
            "title": f"Lesson {lesson}",
            "holdBeforeMs": INTRO_HOLD_MS,
            "durationMs": INTRO_DURATION_MS,
        },
        "soundtrack": {"main": STUDY_LESSON},
        "timing": gallery_seal_timing(),
        "background": {
            "mode": "image",
            "kenBurns": True,
            "overlayOpacity": 0.45,
            "blurPx": 0,
        },
        "display": {
            "showKeyword": True,
            "showFurigana": False,
            "loop": False,
            "autoAdvance": True,
        },
        "scenes": scenes,
    }


def youtube_study_config(
    *,
    lesson: int,
    title: str,
    notes: str,
    scenes: list[dict],
    assets_base: str = "../../assets",
) -> dict:
    return {
        "id": f"lesson_{lesson}_study",
        "title": title,
        "presentation": "study",
        "assetsBase": assets_base,
        "notes": notes,
        "intro": {
            "image": f"covers/lesson_{lesson}.png",
            "title": f"Lesson {lesson}",
            "holdBeforeMs": INTRO_HOLD_MS,
            "durationMs": INTRO_DURATION_MS,
        },
        "soundtrack": {"main": STUDY_LESSON},
        "timing": youtube_timing(),
        "background": {
            "mode": "image",
            "kenBurns": True,
            "overlayOpacity": 0.45,
            "blurPx": 0,
        },
        "display": {
            "showKeyword": True,
            "showFurigana": False,
            "loop": True,
            "autoAdvance": True,
        },
        "scenes": scenes,
    }
