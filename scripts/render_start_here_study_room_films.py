#!/usr/bin/env python3
"""Batch-render Start Here study-room prototype films (Room 28 design reference).

Outputs to exports/start-here-prototypes/ and /opt/cursor/artifacts/start-here-prototypes/.
Does not modify site wiring or upload to YouTube.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from parse_study_room_html import parse_lesson  # noqa: E402
from start_here_study_film_lib import run, render_study_room_film  # noqa: E402

OUT_DIR = ROOT / "exports" / "start-here-prototypes"
ARTIFACT_DIR = Path("/opt/cursor/artifacts/start-here-prototypes")

# Study rooms appropriate for Room 28-style treatment (28 already rendered separately).
STUDY_ROOMS = [
    2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    19, 20, 21, 22, 23, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
]

SKIP_ROOMS: dict[int, str] = {
    0: "guided-song — lyrics/scenes need sung-section timing",
    1: "guided-song — render via scripts/render_start_here_guided_song_films.py",
    3: "guided-song — render via scripts/render_start_here_guided_song_films.py",
    5: "guided-song — render via scripts/render_start_here_guided_song_films.py",
    17: "guided-song interlude — render via scripts/render_start_here_guided_song_films.py",
    18: "guided-song — render via scripts/render_start_here_guided_song_films.py",
    24: "guided-song — full listen film: room-24-take-no-oto.mp4; after-section recap: room-24-竹の音.mp4",
    25: "guided-song listen-only interlude — render via scripts/render_start_here_guided_song_films.py",
    28: "approved prototype — already rendered",
    39: "curtain-call YouTube film — existing embed, not a study-room lesson",
    40: "guided-song hiragana epilogue — already on YouTube; timed JSON scenes",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    targets = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else STUDY_ROOMS
    explicit = {str(x) for x in sys.argv[1:]}
    rendered: list[dict] = []
    failed: list[dict] = []
    skipped: list[dict] = [{"room": k, "reason": v} for k, v in SKIP_ROOMS.items()]

    for room_id in targets:
        if room_id in SKIP_ROOMS and str(room_id) not in explicit:
            continue
        print(f"\n=== Room {room_id} ===", flush=True)
        try:
            spec = parse_lesson(room_id)
            if not spec["beats"]:
                failed.append({"room": room_id, "error": "no beats parsed"})
                continue
            out = OUT_DIR / f"room-{room_id:02d}-{spec['slug']}.mp4"
            meta = render_study_room_film(
                room_id=room_id,
                slug=spec["slug"],
                beats=spec["beats"],
                default_image=Path(spec["default_image"]),
                out_path=out,
                review_flags=spec.get("review_flags") or [],
            )
            run(["cp", "-f", str(out), str(ARTIFACT_DIR / out.name)])
            size_mb = out.stat().st_size / 1e6
            print(f"Wrote {out} ({size_mb:.1f} MB, {meta['duration']:.0f}s)", flush=True)
            rendered.append({**meta, "file": out.name, "path": str(out)})
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED room {room_id}: {exc}", flush=True)
            failed.append({"room": room_id, "error": str(exc)})

    review = [
        r for r in rendered if r.get("review_flags")
    ]
    report = {
        "rendered": rendered,
        "skipped": skipped,
        "failed": failed,
        "needs_human_review": review,
        "artifact_dir": str(ARTIFACT_DIR),
        "export_dir": str(OUT_DIR),
    }
    report_path = ARTIFACT_DIR / "batch-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUT_DIR / "batch-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport: {report_path}", flush=True)
    print(f"Rendered: {len(rendered)}  Failed: {len(failed)}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
