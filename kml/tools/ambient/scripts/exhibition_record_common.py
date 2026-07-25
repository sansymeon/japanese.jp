"""Shared helpers for Playwright exhibition MP4 recording.

Soundtrack contract
-------------------
Master MP3s are reusable music only: no baked fade-in, fade-out, or intentional
leading/trailing silence. The renderer owns synchronization:

  adelay          — start delay when the exhibition requires it
  -shortest       — trim to video length
  afade=t=out     — reach silence on the final video frame
                    (default 8s window, computed from video duration)

Prefer mux_exhibition_soundtrack() for exhibition-style series.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

VIEWPORT = {"width": 1920, "height": 1080}

# Must match between capture_exhibition_webm() and preview_recording.py.
# Interactive Chrome (variable window + often DPR=2) is NOT the approval surface.
DEVICE_SCALE_FACTOR = 1
RECORDING_COLOR_SCHEME = "dark"
RECORDING_CHROMIUM_ARGS = [
    "--autoplay-policy=no-user-gesture-required",
    "--disable-dev-shm-usage",
]

# Global end-fade for clean music masters. Tunable in one place.
DEFAULT_SOUNDTRACK_END_FADE_S = 8.0

_AMBIENT_ROOT = Path(__file__).resolve().parents[1]
_PLAYWRIGHT_BROWSERS = _AMBIENT_ROOT / ".playwright-browsers"
# Prefer the ambient-local browser cache. Cursor sandboxes often pre-set
# PLAYWRIGHT_BROWSERS_PATH to an empty cache; setdefault would leave that broken.
if _PLAYWRIGHT_BROWSERS.is_dir():
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_PLAYWRIGHT_BROWSERS)


def launch_recording_browser(playwright, *, headless: bool = True):
    """Launch the Chromium build used for exhibition MP4 capture."""
    return playwright.chromium.launch(
        headless=headless,
        args=list(RECORDING_CHROMIUM_ARGS),
    )


def new_recording_context(
    browser,
    *,
    viewport: dict | None = None,
    record_video_dir: str | Path | None = None,
):
    """Browser context identical for live recording-preview and MP4 capture."""
    viewport = viewport or VIEWPORT
    kwargs: dict = {
        "viewport": viewport,
        "device_scale_factor": DEVICE_SCALE_FACTOR,
        "color_scheme": RECORDING_COLOR_SCHEME,
    }
    if record_video_dir is not None:
        kwargs["record_video_dir"] = str(record_video_dir)
        kwargs["record_video_size"] = viewport
    return browser.new_context(**kwargs)


def exhibition_record_url(
    *,
    port: int,
    collection_id: str,
    display: dict | None = None,
    extra_params: dict | None = None,
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
    for key, value in (extra_params or {}).items():
        if value not in (None, ""):
            params.append(f"{key}={value}")
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


def _closing_holds_for_soundtrack(collection: dict) -> bool:
    """True when the engine will pad the closing crest until the bed ends."""
    closing = ((collection.get("bookends") or {}).get("closing")) or {}
    if not closing:
        return False
    # Engine default: holdUntilSoundtrackEnds is true unless explicitly false.
    return closing.get("holdUntilSoundtrackEnds") is not False


def presentation_timeout_ms(collection: dict, root: Path, *, extra_ms: int = 120_000) -> int:
    """Upper bound for Playwright wait (video length + buffer).

    When holdUntilSoundtrackEnds is false, prefer estimated content runtime over
    the master bed length so capture does not wait for long reusable MP3s.
    """
    t = collection.get("exhibition") or {}
    bookends = collection.get("bookends") or {}
    scenes = collection.get("scenes") or []
    soundtrack = collection.get("soundtrack") or {}
    hold_for_bed = _closing_holds_for_soundtrack(collection)
    estimated_content_ms = (collection.get("meta") or {}).get("estimatedContentRuntimeMs")

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
        # Per-scene artworkAloneMs overrides (ambient gallery film) — sum holds.
        alone_overrides = [
            int(s["artworkAloneMs"])
            for s in scenes
            if isinstance(s, dict) and s.get("artworkAloneMs") is not None
        ]
        if alone_overrides and len(alone_overrides) == len(scenes):
            phantom = per - int(t.get("artworkAloneMs", 0)) - int(t.get("exhibitTransitionMs", 4000))
            transition = int(t.get("exhibitTransitionMs", 4000))
            content_ms = sum(alone_overrides) + phantom * len(scenes) + transition * max(0, len(scenes) - 1)
            scene_total = int(
                open_ms
                + int(t.get("artworkArrivalFadeMs", 0))
                + content_ms
                + close_ms
            )
        else:
            scene_total = int(open_ms + per * len(scenes) + close_ms)
        if not hold_for_bed:
            return scene_total + extra_ms
        main_path = root / (soundtrack.get("main") or "")
        main_ms = int(probe_duration_seconds(main_path) * 1000) if main_path.is_file() else 0
        soundtrack_bound = int(
            open_ms
            + int(t.get("artworkArrivalFadeMs", 0))
            + main_ms
            + int(t.get("closingRevealMs", 0))
            + int(t.get("closingHoldMs", 0))
            + int(t.get("closingFadeToBlackMs", t.get("closingExhaleMs", 3000)))
            + int(t.get("closingSilenceHoldMs", 0))
            + int(t.get("closingBlackAfterMs", 0))
        )
        return max(scene_total, soundtrack_bound) + extra_ms

    if not hold_for_bed and estimated_content_ms:
        return int(estimated_content_ms) + max(extra_ms, 300_000)

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


def soundtrack_end_fade_plan(
    video_duration_s: float,
    *,
    end_fade_s: float = DEFAULT_SOUNDTRACK_END_FADE_S,
) -> tuple[float, float]:
    """Return (fade_start_s, fade_duration_s) so silence lands on the last frame.

    The fade is anchored to video duration, never to the master MP3 length.
    """
    video_duration_s = max(0.0, float(video_duration_s))
    fade_s = min(float(end_fade_s), max(0.0, video_duration_s - 0.05))
    fade_start = max(0.0, video_duration_s - fade_s)
    return round(fade_start, 3), round(fade_s, 3)


def exhibition_soundtrack_filter(
    *,
    soundtrack_start_ms: int = 0,
    video_duration_s: float,
    end_fade_s: float = DEFAULT_SOUNDTRACK_END_FADE_S,
    audio_label: str = "1:a",
) -> str:
    """Build the standard filter_complex for a clean music master.

    adelay (optional) → reset timestamps → afade to silence on last frame → apad.
    Pair with ffmpeg -shortest so the output ends with the video.
    """
    fade_start, fade_s = soundtrack_end_fade_plan(
        video_duration_s, end_fade_s=end_fade_s
    )
    parts: list[str] = []
    start_ms = max(0, int(soundtrack_start_ms))
    if start_ms > 0:
        parts.append(f"adelay={start_ms}|{start_ms}")
    parts.append("asetpts=PTS-STARTPTS")
    if fade_s > 0:
        parts.append(f"afade=t=out:st={fade_start:.3f}:d={fade_s:.3f}")
    parts.append("apad")
    return f"[{audio_label}]{','.join(parts)}[a]"


def mux_exhibition_soundtrack(
    *,
    webm: Path,
    output_mp4: Path,
    soundtrack: Path,
    soundtrack_start_ms: int = 0,
    end_fade_s: float = DEFAULT_SOUNDTRACK_END_FADE_S,
    video_from_mp4: bool = False,
) -> dict:
    """Mux a clean music master onto captured exhibition video.

    Master MP3 = continuous music only. This helper owns:
      - start delay (adelay)
      - trim to video (-shortest)
      - end fade reaching silence on the final frame
    """
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    video_dur = probe_duration_seconds(webm)
    fade_start, fade_s = soundtrack_end_fade_plan(video_dur, end_fade_s=end_fade_s)
    filter_complex = exhibition_soundtrack_filter(
        soundtrack_start_ms=soundtrack_start_ms,
        video_duration_s=video_dur,
        end_fade_s=end_fade_s,
    )

    print(
        f"  Audio plan: delay={max(0, int(soundtrack_start_ms))}ms · "
        f"video={video_dur:.1f}s · fade {fade_s:.1f}s from {fade_start:.1f}s → silence"
    )

    mux_video_with_audio(
        webm=webm,
        output_mp4=output_mp4,
        filter_complex=filter_complex,
        audio_inputs=[soundtrack],
        video_from_mp4=video_from_mp4,
    )
    return {
        "videoDurationS": video_dur,
        "soundtrackStartMs": max(0, int(soundtrack_start_ms)),
        "fadeStartS": fade_start,
        "fadeDurationS": fade_s,
    }


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


def ensure_noto_serif_jp_ready(page, *, timeout_ms: int = 120_000) -> None:
    """Fail the recording if Noto Serif JP is not actually usable.

    Without this, Chromium falls through to Noto Sans CJK JP (blocky gothic)
    whenever the CDN miss / local face fails — and that gets baked into the MP4.
    """
    page.wait_for_function(
        """async () => {
          if (!document.fonts?.load) return false;
          await document.fonts.ready;
          const sample = '静工忘れ忌左';
          await Promise.all([
            document.fonts.load('400 82px \"Noto Serif JP\"', sample),
            document.fonts.load('500 82px \"Noto Serif JP\"', sample),
            document.fonts.load('600 82px \"Noto Serif JP\"', sample),
          ]);
          await document.fonts.ready;
          return document.fonts.status === 'loaded';
        }""",
        timeout=timeout_ms,
    )
    result = page.evaluate(
        """() => {
          const sample = ['静', '工', '忘', 'れ', '忌', '左'];
          const missing = [];
          for (const weight of [400, 500, 600]) {
            for (const ch of sample) {
              if (!document.fonts.check(`${weight} 82px \"Noto Serif JP\"`, ch)) {
                missing.push(`${weight}:${ch}`);
              }
            }
          }
          const faces = [...document.fonts].filter(
            (f) => f.family.replace(/[\"']/g, '') === 'Noto Serif JP' && f.status === 'loaded'
          );
          return {
            ok: missing.length === 0 && faces.length > 0,
            missing,
            faceCount: faces.length,
          };
        }"""
    )
    if not result.get("ok"):
        raise RuntimeError(
            "Noto Serif JP is not available for capture "
            f"(faces={result.get('faceCount')}, missing={result.get('missing')}). "
            "Run: bash scripts/fetch_noto_serif_jp_fonts.sh "
            "and ensure css/gallery-fonts-local.css is linked before recording."
        )
    print(f"  Fonts OK: Noto Serif JP ({result.get('faceCount')} faces loaded)")


def ensure_yuji_syuku_ready(page, *, timeout_ms: int = 120_000) -> None:
    """Fail if hero kanji cannot paint as Yuji Syuku (protected KML identity).

    document.fonts.check('Yuji Syuku') alone is unreliable (false positives).
    We fingerprint canvas ink: Yuji brush strokes are denser than Noto Serif JP.
    Without this gate, hermetic Noto loads and the hero silently falls through
    to clean Mincho — readable, but not the original artistic presence.
    """
    page.wait_for_function(
        """async () => {
          if (!document.fonts?.load) return false;
          await document.fonts.ready;
          const sample = '工静左忘忌';
          await document.fonts.load('400 320px \"Yuji Syuku\"', sample);
          await document.fonts.ready;
          const faces = [...document.fonts].filter(
            (f) => f.family.replace(/[\"']/g, '') === 'Yuji Syuku' && f.status === 'loaded'
          );
          return faces.length > 0;
        }""",
        timeout=timeout_ms,
    )
    result = page.evaluate(
        """() => {
          const sample = '工';
          const size = 320;
          function ink(family) {
            const canvas = document.createElement('canvas');
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            ctx.clearRect(0, 0, size, size);
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, size, size);
            ctx.fillStyle = '#fff';
            ctx.font = `400 ${size * 0.72}px ${family}`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(sample, size / 2, size / 2);
            const data = ctx.getImageData(0, 0, size, size).data;
            let bright = 0;
            for (let i = 0; i < data.length; i += 4) {
              if (data[i] > 180) bright += 1;
            }
            return bright;
          }
          const yujiInk = ink('"Yuji Syuku"');
          const notoInk = ink('"Noto Serif JP"');
          const faces = [...document.fonts].filter(
            (f) => f.family.replace(/[\"']/g, '') === 'Yuji Syuku' && f.status === 'loaded'
          );
          // Yuji must be distinctly denser than Noto; identical ink ⇒ fallback.
          const distinct = yujiInk > notoInk * 1.12 && (yujiInk - notoInk) > 400;
          return {
            ok: faces.length > 0 && distinct,
            faceCount: faces.length,
            yujiInk,
            notoInk,
            distinct,
          };
        }"""
    )
    if not result.get("ok"):
        raise RuntimeError(
            "Yuji Syuku (hero kanji face) is not available for capture "
            f"(faces={result.get('faceCount')}, yujiInk={result.get('yujiInk')}, "
            f"notoInk={result.get('notoInk')}, distinct={result.get('distinct')}). "
            "Run: bash scripts/fetch_yuji_syuku_font.sh "
            "and ensure css/gallery-fonts-local.css registers @font-face for Yuji Syuku."
        )
    print(
        f"  Fonts OK: Yuji Syuku hero "
        f"(faces={result.get('faceCount')}, ink={result.get('yujiInk')} vs Noto {result.get('notoInk')})"
    )


def assert_local_noto_serif_files(root: Path | None = None) -> None:
    """Ensure self-hosted OTFs exist on disk before starting a text-stage record."""
    root = root or _AMBIENT_ROOT
    needed = [
        "NotoSerifCJKjp-Regular.otf",
        "NotoSerifCJKjp-Medium.otf",
        "NotoSerifCJKjp-SemiBold.otf",
    ]
    font_dir = root / "fonts" / "noto-serif-jp"
    missing = [name for name in needed if not (font_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"Missing self-hosted Noto Serif JP fonts in {font_dir}: {missing}. "
            "Run: bash scripts/fetch_noto_serif_jp_fonts.sh"
        )


def assert_local_yuji_syuku_files(root: Path | None = None) -> None:
    """Ensure self-hosted Yuji Syuku TTF exists (protected hero kanji face)."""
    root = root or _AMBIENT_ROOT
    path = root / "fonts" / "yuji-syuku" / "YujiSyuku-Regular.ttf"
    if not path.is_file() or path.stat().st_size < 100_000:
        raise FileNotFoundError(
            f"Missing self-hosted Yuji Syuku font at {path}. "
            "Run: bash scripts/fetch_yuji_syuku_font.sh"
        )


def capture_exhibition_webm(
    *,
    url: str,
    tmp_dir: Path,
    timeout_ms: int,
    viewport: dict | None = None,
    preload_fonts: list[str] | None = None,
    require_noto_serif_jp: bool = True,
    require_yuji_syuku: bool = True,
) -> Path:
    from playwright.sync_api import sync_playwright

    viewport = viewport or VIEWPORT
    tmp_dir.mkdir(parents=True, exist_ok=True)
    print(f"  URL: {url}")
    print(f"  Viewport: {viewport['width']}×{viewport['height']}")
    print(f"  Max wait: {timeout_ms // 1000}s")

    if require_noto_serif_jp:
        assert_local_noto_serif_files()
    if require_yuji_syuku:
        assert_local_yuji_syuku_files()

    with sync_playwright() as p:
        browser = launch_recording_browser(p, headless=True)
        context = new_recording_context(
            browser,
            viewport=viewport,
            record_video_dir=tmp_dir,
        )
        page = context.new_page()
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_function("() => window.kmlExhibition", timeout=120_000)
        if preload_fonts:
            # The engine only preloads the weights it ships with; anything a
            # prototype introduces has to be requested before the gate opens or
            # the first slides capture a fallback face.
            page.evaluate(
                "specs => Promise.all(specs.map(s => document.fonts.load(s)))",
                preload_fonts,
            )
        page.wait_for_function(
            "() => document.fonts && document.fonts.status === 'loaded'",
            timeout=120_000,
        )
        if require_noto_serif_jp:
            ensure_noto_serif_jp_ready(page)
        if require_yuji_syuku:
            ensure_yuji_syuku_ready(page)

        gate = page.locator("[data-exhibition-autoplay-gate]")
        try:
            if gate.is_visible():
                gate.click()
            else:
                page.wait_for_timeout(300)
        except Exception:
            page.mouse.click(viewport["width"] // 2, viewport["height"] // 2)

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
