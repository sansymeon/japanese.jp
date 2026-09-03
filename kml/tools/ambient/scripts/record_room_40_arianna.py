#!/usr/bin/env python3
"""Record Start Here Room 41 言葉が咲く MP4 via Playwright.

Output: start-here/films/room_41_kotoba_ga_saku.mp4

Player: start-here/lesson-40/record-arianna.html
Conductor: start-here/data/rooms/40.js (== 40.json) — timings/images unchanged
Soundtrack: start-here/audio/hiragana_song.mp3 (~4:24.75)
Lyric CSS only: centered, large hiragana; lower frame kept clear.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

AMBIENT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
DEFAULT_PORT = 8797
PLAYWRIGHT_BROWSERS = AMBIENT / ".playwright-browsers"
ROOM_JSON = REPO / "start-here" / "data" / "rooms" / "40.json"
AUDIO = REPO / "start-here" / "audio" / "hiragana_song.mp3"
OUT_PATH = REPO / "start-here" / "films" / "room_41_kotoba_ga_saku.mp4"
RECORD_URL_PATH = "/start-here/lesson-40/record-arianna.html"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    ensure_deps,
    launch_recording_browser,
    mux_video_with_audio,
    new_recording_context,
    probe_duration_seconds,
    stop_server,
)


def assert_assets() -> dict:
    data = json.loads(ROOM_JSON.read_text(encoding="utf-8"))
    base = ROOM_JSON.parent
    missing = []
    names = []
    seen = set()
    for item in data.get("film") or []:
        rel = item.get("image") or ""
        name = Path(rel).name
        if name in seen:
            continue
        seen.add(name)
        names.append(name)
        path = (base / rel).resolve()
        if not path.is_file():
            missing.append(str(path))
    if not AUDIO.is_file():
        missing.append(str(AUDIO))
    if missing:
        raise FileNotFoundError("Missing assets:\n" + "\n".join(missing))
    print(f"  Stills OK ({len(names)}): {', '.join(names)}")
    print(f"  Audio: {AUDIO} ({probe_duration_seconds(AUDIO):.2f}s)")
    print(f"  Film cuts: {len(data.get('film') or [])}  Lyrics: {len(data.get('lyrics') or [])}")
    return data


def start_repo_server(port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=REPO,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def capture(*, port: int, tmp_dir: Path, timeout_ms: int) -> tuple[Path, int]:
    from playwright.sync_api import sync_playwright

    url = f"http://127.0.0.1:{port}{RECORD_URL_PATH}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    print(f"  URL: {url}")

    with sync_playwright() as p:
        browser = launch_recording_browser(p, headless=True)
        context = new_recording_context(browser, record_video_dir=tmp_dir)
        page = context.new_page()
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_function(
            "() => document.fonts && document.fonts.status === 'loaded'",
            timeout=120_000,
        )
        page.wait_for_function(
            """() => !!(
              window.KmlBeginnerRoomData &&
              window.__room40Audio &&
              !window.__room40Audio.paused &&
              window.__room40Audio.currentTime > 0.05
            )""",
            timeout=30_000,
        )
        listen_perf = page.evaluate("() => window.__room40ListenPerf || 0")
        print(f"  Listen at performance.now()={listen_perf:.0f}ms")
        page.wait_for_function(
            "() => window.__room40Ended === true || (window.__room40Audio && window.__room40Audio.ended)",
            timeout=timeout_ms,
        )
        page.wait_for_timeout(800)

        video = page.video
        page.close()
        video_path = video.path() if video else None
        context.close()
        browser.close()

    webm_files = list(tmp_dir.glob("*.webm"))
    webm = Path(video_path) if video_path else (webm_files[0] if webm_files else None)
    if not webm or not webm.is_file():
        raise RuntimeError("No video captured")
    start_ms = int(round(listen_perf)) if listen_perf else 0
    return webm, start_ms


def trim_webm(webm: Path, start_ms: int, dest: Path) -> Path:
    """Drop pre-Listen frames so video t=0 is soundtrack t=0."""
    ss = max(0, start_ms) / 1000.0
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{ss:.3f}",
        "-i",
        str(webm),
        "-c",
        "copy",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dest


def record(*, port: int) -> Path:
    data = assert_assets()
    duration_s = float((data.get("timing") or {}).get("audioDuration") or 264.75)
    timeout_ms = int((duration_s + 90) * 1000)

    out_dir = OUT_PATH.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_dir / ".tmp_room_41_kotoba_ga_saku"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording Room 41 言葉が咲く → {OUT_PATH}")
    print(f"  Max wait: {timeout_ms // 1000}s")

    webm, start_ms = capture(port=port, tmp_dir=tmp_dir, timeout_ms=timeout_ms)
    trimmed = tmp_dir / "from_listen.webm"
    try:
        trim_webm(webm, start_ms, trimmed)
        use_webm = trimmed if trimmed.is_file() and trimmed.stat().st_size > 0 else webm
        if use_webm is webm:
            print("  Trim copy failed; muxing untrimmed webm with adelay")
            delay = start_ms
        else:
            print(f"  Trimmed {start_ms}ms of pre-Listen video")
            delay = 0
    except subprocess.CalledProcessError:
        use_webm = webm
        delay = start_ms
        print("  Trim failed; muxing untrimmed webm with adelay")

    webm_s = probe_duration_seconds(use_webm)
    mp3_s = probe_duration_seconds(AUDIO)
    pad_s = max(1.0, webm_s - (delay / 1000.0) - mp3_s + 0.5)
    print(f"  Video: {webm_s:.1f}s  MP3: {mp3_s:.1f}s  adelay: {delay}ms  pad: {pad_s:.1f}s")

    filter_complex = (
        f"[1:a]adelay={delay}|{delay},"
        f"apad=pad_dur={pad_s:.3f}[m];"
        f"[m]asetpts=PTS-STARTPTS[a]"
    )
    tmp_mux = tmp_dir / "muxed.mp4"
    mux_video_with_audio(
        webm=use_webm,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[AUDIO],
    )
    shutil.move(str(tmp_mux), str(OUT_PATH))
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"  → {OUT_PATH}")
    return OUT_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    ensure_deps()
    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(PLAYWRIGHT_BROWSERS)

    server = start_repo_server(args.port)
    try:
        record(port=args.port)
    finally:
        stop_server(server)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
