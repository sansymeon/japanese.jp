"""Shared helpers for Playwright exhibition MP4 recording."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

VIEWPORT = {"width": 1920, "height": 1080}

_AMBIENT_ROOT = Path(__file__).resolve().parents[1]
_PLAYWRIGHT_BROWSERS = _AMBIENT_ROOT / ".playwright-browsers"
if _PLAYWRIGHT_BROWSERS.is_dir():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(_PLAYWRIGHT_BROWSERS))


def exhibition_record_url(
    *,
    port: int,
    collection_id: str,
    display: dict | None = None,
) -> str:
    """Build exhibition.html URL with typography / verseMode from collection display."""
    display = display or {}
    params = [f"collection={collection_id}"]
    typo = display.get("typography")
    if typo:
        params.append(f"typography={typo}")
    verse_mode = display.get("verseMode")
    if verse_mode:
        params.append(f"verseMode={verse_mode}")
    query = "&".join(params)
    return f"http://127.0.0.1:{port}/exhibition.html?{query}"


def ensure_deps() -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required on PATH.", file=sys.stderr)
        sys.exit(1)
    try:
        import playwright  # noqa: F401
    except ImportError:
        print(
            "Playwright required:\n"
            "  python3 -m venv .venv && .venv/bin/pip install playwright\n"
            "  .venv/bin/playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)


def probe_duration_seconds(path: Path) -> float:
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
    return float(out)


def exhibit_ms_image_verse(t: dict) -> int:
    return (
        t["artworkAloneMs"]
        + t["kanjiRevealMs"]
        + t.get("imageVerseKanjiHoldMs", 2000)
        + t.get("imageVerseKanjiFadeMs", t.get("titleFadeMs", 1600))
        + t["verseJpRevealMs"]
        + t["verseJpHoldMs"]
        + t["verseJpFadeMs"]
        + t["verseEnRevealMs"]
        + t["verseEnHoldMs"]
        + t["verseEnFadeMs"]
        + t.get("exhibitTransitionMs", 4000)
    )


def heart_opening_timeline_ms(collection: dict, root: Path) -> tuple[int, int]:
    """Return (flute_delay_ms, ambient_start_ms)."""
    t = collection.get("exhibition") or {}
    bookends = collection.get("bookends") or {}
    before = int(t.get("openingBlackBeforeMs", 2000))
    exhale = int(t.get("openingExhaleMs", 6000))
    after = int(t.get("openingBlackAfterMs", 0))
    flute_path = root / (bookends.get("opening", {}).get("audio") or "audio/exhibition_flute_intro.mp3")
    flute_ms = int(probe_duration_seconds(flute_path) * 1000) if flute_path.is_file() else 0
    return before, before + flute_ms + exhale + after


def stroke_order_soundtrack_start_ms(collection: dict) -> int:
    """When main soundtrack begins — after initial exhibition black on scene 0."""
    t = collection.get("exhibition") or {}
    return int(t.get("exhibitionBlackBeforeMs", 0))


def grade_stroke_order_soundtrack_start_ms(collection: dict) -> int:
    """When main soundtrack begins for elementary grade stroke-order bookends.

    Matches exhibition-engine.js: scheduleSoundtrackAfterBookendImage fires from
    onImageReady (after openingBlackBeforeMs, before the reveal fade completes).
    """
    t = collection.get("exhibition") or {}
    opening = (collection.get("bookends") or {}).get("opening") or {}
    if opening.get("startSoundtrackWithImage"):
        before = int(t.get("openingBlackBeforeMs", 0))
        delay = int(
            opening.get("startSoundtrackAfterImageMs")
            or t.get("openingSoundtrackDelayMs", 0)
        )
        return before + delay
    return stroke_order_soundtrack_start_ms(collection)


def compounds_exhibition_soundtrack_start_ms(collection: dict) -> int:
    """When main soundtrack begins — after initial black on first compounds exhibit."""
    t = collection.get("exhibition") or {}
    return int(t.get("exhibitionBlackBeforeMs", 0))


def vocabulary_exhibition_soundtrack_start_ms(collection: dict) -> int:
    """When main soundtrack begins — after intro black + artwork fade-in."""
    t = collection.get("exhibition") or {}
    return int(t.get("exhibitionBlackBeforeMs", 0)) + int(t.get("artworkArrivalFadeMs", 0))


def reading_exhibition_soundtrack_start_ms(collection: dict) -> int:
    """When main soundtrack begins — after initial black, with first artwork fade."""
    t = collection.get("exhibition") or {}
    return int(t.get("exhibitionBlackBeforeMs", 0))


def compounds_school_soundtrack_start_ms(collection: dict) -> int:
    """When main soundtrack begins — aligned to opening bookend image + delay."""
    t = collection.get("exhibition") or {}
    opening = (collection.get("bookends") or {}).get("opening") or {}
    lead = int(t.get("recordingLeadMs", 0))
    before = int(t.get("openingBlackBeforeMs", 0))
    delay = int(
        opening.get("startSoundtrackAfterImageMs")
        or t.get("openingSoundtrackDelayMs", 2500)
    )
    return lead + before + delay


def reflections_audio_timeline_ms(collection: dict, root: Path) -> tuple[int, int, int]:
    """Return (intro_delay_ms, main_start_ms, outro_start_ms) for gallery-crest bookends."""
    t = collection.get("exhibition") or {}
    bookends = collection.get("bookends") or {}
    soundtrack = collection.get("soundtrack") or {}
    opening = bookends.get("opening") or {}
    closing = bookends.get("closing") or {}

    intro_path = root / (opening.get("audio") or "")
    main_path = root / (soundtrack.get("main") or "")
    outro_path = root / (closing.get("audio") or "")

    intro_ms = int(probe_duration_seconds(intro_path) * 1000) if intro_path.is_file() else 0
    main_ms = int(probe_duration_seconds(main_path) * 1000) if main_path.is_file() else 0

    black_before = int(t.get("openingBlackBeforeMs", 0))
    exhale = int(t.get("openingExhaleMs", 0))
    black_after = int(t.get("openingBlackAfterMs", 0))
    intro_delay = black_before
    main_start = black_before + intro_ms + exhale + black_after

    closing_black = int(t.get("closingBlackBeforeMs", t.get("blackHoldMs", 0)))
    closing_reveal = int(t.get("closingRevealMs", 0))
    crest_fade = int(t.get("closingExhaleMs", t.get("closingFadeToBlackMs", 3000)))
    outro_start = main_start + main_ms + closing_black + closing_reveal + crest_fade

    return intro_delay, main_start, outro_start


def presentation_timeout_ms(collection: dict, root: Path, *, extra_ms: int = 120_000) -> int:
    """Upper bound for Playwright wait (video length + buffer)."""
    t = collection.get("exhibition") or {}
    bookends = collection.get("bookends") or {}
    scenes = collection.get("scenes") or []
    soundtrack = collection.get("soundtrack") or {}

    if (collection.get("display") or {}).get("exhibitProfile") in ("imageVerse", "gallery"):
        per = exhibit_ms_image_verse(t)
        opening = bookends.get("opening") or {}
        intro_path = root / (opening.get("audio") or "")
        intro_ms = int(probe_duration_seconds(intro_path) * 1000) if intro_path.is_file() else 0
        open_ms = (
            int(t.get("openingBlackBeforeMs", 0))
            + intro_ms
            + int(t.get("openingExhaleMs", 0))
            + int(t.get("openingBlackAfterMs", 0))
        )
        closing = bookends.get("closing") or {}
        outro_path = root / (closing.get("audio") or "")
        outro_ms = int(probe_duration_seconds(outro_path) * 1000) if outro_path.is_file() else 0
        close_ms = (
            int(t.get("closingRevealMs", 0))
            + int(t.get("closingExhaleMs", t.get("closingFadeToBlackMs", 3000)))
            + int(t.get("closingTitleRevealMs", 2500))
            + int(t.get("closingTitleFadeMs", t.get("closingFadeToBlackMs", 3000)))
            + outro_ms
        )
        return int(open_ms + per * len(scenes) + close_ms + extra_ms)

    main_path = root / (soundtrack.get("main") or "audio/ambient_kanji_exhibition.mp3")
    main_ms = int(probe_duration_seconds(main_path) * 1000) if main_path.is_file() else 0
    _, ambient_start = heart_opening_timeline_ms(collection, root)
    tail_ms = int(
        (t.get("closingPostSoundtrackHoldMs") or 0)
        + (t.get("closingSilenceHoldMs") or 0)
        + (t.get("closingFadeToBlackMs") or t.get("closingExhaleMs") or 0)
        + (t.get("closingBlackAfterMs") or 0)
        + 15_000
    )
    return ambient_start + main_ms + tail_ms + extra_ms


def start_server(root: Path, port: int) -> subprocess.Popen:
    if not (root / "assets" / "studies").exists():
        print(f"Missing assets symlink. From {root}: ln -s ../../assets assets", file=sys.stderr)
        sys.exit(1)
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def stop_server(proc: subprocess.Popen) -> None:
    """Stop the local http.server; ignore sandbox PermissionError on terminate."""
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except (PermissionError, ProcessLookupError, subprocess.TimeoutExpired):
        try:
            proc.kill()
        except (PermissionError, ProcessLookupError):
            pass


def mux_video_with_audio(
    *,
    webm: Path,
    output_mp4: Path,
    filter_complex: str,
    audio_inputs: list[Path],
    video_from_mp4: bool = False,
) -> None:
    cmd = ["ffmpeg", "-y", "-i", str(webm)]
    for audio in audio_inputs:
        cmd.extend(["-i", str(audio)])
    cmd.extend(
        [
            "-filter_complex",
            filter_complex,
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "copy" if video_from_mp4 else "libx264",
        ]
    )
    if not video_from_mp4:
        cmd.extend(
            [
                "-preset",
                "slow",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
            ]
        )
    cmd.extend(
        [
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(output_mp4),
        ]
    )
    subprocess.run(cmd, check=True)


def apply_mp4_end_fade(
    path: Path,
    *,
    fade_start_s: int,
    fade_duration_s: int = 10,
    preset: str = "medium",
) -> None:
    """Fade video/audio out from fade_start_s and trim the file at fade end."""
    cut_s = fade_start_s + fade_duration_s
    tmp = path.with_name(f"{path.stem}.fade.tmp{path.suffix}")
    if tmp.exists():
        tmp.unlink()
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-vf",
            f"fade=t=out:st={fade_start_s}:d={fade_duration_s}",
            "-af",
            f"afade=t=out:st={fade_start_s}:d={fade_duration_s}",
            "-t",
            str(cut_s),
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(tmp),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tmp.replace(path)


def format_mmss(total_s: int) -> str:
    return f"{total_s // 60}:{total_s % 60:02d}"


def capture_exhibition_webm(
    *,
    url: str,
    tmp_dir: Path,
    timeout_ms: int,
) -> Path:
    from playwright.sync_api import sync_playwright

    tmp_dir.mkdir(parents=True, exist_ok=True)
    print(f"  URL: {url}")
    print(f"  Max wait: {timeout_ms // 1000}s")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--autoplay-policy=no-user-gesture-required",
                "--disable-dev-shm-usage",
            ],
        )
        context = browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(tmp_dir),
            record_video_size=VIEWPORT,
            color_scheme="dark",
        )
        page = context.new_page()
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_function("() => window.kmlExhibition", timeout=120_000)
        page.wait_for_function(
            "() => document.fonts && document.fonts.status === 'loaded'",
            timeout=120_000,
        )

        gate = page.locator("[data-exhibition-autoplay-gate]")
        try:
            if gate.is_visible():
                gate.click()
            else:
                page.wait_for_timeout(300)
        except Exception:
            page.mouse.click(VIEWPORT["width"] // 2, VIEWPORT["height"] // 2)

        page.wait_for_function(
            "() => window.kmlExhibition && window.kmlExhibition.presentationEnded === true",
            timeout=timeout_ms,
        )
        page.wait_for_timeout(1500)

        video = page.video
        page.close()
        video_path = video.path() if video else None
        context.close()
        browser.close()

    webm_files = list(tmp_dir.glob("*.webm"))
    webm = Path(video_path) if video_path else (webm_files[0] if webm_files else None)
    if not webm or not webm.is_file():
        raise RuntimeError("No video captured")
    return webm


def load_collection(root: Path, collection_id: str) -> dict:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from collection_paths import collection_json_path  # noqa: E402

    path = collection_json_path(root, collection_id)
    if not path.is_file():
        raise FileNotFoundError(f"Missing collection: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
