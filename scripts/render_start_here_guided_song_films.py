#!/usr/bin/env python3
"""Render Start Here guided-song / listen films for unlisted YouTube upload.

Reads timing from start-here/data/rooms/{id}.json (same conductor as the web
player). Outputs to exports/start-here-prototypes/ and artifacts.

  scenes[]  — Rooms 1, 3, 5, 18, 24 (image dissolves + ja/romaji overlays)
  film[]    — Rooms 17, 25 (painting sequence; 17 adds timed hiragana vocals)
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "start-here" / "data" / "rooms"
OUT_DIR = ROOT / "exports" / "start-here-prototypes"
ARTIFACT_DIR = Path("/opt/cursor/artifacts/start-here-prototypes")
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

INK = "0xF3F1EB"
INK_SOFT = "0xD8D4CB"
SHADOW = "0x171512@0.55"

# Full guided-song listen exports (Room 24 recap stays room-24-竹の音.mp4).
OUTPUT_NAMES: dict[str, str] = {
    "1": "room-01-nihongo-ga-tanoshii.mp4",
    "3": "room-03-whats-your-name.mp4",
    "5": "room-05-japanese-food-is-good.mp4",
    "17": "room-17-nureta-hashi.mp4",
    "18": "room-18-sushi-o-tabemasu.mp4",
    "24": "room-24-take-no-oto.mp4",
    "25": "room-25-yama-no-kawa.mp4",
}

LISTEN_ROOMS = ["1", "3", "5", "17", "18", "24", "25"]


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


def resolve_asset(rel: str) -> Path:
    return (DATA_DIR / rel).resolve()


def load_room(room_id: str) -> dict:
    path = DATA_DIR / f"{room_id}.json"
    return json.loads(path.read_text())


def drawtext_line(
    text: str,
    start: float,
    end: float,
    *,
    fontsize: int = 72,
    y: str = "h*0.68",
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


def image_timeline_from_scenes(scenes: list[dict], default_xfade: float) -> list[dict]:
    events: list[dict] = []
    prev_image: str | None = None
    for scene in scenes:
        image = str(scene["image"])
        if image != prev_image:
            xf = 0.0 if not events else float(scene.get("crossfade") or default_xfade)
            events.append({"start": float(scene["start"]), "image": image, "crossfade": xf})
            prev_image = image
    return events


def scene_lyric_filters(scenes: list[dict], total: float, *, show_romaji: bool) -> list[str]:
    filters: list[str] = []
    for i, scene in enumerate(scenes):
        ja = str(scene.get("ja") or "").strip()
        if not ja or scene.get("overlay") == "none":
            continue
        start = float(scene["start"])
        end = total
        for nxt in scenes[i + 1 :]:
            nja = str(nxt.get("ja") or "").strip()
            if nja != ja or nxt.get("overlay") == "none":
                end = float(nxt["start"])
                break
        filters.append(drawtext_line(ja, start, end, fontsize=64, y="h*0.66"))
        romaji = str(scene.get("romaji") or "").strip()
        if show_romaji and romaji:
            filters.append(
                drawtext_line(romaji, start, end, fontsize=44, y="h*0.76", color=INK_SOFT, borderw=2)
            )
    return filters


def vocal_hiragana_filters(vocals: list[dict], total: float) -> list[str]:
    hold_after_line = 6.0
    max_gap = 12.0
    filters: list[str] = []
    for i, item in enumerate(vocals):
        start = float(item["start"])
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        if i + 1 < len(vocals):
            nxt = float(vocals[i + 1]["start"])
            end = nxt if (nxt - start) <= max_gap else start + hold_after_line
        else:
            end = min(total, start + hold_after_line)
        filters.append(drawtext_line(text, start, end, fontsize=96, y="h*0.48"))
    return filters


def build_crossfade_video(
    items: list[dict],
    total: float,
    tmp_path: Path,
    *,
    default_xfade: float,
    ken_burns: bool = False,
    preset: str = "fast",
    crf: int = 19,
) -> Path:
    if not items:
        raise ValueError("image timeline is empty")

    starts = [float(item["start"]) for item in items]
    images = [resolve_asset(str(item["image"])) for item in items]
    crossfades: list[float] = []
    for i, item in enumerate(items):
        if i == 0:
            crossfades.append(0.0)
        else:
            crossfades.append(float(item.get("crossfade") or default_xfade))

    clips: list[Path] = []
    for i, img in enumerate(images):
        if i + 1 < len(starts):
            seg_dur = (starts[i + 1] - starts[i]) + crossfades[i + 1]
        else:
            seg_dur = max(0.2, total - starts[i])
        seg_dur = max(0.2, seg_dur)
        clip = tmp_path / f"clip_{i:02d}.mp4"
        base = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
        if ken_burns:
            filt = (
                f"{base},"
                "zoompan=z='min(1.04,1+0.00008*on)':x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,format=yuv420p"
            )
        else:
            filt = f"{base},format=yuv420p"
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
                preset,
                "-crf",
                str(crf),
                str(clip),
            ]
        )
        clips.append(clip)

    if len(clips) == 1:
        return clips[0]

    current = clips[0]
    acc_dur = duration(current)
    for i in range(1, len(clips)):
        nxt = clips[i]
        xf = crossfades[i]
        xf = min(xf, acc_dur * 0.45, duration(nxt) * 0.45)
        merged = tmp_path / f"merge_{i:02d}.mp4"
        if xf <= 0.05:
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
                    preset,
                    "-crf",
                    str(crf),
                    str(merged),
                ]
            )
        else:
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
                    (
                        f"[0:v][1:v]xfade=transition=fade:duration={xf:.3f}:"
                        f"offset={offset:.3f},format=yuv420p[v]"
                    ),
                    "-map",
                    "[v]",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    preset,
                    "-crf",
                    str(crf),
                    str(merged),
                ]
            )
        current = merged
        acc_dur = duration(current)
    return current


def apply_captions(
    video: Path,
    filters: list[str],
    tmp_path: Path,
    *,
    preset: str = "fast",
    crf: int = 19,
) -> Path:
    if not filters:
        return video
    out = tmp_path / "captioned.mp4"
    vf = ",".join(filters + ["format=yuv420p"])
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            preset,
            "-crf",
            str(crf),
            str(out),
        ]
    )
    return out


def mux_audio(video: Path, audio: Path, out: Path, *, preset: str = "fast", crf: int = 19) -> None:
    aud_dur = duration(audio)
    out.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
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


def render_scenes_room(room_id: str, out: Path) -> dict:
    data = load_room(room_id)
    audio = resolve_asset(data["audio"])
    scenes = sorted(data.get("scenes") or [], key=lambda s: float(s["start"]))
    if not scenes:
        raise ValueError(f"Room {room_id}: no scenes[]")

    default_xfade = float(data.get("imageCrossfade") or 2.8)
    total = max(float(data.get("timing", {}).get("audioDuration") or 0), duration(audio))
    show_romaji = str(data.get("romajiDefault") or "on").lower() != "off"
    timeline = image_timeline_from_scenes(scenes, default_xfade)

    with tempfile.TemporaryDirectory(prefix=f"room{room_id}-") as tmp:
        tmp_path = Path(tmp)
        video = build_crossfade_video(
            timeline,
            total,
            tmp_path,
            default_xfade=default_xfade,
            ken_burns=False,
        )
        captions = scene_lyric_filters(scenes, total, show_romaji=show_romaji)
        video = apply_captions(video, captions, tmp_path)
        mux_audio(video, audio, out)
    return {"room": int(room_id), "duration": duration(out), "file": out.name}


def render_film_room(room_id: str, out: Path) -> dict:
    data = load_room(room_id)
    audio = resolve_asset(data["audio"])
    film = sorted(data.get("film") or [], key=lambda s: float(s["start"]))
    if not film:
        raise ValueError(f"Room {room_id}: no film[]")

    default_xfade = float(data.get("imageCrossfade") or 2.0)
    total = max(float(data.get("timing", {}).get("audioDuration") or 0), duration(audio))
    ken_burns = room_id != "25"
    preset = "medium" if room_id == "17" else "fast"
    crf = 18 if room_id == "17" else 19

    with tempfile.TemporaryDirectory(prefix=f"room{room_id}-") as tmp:
        tmp_path = Path(tmp)
        video = build_crossfade_video(
            film,
            total,
            tmp_path,
            default_xfade=default_xfade,
            ken_burns=ken_burns,
            preset=preset,
            crf=crf,
        )
        vocals = data.get("vocals") or []
        if room_id == "17" and vocals:
            captions = vocal_hiragana_filters(vocals, total)
            video = apply_captions(video, captions, tmp_path, preset=preset, crf=crf)
        mux_audio(video, audio, out, preset=preset, crf=crf)
    return {"room": int(room_id), "duration": duration(out), "file": out.name}


def render_room(room_id: str) -> dict:
    out = OUT_DIR / OUTPUT_NAMES[room_id]
    print(f"\n=== Room {room_id} → {out.name} ===", flush=True)
    data = load_room(room_id)
    if data.get("film"):
        meta = render_film_room(room_id, out)
    elif data.get("scenes"):
        meta = render_scenes_room(room_id, out)
    else:
        raise ValueError(f"Room {room_id}: no film[] or scenes[]")
    run(["cp", "-f", str(out), str(ARTIFACT_DIR / out.name)])
    size_mb = out.stat().st_size / 1e6
    print(f"Wrote {out} ({size_mb:.1f} MB, {meta['duration']:.0f}s)", flush=True)
    return meta


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    targets = [str(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else LISTEN_ROOMS
    rendered: list[dict] = []
    failed: list[dict] = []

    for room_id in targets:
        if room_id not in OUTPUT_NAMES:
            failed.append({"room": room_id, "error": "unknown room"})
            continue
        try:
            rendered.append(render_room(room_id))
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED room {room_id}: {exc}", flush=True)
            failed.append({"room": room_id, "error": str(exc)})

    report = OUT_DIR / "guided-song-render-report.json"
    report.write_text(json.dumps({"rendered": rendered, "failed": failed}, indent=2) + "\n")
    print(f"\nReport: {report}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
