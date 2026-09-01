"""Shared helpers for Start Here study-room YouTube prototype films."""

from __future__ import annotations

import re
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

HOLD_AFTER_CONTENT = 3.0
FADE_OUT = 4.0
PAUSE_WEIGHT = 0.55
GRID_DURATION = 20.0
PUZZLE_HEADING_DURATION = 5.0
PUZZLE_NOTE_DURATION = 10.0
# Seconds per pace-weight unit for lesson beats (generous for kana; not soundtrack-fill).
LESSON_SECONDS_PER_WEIGHT = 24.0

PACE = {
    "grid": 3.0,  # unused for absolute grid timing; kept for reference
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
SHADOW = "0x171512@0.65"
GOLD = "0xC9A458"
TEXT_BOX = "0x171512@0.78"

# Picture-sentence glosses for これは〜です / これは〜ですか exhibits.
KORE_WA_NOUN_EN: dict[str, str] = {
    "ほん": "book",
    "ねこ": "cat",
    "やま": "mountain",
    "いぬ": "dog",
    "すし": "sushi",
    "いす": "chair",
}

# Short answers: はなです。 → It is a flower.
DESU_REPLY_EN: dict[str, str] = {
    "はな": "flower",
    "いす": "chair",
    "かさ": "umbrella",
    "さかな": "fish",
    "ほし": "star",
}

# ねこが います / ねこが いますか
GA_IMARU_NOUN_EN: dict[str, str] = {
    "ねこ": "cat",
    "いぬ": "dog",
    "さかな": "fish",
}


def ga_imasu_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").replace("？", "").replace("　", " ").strip()
    m = re.search(r"(.+?)が\s*います$", cleaned)
    if not m:
        return None
    noun = GA_IMARU_NOUN_EN.get(m.group(1).strip())
    return f"There is a {noun}." if noun else None


def ga_imasu_ka_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").replace("？", "").replace("　", " ").strip()
    m = re.search(r"(.+?)が\s*いますか", cleaned)
    if not m:
        return None
    noun = GA_IMARU_NOUN_EN.get(m.group(1).strip())
    return f"Is there a {noun}?" if noun else None


# いすが あります / ほしが あります (plural gloss for stars)
GA_ARIMASU_EN: dict[str, str] = {
    "いす": "There is a chair.",
    "ほん": "There is a book.",
    "やま": "There is a mountain.",
    "ほし": "There are stars.",
}

GA_ARIMASU_KA_EN: dict[str, str] = {
    "いす": "Is there a chair?",
    "ほん": "Is there a book?",
    "やま": "Is there a mountain?",
    "ほし": "Are there stars?",
}


def ga_arimasu_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").replace("？", "").replace("　", " ").strip()
    m = re.search(r"(.+?)が\s*あります$", cleaned)
    if not m:
        return None
    noun = m.group(1).strip()
    if noun in GA_ARIMASU_EN:
        return GA_ARIMASU_EN[noun]
    en_noun = KORE_WA_NOUN_EN.get(noun)
    return f"There is a {en_noun}." if en_noun else None


def ga_arimasu_ka_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").replace("？", "").replace("　", " ").strip()
    m = re.search(r"(.+?)が\s*ありますか", cleaned)
    if not m:
        return None
    noun = m.group(1).strip()
    if noun in GA_ARIMASU_KA_EN:
        return GA_ARIMASU_KA_EN[noun]
    en_noun = KORE_WA_NOUN_EN.get(noun)
    return f"Is there a {en_noun}?" if en_noun else None


# しずかな やま / ほし / あかり / ひかり
SHIZUKA_NA_EN: dict[str, str] = {
    "やま": "A quiet mountain.",
    "ほし": "Quiet stars.",
    "あかり": "A quiet light.",
    "ひかり": "A quiet light.",
}

# Single-word picture exhibits.
WORD_EXHIBIT_EN: dict[str, str] = {
    "ひかり": "light",
    "あかり": "lamp",
    "はし": "bridge",
    "つりがね": "Temple Bell",
    "つくえ": "desk",
    "いし": "stone",
    "あさひ": "morning sun",
    "かわ": "river",
    "おと": "sound",
    "まど": "window",
    "とおい": "distant",
    "かね": "bell",
    "ひとつ": "one",
    "げんき": "fine",
    "こんにちは": "hello",
    "しあわせ": "happiness",
}

# Short picture phrases.
PHRASE_EXHIBIT_EN: dict[str, str] = {
    "ぬれた はし": "a wet bridge",
    "ぬれたはし": "a wet bridge",
    "ぬれた はしに": "on the wet bridge",
    "ぬれたはしに": "on the wet bridge",
    "つくえの うえ": "on the desk",
    "つくえのうえ": "on the desk",
    "いしを こえ": "over the stones",
    "いしをこえ": "over the stones",
    "あさひを うつし": "Reflecting the morning sun.",
    "あさひをうつし": "Reflecting the morning sun.",
    "やまの かわ": "mountain river",
    "やまのかわ": "mountain river",
    "かわの おと": "the sound of the river",
    "かわのおと": "the sound of the river",
    "とおい ひかり": "distant light",
    "とおいひかり": "distant light",
    "たけのおと": "the sound of bamboo",
    "たけの おと": "the sound of bamboo",
    "やまのこえ": "the voice of the mountain",
    "やまの こえ": "the voice of the mountain",
    "はてまで": "to the horizon",
}

# Solo unpack glosses — keep tiny; do not teach grammar.
UNPACK_EN: dict[str, str] = {
    "に": "on",
}


def word_exhibit_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").strip()
    return WORD_EXHIBIT_EN.get(cleaned)


def phrase_exhibit_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").replace("？", "").replace("　", " ").strip()
    if cleaned in PHRASE_EXHIBIT_EN:
        return PHRASE_EXHIBIT_EN[cleaned]
    compact = cleaned.replace(" ", "")
    return PHRASE_EXHIBIT_EN.get(compact)


def unpack_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").replace("　", " ").strip()
    return UNPACK_EN.get(cleaned)


def shizuka_na_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").replace("？", "").replace("　", " ").strip()
    m = re.match(r"しずかな\s*(.+)", cleaned)
    if not m:
        return None
    return SHIZUKA_NA_EN.get(m.group(1).strip())


def kore_wa_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").replace("？", "").replace("　", " ").strip()
    if re.search(r"これは\s*なん\s*ですか", cleaned):
        return "What is this?"
    m = re.search(r"これは\s*(.+?)\s*ですか", cleaned)
    if m:
        noun = KORE_WA_NOUN_EN.get(m.group(1).strip())
        return f"Is this a {noun}?" if noun else None
    m = re.search(r"これは\s*(.+?)\s*です", cleaned)
    if m:
        noun = KORE_WA_NOUN_EN.get(m.group(1).strip())
        return f"This is a {noun}." if noun else None
    return None


def reply_desu_english(kana: str) -> str | None:
    cleaned = (kana or "").replace("。", "").strip()
    m = re.match(r"^(.+?)です$", cleaned)
    if not m:
        return None
    noun = DESU_REPLY_EN.get(m.group(1).strip())
    return f"It is a {noun}." if noun else None


def puzzle_note_for_film(text: str) -> str:
    """Drop progress counts from puzzle notes — the chart is enough."""
    cleaned = re.sub(r"\d+ of 46 is not unfinished work(?:\.|[ —-]\s*)?", "", text or "").strip()
    cleaned = re.sub(r"\s*[—-]\s*", " ", cleaned).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"(?<=\. )([a-z])", lambda m: m.group(1).upper(), cleaned)
    return cleaned


def reply_yes_no(kana: str) -> tuple[str, str] | None:
    """Return (はい/いいえ display focus, Yes/No) for answer lines."""
    text = (kana or "").strip()
    if text.startswith("はい"):
        return ("はい", "Yes")
    if text.startswith("いいえ"):
        return ("いいえ", "No")
    return None


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


def normalize_film_text(text: str) -> str:
    """Latin punctuation that draws safely with the CJK film font.

    Curly quotes render overly wide; ASCII apostrophe breaks ffmpeg
    drawtext single-quoting. Prefer a narrow modifier apostrophe.
    """
    return (
        (text or "")
        .replace("\u2019", "\u02bc")
        .replace("\u2018", "\u02bc")
        .replace("'", "\u02bc")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2014", " - ")
        .replace("\u2013", "-")
    )


def display_vocab_kana(kana: str) -> str:
    """Vocabulary overlays omit the trailing Japanese period."""
    return (kana or "").rstrip("。．")


def display_vocab_romaji(romaji: str) -> str:
    """Vocabulary romaji overlays omit the trailing Latin period."""
    return (romaji or "").rstrip(".")


def escape_drawtext(text: str) -> str:
    text = normalize_film_text(text)
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
    kana = beat.get("kana") or ""
    kana_compact = kana.replace(" ", "").replace("　", "")
    if kind == "exhibit" and "なんですか" in kana_compact:
        return 0.55
    if kind == "exhibit" and "がいます" in kana_compact:
        return 0.55
    if kind == "exhibit" and "があります" in kana_compact:
        return 0.55
    if kind == "exhibit" and kore_wa_english(kana):
        return 0.65
    if kind == "reply" and reply_desu_english(kana):
        return 0.75
    if kind == "reply" and kana.startswith("はい") and ("います" in kana or "あります" in kana):
        return 0.65
    if kind == "kana_return" and kana.strip() in {"なん", "います", "あります"}:
        return 0.38
    if kind == "kana_return" and (
        phrase_exhibit_english(kana) or word_exhibit_english(kana) or (beat.get("en") or "").strip()
    ):
        return 0.55
    if kind == "unpack" and len(kana_compact) <= 4:
        return 0.42
    if kind == "prose" and not text_has_kana(beat.get("text") or ""):
        text = beat.get("text") or ""
        # Longer door / recognition copy needs a little more air than a short cue.
        return 0.7 if len(text) > 80 else 0.35
    if kind == "prose" and text_mentions_new_kana(beat.get("text") or "", new_kana):
        return 0.45
    if kind == "prose" and text_has_kana(beat.get("text") or ""):
        text = beat.get("text") or ""
        # Room 19 を recognition beat — keep readable after the faster track.
        return 0.9 if len(text) > 80 else 0.45
    if kind == "exhibit" and word_exhibit_english(kana):
        return 0.45
    if kind == "exhibit" and phrase_exhibit_english(kana):
        return 0.55
    if kind == "exhibit" and (beat.get("en") or "").strip() and " " not in kana.replace("　", " "):
        return 0.45
    if kind == "exhibit" and (beat.get("en") or "").strip():
        return 0.55
    if kind == "exhibit" and kana.strip() == "しずか":
        return 0.45
    if kind == "exhibit" and "しずかな" in kana:
        return 0.55
    if kind == "unpack" and unpack_english(kana):
        return 0.38
    if kind == "grid":
        return PACE["grid"]
    if kind == "pause":
        return PACE["pause"]
    if kind == "verse":
        verse_text = (beat.get("text") or "").replace(" ", "").replace("　", "")
        # Two-line temple-bell verse — enough time to read, without the longest quiet hold.
        if "つりがね" in verse_text:
            return 1.25
        if "しずかなへや" in verse_text or "ぬれたはしに" in verse_text:
            return 1.35
        if "しずかな" in verse_text:
            return 1.35
        return 0.75
    if kind in {"exhibit", "reply", "unpack", "kana_return"}:
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
        return 0.35
    if kind == "puzzle_count":
        return 0.0  # omitted from films — chart is enough
    return PACE["kana_note"]


CHART_KINDS = {"puzzle_heading", "puzzle_note", "puzzle_count", "grid"}


def schedule_beats(beats: list[dict], new_kana: set[str], content_seconds: float | None = None) -> list[dict]:
    """Schedule lesson beats generously; keep the progress chart brief (~25s).

    Instructional content is not stretched to fill the soundtrack. After the
    chart, the renderer holds a clean background with music.
    """
    lesson = [b for b in beats if b.get("kind") not in CHART_KINDS]
    chart = [b for b in beats if b.get("kind") in CHART_KINDS and b.get("kind") != "puzzle_count"]

    lesson_weights = [pace_weight(b, new_kana) for b in lesson]
    # Door cue already points at the verse — keep only a short breath before it.
    for i, b in enumerate(lesson):
        if (
            b.get("kind") == "pause"
            and i + 1 < len(lesson)
            and lesson[i + 1].get("kind") == "verse"
        ):
            lesson_weights[i] = 0.12
    total_w = sum(lesson_weights) or 1.0
    nan_q_count = sum(
        1
        for b in lesson
        if b.get("kind") == "exhibit"
        and "なんですか" in (b.get("kana") or "").replace(" ", "").replace("　", "")
    )
    imasu_count = sum(
        1
        for b in lesson
        if b.get("kind") == "exhibit"
        and "がいます" in (b.get("kana") or "").replace(" ", "").replace("　", "")
    )
    arimasu_count = sum(
        1
        for b in lesson
        if b.get("kind") == "exhibit"
        and "があります" in (b.get("kana") or "").replace(" ", "").replace("　", "")
    )
    shizuka_count = sum(
        1
        for b in lesson
        if b.get("kind") == "exhibit" and "しずか" in (b.get("kana") or "")
    )
    word_exhibit_count = sum(
        1
        for b in lesson
        if b.get("kind") == "exhibit" and word_exhibit_english(b.get("kana") or "")
    )
    phrase_exhibit_count = sum(
        1
        for b in lesson
        if b.get("kind") == "exhibit" and phrase_exhibit_english(b.get("kana") or "")
    )
    if content_seconds is None:
        # Single glossed word rooms (e.g. Room 15 つりがね) use the faster track too.
        sec_per_weight = (
            14.0
            if nan_q_count >= 3
            or imasu_count >= 2
            or arimasu_count >= 2
            or shizuka_count >= 3
            or word_exhibit_count >= 1
            or phrase_exhibit_count >= 2
            else LESSON_SECONDS_PER_WEIGHT
        )
        content_seconds = total_w * sec_per_weight
        content_seconds = max(45.0, min(content_seconds, 220.0))

    out: list[dict] = []
    cursor = 0.0
    for beat, w in zip(lesson, lesson_weights):
        dur = content_seconds * (w / total_w)
        out.append({**beat, "start": cursor, "end": cursor + dur, "duration": dur})
        cursor += dur

    for beat in chart:
        kind = beat.get("kind")
        if kind == "puzzle_heading":
            dur = PUZZLE_HEADING_DURATION
        elif kind == "puzzle_note":
            dur = PUZZLE_NOTE_DURATION
        elif kind == "grid":
            dur = GRID_DURATION
        else:
            continue
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


def wrap_instruction_text(
    text: str, fontsize: int = 64, max_width: float = 1500.0, max_lines: int = 3
) -> list[str]:
    """Split long instructional copy onto centered lines (default up to three)."""
    text = " ".join(text.split())
    if estimate_text_width(text, fontsize) <= max_width:
        return [text]

    # Prefer a sentence boundary when it yields two balanced lines.
    for sep in (". ", " — ", " - "):
        if sep in text:
            left, right = text.split(sep, 1)
            first = (left + sep.rstrip()).strip()
            second = right.strip()
            if (
                first
                and second
                and estimate_text_width(first, fontsize) <= max_width + 80
                and estimate_text_width(second, fontsize) <= max_width
            ):
                return [first, second]

    words = text.split(" ")
    if len(words) == 1:
        return [text]

    lines: list[str] = []
    current: list[str] = []
    for i, word in enumerate(words):
        candidate = " ".join(current + [word])
        if current and estimate_text_width(candidate, fontsize) > max_width:
            lines.append(" ".join(current))
            current = [word]
            if len(lines) >= max_lines - 1:
                # Dump the remainder onto the last line.
                lines.append(" ".join(words[i:]))
                return [ln for ln in lines if ln]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return [ln for ln in lines if ln] or [text]


def beat_lines(beat: dict) -> list[dict]:
    """Convert a beat dict into drawtext line specs."""
    lines: list[dict] = []
    kind = beat.get("kind")

    if kind == "exhibit":
        kana = beat.get("kana") or ""
        shown = display_vocab_kana(kana)
        word_gloss = word_exhibit_english(kana)
        if word_gloss and " " not in kana.replace("　", " "):
            # Single-word exhibits (ひかり。 / あかり。) — stack with room for text boxes.
            lines.append({"text": shown, "fontsize": 156, "y": "h*0.16", "color": INK})
            romaji = display_vocab_romaji(beat.get("romaji") or "")
            if romaji:
                lines.append(
                    {"text": romaji, "fontsize": 64, "y": "h*0.34", "color": INK_SOFT, "borderw": 2}
                )
            lines.append(
                {
                    "text": word_gloss,
                    "fontsize": 58,
                    "y": "h*0.52",
                    "color": INK,
                    "borderw": 3,
                    "fade": True,
                    "box": True,
                }
            )
            return lines
        if shown:
            fs = 156 if len(shown) <= 4 else 128 if len(shown) <= 8 else 96
            while fs > 72 and estimate_text_width(shown, fs) > 1500:
                fs -= 12
            if " " in shown and estimate_text_width(shown, fs) > 1200:
                parts = wrap_instruction_text(shown, fontsize=fs, max_width=1200, max_lines=2)
                if len(parts) > 1:
                    lines.append({"text": parts[0], "fontsize": fs, "y": "h*0.22", "color": INK})
                    lines.append({"text": parts[1], "fontsize": fs, "y": "h*0.34", "color": INK})
                else:
                    lines.append({"text": shown, "fontsize": fs, "y": "h*0.28", "color": INK})
            else:
                lines.append({"text": shown, "fontsize": fs, "y": "h*0.28", "color": INK})
        # Long が います / が あります sentences read better on two lines.
        ga_verb = "が います" if "が います" in shown else "が あります" if "が あります" in shown else None
        if (
            ga_verb
            and len(lines) == 1
            and estimate_text_width(shown, int(lines[0].get("fontsize") or fs)) > 1100
        ):
            m = re.match(r"(.+が)\s*(います[。]?|あります[。]?)", shown)
            if m:
                fs = int(lines[0]["fontsize"])
                lines = [
                    {"text": m.group(1), "fontsize": fs, "y": "h*0.22", "color": INK},
                    {"text": display_vocab_kana(m.group(2)), "fontsize": fs, "y": "h*0.34", "color": INK},
                ]
        romaji = display_vocab_romaji(beat.get("romaji") or "")
        romaji_y = "h*0.48" if len(lines) > 1 else "h*0.40"
        if romaji:
            lines.append(
                {"text": romaji, "fontsize": 64, "y": romaji_y, "color": INK_SOFT, "borderw": 2}
            )
        # Question/statement English — fades in/out on each picture.
        gloss = (
            kore_wa_english(kana)
            or word_exhibit_english(kana)
            or phrase_exhibit_english(kana)
            or shizuka_na_english(kana)
            or ga_imasu_ka_english(kana)
            or ga_imasu_english(kana)
            or ga_arimasu_ka_english(kana)
            or ga_arimasu_english(kana)
            or (None if (beat.get("en") or "").startswith("New:") else beat.get("en") or None)
        )
        note = beat.get("en") if (beat.get("en") or "").startswith("New:") else None
        gloss_y = "h*0.60" if len([ln for ln in lines if "h*0.34" in str(ln.get("y"))]) else "h*0.54"
        if gloss:
            lines.append(
                {
                    "text": gloss,
                    "fontsize": 58,
                    "y": gloss_y,
                    "color": INK,
                    "borderw": 3,
                    "fade": True,
                    "box": True,
                }
            )
        if note:
            fs = 50
            wrapped = wrap_instruction_text(note, fontsize=fs, max_width=1180)
            if len(wrapped) == 1:
                lines.append(
                    {
                        "text": wrapped[0],
                        "fontsize": fs,
                        "y": "h*0.78",
                        "color": INK_SOFT,
                        "borderw": 3,
                    }
                )
            else:
                y0 = 0.70
                for i, part in enumerate(wrapped[:3]):
                    lines.append(
                        {
                            "text": part,
                            "fontsize": fs,
                            "y": f"h*{y0 + i * 0.08:.2f}",
                            "color": INK_SOFT,
                            "borderw": 3,
                        }
                    )
    elif kind == "reply":
        kana = beat.get("kana") or ""
        yn = reply_yes_no(kana)
        if yn:
            focus, en = yn
            lines.append(
                {
                    "text": focus,
                    "fontsize": 168,
                    "y": "h*0.30",
                    "color": INK,
                    "fade": True,
                }
            )
            # Remainder after はい、 / いいえ、 when present.
            rest = ""
            for sep in ("、", ","):
                if sep in kana:
                    rest = kana.split(sep, 1)[1].strip()
                    break
            if rest:
                lines.append(
                    {
                        "text": rest,
                        "fontsize": 96,
                        "y": "h*0.48",
                        "color": INK_SOFT,
                        "borderw": 2,
                    }
                )
            lines.append(
                {
                    "text": en,
                    "fontsize": 72,
                    "y": "h*0.64" if rest else "h*0.52",
                    "color": INK,
                    "borderw": 3,
                    "fade": True,
                }
            )
        else:
            desu_en = reply_desu_english(kana)
            if desu_en:
                display = kana.replace("。", "")
                lines.append(
                    {
                        "text": display,
                        "fontsize": 128,
                        "y": "h*0.34",
                        "color": INK,
                        "fade": True,
                    }
                )
                romaji = display_vocab_romaji(beat.get("romaji") or "")
                if romaji:
                    lines.append(
                        {
                            "text": romaji,
                            "fontsize": 58,
                            "y": "h*0.50",
                            "color": INK_SOFT,
                            "borderw": 2,
                        }
                    )
                lines.append(
                    {
                        "text": desu_en,
                        "fontsize": 72,
                        "y": "h*0.64",
                        "color": INK,
                        "borderw": 3,
                        "fade": True,
                    }
                )
            elif kana:
                lines.append({"text": kana, "fontsize": 128, "y": "h*0.36", "color": INK})
                romaji = display_vocab_romaji(beat.get("romaji") or "")
                if romaji:
                    lines.append(
                        {
                            "text": romaji,
                            "fontsize": 58,
                            "y": "h*0.52",
                            "color": INK_SOFT,
                            "borderw": 2,
                        }
                    )
    elif kind == "unpack":
        kana = display_vocab_kana(beat.get("kana") or "")
        if kana:
            lines.append({"text": kana, "fontsize": 156, "y": "h*0.30", "color": INK})
        romaji = display_vocab_romaji(beat.get("romaji") or "")
        if romaji:
            lines.append(
                {"text": romaji, "fontsize": 58, "y": "h*0.46", "color": INK_SOFT, "borderw": 2}
            )
        en = beat.get("en") or unpack_english(beat.get("kana") or "")
        if en:
            lines.append(
                {
                    "text": en,
                    "fontsize": 58,
                    "y": "h*0.62",
                    "color": INK,
                    "borderw": 3,
                    "fade": True,
                    "box": True,
                }
            )
    elif kind == "kana_return":
        kana = display_vocab_kana(beat.get("kana") or "")
        romaji = display_vocab_romaji(beat.get("romaji") or "")
        en = beat.get("en") or ""
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
                parts = wrap_instruction_text(kana, fontsize=fs, max_width=1200, max_lines=2)
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
                    if en:
                        lines.append(
                            {
                                "text": en,
                                "fontsize": 58,
                                "y": "h*0.74",
                                "color": INK,
                                "borderw": 3,
                                "fade": True,
                                "box": True,
                            }
                        )
                    return lines
            lines.append({"text": kana, "fontsize": fs, "y": "h*0.40", "color": INK})
        if romaji:
            lines.append(
                {"text": romaji, "fontsize": 64, "y": "h*0.56", "color": INK_SOFT, "borderw": 2}
            )
        if en:
            lines.append(
                {
                    "text": en,
                    "fontsize": 64,
                    "y": "h*0.70",
                    "color": INK,
                    "borderw": 3,
                    "fade": True,
                    "box": True,
                }
            )
        elif kana.strip() == "います":
            lines.append(
                {
                    "text": "is",
                    "fontsize": 64,
                    "y": "h*0.70",
                    "color": INK,
                    "borderw": 3,
                    "fade": True,
                    "box": True,
                }
            )
        elif kana.strip() == "あります":
            lines.append(
                {
                    "text": "is/are",
                    "fontsize": 64,
                    "y": "h*0.70",
                    "color": INK,
                    "borderw": 3,
                    "fade": True,
                    "box": True,
                }
            )
    elif kind == "verse":
        text = (beat.get("text") or "").replace("\n", " ")
        fs = 72 if len(text) <= 28 else 58
        wrapped = wrap_instruction_text(text, fontsize=fs, max_width=1500, max_lines=2)
        if len(wrapped) == 1:
            lines.append({"text": wrapped[0], "fontsize": fs, "y": "h*0.44", "color": INK, "box": True})
        else:
            lines.append({"text": wrapped[0], "fontsize": fs, "y": "h*0.40", "color": INK, "box": True})
            lines.append({"text": wrapped[1], "fontsize": fs, "y": "h*0.52", "color": INK, "box": True})
    elif kind in {"prose", "puzzle_heading", "puzzle_note"}:
        text = normalize_film_text(beat.get("text") or "")
        if kind == "puzzle_note":
            text = puzzle_note_for_film(text)
        if text:
            # Choose a font size that keeps wrapped lines inside the safe width.
            fs = 72
            wrapped = wrap_instruction_text(text, fontsize=fs, max_width=1400)
            if len(wrapped) > 1 or estimate_text_width(text, fs) > 1400:
                fs = 64
                wrapped = wrap_instruction_text(text, fontsize=fs, max_width=1400)
            if max(estimate_text_width(part, fs) for part in wrapped) > 1400 or len(wrapped) > 2:
                fs = 56
                wrapped = wrap_instruction_text(text, fontsize=fs, max_width=1400)
            if max(estimate_text_width(part, fs) for part in wrapped) > 1400:
                fs = 50
                wrapped = wrap_instruction_text(text, fontsize=fs, max_width=1400)
            if len(wrapped) == 1:
                lines.append({"text": wrapped[0], "fontsize": fs, "y": "h*0.48", "color": INK, "box": True})
            elif len(wrapped) == 2:
                lines.append({"text": wrapped[0], "fontsize": fs, "y": "h*0.44", "color": INK, "box": True})
                lines.append({"text": wrapped[1], "fontsize": fs, "y": "h*0.52", "color": INK, "box": True})
            else:
                y0 = 0.40
                for i, part in enumerate(wrapped[:3]):
                    lines.append(
                        {
                            "text": part,
                            "fontsize": fs,
                            "y": f"h*{y0 + i * 0.08:.2f}",
                            "color": INK,
                            "box": True,
                        }
                    )
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
    box: bool = True,
    fade: bool = False,
    fade_in: float = 1.0,
    fade_out: float = 1.0,
) -> str:
    t = escape_drawtext(text)
    box_part = f":box=1:boxcolor={TEXT_BOX}:boxborderw=18" if box else ""
    alpha_part = ""
    if fade:
        dur = max(0.05, end - start)
        fi = min(fade_in, dur * 0.35)
        fo = min(fade_out, dur * 0.35)
        # Relative timeline inside this drawtext enable window uses absolute t.
        alpha_part = (
            f":alpha='if(lt(t\\,{start + fi:.3f})\\,(t-{start:.3f})/{fi:.3f}\\,"
            f"if(gt(t\\,{end - fo:.3f})\\,({end:.3f}-t)/{fo:.3f}\\,1))'"
        )
    return (
        f"drawtext=fontfile={FONT}:text='{t}':fontsize={fontsize}:"
        f"fontcolor={color}:borderw={borderw}:bordercolor={SHADOW}:"
        f"x=(w-text_w)/2:y={y}{box_part}{alpha_part}:"
        f"enable='between(t,{start:.2f},{end:.2f})'"
    )


def kana_grid_png(path: Path, encountered: set[str], new_kana: set[str]) -> None:
    if Image is None:
        raise SystemExit("Pillow required for kana grid rendering.")

    cell = 112
    gap = 10
    pad = 32
    cols = list(reversed(GOJUON))
    rows = 5
    inner_w = len(cols) * cell + (len(cols) - 1) * gap
    inner_h = rows * cell + (rows - 1) * gap
    width = inner_w + pad * 2
    height = inner_h + pad * 2
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 62)

    # Fully opaque dark panel so chart reads clearly over any photograph.
    draw.rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=18,
        fill=(8, 7, 6, 255),
        outline=(70, 58, 44, 255),
        width=3,
    )

    gold = (245, 214, 130, 255)
    ivory = (252, 250, 244, 255)
    # Ghost kana stay quiet; cell fills must stay opaque or ffmpeg shows the photo through.
    ghost = (243, 241, 235, 40)
    learned_border = (210, 175, 100, 255)
    learned_bg = (32, 28, 22, 255)
    pending_border = (90, 82, 72, 255)
    pending_bg = (18, 16, 14, 255)
    void_fill = (14, 12, 10, 255)
    void_border = (48, 42, 36, 255)
    new_border = (245, 214, 130, 255)
    new_bg = (48, 36, 18, 255)

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


def resolve_chart_background(scheduled: list[dict], default_image: Path) -> Path:
    """Image under the kana chart — prefer quiet-light / hikari exhibits when present."""
    grid_idx = next((i for i, b in enumerate(scheduled) if b.get("kind") == "grid"), len(scheduled))
    for b in reversed(scheduled[:grid_idx]):
        kana = b.get("kana") or ""
        if b.get("kind") == "exhibit" and "しずかな" in kana and "ひかり" in kana:
            return resolve_beat_image(b, default_image)
    for b in reversed(scheduled[:grid_idx]):
        if b.get("kind") == "exhibit" and "あかり" in (b.get("kana") or ""):
            return resolve_beat_image(b, default_image)
    for b in reversed(scheduled[:grid_idx]):
        if b.get("kind") == "exhibit" and b.get("image"):
            return resolve_beat_image(b, default_image)
    return default_image


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
        beat_dur = max(0.05, rel_end - rel_start)
        for line in beat_lines(beat):
            line_start = rel_start
            line_end = rel_end
            # Sentence English arrives after kana has settled, then fades out.
            if line.get("fade"):
                line_start = rel_start + beat_dur * 0.18
                line_end = rel_end - beat_dur * 0.08
            filters.append(
                drawtext_filter(
                    line["text"],
                    line_start,
                    line_end,
                    fontsize=int(line.get("fontsize") or 72),
                    y=str(line.get("y") or "h*0.48"),
                    color=str(line.get("color") or INK),
                    borderw=int(line.get("borderw") or 3),
                    box=bool(line.get("box", True)),
                    fade=bool(line.get("fade")),
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

    # Lesson beats keep generous kana pacing; chart is brief and not soundtrack-fill.
    scheduled = schedule_beats(beats, new_kana)
    content_end = scheduled[-1]["end"] if scheduled else 90.0
    # Short clean hold after the chart, then fade image + music — no need to finish the track.
    fade_start = content_end + HOLD_AFTER_CONTENT
    film_total = fade_start + FADE_OUT

    if audio_len < film_total:
        review_flags.append(f"audio_loop ({audio_len:.0f}s track, {film_total:.0f}s film)")
    review_flags.append("batch_static_background")
    review_flags.append(f"grid_cap ({GRID_DURATION:.0f}s)")

    chart_bg = resolve_chart_background(scheduled, default_image)
    grid_beat = next((b for b in scheduled if b.get("kind") == "grid"), None)

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
                # Hold the quiet-light (or last exhibit) image under the chart.
                flush_group()
                img_path = chart_bg
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

        # Clean background hold after the chart, then fade image + music.
        if scheduled:
            last_img = chart_bg if grid_beat else resolve_beat_image(scheduled[-1], default_image)
            post = max(0.0, fade_start - scheduled[-1]["end"])
            if post > 0.05:
                seg = tmp_path / f"seg_{len(segments):03d}.mp4"
                run(
                    [
                        "ffmpeg",
                        "-y",
                        "-loop",
                        "1",
                        "-i",
                        str(last_img),
                        "-vf",
                        "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p",
                        "-t",
                        f"{post:.3f}",
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

        silent = tmp_path / "silent.mp4"
        concat_segments(segments, silent)

        video_in = silent
        if grid_beat:
            grid_png = tmp_path / "grid.png"
            kana_grid_png(grid_png, encountered, new_kana)
            overlay_out = tmp_path / "with-grid.mp4"
            grid_end = grid_beat["end"]
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
                        f"enable='between(t,{grid_beat['start']:.2f},{grid_end:.2f})',"
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
