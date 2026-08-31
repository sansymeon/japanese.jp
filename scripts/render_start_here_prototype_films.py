#!/usr/bin/env python3
"""Render Start Here prototype films for unlisted YouTube upload.

Outputs (gitignored / artifacts — not for Netlify deploy):
  exports/start-here-prototypes/room-17-nureta-hashi.mp4
  exports/start-here-prototypes/room-28-heya.mp4

Room 17: listen-only master film from data/rooms/17.json timings,
  with hiragana-only captions synced to vocals[].
Room 28: full lesson film from the static page — sequential beats on the
  complete room soundtrack (~lesson-7.mp3). Instrumental rooms use unused
  musical time for teaching; lyrics would take priority where present.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[misc, assignment]
    ImageDraw = None  # type: ignore[misc, assignment]
    ImageFont = None  # type: ignore[misc, assignment]

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


def escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "%%")
    )


def room17_hiragana_captions(vocals: list, total: float) -> list[str]:
    """Timed hiragana-only captions from 17.json vocals[]."""
    ink = "0xF3F1EB"
    shadow = "0x171512@0.42"
    hold_after_line = 6.0
    max_gap = 12.0
    filters: list[str] = []

    for i, item in enumerate(vocals):
        start = float(item["start"])
        text = escape_drawtext(str(item.get("text") or ""))
        if not text:
            continue
        if i + 1 < len(vocals):
            nxt = float(vocals[i + 1]["start"])
            end = nxt if (nxt - start) <= max_gap else start + hold_after_line
        else:
            end = min(total, start + hold_after_line)
        filters.append(
            f"drawtext=fontfile={FONT}:text='{text}':fontsize=96:"
            f"fontcolor={ink}:borderw=3:bordercolor={shadow}:"
            f"x=(w-text_w)/2:y=h*0.48:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )
    return filters


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

        captions = room17_hiragana_captions(data.get("vocals") or [], total)
        if captions:
            captioned = tmp_path / "captioned.mp4"
            vf = ",".join(captions + ["format=yuv420p"])
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(video_only),
                    "-vf",
                    vf,
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-preset",
                    "medium",
                    "-crf",
                    "18",
                    str(captioned),
                ]
            )
            video_only = captioned

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


ROOM28_GOJUON = [
    ["あ", "い", "う", "え", "お"],
    ["か", "き", "く", "け", "こ"],
    ["さ", "し", "す", "せ", "そ"],
    ["た", "ち", "つ", "て", "と"],
    ["な", "に", "ぬ", "ね", "の"],
    ["は", "ひ", "ふ", "へ", "ほ"],
    ["ま", "み", "む", "め", "も"],
    ["や", None, "ゆ", None, "よ"],
    ["ら", "り", "る", "れ", "ろ"],
    ["わ", None, "を", None, "ん"],
]
# L28 encountered kana (34/46); へ is new in this room.
ROOM28_ENCOUNTERED = {
    "あ", "い", "う", "え", "お", "は", "す", "か", "し", "た", "の", "な", "ま", "ん",
    "さ", "こ", "れ", "ほ", "ね", "や", "ぬ", "り", "ひ", "に", "つ", "く", "を", "わ",
    "と", "け", "て", "き", "ち", "へ",
}
ROOM28_NEW = {"へ"}

# Teaching beats end before a short hold + fade-out (film does not run full BGM tail).
ROOM28_HOLD_AFTER_CONTENT = 5.0
ROOM28_FADE_OUT = 4.0


def room28_typography() -> dict[str, str]:
    return {
        "ink": "0xF3F1EB",
        "ink_soft": "0xD8D4CB",
        "ink_quiet": "0x9A958C",
        "shadow": "0x171512@0.42",
    }


def room28_timeline(content_seconds: float) -> list[dict]:
    """Pedagogical beats from start-here/lesson-28/index.html (no nav/chrome)."""
    colors = room28_typography()
    ink = colors["ink"]
    soft = colors["ink_soft"]
    quiet = colors["ink_quiet"]

    beats = [
        {
            "weight": 1.45,
            "lines": [
                {"text": "へや", "fontsize": 188, "y": "h*0.36", "color": ink},
                {"text": "heya", "fontsize": 64, "y": "h*0.52", "color": soft, "borderw": 2},
                {"text": "room", "fontsize": 54, "y": "h*0.58", "color": quiet, "borderw": 2},
            ],
        },
        {
            "weight": 1.25,
            "lines": [
                {"text": "へ　や", "fontsize": 156, "y": "h*0.40", "color": ink},
                {"text": "he　ya", "fontsize": 58, "y": "h*0.54", "color": soft, "borderw": 2},
            ],
        },
        {
            "weight": 1.05,
            "lines": [
                {"text": "や you already have.", "fontsize": 72, "y": "h*0.48", "color": ink},
            ],
        },
        {
            "weight": 1.05,
            "lines": [
                {"text": "へ is new.", "fontsize": 72, "y": "h*0.48", "color": ink},
            ],
        },
        {
            "weight": 1.25,
            "lines": [
                {"text": "へや", "fontsize": 188, "y": "h*0.40", "color": ink},
                {"text": "heya", "fontsize": 64, "y": "h*0.56", "color": soft, "borderw": 2},
            ],
        },
        {
            "weight": 0.95,
            "lines": [
                {"text": "Your Hiragana", "fontsize": 72, "y": "h*0.48", "color": ink},
            ],
        },
        {
            "weight": 1.15,
            "lines": [
                {
                    "text": "へ joins because へや needed it.",
                    "fontsize": 72,
                    "y": "h*0.48",
                    "color": ink,
                },
            ],
        },
        {
            "weight": 1.15,
            "lines": [
                {
                    "text": "34 of 46 is not unfinished work.",
                    "fontsize": 72,
                    "y": "h*0.48",
                    "color": ink,
                },
            ],
        },
        {
            "weight": 0.85,
            "lines": [
                {
                    "text": "Hiragana: 34 / 46",
                    "fontsize": 58,
                    "y": "h*0.44",
                    "color": "0xC9A458",
                    "borderw": 2,
                },
            ],
        },
        {"weight": 2.35, "grid": True},
    ]

    weight_sum = sum(float(b["weight"]) for b in beats)
    cursor = 0.0
    scheduled: list[dict] = []
    for beat in beats:
        dur = content_seconds * (float(beat["weight"]) / weight_sum)
        scheduled.append({**beat, "start": cursor, "end": cursor + dur})
        cursor += dur
    return scheduled


def room28_drawtext(
    text: str,
    start: float,
    end: float,
    *,
    fontsize: int = 72,
    y: str = "h*0.48",
    color: str,
    borderw: int = 3,
    shadow: str,
    font: str = FONT,
) -> str:
    t = escape_drawtext(text)
    return (
        f"drawtext=fontfile={font}:text='{t}':fontsize={fontsize}:"
        f"fontcolor={color}:borderw={borderw}:bordercolor={shadow}:"
        f"x=(w-text_w)/2:y={y}:"
        f"enable='between(t,{start:.2f},{end:.2f})'"
    )


def room28_cell_kind(kana: str | None) -> str:
    if kana is None:
        return "void"
    if kana in ROOM28_NEW:
        return "new"
    if kana in ROOM28_ENCOUNTERED:
        return "learned"
    return "pending"


def _room28_draw_centered_kana(
    draw: "ImageDraw.ImageDraw",
    kana: str,
    box: tuple[int, int, int, int],
    font: "ImageFont.FreeTypeFont",
    fill: tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), kana, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (x0 + (x1 - x0 - tw) / 2, y0 + (y1 - y0 - th) / 2 - 2),
        kana,
        font=font,
        fill=fill,
    )


def room28_kana_grid_png(path: Path) -> None:
    """10×5 gojūon chart: a cell at every box, including unlearned and voids.

    46 hiragana positions always draw a cell. Unlearned kana keep a subdued
    border plus an 8–12% ghost of the character. Structurally absent slots
    (や/ゆ/よ, わ/を/ん gaps) are dark-filled with no ghost.
    """
    if Image is None:
        raise SystemExit("Pillow is required for Room 28 kana grid rendering.")

    cell = 108
    gap = 10
    cols = list(reversed(ROOM28_GOJUON))  # row-reverse on the site
    rows = 5
    width = len(cols) * cell + (len(cols) - 1) * gap
    height = rows * cell + (rows - 1) * gap
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 58)

    gold = (201, 164, 88, 255)
    ivory = (243, 241, 235, 255)
    # ~10% ivory ghost — almost imperceptible, discoverable on inspection.
    ghost = (243, 241, 235, 28)
    learned_border = (201, 164, 88, 90)
    learned_bg = (201, 164, 88, 22)
    pending_border = (214, 202, 178, 130)
    pending_bg = (16, 14, 12, 72)
    void_fill = (22, 19, 16, 236)
    void_border = (52, 46, 40, 255)
    new_border = (201, 164, 88, 220)
    new_bg = (201, 164, 88, 32)

    counts = {"learned": 0, "new": 0, "pending": 0, "void": 0}
    for cx, column in enumerate(cols):
        for ry in range(rows):
            kana = column[ry] if ry < len(column) else None
            kind = room28_cell_kind(kana)
            counts[kind] += 1
            x0 = cx * (cell + gap)
            y0 = ry * (cell + gap)
            x1 = x0 + cell
            y1 = y0 + cell
            box = (x0, y0, x1, y1)

            if kind == "void":
                draw.rounded_rectangle(box, radius=3, fill=void_fill, outline=void_border, width=2)
                continue
            if kind == "new":
                draw.rounded_rectangle(box, radius=3, fill=new_bg, outline=new_border, width=2)
                _room28_draw_centered_kana(draw, kana, box, font, gold)
                continue
            if kind == "learned":
                draw.rounded_rectangle(box, radius=3, fill=learned_bg, outline=learned_border, width=2)
                _room28_draw_centered_kana(draw, kana, box, font, ivory)
                continue
            # pending: always a cell + ghost of the future kana
            draw.rounded_rectangle(box, radius=3, fill=pending_bg, outline=pending_border, width=2)
            _room28_draw_centered_kana(draw, kana, box, font, ghost)

    if counts["learned"] + counts["new"] != 34 or counts["pending"] != 12 or counts["void"] != 4:
        raise SystemExit(f"Room 28 grid cell counts unexpected: {counts}")
    img.save(path)


def render_room_28(out: Path) -> None:
    image = ROOT / "kml/assets/studies/room.png"
    audio = ROOT / "start-here/audio/lesson-7.mp3"
    if not image.exists() or image.stat().st_size < 1000:
        raise SystemExit(f"Missing room image: {image}")
    if not audio.exists():
        raise SystemExit(f"Missing room audio: {audio}")

    audio_total = duration(audio)
    # Pace teaching across most of the track; end with hold + fade (no repeat coda).
    content_seconds = max(120.0, audio_total - ROOM28_HOLD_AFTER_CONTENT - ROOM28_FADE_OUT - 8.0)
    colors = room28_typography()
    shadow = colors["shadow"]
    beats = room28_timeline(content_seconds)
    content_end = beats[-1]["end"] if beats else content_seconds
    fade_start = content_end + ROOM28_HOLD_AFTER_CONTENT
    film_total = fade_start + ROOM28_FADE_OUT

    draw_filters: list[str] = [
        "scale=1920:1080:force_original_aspect_ratio=increase",
        "crop=1920:1080",
        "zoompan=z='min(1.03,1+0.00004*on)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30",
    ]

    grid_beat: dict | None = None
    for beat in beats:
        if beat.get("grid"):
            grid_beat = beat
            continue
        for line in beat.get("lines") or []:
            draw_filters.append(
                room28_drawtext(
                    line["text"],
                    beat["start"],
                    beat["end"],
                    fontsize=int(line.get("fontsize") or 72),
                    y=str(line.get("y") or "h*0.48"),
                    color=str(line.get("color") or colors["ink"]),
                    borderw=int(line.get("borderw") or 3),
                    shadow=shadow,
                )
            )
    draw_filters.append(f"fade=t=out:st={fade_start:.3f}:d={ROOM28_FADE_OUT:.3f}")
    draw_filters.append("format=yuv420p")
    vf = ",".join(draw_filters)

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
                f"{film_total:.3f}",
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

        video_in = silent
        if grid_beat:
            grid_png = tmp_path / "kana-grid.png"
            room28_kana_grid_png(grid_png)
            overlay_out = tmp_path / "with-grid.mp4"
            start = grid_beat["start"]
            end = fade_start  # hold full grid through post-lesson pause
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(silent),
                    "-loop",
                    "1",
                    "-i",
                    str(grid_png),
                    "-filter_complex",
                    (
                        f"[0:v][1:v]overlay=x=(W-w)/2:y=(H-h)/2:"
                        f"enable='between(t,{start:.2f},{end:.2f})',format=yuv420p[v]"
                    ),
                    "-map",
                    "[v]",
                    "-t",
                    f"{film_total:.3f}",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-preset",
                    "medium",
                    "-crf",
                    "18",
                    str(overlay_out),
                ]
            )
            video_in = overlay_out

        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_in),
                "-i",
                str(audio),
                "-filter_complex",
                (
                    f"[1:a]afade=t=out:st={fade_start:.3f}:d={ROOM28_FADE_OUT:.3f}[a]"
                ),
                "-map",
                "0:v:0",
                "-map",
                "[a]",
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
                f"{film_total:.3f}",
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
