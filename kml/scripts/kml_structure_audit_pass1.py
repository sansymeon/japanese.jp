#!/usr/bin/env python3
"""
PASS 1 — KML structure audit (read-only harvest).
Scans lessons 1–22 HTML + kanji_master_with_components.csv.
Does NOT rewrite lesson HTML or normalize structures.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LESSONS_DIR = BASE / "contents/books/book_01/lessons"
KANJI_MASTER = BASE / "data/kanji/kanji_master_with_components.csv"
LESSON_NUMBERS = BASE / "data/kanji/kanji_image_production.csv"
OUT_DIR = BASE / "data/kanji"

LESSON_RANGE = range(1, 23)

# Standard layout codes
STD_LAYOUTS = frozenset({"a", "v", "h", "2l", "2r", "2t", "2b", "e", "ei"})

# HTML/CSS layout names -> preferred tier + standard code hint
OUTER_LAYOUT_MAP = {
    "stack-vertical": ("preferred", "v"),
    "stack-horizontal": ("preferred", "h"),
    "kanji-composite": ("preferred", None),  # resolved from children
    "enclosure-layout": ("preferred", "e"),
    "anchor-box": ("preferred", "a"),
    "composite-horizontal": ("legacy", None),
    "composite-vertical": ("legacy", None),
    "component-horizontal": ("legacy", "2l"),
    "component-composite": ("legacy", None),
}

CSV_LAYOUT_MAP = {
    "vertical": "v",
    "horizontal": "h",
    "box": "e",
    "unknown": "",
    "anchor": "a",
}

# Legacy naming pairs (component-* vs kanji-*)
LEGACY_PAIRS = [
    ("component-horizontal", "kanji-composite / stack-horizontal"),
    ("component-left", "kanji-left"),
    ("component-right", "kanji-right"),
    ("component-composite", "kanji-composite"),
    ("outer-kanji", "enclosure-part / enclosure outer"),
    ("inner-kanji", "enclosure-inner"),
]


def is_cjk_char(ch: str) -> bool:
    if len(ch) != 1:
        return False
    o = ord(ch)
    return (
        0x4E00 <= o <= 0x9FFF
        or 0x3400 <= o <= 0x4DBF
        or 0x20000 <= o <= 0x2A6DF
        or 0xF900 <= o <= 0xFAFF
    )


# Modified radicals / stroke forms seen in lessons 1–22 (not standalone master entries)
RADICAL_FORMS = frozenset(
    "氵扌忄衤辶灬犭刂廴罒冖冂⺌⼇ㇵ𠂊𠂇𧘇厂⻌丶ノ丷㇀"
    + "艹宀儿夂丬"
    + "エニ勹乚几巛戔畐聿兪卂匀"
)


def is_radical_or_variant(sym: str) -> bool:
    sym = sym.strip()
    if len(sym) != 1:
        return False
    o = ord(sym)
    if 0x2E80 <= o <= 0x2FDF:
        return True
    return sym in RADICAL_FORMS


def is_kanji_like(sym: str) -> bool:
    sym = sym.strip()
    if not sym:
        return False
    if is_radical_or_variant(sym):
        return False
    if len(sym) == 1:
        cat = unicodedata.category(sym)
        if cat.startswith("L") or cat == "So":
            return is_cjk_char(sym) or ord(sym) >= 0x2E80
    return any(is_cjk_char(c) for c in sym)


@dataclass
class ComponentUse:
    symbol: str
    labels: set[str] = field(default_factory=set)
    first_lesson: int | None = None
    first_kanji: str = ""
    first_use: str = ""
    sources: set[str] = field(default_factory=set)
    is_future_link: bool = False
    parent_kanji: set[str] = field(default_factory=set)


class LessonComponentParser(HTMLParser):
    """Extract kanji entries and component trees from lesson HTML."""

    def __init__(self, lesson_num: int) -> None:
        super().__init__()
        self.lesson_num = lesson_num
        self.current_kanji = ""
        self.current_slug = ""
        self.in_kanji_entry = False
        self.in_component_box = False
        self.class_stack: list[list[str]] = []
        self.layout_records: list[dict] = []
        self.component_uses: list[tuple[str, str, bool]] = []  # sym, parent, future
        self._pending_future = False

    def _classes(self) -> list[str]:
        return self.class_stack[-1] if self.class_stack else []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k: (v or "") for k, v in attrs}
        cls = d.get("class", "").split()
        self.class_stack.append(cls)

        if tag == "section" and "kanji-entry" in cls:
            self.in_kanji_entry = True
            self.current_kanji = d.get("data-kanji", "")
            self.current_slug = d.get("data-slug", "")

        if tag == "div" and "component-box" in cls:
            self.in_component_box = True

        if tag == "a" and "future-kanji-link" in cls:
            self._pending_future = True

        if self.in_component_box and tag == "div" and "component-layout" in cls:
            outer = next((c for c in cls if c != "component-layout"), "")
            if not outer:
                # component-layout may be sole class on div
                outer = "component-layout-only"
            nested = self._detect_nested_layout()
            std = infer_standard_layout(outer, nested)
            self.layout_records.append(
                {
                    "lesson": self.lesson_num,
                    "kanji": self.current_kanji,
                    "slug": self.current_slug,
                    "outer_html": outer,
                    "nested": nested,
                    "standard": std,
                }
            )

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self.in_kanji_entry:
            self.in_kanji_entry = False
            self.current_kanji = ""
            self.current_slug = ""
        if tag == "div" and self.in_component_box:
            # pop happens below
            pass
        if self.class_stack:
            ended = self.class_stack[-1]
            if tag == "div" and "component-box" in ended:
                self.in_component_box = False
        if self.class_stack:
            self.class_stack.pop()

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text or not self.in_component_box:
            return
        # kanji-part text
        if self.in_kanji_entry and text and not text.startswith("<"):
            sym = text
            if len(sym) <= 4:  # skip whitespace noise
                self.component_uses.append(
                    (sym, self.current_kanji, self._pending_future)
                )
                self._pending_future = False

    def _detect_nested_layout(self) -> str:
        """Summarize child layout classes from current class stack tail."""
        parts = []
        for cls in self.class_stack:
            for name in (
                "kanji-left",
                "kanji-right",
                "component-left",
                "component-right",
                "stack-vertical",
                "stack-horizontal",
                "enclosure-inner",
                "enclosure-part",
                "outer-kanji",
                "inner-kanji",
                "composite-horizontal",
                "composite-vertical",
            ):
                if name in cls:
                    parts.append(name)
        return "|".join(dict.fromkeys(parts))  # preserve order, unique


def infer_standard_layout(outer: str, nested: str) -> str:
    if outer in ("stack-vertical", "composite-vertical") and "stack-horizontal" in nested:
        if "kanji-right" in nested or "component-right" in nested:
            return "2r"
        if "kanji-left" in nested or "component-left" in nested:
            return "2l"
        # two on top pattern
        return "2t"
    if outer in ("stack-horizontal", "composite-horizontal"):
        if "stack-vertical" in nested:
            return "2b"
        hint = OUTER_LAYOUT_MAP.get(outer, (None, None))[1]
        if hint:
            return hint
        return "h"
    if outer == "kanji-composite":
        if "kanji-left" in nested and "stack-vertical" in nested:
            if "kanji-right" in nested:
                return "2l"
        if "kanji-right" in nested and "stack-vertical" in nested:
            return "2l" if "kanji-left" in nested else "2r"
        if "kanji-left" in nested and "kanji-right" in nested:
            return "h"
        return "2l"
    if outer == "component-horizontal":
        return "2l"
    if outer == "enclosure-layout":
        if "enclosure-inner" in nested or "inner-kanji" in nested:
            return "ei"
        return "e"
    if outer == "anchor-box":
        return "a"
    hint = OUTER_LAYOUT_MAP.get(outer, (None, None))[1]
    return hint or ""


def parse_lesson_html(path: Path, lesson_num: int) -> LessonComponentParser:
    p = LessonComponentParser(lesson_num)
    p.feed(path.read_text(encoding="utf-8"))
    return p


def regex_harvest_lesson(path: Path, lesson_num: int) -> tuple[list[dict], list[tuple]]:
    """Regex supplement — HTMLParser misses some kanji-part spans."""
    text = path.read_text(encoding="utf-8")
    layouts = []
    components = []

    # Split by kanji-entry sections
    sections = re.split(r'<section\s+class="kanji-entry"', text)
    for block in sections[1:]:
        km = re.search(r'data-kanji="([^"]*)"', block)
        parent = km.group(1) if km else ""

        for m in re.finditer(
            r'<div\s+class="component-layout\s+([^"]+)"', block
        ):
            outer = m.group(1).strip()
            # snippet after this match until next section or component-box end
            start = m.start()
            snippet = block[start : start + 2500]
            nested_parts = []
            for name in (
                "kanji-left",
                "kanji-right",
                "component-left",
                "component-right",
                "stack-vertical",
                "stack-horizontal",
                "enclosure-inner",
                "enclosure-part",
                "outer-kanji",
                "inner-kanji",
            ):
                if name in snippet:
                    nested_parts.append(name)
            nested = "|".join(dict.fromkeys(nested_parts))
            std = infer_standard_layout(outer, nested)
            layouts.append(
                {
                    "lesson": lesson_num,
                    "kanji": parent,
                    "outer_html": outer,
                    "nested": nested,
                    "standard": std,
                }
            )

        for m in re.finditer(
            r'<span\s+class="kanji-part[^"]*">([^<]+)</span>', block
        ):
            sym = m.group(1).strip()
            if sym:
                # Look backward for wrapping future-kanji-link anchor
                before = block[max(0, m.start() - 400) : m.start()]
                future = "future-kanji-link" in before and "<a " in before
                components.append((sym, parent, future))

        # outer-kanji / inner without kanji-part class
        for m in re.finditer(r'class="outer-kanji">\s*([^<]+)', block):
            sym = m.group(1).strip()
            if sym:
                components.append((sym, parent, False))
        for m in re.finditer(r'class="inner-kanji">\s*([^<]+)', block):
            sym = m.group(1).strip()
            if sym:
                components.append((sym, parent, False))
        for m in re.finditer(r'enclosure-part">\s*([^<]+)', block):
            sym = m.group(1).strip()
            if sym:
                components.append((sym, parent, False))
        for m in re.finditer(
            r'<div\s+class="enclosure-inner"[^>]*>\s*<span[^>]*>([^<]+)</span>',
            block,
        ):
            sym = m.group(1).strip()
            if sym:
                components.append((sym, parent, False))

    return layouts, components


def load_lesson_numbers() -> dict[str, int]:
    out: dict[str, int] = {}
    if not LESSON_NUMBERS.exists():
        return out
    with open(LESSON_NUMBERS, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = row.get("kanji", "").strip()
            ln = row.get("lesson_number", "").strip()
            if k and ln:
                try:
                    out[k] = int(ln)
                except ValueError:
                    pass
    return out


def parse_lesson_range(start: str, end: str) -> int | None:
    """Best-effort lesson from lesson_start (often joyo band, not lesson)."""
    m = re.match(r"(\d+)", (start or "").replace("–", "-"))
    if not m:
        return None
    # Heisig book: 20 kanji/lesson by index in production file is authoritative;
    # joyo bands like 41-60 do NOT map to lesson 3 — return None here.
    return None


def csv_layout_to_std(raw: str) -> str:
    if not raw:
        return ""
    raw = raw.strip().lower()
    if raw in STD_LAYOUTS:
        return raw
    return CSV_LAYOUT_MAP.get(raw, "")


def classify_primitive_status(
    sym: str,
    master_kanji: set[str],
    use_count: int,
    is_future: bool,
) -> str:
    if sym in master_kanji:
        return "verified"
    if is_future:
        return "hidden_component"
    if is_kanji_like(sym) and use_count >= 1:
        return "hidden_component"
    if not is_kanji_like(sym):
        return "primitive_only"
    return "unresolved"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lesson_num_by_kanji = load_lesson_numbers()

    # --- Scan lessons 1-22 ---
    all_layouts: list[dict] = []
    all_components: list[tuple[str, str, bool, int]] = []

    for n in LESSON_RANGE:
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if not path.exists():
            continue
        layouts, comps = regex_harvest_lesson(path, n)
        all_layouts.extend(layouts)
        for sym, parent, fut in comps:
            sym = sym.strip()
            if sym:
                all_components.append((sym, parent, fut, n))

    # --- Load kanji master ---
    master_rows: list[dict] = []
    master_kanji: set[str] = set()
    whitespace_kanji: list[str] = []
    with open(KANJI_MASTER, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            master_rows.append(row)
            raw_k = row.get("kanji") or ""
            k = raw_k.strip()
            if k:
                master_kanji.add(k)
            if raw_k and raw_k != k:
                whitespace_kanji.append(repr(raw_k))

    # --- Primitive harvest ---
    primitives: dict[str, ComponentUse] = {}

    def register_primitive(
        sym: str,
        *,
        label: str = "",
        lesson: int | None = None,
        parent: str = "",
        source: str = "",
        future: bool = False,
    ) -> None:
        sym = sym.strip()
        if not sym:
            return
        if sym not in primitives:
            primitives[sym] = ComponentUse(symbol=sym)
        pu = primitives[sym]
        if label:
            pu.labels.add(label)
        if source:
            pu.sources.add(source)
        if future:
            pu.is_future_link = True
        if parent:
            pu.parent_kanji.add(parent)
        if lesson is not None:
            if pu.first_lesson is None or lesson < pu.first_lesson:
                pu.first_lesson = lesson
                pu.first_kanji = parent
                pu.first_use = f"lesson_{lesson:02d}"

    for sym, parent, fut, lesson in all_components:
        register_primitive(
            sym, lesson=lesson, parent=parent, source="html", future=fut
        )

    for row in master_rows:
        parent = (row.get("kanji") or "").strip()
        ln = lesson_num_by_kanji.get(parent)
        for field in ("kml_primitives", "cluster_components"):
            raw = (row.get(field) or "").strip()
            if not raw:
                continue
            for part in raw.split("|"):
                part = part.strip()
                if part:
                    register_primitive(
                        part,
                        lesson=ln,
                        parent=parent,
                        source=f"csv:{field}",
                    )

    # --- Layout audit stats ---
    outer_counter = Counter(r["outer_html"] for r in all_layouts)
    std_counter = Counter(r["standard"] for r in all_layouts if r["standard"])
    nested_counter = Counter()
    for r in all_layouts:
        for part in r["nested"].split("|"):
            if part:
                nested_counter[part] += 1

    csv_layout_counter = Counter()
    for row in master_rows:
        lt = (row.get("layout_type") or "").strip() or "(empty)"
        csv_layout_counter[lt] += 1

    # --- Missing reusable kanji (actual kanji used as components, not in master) ---
    missing_kanji: list[dict] = []
    future_linked_in_master: list[dict] = []
    for sym, pu in sorted(primitives.items()):
        if len(sym) != 1:
            continue
        if not is_kanji_like(sym):
            continue
        if sym in master_kanji:
            if pu.is_future_link:
                future_linked_in_master.append(
                    {
                        "kanji": sym,
                        "first_lesson": pu.first_lesson,
                        "first_parent": pu.first_kanji,
                        "note": "in master; used with future-kanji-link in HTML",
                    }
                )
            continue
        missing_kanji.append(
            {
                "kanji": sym,
                "first_lesson": pu.first_lesson or "",
                "first_parent": pu.first_kanji,
                "parent_count": len(pu.parent_kanji),
                "parents": ";".join(sorted(pu.parent_kanji)[:8]),
                "future_link": pu.is_future_link,
                "sources": ";".join(sorted(pu.sources)),
            }
        )

    # --- Write layout_audit_report.txt ---
    report_lines = [
        "KML STRUCTURE AUDIT — PASS 1",
        "=" * 60,
        "",
        "SCOPE: Lessons 1–22 HTML + kanji_master_with_components.csv",
        "MODE: Audit only (no rewrites)",
        "",
        "## 1. OUTER LAYOUT CLASSES (HTML, lessons 1–22)",
        "",
    ]
    for name, count in outer_counter.most_common():
        tier, std_hint = OUTER_LAYOUT_MAP.get(name, ("unknown", ""))
        report_lines.append(
            f"  {count:4d}  {name:28s}  tier={tier:10s}  std_hint={std_hint or '—'}"
        )

    report_lines += [
        "",
        "## 2. INFERRED STANDARD LAYOUT CODES (from HTML)",
        "",
    ]
    for code, count in std_counter.most_common():
        report_lines.append(f"  {count:4d}  {code}")

    report_lines += [
        "",
        "## 3. NESTED LAYOUT HELPERS (HTML)",
        "",
    ]
    for name, count in nested_counter.most_common():
        tier = "legacy" if name.startswith("component-") else "preferred"
        report_lines.append(f"  {count:4d}  {name:28s}  tier={tier}")

    report_lines += [
        "",
        "## 4. CSV layout_type VALUES (full master)",
        "",
    ]
    for name, count in csv_layout_counter.most_common():
        mapped = csv_layout_to_std(name if name != "(empty)" else "")
        report_lines.append(
            f"  {count:4d}  {name:20s}  -> std '{mapped or '—'}'"
        )

    report_lines += [
        "",
        "## 5. LEGACY / DUPLICATE NAMING",
        "",
        "Assume kanji-* preferred over component-*.",
        "",
    ]
    for legacy, preferred in LEGACY_PAIRS:
        lc = nested_counter.get(legacy.split("-")[0] + "-" + legacy.split("-")[1], 0)
        # count from nested and outer
        leg_count = sum(
            1
            for r in all_layouts
            if legacy in r["outer_html"] or legacy in r["nested"]
        )
        pref_count = sum(
            1
            for r in all_layouts
            if preferred.split()[0] in r["nested"]
            or preferred.split()[0] in r["outer_html"]
        )
        report_lines.append(
            f"  {legacy:24s}  html_uses={leg_count:3d}   preferred: {preferred}"
        )

    report_lines += [
        "",
        "## 6. PREFERRED vs LEGACY OUTER SYSTEMS",
        "",
        "Preferred (newer): stack-vertical, stack-horizontal, kanji-composite,",
        "  enclosure-layout, anchor-box",
        "Legacy: composite-horizontal, composite-vertical, component-horizontal",
        "",
    ]
    pref_outer = sum(
        c for n, c in outer_counter.items() if OUTER_LAYOUT_MAP.get(n, ("", ""))[0] == "preferred"
    )
    leg_outer = sum(
        c for n, c in outer_counter.items() if OUTER_LAYOUT_MAP.get(n, ("", ""))[0] == "legacy"
    )
    unk_outer = sum(c for n, c in outer_counter.items() if n not in OUTER_LAYOUT_MAP)
    report_lines.append(f"  preferred outer layouts: {pref_outer}")
    report_lines.append(f"  legacy outer layouts:    {leg_outer}")
    report_lines.append(f"  unmapped outer layouts:  {unk_outer}")

    report_lines += [
        "",
        "## 7. INCONSISTENCIES (HTML std vs CSV std, lessons 1–22 only)",
        "",
    ]
    html_by_kanji = defaultdict(list)
    for r in all_layouts:
        if r["kanji"]:
            html_by_kanji[r["kanji"]].append(r["standard"])

    mismatches = 0
    for row in master_rows:
        k = (row.get("kanji") or "").strip()
        ln = lesson_num_by_kanji.get(k)
        if not ln or ln > 22:
            continue
        csv_std = csv_layout_to_std((row.get("layout_type") or "").strip())
        html_stds = [s for s in html_by_kanji.get(k, []) if s]
        if not html_stds:
            continue
        html_std = html_stds[0]
        if csv_std and html_std and csv_std != html_std:
            mismatches += 1
            if mismatches <= 40:
                report_lines.append(
                    f"  {k} (L{ln}): csv={csv_std} html={html_std} "
                    f"outer={all_layouts[0]['outer_html'] if all_layouts else '?'}"
                )
    report_lines.append(f"  Total mismatches (capped listing at 40): {mismatches}")

    report_lines += [
        "",
        "## 8. DATA QUALITY (kanji_master)",
        "",
    ]
    if whitespace_kanji:
        report_lines.append(
            f"  kanji fields with trailing/leading whitespace: {len(whitespace_kanji)}"
        )
        for w in whitespace_kanji[:10]:
            report_lines.append(f"    {w}")
    else:
        report_lines.append("  No whitespace anomalies in kanji column.")

    report_lines += [
        "",
        "## 9. STANDARD CODE LEGEND",
        "",
        "  a=anchor  v=vertical  h=horizontal  2l=two-left  2r=two-right",
        "  2t=two-top  2b=two-bottom  e=enclosure  ei=enclosure-inner",
        "",
    ]

    (OUT_DIR / "layout_audit_report.txt").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )

    # --- primitive_dictionary.csv ---
    prim_rows = []
    for sym in sorted(primitives.keys(), key=lambda s: (primitives[s].first_lesson or 999, s)):
        pu = primitives[sym]
        pref = sorted(pu.labels)[0] if pu.labels else ""
        alts = "|".join(sorted(pu.labels - {pref})) if pu.labels else ""
        status = classify_primitive_status(
            sym, master_kanji, len(pu.parent_kanji), pu.is_future_link
        )
        notes_parts = []
        if pu.is_future_link:
            notes_parts.append("future-kanji-link in HTML")
        if len(pu.parent_kanji) > 1:
            notes_parts.append(f"used in {len(pu.parent_kanji)} parents")
        if pu.sources:
            notes_parts.append("sources=" + ",".join(sorted(pu.sources)))
        prim_rows.append(
            {
                "symbol": sym,
                "preferred_name": pref,
                "alternate_name": alts,
                "first_use": pu.first_use,
                "first_kanji": pu.first_kanji,
                "status": status,
                "notes": "; ".join(notes_parts),
            }
        )

    with open(OUT_DIR / "primitive_dictionary.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "symbol",
                "preferred_name",
                "alternate_name",
                "first_use",
                "first_kanji",
                "status",
                "notes",
            ],
        )
        w.writeheader()
        w.writerows(prim_rows)

    # --- missing_reusable_kanji.txt ---
    miss_lines = [
        "IMPLIED REUSABLE KANJI — NOT IN kanji_master",
        "=" * 60,
        "PASS 1: report only; do not auto-add.",
        "",
    ]
    for item in sorted(missing_kanji, key=lambda x: (-x["parent_count"], x["kanji"])):
        miss_lines.append(
            f"{item['kanji']}\tparents={item['parent_count']}\t"
            f"first=L{item['first_lesson']}\tparent={item['first_parent']}\t"
            f"future_link={item['future_link']}\t{item['parents']}"
        )
    miss_lines += [
        "",
        "## IN MASTER BUT future-kanji-link IN LESSONS 1–22",
        "(taught later; linked early as reusable component)",
        "",
    ]
    for item in future_linked_in_master:
        miss_lines.append(
            f"{item['kanji']}\tL{item['first_lesson']}\tparent={item['first_parent']}\t{item['note']}"
        )
    miss_lines.append("")
    miss_lines.append(f"Missing from master (actual kanji): {len(missing_kanji)}")
    miss_lines.append(f"Future-linked but already in master: {len(future_linked_in_master)}")
    (OUT_DIR / "missing_reusable_kanji.txt").write_text(
        "\n".join(miss_lines) + "\n", encoding="utf-8"
    )

    # --- kanji_master_with_components.v2.csv ---
    v2_rows = []
    for row in master_rows:
        k = (row.get("kanji") or "").strip()
        ln = lesson_num_by_kanji.get(k, "")
        lt_raw = (row.get("layout_type") or "").strip()
        lt = csv_layout_to_std(lt_raw)
        notes = ""
        if lt_raw and lt_raw not in STD_LAYOUTS and lt_raw.lower() not in CSV_LAYOUT_MAP:
            notes = f"csv layout_type={lt_raw}"
        elif lt_raw == "unknown":
            notes = "layout_type unknown in source"
        # HTML override note for lessons 1-22
        if k in html_by_kanji and ln and int(ln) <= 22:
            hs = [s for s in html_by_kanji[k] if s]
            if hs and lt and hs[0] != lt:
                notes = (notes + "; " if notes else "") + f"html suggests {hs[0]}"

        v2_rows.append(
            {
                "kanji": k,
                "keyword": (row.get("keyword") or "").strip(),
                "lesson_number": ln,
                "kml_primitives": (row.get("kml_primitives") or "").strip(),
                "cluster_components": (row.get("cluster_components") or "").strip(),
                "collapse_to": (row.get("collapse_to") or "").strip(),
                "layout_type": lt,
                "first_use": "",
                "notes": notes,
            }
        )

    with open(OUT_DIR / "kanji_master_with_components.v2.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "kanji",
                "keyword",
                "lesson_number",
                "kml_primitives",
                "cluster_components",
                "collapse_to",
                "layout_type",
                "first_use",
                "notes",
            ],
        )
        w.writeheader()
        w.writerows(v2_rows)

    print("PASS 1 audit complete.")
    print(f"  Lessons scanned: {len(LESSON_RANGE)}")
    print(f"  HTML layout blocks: {len(all_layouts)}")
    print(f"  Unique primitives: {len(primitives)}")
    print(f"  Missing reusable kanji: {len(missing_kanji)}")
    print(f"  Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
