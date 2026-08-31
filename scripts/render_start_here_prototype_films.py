#!/usr/bin/env python3
"""Render Start Here prototype films for unlisted YouTube upload.

Outputs (gitignored / artifacts — not for Netlify deploy):
  exports/start-here-prototypes/room-17-nureta-hashi.mp4
  exports/start-here-prototypes/room-28-heya.mp4

Room 17: listen-only master film from data/rooms/17.json timings.
Room 28: calm “page performs itself” still + timed text + BGM.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "exports" / "start-here-prototypes"
ARTIFACT_DIR = Path("/opt/cursor/artifacts/start-here-prototypes")
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def render_room_17(out: Path) -> None:
    data = json.loads((ROOT / "start-here/data/rooms/17.json").read_text())
    audio = (ROOT / "start-here/data/rooms" / data["audio"]).resolve()
    film = data["film"]
    total = float(data["timing"]["audioDuration"])
    # Pad slightly past last cue using real audio length.
    total = max(total, duration(audio))

    # Build concat list of still segments with crossfades approximated as holds
    # that start at each cue (incoming painting begins to appear).
    starts = [float(item["start"]) for item in film]
    images = [
        (ROOT / "start-here/data/rooms" / item["image"]).resolve() for item in film
    ]
    # Each still must extend through the outgoing crossfade so xfade offsets
    # land on the JSON "incoming begins to appear" times.
    crossfades = []
    for i, item in enumerate(film):
        if i == 0:
            crossfades.append(0.0)
        else:
            crossfades.append(
                float(item.get("crossfade") or data.get("imageCrossfade") or 2.0)
            )

    with tempfile.TemporaryDirectory(prefix="room17-") as tmp:
        tmp_path = Path(tmp)
        clips = []
        for i, img in enumerate(images):
            if i + 1 < len(starts):
                # Hold until next cue, plus the crossfade into the next painting.
                seg_dur = (starts[i + 1] - starts[i]) + crossfades[i + 1]
            else:
                seg_dur = max(0.2, total - starts[i])
            seg_dur = max(0.2, seg_dur)
            clip = tmp_path / f"clip_{i:02d}.mp4"
            # Scale/crop to 1920x1080, slow push-in via zoompan for presence.
            filt = (
                "scale=1920:1080:force_original_aspect_ratio=increase,"
                "crop=1920:1080,"
                f"zoompan=z='min(1.04,1+0.00008*on)':x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,"
                "format=yuv420p"
            )
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-loop",
                    "1",
                    "-i",
                    str(img),
                    "-vf",
                    filt,
                    "-t",
                    f"{seg_dur:.3f}",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-preset",
                    "medium",
                    "-crf",
                    "18",
                    str(clip),
                ]
            )
            clips.append(clip)

        # Crossfade chain between clips using xfade.
        if len(clips) == 1:
            video_only = clips[0]
        else:
            current = clips[0]
            acc_dur = duration(current)
            for i in range(1, len(clips)):
                nxt = clips[i]
                xf = crossfades[i]
                xf = min(xf, acc_dur * 0.45, duration(nxt) * 0.45)
                if xf <= 0.05:
                    # Hard cut fallback
                    merged = tmp_path / f"merge_{i:02d}.mp4"
                    run(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            str(current),
                            "-i",
                            str(nxt),
                            "-filter_complex",
                            "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p[v]",
                            "-map",
                            "[v]",
                            "-an",
                            "-c:v",
                            "libx264",
                            "-preset",
                            "medium",
                            "-crf",
                            "18",
                            str(merged),
                        ]
                    )
                    current = merged
                    acc_dur = duration(current)
                    continue
                merged = tmp_path / f"merge_{i:02d}.mp4"
                offset = max(0.0, acc_dur - xf)
                run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(current),
                        "-i",
                        str(nxt),
                        "-filter_complex",
                        f"[0:v][1:v]xfade=transition=fade:duration={xf:.3f}:offset={offset:.3f},format=yuv420p[v]",
                        "-map",
                        "[v]",
                        "-an",
                        "-c:v",
                        "libx264",
                        "-preset",
                        "medium",
                        "-crf",
                        "18",
                        str(merged),
                    ]
                )
                current = merged
                acc_dur = duration(current)
            video_only = current

        out.parent.mkdir(parents=True, exist_ok=True)
        aud_dur = duration(audio)
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_only),
                "-i",
                str(audio),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-t",
                f"{aud_dur:.3f}",
                "-movflags",
                "+faststart",
                str(out),
            ]
        )


def escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "%%")
    )


def render_room_28(out: Path) -> None:
    image = ROOT / "kml/assets/studies/room.png"
    audio = ROOT / "start-here/audio/lesson-7.mp3"
    if not image.exists() or image.stat().st_size < 1000:
        raise SystemExit(f"Missing room image: {image}")

    # Calm ~75s page performance. Text holds match the room's intellectual content.
    # Beats (seconds): open still → へや → heya/room → unpack → note → へや → rest
    total = 75.0
    font = FONT

    def dt(text: str, start: float, end: float, fontsize: int = 72, y: str = "h*0.72") -> str:
        t = escape_drawtext(text)
        return (
            f"drawtext=fontfile={font}:text='{t}':fontsize={fontsize}:"
            f"fontcolor=white:borderw=2:bordercolor=0x080809@0.55:"
            f"x=(w-text_w)/2:y={y}:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )

    filters = [
        "scale=1920:1080:force_original_aspect_ratio=increase",
        "crop=1920:1080",
        "zoompan=z='min(1.05,1+0.00006*on)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30",
        # Soft bottom veil for readable type
        "drawbox=x=0:y=ih*0.58:w=iw:h=ih*0.42:color=0x080809@0.42:t=fill",
        dt("へや", 6, 18, 96),
        dt("heya", 10, 18, 42, "h*0.82"),
        dt("room", 12, 18, 36, "h*0.88"),
        dt("へ　や", 20, 32, 84),
        dt("he　ya", 24, 32, 40, "h*0.82"),
        dt("や you already have. へ is new.", 34, 50, 36, "h*0.76"),
        dt("へや", 52, 66, 96),
        dt("heya", 56, 66, 42, "h*0.82"),
        "format=yuv420p",
    ]
    vf = ",".join(filters)

    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="room28-") as tmp:
        tmp_path = Path(tmp)
        silent = tmp_path / "silent.mp4"
        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(image),
                "-vf",
                vf,
                "-t",
                f"{total:.2f}",
                "-an",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "medium",
                "-crf",
                "18",
                str(silent),
            ]
        )
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(silent),
                "-i",
                str(audio),
                "-filter_complex",
                f"[1:a]afade=t=in:st=0:d=2,afade=t=out:st={total-3:.1f}:d=3,volume=0.55[a]",
                "-map",
                "0:v:0",
                "-map",
                "[a]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-t",
                f"{total:.2f}",
                "-movflags",
                "+faststart",
                str(out),
            ]
        )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    room17 = OUT_DIR / "room-17-nureta-hashi.mp4"
    room28 = OUT_DIR / "room-28-heya.mp4"

    targets = sys.argv[1:] or ["17", "28"]
    if "17" in targets:
        print("Rendering Room 17…", flush=True)
        render_room_17(room17)
        run(["cp", "-f", str(room17), str(ARTIFACT_DIR / room17.name)])
        print(f"Wrote {room17} ({room17.stat().st_size / 1e6:.1f} MB)", flush=True)
    if "28" in targets:
        print("Rendering Room 28…", flush=True)
        render_room_28(room28)
        run(["cp", "-f", str(room28), str(ARTIFACT_DIR / room28.name)])
        print(f"Wrote {room28} ({room28.stat().st_size / 1e6:.1f} MB)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
