#!/usr/bin/env python3
"""Skip the Different Strokes intro on subsequent website stroke-order pages.

Website only. Does not touch SVG markup, KanjiVG sources, exhibition JSON,
or YouTube recording scripts.

Rule:
  Keep intro for the first kanji of each lesson (1–153) and for hub Sets 1–15.
  Mark every other lesson stroke page with data-skip-intro="1".
  strokes_sequence.js skips the intro hold/fade when that marker is present.

Usage:
  python3 kml/scripts/apply_lesson_stroke_intro_skip.py
  python3 kml/scripts/apply_lesson_stroke_intro_skip.py --apply
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "contents/books/book_01/lessons"
PAGES_DIR = ROOT / "tools/strokes/pages"
HUB_INDEX = ROOT / "tools/strokes/index.html"
SEQUENCE_JS = ROOT / "tools/strokes/js/strokes_sequence.js"

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)
HUB_SLUG_RE = re.compile(r'class="stroke-set-link"[^>]*href="[^"]*/pages/([^"/]+)\.html"')
BODY_RE = re.compile(r"<body([^>]*)>", re.IGNORECASE)
SKIP_ATTR_RE = re.compile(
    r"\s*data-skip-intro(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?",
    re.IGNORECASE,
)

INTRO_BLOCK = """  /* ===== INTRO ===== */

  intro?.classList.add('visible');
  await delay(INTRO_HOLD);

  intro?.classList.add('fade-out');
  await delay(INTRO_FADE);
"""

INTRO_SKIP_BLOCK = """  /* ===== INTRO ===== */

  const skipIntro = document.body?.dataset.skipIntro === "1";
  if (!skipIntro) {
    intro?.classList.add('visible');
    await delay(INTRO_HOLD);

    intro?.classList.add('fade-out');
    await delay(INTRO_FADE);
  }
"""


def parse_lesson_slugs(lesson: int) -> list[str]:
    path = LESSONS_DIR / f"lesson_{lesson:02d}.html"
    if not path.is_file():
        return []
    html = path.read_text(encoding="utf-8")
    slugs: list[str] = []
    for block in SECTION_RE.findall(html):
        slug_m = re.search(r'data-slug="([^"]+)"', block)
        if slug_m:
            slugs.append(slug_m.group(1))
    return slugs


def parse_hub_set_slugs() -> list[str]:
    html = HUB_INDEX.read_text(encoding="utf-8")
    return HUB_SLUG_RE.findall(html)


def page_path(slug: str) -> Path:
    return PAGES_DIR / f"{slug}.html"


def body_has_skip(html: str) -> bool:
    match = BODY_RE.search(html)
    if not match:
        return False
    return bool(re.search(r"data-skip-intro", match.group(1), re.IGNORECASE))


def set_body_skip(html: str, skip: bool) -> str:
    matches = list(BODY_RE.finditer(html))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one <body> tag, found {len(matches)}")

    def repl(match: re.Match[str]) -> str:
        attrs = SKIP_ATTR_RE.sub("", match.group(1))
        if skip:
            attrs = f'{attrs} data-skip-intro="1"'
        attrs = re.sub(r" {2,}", " ", attrs).rstrip()
        if attrs and not attrs.startswith(" "):
            attrs = " " + attrs
        return f"<body{attrs}>"

    return BODY_RE.sub(repl, html, count=1)


def sequencer_status(js: str) -> str:
    if "dataset.skipIntro" in js and "if (!skipIntro)" in js:
        return "already_patched"
    if INTRO_BLOCK in js:
        return "needs_patch"
    return "unexpected"


def plan() -> dict:
    first_slugs: list[tuple[int, str]] = []
    subsequent_slugs: set[str] = set()
    all_lesson_slugs: set[str] = set()
    lesson_sizes: dict[int, int] = {}

    for lesson in range(1, 154):
        slugs = parse_lesson_slugs(lesson)
        lesson_sizes[lesson] = len(slugs)
        if not slugs:
            continue
        first_slugs.append((lesson, slugs[0]))
        all_lesson_slugs.update(slugs)
        subsequent_slugs.update(slugs[1:])

    hub_slugs = parse_hub_set_slugs()
    hub_keep: list[str] = []
    hub_missing: list[str] = []
    for slug in hub_slugs:
        path = page_path(slug)
        if path.is_file():
            hub_keep.append(slug)
        else:
            hub_missing.append(slug)

    keep_slugs = {slug for _, slug in first_slugs} | set(hub_keep)
    skip_slugs = sorted(subsequent_slugs - keep_slugs)

    page_files = sorted(PAGES_DIR.glob("*.html"))
    page_slugs = {path.stem for path in page_files}
    odd_names = [path.name for path in page_files if " " in path.name or path.stem in {"", ".html"}]
    missing_pages = sorted(all_lesson_slugs - page_slugs)
    extra_pages = sorted(page_slugs - all_lesson_slugs)

    js_text = SEQUENCE_JS.read_text(encoding="utf-8")
    return {
        "first_slugs": first_slugs,
        "hub_slugs": hub_slugs,
        "hub_keep": hub_keep,
        "hub_missing": hub_missing,
        "hub_extra_keep": [s for s in hub_keep if s not in {slug for _, slug in first_slugs}],
        "keep_slugs": keep_slugs,
        "skip_slugs": skip_slugs,
        "lesson_sizes": lesson_sizes,
        "page_files": page_files,
        "missing_pages": missing_pages,
        "extra_pages": extra_pages,
        "odd_names": odd_names,
        "js_status": sequencer_status(js_text),
        "js_text": js_text,
    }


def classify_page_action(html: str, skip: bool) -> str:
    has_skip = body_has_skip(html)
    if skip and not has_skip:
        return "add_skip"
    if skip and has_skip:
        return "already_skip"
    if not skip and has_skip:
        return "remove_skip"
    return "keep_intro"


def apply_pages(skip_slugs: set[str], keep_slugs: set[str], dry_run: bool) -> dict[str, int]:
    counts = {
        "add_skip": 0,
        "already_skip": 0,
        "remove_skip": 0,
        "keep_intro": 0,
        "missing_target": 0,
        "body_error": 0,
    }
    targets = sorted(skip_slugs | keep_slugs)
    for slug in targets:
        path = page_path(slug)
        if not path.is_file():
            counts["missing_target"] += 1
            continue
        html = path.read_text(encoding="utf-8")
        skip = slug in skip_slugs
        action = classify_page_action(html, skip)
        counts[action] += 1
        if dry_run or action in {"already_skip", "keep_intro"}:
            continue
        try:
            updated = set_body_skip(html, skip)
        except ValueError:
            counts["body_error"] += 1
            counts[action] -= 1
            continue
        if updated != html:
            path.write_text(updated, encoding="utf-8")
    return counts


def apply_sequencer(js_text: str, status: str, dry_run: bool) -> str:
    if status == "already_patched":
        return status
    if status != "needs_patch":
        return status
    if dry_run:
        return "would_patch"
    SEQUENCE_JS.write_text(js_text.replace(INTRO_BLOCK, INTRO_SKIP_BLOCK, 1), encoding="utf-8")
    return "patched"


def print_report(data: dict, page_counts: dict[str, int], js_result: str, dry_run: bool) -> None:
    empty_lessons = [n for n, size in data["lesson_sizes"].items() if size == 0]
    print("Different Strokes intro skip")
    print(f"  mode: {'dry-run' if dry_run else 'apply'}")
    print()
    print("Keep intro")
    print(f"  first kanji of lessons 1–153: {len(data['first_slugs'])}")
    print(f"  hub set entry points with pages: {len(data['hub_keep'])}")
    print(f"  hub entries not already lesson-first: {len(data['hub_extra_keep'])}")
    if data["hub_extra_keep"]:
        print("   ", ", ".join(data["hub_extra_keep"]))
    print(f"  unique keep slugs: {len(data['keep_slugs'])}")
    print()
    print("Skip intro")
    print(f"  subsequent lesson pages: {len(data['skip_slugs'])}")
    print()
    print("Sequencer")
    print(f"  {SEQUENCE_JS.relative_to(ROOT.parent)}: {js_result}")
    print()
    print("Page actions")
    for key in ("add_skip", "already_skip", "remove_skip", "keep_intro", "missing_target", "body_error"):
        print(f"  {key}: {page_counts[key]}")
    print()
    print("Unexpected / notes")
    print(f"  lesson files with no kanji-entry: {empty_lessons or 'none'}")
    print(f"  hub set slugs with no page: {data['hub_missing'] or 'none'}")
    print(f"  lesson slugs missing pages: {data['missing_pages'] or 'none'}")
    print(f"  pages not in lessons 1–153: {data['extra_pages'] or 'none'}")
    print(f"  odd page filenames: {data['odd_names'] or 'none'}")
    first_preview = ", ".join(f"L{n:02d}={slug}" for n, slug in data["first_slugs"][:5])
    print(f"  first-kanji preview: {first_preview}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write page markers and the sequencer guard (default is dry-run)",
    )
    args = parser.parse_args()
    dry_run = not args.apply

    data = plan()
    skip_slugs = set(data["skip_slugs"])
    page_counts = apply_pages(skip_slugs, data["keep_slugs"], dry_run=dry_run)
    js_result = apply_sequencer(data["js_text"], data["js_status"], dry_run=dry_run)
    print_report(data, page_counts, js_result, dry_run)
    if data["js_status"] == "unexpected":
        return 1
    if page_counts["body_error"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
