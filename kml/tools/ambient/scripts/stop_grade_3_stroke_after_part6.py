#!/usr/bin/env python3
"""Stop Grade 3 stroke --all queue after part 6 fully completes (post-fade)."""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "extended_exhibitions" / "grade_3_stroke_rerecord.log"
STOP = ROOT / "extended_exhibitions" / "grade_3_stroke_stop_after_06.log"
TMP6 = ROOT / "collections" / "grade_3" / ".tmp_grade_3_strokes_06"
TMP7 = ROOT / "collections" / "grade_3" / ".tmp_grade_3_strokes_07"
OUT6 = ROOT / "collections" / "grade_3" / "grade_3_strokes_06.mp4"

DONE_RE = re.compile(r"→\s+\S*grade_3_strokes_06\.mp4")
START7_RE = re.compile(r"Recording grade_3_strokes_07")


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}"
    print(line, flush=True)
    with STOP.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def recorder_alive() -> bool:
    return (
        subprocess.run(
            ["pgrep", "-f", "record_grade_3_stroke_order.py --all"],
            capture_output=True,
        ).returncode
        == 0
    )


def fade_running() -> bool:
    r = subprocess.run(
        ["pgrep", "-af", "grade_3_strokes_06"],
        capture_output=True,
        text=True,
    )
    return "fade.tmp" in r.stdout or "strokes_06.fade" in r.stdout


def kill_queue() -> None:
    subprocess.run(["pkill", "-f", "record_grade_3_stroke_order.py --all"], check=False)
    subprocess.run(["pkill", "-f", "run_grade_3_stroke_playwright.sh 8771"], check=False)
    if TMP7.exists():
        log("aborting in-progress part 7 tmp")
        subprocess.run(["pkill", "-f", ".tmp_grade_3_strokes_07"], check=False)
        subprocess.run(["rm", "-rf", str(TMP7)], check=False)
    time.sleep(2)
    r = subprocess.run(
        ["pgrep", "-af", "record_grade_3_stroke|run_grade_3_stroke"],
        capture_output=True,
        text=True,
    )
    log("remaining: " + (r.stdout.strip() or "none"))


def main() -> int:
    STOP.parent.mkdir(parents=True, exist_ok=True)
    log("watcher armed: stop after part 6 fully completes")
    baseline = OUT6.stat().st_mtime if OUT6.exists() else 0.0
    log(f"baseline mtime={baseline}")

    while True:
        if not recorder_alive():
            log("recorder already exited")
            return 0

        text = LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""
        done = bool(DONE_RE.search(text))
        started7 = bool(START7_RE.search(text))

        if TMP6.exists():
            time.sleep(8)
            continue

        if fade_running():
            log("fade still running; waiting…")
            time.sleep(5)
            continue

        if done:
            log("part 6 completion seen — stopping queue (no part 7–8)")
            kill_queue()
            return 0

        if started7:
            log("part 7 started — stopping queue now")
            kill_queue()
            return 0

        if OUT6.exists() and OUT6.stat().st_mtime > baseline:
            # mp4 replaced and tmp cleared; wait briefly for log line then stop
            time.sleep(10)
            text = LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""
            if DONE_RE.search(text) or START7_RE.search(text) or (
                OUT6.exists() and OUT6.stat().st_mtime > baseline and not TMP6.exists() and not fade_running()
            ):
                log(
                    f"part 6 finished (mtime {baseline} → {OUT6.stat().st_mtime}); stopping"
                )
                kill_queue()
                return 0

        time.sleep(8)


if __name__ == "__main__":
    raise SystemExit(main())
