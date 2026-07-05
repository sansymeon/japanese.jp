#!/usr/bin/env python3
"""Editorial QA for Lesson 2 Vocabulary Exhibition."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
STEPS_MOD = Path(__file__).resolve().parent / "lesson_02_vocabulary_steps.py"
LESSON_HTML = REPO / "contents/books/book_01/lessons/lesson_02.html"
COLLECTION = ROOT / "collections/lesson_02/lesson_02_vocabulary.json"

RUBY_RE = re.compile(r"<ruby>([^<]+)<rt>([^<]*)</rt></ruby>")
KANJI_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

WHOLE_WORD_RUBY: dict[str, str] = {
    "障子": "しょうじ",
    "部屋": "へや",
    "夕暮れ": "ゆうぐれ",
    "鐘楼": "しょうろう",
    "釣り鐘": "つりがね",
    "朝日": "あさひ",
    "幾世代": "いくせだい",
    "黄金": "おうごん",
    "折り紙": "おりがみ",
    "一人": "ひとり",
    "静けさ": "しずけさ",
    "三日月": "みかづき",
    "夕焼け": "ゆうやけ",
    "夕光": "ゆうこう",
    "中央": "ちゅうおう",
    "水平線": "すいへいせん",
}

BANNED_STEP_KEYS = {"commonReadings", "hint"}
BANNED_JP = {"梯田"}
READING_FIXES: dict[str, str] = {}


def load_steps() -> dict[str, list[dict]]:
    ns: dict = {}
    code = STEPS_MOD.read_text(encoding="utf-8")
    exec(compile(code, str(STEPS_MOD), "exec"), ns)
    return ns["VOCABULARY_BY_SLUG"]


def split_ruby_pattern(compound: str) -> str:
    return "".join(
        rf"<ruby>{re.escape(ch)}<rt>[^<]*</rt></ruby>" for ch in compound
    )


def errors_for_html(html: str, *, label: str) -> list[str]:
    errs: list[str] = []
    if "梯田" in html:
        errs.append(f"{label}: uses 梯田 — prefer 棚田（たなだ）")
    for compound, reading in WHOLE_WORD_RUBY.items():
        if split_ruby_pattern(compound) in html:
            errs.append(
                f"{label}: split ruby for {compound} — "
                f"use <ruby>{compound}<rt>{reading}</rt></ruby>"
            )
    return errs


def normalize_jp(text: str) -> str:
    return re.sub(r"[\s　]+", "", text)


def verse_text_lines(jp_html: str) -> list[str]:
    plain = re.sub(r"<br\s*/?>", "\n", jp_html, flags=re.I)
    plain = re.sub(r"<ruby>([^<]+)<rt>[^<]*</rt></ruby>", r"\1", plain)
    plain = re.sub(r"<[^>]+>", "", plain)
    return [normalize_jp(line) for line in plain.split("\n") if line.strip()]


def verses_by_slug() -> dict[str, str]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_lesson_02_vocabulary_exhibition import parse_lesson_scenes

    return {
        s["meta"]["slug"]: s["verse"]["jpHtml"]
        for s in parse_lesson_scenes(2)
    }


def errors_for_steps(steps_by_slug: dict[str, list[dict]]) -> list[str]:
    errs: list[str] = []
    seen_global: dict[str, str] = {}
    verses = verses_by_slug()

    for slug, steps in steps_by_slug.items():
        seen_local: set[str] = set()

        for i, step in enumerate(steps):
            jp = step.get("jp", "")
            label = f"{slug}[{i}] {jp!r}"

            for key in BANNED_STEP_KEYS:
                if key in step:
                    errs.append(f"{label}: remove dictionary field {key!r}")

            if jp in BANNED_JP:
                errs.append(f"{label}: use 棚田 instead of 梯田")

            if jp in READING_FIXES:
                want = READING_FIXES[jp]
                got = step.get("reading", "")
                if got and got != want:
                    errs.append(f"{label}: reading should be {want!r}, got {got!r}")

            if jp in seen_local:
                errs.append(f"{label}: duplicate step in exhibit")
            seen_local.add(jp)

            if jp in seen_global and seen_global[jp] != slug:
                pass
            elif jp and not step.get("phrase"):
                seen_global[jp] = slug

            reading = step.get("reading", "")
            if reading and KANJI_RE.search(jp) and not step.get("phrase"):
                if jp in WHOLE_WORD_RUBY and reading != WHOLE_WORD_RUBY[jp]:
                    errs.append(
                        f"{label}: whole-word reading should be {WHOLE_WORD_RUBY[jp]!r}, got {reading!r}"
                    )

            jp_html = step.get("jpHtml", "")
            if jp_html:
                errs.extend(errors_for_html(jp_html, label=f"{label} jpHtml"))

        if not steps:
            errs.append(f"{slug}: empty vocabulary sequence")

        final = steps[-1] if steps else {}
        if not final.get("phrase"):
            errs.append(f"{slug}: final step should be a phrase building into the verse")

        verse_html = verses.get(slug, "")
        if final.get("phrase") and verse_html:
            final_jp = normalize_jp(final.get("jp", ""))
            lines = verse_text_lines(verse_html)
            if final_jp and not any(
                final_jp in line or line in final_jp for line in lines
            ):
                errs.append(
                    f"{slug}: final phrase {final.get('jp')!r} not found in verse"
                )

    return errs


def errors_for_collection(path: Path) -> list[str]:
    errs: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON: {exc}"]

    for scene in data.get("scenes", []):
        sid = scene.get("id", "?")
        verse = (scene.get("verse") or {}).get("jpHtml", "")
        errs.extend(errors_for_html(verse, label=f"collection {sid} verse"))

        for i, step in enumerate((scene.get("vocabulary") or {}).get("steps", [])):
            for key in BANNED_STEP_KEYS:
                if key in step:
                    errs.append(f"collection {sid} step[{i}]: has {key!r}")
            jp_html = step.get("jpHtml", "")
            if jp_html:
                errs.extend(
                    errors_for_html(jp_html, label=f"collection {sid} step[{i}]")
                )
    return errs


def main() -> int:
    steps = load_steps()
    lesson_html = LESSON_HTML.read_text(encoding="utf-8")

    all_errors: list[str] = []
    all_errors.extend(errors_for_html(lesson_html, label="lesson_02.html"))
    all_errors.extend(errors_for_steps(steps))
    if COLLECTION.is_file():
        all_errors.extend(errors_for_collection(COLLECTION))

    if all_errors:
        print("Vocabulary validation FAILED:\n", file=sys.stderr)
        for err in all_errors:
            print(f"  • {err}", file=sys.stderr)
        return 1

    print(
        f"Vocabulary validation OK — {len(steps)} exhibits, "
        f"{sum(len(s) for s in steps.values())} steps"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
