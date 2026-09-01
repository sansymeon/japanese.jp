#!/usr/bin/env python3
"""Remove local film audio from YouTube-wired Start Here rooms."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START_HERE = ROOT / "start-here"
COURSE_JS = START_HERE / "js" / "beginner-course.js"

GUIDED_ROOMS = ("0", "1", "3", "5", "17", "18", "24", "25", "40")

IFRAME = """          <div class="pathway-film">
            <iframe
              src="https://www.youtube.com/embed/{youtube_id}?rel=0&modestbranding=1"
              title="{title}"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerpolicy="strict-origin-when-cross-origin"
              allowfullscreen
            ></iframe>
          </div>"""

ROOM25_STATIC_VERSES = """
        <div class="interlude-static-verses reveal">
          <div class="guided-verse" data-static-verse="romaji" hidden>
            <p>yama no kawa ga ishi o koe</p>
            <p>taenu oto dake ga tani ni hibiite ita</p>
          </div>
          <div class="guided-verse" data-static-verse="hiragana" hidden lang="ja">
            <p>やまの かわが　いしを こえ</p>
            <p>たえぬ おとだけが　たにに ひびいていた</p>
          </div>
          <div class="guided-verse guided-verse--furigana" data-static-verse="furigana" hidden>
            <p class="jp-verse" lang="ja">
              <ruby>山<rt>やま</rt></ruby>の<ruby>川<rt>かわ</rt></ruby>が　<ruby>石<rt>いし</rt></ruby>を<ruby>越<rt>こ</rt></ruby>え<br>
              <ruby>絶<rt>た</rt></ruby>えぬ<ruby>音<rt>おと</rt></ruby>だけが　<ruby>谷<rt>たに</rt></ruby>に<ruby>響<rt>ひび</rt></ruby>いていた
            </p>
          </div>
          <div class="guided-verse" data-static-verse="japanese" hidden lang="ja">
            <p>山の川が　石を越え</p>
            <p>絶えぬ音だけが　谷に響いていた</p>
          </div>
        </div>"""


def parse_youtube_ids() -> dict[str, str]:
    text = COURSE_JS.read_text(encoding="utf-8")
    ids: dict[str, str] = {}
    for match in re.finditer(
        r'"(\d+)":\s*\{[^}]*?watchYoutubeId:\s*"([^"]+)"',
        text,
        re.DOTALL,
    ):
        ids[match.group(1)] = match.group(2)
    return ids


def strip_course_atmosphere() -> None:
    text = COURSE_JS.read_text(encoding="utf-8")
    youtube_ids = parse_youtube_ids()

    def scrub_block(block: str) -> str:
        lesson_id = re.search(r'"(\d+)":\s*\{', block)
        if not lesson_id or lesson_id.group(1) not in youtube_ids:
            return block
        block = re.sub(r"\n\s*atmosphereAudio:.*", "", block)
        block = re.sub(r"\n\s*atmospherePool:.*", "", block)
        return block

    parts = re.split(r'(?="\d+":\s*\{)', text)
    rebuilt = parts[0]
    for part in parts[1:]:
        end = part.find("\n    },")
        if end == -1:
            rebuilt += part
            continue
        block = part[: end + len("\n    },")]
        tail = part[end + len("\n    },") :]
        rebuilt += scrub_block(block) + tail
    COURSE_JS.write_text(rebuilt, encoding="utf-8")


def remove_script_tags(html: str) -> str:
    html = re.sub(
        r'\s*<script src="\.\./data/rooms/\d+\.js" defer></script>\n',
        "\n",
        html,
    )
    for name in ("../js/beginner-guided-song.js", "../js/beginner-watch.js"):
        html = re.sub(
            rf'\s*<script src="{re.escape(name)}" defer></script>\n',
            "\n",
            html,
        )
    return html


def convert_guided_room(room_id: str, youtube_id: str) -> None:
    path = START_HERE / f"lesson-{room_id}" / "index.html"
    html = path.read_text(encoding="utf-8")
    title_match = re.search(r"<title>([^<]+)</title>", html)
    title = title_match.group(1) if title_match else f"Room {room_id}"

    html = remove_script_tags(html)
    html = html.replace(" beginner-guided-page", "")
    html = re.sub(
        r"<!-- YouTube primary path \(shown when watchYoutubeId is set\)\. -->\n",
        "<!-- Film on YouTube — no local MP3 player. -->\n",
        html,
    )
    html = re.sub(
        r'\s*data-watch-youtube-primary\n\s*hidden\n',
        "\n",
        html,
    )
    html = re.sub(
        r"<div data-watch-film></div>",
        IFRAME.format(youtube_id=youtube_id, title=title.replace('"', "&quot;")),
        html,
        count=1,
    )
    html = re.sub(
        r"\n\s*<section class=\"guided-stage\"[\s\S]*?</section>\n",
        "\n",
        html,
        count=1,
    )
    html = re.sub(
        r"\s*data-guided-after\n",
        "\n",
        html,
    )
    html = re.sub(
        r"\n\s*<button type=\"button\" class=\"museum-btn museum-btn--ghost\" data-guided-replay>[\s\S]*?</button>",
        "",
        html,
    )
    html = re.sub(
        r"\n\s*<div class=\"interlude-keep reveal\">[\s\S]*?</div>",
        "",
        html,
    )

    if room_id == "17":
        html = re.sub(
            r"\n\s*<!-- Local guided-song replay views[\s\S]*?</ul>\n\n\s*<!-- Static verse views[\s\S]*?<ul class=\"interlude-view-list reveal\" data-static-verse-list hidden>",
            '\n        <ul class="interlude-view-list reveal" data-static-verse-list>',
            html,
            count=1,
        )

    if room_id == "25":
        html = html.replace('data-guided-view="', 'data-static-verse-select="')
        html = html.replace(
            'data-static-verse-select="none"',
            'data-static-verse-select="none" aria-pressed="true"',
        )
        for view in ("romaji", "hiragana", "furigana", "japanese"):
            html = html.replace(
                f'data-static-verse-select="{view}"',
                f'data-static-verse-select="{view}" aria-pressed="false"',
            )
        html = html.replace(
            "</ul>\n\n        <aside",
            "</ul>\n" + ROOM25_STATIC_VERSES + "\n        <aside",
        )

    path.write_text(html, encoding="utf-8")


def strip_study_music(room_ids: set[str]) -> None:
    pattern = re.compile(
        r"\n\s*<button type=\"button\" data-study-music hidden>♪ Play room music</button>"
    )
    for room_id in sorted(room_ids, key=int):
        path = START_HERE / f"lesson-{room_id}" / "index.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        html = pattern.sub("", html)
        path.write_text(html, encoding="utf-8")


def main() -> None:
    youtube_ids = parse_youtube_ids()
    strip_course_atmosphere()
    for room_id in GUIDED_ROOMS:
        yt = youtube_ids.get(room_id)
        if not yt:
            raise SystemExit(f"Missing watchYoutubeId for guided room {room_id}")
        convert_guided_room(room_id, yt)
    strip_study_music(set(youtube_ids.keys()))
    print(f"Cleaned {len(GUIDED_ROOMS)} guided rooms and stripped study music from {len(youtube_ids)} YouTube rooms.")


if __name__ == "__main__":
    main()
