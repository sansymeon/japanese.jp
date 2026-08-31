"""Shared helpers for Start Here study-room YouTube prototype films."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[misc, assignment]
    ImageDraw = None  # type: ignore[misc, assignment]
    ImageFont = None  # type: ignore[misc, assignment]

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

GOJUON = [
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

# Cumulative encountered kana (gojūon boxes only) — mirrors beginner-course.js
_L0 = ["あ", "い", "う", "え", "お"]
_L1 = _L0 + ["は", "す", "か", "し", "た", "の"]
_L2 = _L1
_L4 = _L2 + ["な", "ま", "ん", "さ", "こ"]
_L5 = _L4
_L6 = _L5 + ["れ"]
_L7 = _L6 + ["ほ", "ね", "や", "ぬ"]
_L8 = _L7
_L9 = _L8
_L10 = _L9
_L11 = _L10 + ["り"]
_L12 = _L11
_L13 = _L12 + ["ひ"]
_L14 = _L13 + ["に"]
_L15 = _L14 + ["つ"]
_L16 = _L15 + ["く"]
_L17 = _L16
_L18 = _L17 + ["を"]
_L19 = _L18
_L20 = _L19 + ["わ"]
_L21 = _L20 + ["と"]
_L22 = _L21
_L23 = _L22
_L24 = _L23 + ["け", "て"]
_L25 = _L24
_L26 = _L25 + ["き"]
_L27 = _L26 + ["ち"]
_L28 = _L27 + ["へ"]
_L29 = _L28 + ["せ"]
_L30 = _L29 + ["み"]
_L31 = _L30 + ["ら"]
_L32 = _L31 + ["そ"]
_L33 = _L32 + ["も"]
_L34 = _L33 + ["ゆ", "め"]
_L35 = _L34 + ["む", "る"]
_L36 = _L35 + ["ふ"]
_L37 = _L36
_L38 = _L37 + ["よ", "ろ"]
_L39 = _L38
_L40 = _L39

ENCOUNTERED_BY_ROOM: dict[int, set[str]] = {
    i: set(v)
    for i, v in enumerate(
        [
            _L0,
            _L1,
            _L2,
            _L2,
            _L4,
            _L5,
            _L6,
            _L7,
            _L8,
            _L9,
            _L10,
            _L11,
            _L12,
            _L13,
            _L14,
            _L15,
            _L16,
            _L17,
            _L18,
            _L19,
            _L20,
            _L21,
            _L22,
            _L23,
            _L24,
            _L25,
            _L26,
            _L27,
            _L28,
            _L29,
            _L30,
            _L31,
            _L32,
            _L33,
            _L34,
            _L35,
            _L36,
            _L37,
            _L38,
            _L39,
            _L40,
        ]
    )
}

NEW_KANA_BY_ROOM: dict[int, list[str]] = {
    2: ["は", "す", "か", "し"],
    4: ["な", "ま", "ん", "さ", "こ"],
    6: ["れ"],
    7: ["ほ", "ね", "や", "ぬ"],
    11: ["り"],
    13: ["ひ"],
    14: ["に"],
    15: ["つ"],
    16: ["く"],
    18: ["を"],
    20: ["わ"],
    21: ["と"],
    24: ["け", "て"],
    26: ["き"],
    27: ["ち"],
    28: ["へ"],
    29: ["せ"],
    30: ["み"],
    31: ["ら"],
    32: ["そ"],
    33: ["も"],
    34: ["ゆ", "め"],
    35: ["む", "る"],
    36: ["ふ"],
    38: ["よ", "ろ"],
}

AUDIO_POOL = [6, 7, 8, 9, 10, 11]
AUDIO_OVERRIDES: dict[int, int] = {
    12: 7,
    13: 8,
    14: 9,
    15: 6,
    16: 11,
    37: 7,
}
ATMOSPHERE_AUDIO_ROOMS = {2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 37}

HOLD_AFTER_CONTENT = 5.0
FADE_OUT = 4.0
PAUSE_WEIGHT = 0.55

PACE = {
    "grid": 3.0,
    "kana": 1.65,
    "verse": 1.85,
    "new_kana": 1.2,
    "kana_note": 1.0,
    "english": 0.4,
    "pause": PAUSE_WEIGHT,
}

INK = "0xF3F1EB"
INK_SOFT = "0xD8D4CB"
INK_QUIET = "0x9A958C"
SHADOW = "0x171512@0.42"
GOLD = "0xC9A458"


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


def audio_path_for_room(room_id: int) -> Path:
    if room_id in AUDIO_OVERRIDES:
        n = AUDIO_OVERRIDES[room_id]
    elif room_id in {2, 4, 6, 7, 8, 9, 10, 11}:
        n = room_id
    elif room_id == 37:
        n = 7
    else:
        n = AUDIO_POOL[(room_id - 6) % len(AUDIO_POOL)]
    path = ROOT / f"start-here/audio/lesson-{n}.mp3"
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def text_has_kana(text: str) -> bool:
    return any("\u3040" <= ch <= "\u309f" or ch in "　" for ch in text)


def text_mentions_new_kana(text: str, new_kana: set[str]) -> bool:
    return any(k in text for k in new_kana)


def pace_weight(beat: dict, new_kana: set[str]) -> float:
    kind = beat.get("kind")
    if kind == "grid":
        return PACE["grid"]
    if kind == "pause":
        return PACE["pause"]
    if kind == "verse":
        return PACE["verse"]
    if kind in {"exhibit", "unpack", "kana_return"}:
        return PACE["new_kana"] if text_mentions_new_kana(
            beat.get("kana") or "", new_kana
        ) else PACE["kana"]
    if kind == "prose":
        if text_mentions_new_kana(beat.get("text") or "", new_kana):
            return PACE["new_kana"]
        if text_has_kana(beat.get("text") or ""):
            return PACE["kana_note"]
        return PACE["english"]
    if kind == "puzzle_heading":
        return PACE["english"]
    if kind == "puzzle_note":
        if text_has_kana(beat.get("text") or ""):
            return PACE["kana_note"]
        return PACE["english"]
    if kind == "puzzle_count":
        return PACE["english"] * 0.85
    return PACE["kana_note"]


def schedule_beats(beats: list[dict], new_kana: set[str], content_seconds: float) -> list[dict]:
    weights = [pace_weight(b, new_kana) for b in beats]
    total_w = sum(weights)
    cursor = 0.0
    out: list[dict] = []
    for beat, w in zip(beats, weights):
        dur = content_seconds * (w / total_w)
        out.append({**beat, "start": cursor, "end": cursor + dur, "duration": dur})
        cursor += dur
    return out


def estimate_text_width(text: str, fontsize: int) -> float:
    """Rough pixel width for mixed Latin / kana instructional copy."""
    width = 0.0
    for ch in text:
        code = ord(ch)
        if ch == " ":
            width += fontsize * 0.33
        elif 0x3040 <= code <= 0x30FF or 0x4E00 <= code <= 0x9FFF or 0xFF00 <= code <= 0xFFEF:
            width += fontsize * 1.02
        else:
            width += fontsize * 0.58
    return width


def wrap_instruction_text(text: str, fontsize: int = 64, max_width: float = 1500.0) -> list[str]:
    """Split long instructional copy onto at most two centered lines."""
    text = " ".join(text.split())
    if estimate_text_width(text, fontsize) <= max_width:
        return [text]

    words = text.split(" ")
    if len(words) == 1:
        return [text]

    # Build first line until the next word would overflow the safe width.
    first_words: list[str] = []
    for word in words:
        candidate = " ".join(first_words + [word])
        if first_words and estimate_text_width(candidate, fontsize) > max_width:
            break
        first_words.append(word)

    # Keep at least one word on each line when possible.
    if not first_words:
        first_words = [words[0]]
    if len(first_words) >= len(words):
        first_words = words[: max(1, len(words) // 2)]

    first = " ".join(first_words).strip()
    second = " ".join(words[len(first_words) :]).strip()
    if not second:
        return [first]
    return [first, second]


def beat_lines(beat: dict) -> list[dict]:
    """Convert a beat dict into drawtext line specs."""
    lines: list[dict] = []
    kind = beat.get("kind")

    if kind == "exhibit":
        kana = beat.get("kana") or ""
        if kana:
            fs = 156 if len(kana) <= 4 else 128 if len(kana) <= 8 else 96
            lines.append({"text": kana, "fontsize": fs, "y": "h*0.36", "color": INK})
        romaji = beat.get("romaji")
        if romaji:
            lines.append(
                {"text": romaji, "fontsize": 64, "y": "h*0.52", "color": INK_SOFT, "borderw": 2}
            )
        en = beat.get("en")
        if en:
            lines.append(
                {"text": en, "fontsize": 54, "y": "h*0.86", "color": INK_SOFT, "borderw": 3}
            )
    elif kind == "unpack":
        kana = beat.get("kana") or ""
        if kana:
            lines.append({"text": kana, "fontsize": 156, "y": "h*0.40", "color": INK})
        romaji = beat.get("romaji")
        if romaji:
            lines.append(
                {"text": romaji, "fontsize": 58, "y": "h*0.54", "color": INK_SOFT, "borderw": 2}
            )
    elif kind == "kana_return":
        kana = beat.get("kana") or ""
        romaji = beat.get("romaji")
        if kana:
            # Scale long returns down; prefer a two-line break on spaces.
            if len(kana) <= 4:
                fs = 188
            elif len(kana) <= 8:
                fs = 156
            else:
                fs = 128
            while fs > 72 and estimate_text_width(kana, fs) > 1500:
                fs -= 12
            if " " in kana and estimate_text_width(kana, fs) > 1200:
                parts = wrap_instruction_text(kana, fontsize=fs, max_width=1200)
                if len(parts) > 1:
                    lines.append({"text": parts[0], "fontsize": fs, "y": "h*0.34", "color": INK})
                    lines.append({"text": parts[1], "fontsize": fs, "y": "h*0.48", "color": INK})
                    if romaji:
                        lines.append(
                            {
                                "text": romaji,
                                "fontsize": 58,
                                "y": "h*0.62",
                                "color": INK_SOFT,
                                "borderw": 2,
                            }
                        )
                    return lines
            lines.append({"text": kana, "fontsize": fs, "y": "h*0.40", "color": INK})
        if romaji:
            lines.append(
                {"text": romaji, "fontsize": 64, "y": "h*0.56", "color": INK_SOFT, "borderw": 2}
            )
    elif kind == "verse":
        text = beat.get("text") or ""
        # Multi-line verse: show as one centered block (smaller if long)
        fs = 72 if len(text) <= 28 else 58
        y = "h*0.44" if "\n" not in text else "h*0.40"
        lines.append({"text": text.replace("\n", " "), "fontsize": fs, "y": y, "color": INK})
    elif kind in {"prose", "puzzle_heading", "puzzle_note"}:
        text = beat.get("text") or ""
        if text:
            # Choose a font size that keeps two wrapped lines inside the safe width.
            fs = 72
            wrapped = wrap_instruction_text(text, fontsize=fs)
            if len(wrapped) > 1 or estimate_text_width(text, fs) > 1500:
                fs = 64
                wrapped = wrap_instruction_text(text, fontsize=fs)
            if max(estimate_text_width(part, fs) for part in wrapped) > 1500:
                fs = 56
                wrapped = wrap_instruction_text(text, fontsize=fs)
            if len(wrapped) == 1:
                lines.append({"text": wrapped[0], "fontsize": fs, "y": "h*0.48", "color": INK})
            else:
                # Two lines centered as a pair so long copy stays on screen.
                lines.append({"text": wrapped[0], "fontsize": fs, "y": "h*0.44", "color": INK})
                lines.append({"text": wrapped[1], "fontsize": fs, "y": "h*0.52", "color": INK})
    elif kind == "puzzle_count":
        text = beat.get("text") or ""
        if text:
            lines.append(
                {"text": text, "fontsize": 58, "y": "h*0.44", "color": GOLD, "borderw": 2}
            )
    return lines


def drawtext_filter(
    text: str,
    start: float,
    end: float,
    *,
    fontsize: int = 72,
    y: str = "h*0.48",
    color: str = INK,
    borderw: int = 3,
) -> str:
    t = escape_drawtext(text)
    return (
        f"drawtext=fontfile={FONT}:text='{t}':fontsize={fontsize}:"
        f"fontcolor={color}:borderw={borderw}:bordercolor={SHADOW}:"
        f"x=(w-text_w)/2:y={y}:"
        f"enable='between(t,{start:.2f},{end:.2f})'"
    )


def kana_grid_png(path: Path, encountered: set[str], new_kana: set[str]) -> None:
    if Image is None:
        raise SystemExit("Pillow required for kana grid rendering.")

    cell = 108
    gap = 10
    pad = 28
    cols = list(reversed(GOJUON))
    rows = 5
    inner_w = len(cols) * cell + (len(cols) - 1) * gap
    inner_h = rows * cell + (rows - 1) * gap
    width = inner_w + pad * 2
    height = inner_h + pad * 2
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 58)

    # Opaque dark image box behind the chart.
    draw.rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=16,
        fill=(14, 11, 9, 255),
        outline=(52, 44, 36, 255),
        width=2,
    )

    gold = (240, 205, 120, 255)
    ivory = (248, 246, 240, 255)
    # Keep pending ghosts quiet even on the darker box.
    ghost = (243, 241, 235, 20)
    learned_border = (201, 164, 88, 120)
    learned_bg = (28, 24, 18, 80)
    pending_border = (214, 202, 178, 55)
    pending_bg = (16, 14, 12, 35)
    void_fill = (18, 15, 12, 200)
    void_border = (48, 42, 36, 220)
    new_border = (240, 205, 120, 255)
    new_bg = (36, 28, 14, 90)

    def draw_kana(kana: str, box: tuple[int, int, int, int], fill: tuple[int, int, int, int]) -> None:
        x0, y0, x1, y1 = box
        bbox = draw.textbbox((0, 0), kana, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((x0 + (x1 - x0 - tw) / 2, y0 + (y1 - y0 - th) / 2 - 2), kana, font=font, fill=fill)

    for cx, column in enumerate(cols):
        for ry in range(rows):
            kana = column[ry] if ry < len(column) else None
            x0 = pad + cx * (cell + gap)
            y0 = pad + ry * (cell + gap)
            box = (x0, y0, x0 + cell, y0 + cell)
            if kana is None:
                draw.rounded_rectangle(box, radius=3, fill=void_fill, outline=void_border, width=2)
            elif kana in new_kana:
                draw.rounded_rectangle(box, radius=3, fill=new_bg, outline=new_border, width=3)
                draw_kana(kana, box, gold)
            elif kana in encountered:
                draw.rounded_rectangle(box, radius=3, fill=learned_bg, outline=learned_border, width=2)
                draw_kana(kana, box, ivory)
            else:
                draw.rounded_rectangle(box, radius=3, fill=pending_bg, outline=pending_border, width=2)
                draw_kana(kana, box, ghost)

    img.save(path)


FFMPEG_PRESET = "fast"
FFMPEG_CRF = "19"


def resolve_beat_image(beat: dict, default_image: Path) -> Path:
    raw = beat.get("image")
    if raw:
        p = Path(raw)
        if p.exists() and p.stat().st_size >= 500:
            return p
    return default_image


def render_image_group(
    image: Path,
    group_beats: list[dict],
    group_start: float,
    group_duration: float,
    out_path: Path,
) -> None:
    filters = [
        "scale=1920:1080:force_original_aspect_ratio=increase",
        "crop=1920:1080",
        # Static hold — zoompan is prohibitively slow for batch renders.
    ]
    for beat in group_beats:
        rel_start = max(0.0, beat["start"] - group_start)
        rel_end = min(group_duration, beat["end"] - group_start)
        for line in beat_lines(beat):
            filters.append(
                drawtext_filter(
                    line["text"],
                    rel_start,
                    rel_end,
                    fontsize=int(line.get("fontsize") or 72),
                    y=str(line.get("y") or "h*0.48"),
                    color=str(line.get("color") or INK),
                    borderw=int(line.get("borderw") or 3),
                )
            )
    filters.append("format=yuv420p")
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image),
            "-vf",
            ",".join(filters),
            "-t",
            f"{group_duration:.3f}",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            FFMPEG_PRESET,
            "-crf",
            str(FFMPEG_CRF),
            str(out_path),
        ]
    )


def concat_segments(segments: list[Path], out_path: Path) -> None:
    if len(segments) == 1:
        run(["ffmpeg", "-y", "-i", str(segments[0]), "-c", "copy", str(out_path)])
        return
    list_file = out_path.with_suffix(".txt")
    list_file.write_text("\n".join(f"file '{s.resolve()}'" for s in segments) + "\n")
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(out_path),
        ]
    )


def render_study_room_film(
    *,
    room_id: int,
    slug: str,
    beats: list[dict],
    default_image: Path,
    out_path: Path,
    review_flags: list[str] | None = None,
) -> dict:
    review_flags = review_flags or []
    encountered = ENCOUNTERED_BY_ROOM[room_id]
    new_kana = set(NEW_KANA_BY_ROOM.get(room_id, []))
    audio = audio_path_for_room(room_id)
    audio_len = duration(audio)

    content_seconds = max(90.0, min(audio_len * 1.35, audio_len + 45.0))
    if len(beats) > 14:
        content_seconds = max(content_seconds, len(beats) * 7.5)

    scheduled = schedule_beats(beats, new_kana, content_seconds)
    content_end = scheduled[-1]["end"] if scheduled else content_seconds
    fade_start = content_end + HOLD_AFTER_CONTENT
    film_total = fade_start + FADE_OUT

    if audio_len < film_total:
        review_flags.append(f"audio_loop ({audio_len:.0f}s track, {film_total:.0f}s film)")
    review_flags.append("batch_static_background")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"room{room_id}-") as tmp:
        tmp_path = Path(tmp)
        segments: list[Path] = []
        group_beats: list[dict] = []
        group_image: Path | None = None
        group_start = 0.0

        def flush_group() -> None:
            nonlocal group_beats, group_image, group_start
            if not group_beats or group_image is None:
                return
            group_end = group_beats[-1]["end"]
            dur = group_end - group_start
            if dur <= 0.05:
                group_beats = []
                group_image = None
                return
            seg = tmp_path / f"seg_{len(segments):03d}.mp4"
            render_image_group(group_image, group_beats, group_start, dur, seg)
            segments.append(seg)
            group_beats = []
            group_image = None

        for beat in scheduled:
            if beat.get("kind") == "grid":
                # Hold a clean image under the grid so prior text does not freeze underneath.
                flush_group()
                img_path = resolve_beat_image(beat, default_image)
                seg = tmp_path / f"seg_{len(segments):03d}.mp4"
                hold = max(0.1, beat["end"] - beat["start"])
                run(
                    [
                        "ffmpeg",
                        "-y",
                        "-loop",
                        "1",
                        "-i",
                        str(img_path),
                        "-vf",
                        "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p",
                        "-t",
                        f"{hold:.3f}",
                        "-an",
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "-preset",
                        FFMPEG_PRESET,
                        "-crf",
                        str(FFMPEG_CRF),
                        str(seg),
                    ]
                )
                segments.append(seg)
                continue
            img_path = resolve_beat_image(beat, default_image)
            if group_image is None:
                group_image = img_path
                group_start = beat["start"]
                group_beats = [beat]
            elif img_path == group_image:
                group_beats.append(beat)
            else:
                flush_group()
                group_image = img_path
                group_start = beat["start"]
                group_beats = [beat]
        flush_group()

        silent = tmp_path / "silent.mp4"
        concat_segments(segments, silent)

        grid_beat = next((b for b in scheduled if b.get("kind") == "grid"), None)
        video_in = silent
        if grid_beat:
            grid_png = tmp_path / "grid.png"
            kana_grid_png(grid_png, encountered, new_kana)
            overlay_out = tmp_path / "with-grid.mp4"
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
                        f"enable='between(t,{grid_beat['start']:.2f},{fade_start:.2f})',"
                        f"fade=t=out:st={fade_start:.3f}:d={FADE_OUT:.3f},format=yuv420p[v]"
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
                    FFMPEG_PRESET,
                    "-crf",
                    str(FFMPEG_CRF),
                    str(overlay_out),
                ]
            )
            video_in = overlay_out
        else:
            faded = tmp_path / "faded.mp4"
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(silent),
                    "-vf",
                    f"fade=t=out:st={fade_start:.3f}:d={FADE_OUT:.3f},format=yuv420p",
                    "-t",
                    f"{film_total:.3f}",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-preset",
                    FFMPEG_PRESET,
                    "-crf",
                    str(FFMPEG_CRF),
                    str(faded),
                ]
            )
            video_in = faded

        loop_n = max(0, int(film_total / audio_len) + 1)
        run(
            [
                "ffmpeg",
                "-y",
                "-stream_loop",
                str(loop_n),
                "-i",
                str(audio),
                "-i",
                str(video_in),
                "-filter_complex",
                f"[0:a]atrim=0:{film_total:.3f},afade=t=out:st={fade_start:.3f}:d={FADE_OUT:.3f}[a]",
                "-map",
                "1:v:0",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
                "-preset",
                FFMPEG_PRESET,
                "-crf",
                str(FFMPEG_CRF),
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-t",
                f"{film_total:.3f}",
                "-movflags",
                "+faststart",
                str(out_path),
            ]
        )

    return {
        "room_id": room_id,
        "slug": slug,
        "duration": film_total,
        "audio": str(audio.relative_to(ROOT)),
        "review_flags": review_flags,
        "beats": len(scheduled),
    }
