#!/usr/bin/env python3
"""
KML component render engine — structure DATA separated from lesson HTML.

Renders component-box HTML from kanji_master rows + layout templates.
Supports manual overrides; does not assume all lessons will be auto-generated.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE_DIR = BASE / "templates" / "layouts"
PART_TEMPLATE = DEFAULT_TEMPLATE_DIR / "_part.html"

LAYOUT_TEMPLATE_MAP = {
    "a": "anchor.html",
    "h": "horizontal.html",
    "v": "vertical.html",
    "2l": "2l.html",
    "2r": "2r.html",
    "2t": "2t.html",
    "2b": "2b.html",
    "e": "enclosure.html",
    "ei": "enclosure_inner.html",
    "3r": "3r.html",
}

MANUAL_OVERRIDE_MARKERS = (
    "render_override=manual",
    "handcrafted_only",
    "manual_override",
)


@dataclass
class RenderResult:
    kanji: str
    layout_type: str
    html: str
    parts: list[str]
    status: str  # ok | incomplete | skipped_override | unsupported | error
    message: str = ""


@dataclass
class RenderEngineConfig:
    template_dir: Path = DEFAULT_TEMPLATE_DIR
    visibility_default: str = "visible"
    allow_hidden_links: bool = False
    hidden_kanji: set[str] = field(default_factory=set)
    family_by_symbol: dict[str, str] = field(default_factory=dict)
    glossary_hub_symbols: set[str] = field(default_factory=set)


class ComponentRenderEngine:
    """CSV-driven component-box renderer with override support."""

    def __init__(
        self,
        config: RenderEngineConfig | None = None,
        master_by_kanji: dict[str, dict] | None = None,
    ) -> None:
        self.config = config or RenderEngineConfig()
        self.template_dir = self.config.template_dir
        self._part_tpl = (self.template_dir / "_part.html").read_text(encoding="utf-8")
        self._layout_cache: dict[str, str] = {}
        self.master_by_kanji = master_by_kanji or {}

    @classmethod
    def from_csv(
        cls,
        csv_path: Path,
        *,
        config: RenderEngineConfig | None = None,
    ) -> ComponentRenderEngine:
        rows: dict[str, dict] = {}
        hidden: set[str] = set()
        with open(csv_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                k = (row.get("kanji") or "").strip()
                if k:
                    rows[k] = row
                    notes = (row.get("notes") or "").lower()
                    if "hidden_reusable" in notes:
                        hidden.add(k)
        cfg = config or RenderEngineConfig()
        cfg.hidden_kanji = cfg.hidden_kanji | hidden
        return cls(config=cfg, master_by_kanji=rows)

    def _layout_template(self, layout: str) -> str:
        if layout not in LAYOUT_TEMPLATE_MAP:
            raise KeyError(layout)
        if layout not in self._layout_cache:
            path = self.template_dir / LAYOUT_TEMPLATE_MAP[layout]
            self._layout_cache[layout] = path.read_text(encoding="utf-8")
        return self._layout_cache[layout]

    def should_skip_auto_render(self, row: dict) -> bool:
        notes = (row.get("notes") or "").lower()
        return any(m in notes for m in MANUAL_OVERRIDE_MARKERS)

    def resolve_parts(self, row: dict) -> list[str]:
        raw = (
            (row.get("kml_primitives") or "").strip()
            or (row.get("cluster_components") or "").strip()
        )
        if raw:
            return [p.strip() for p in raw.split("|") if p.strip()]

        collapse = (row.get("collapse_to") or "").strip()
        if collapse:
            return [collapse]

        layout = (row.get("layout_type") or "").strip()
        kanji = (row.get("kanji") or "").strip()
        if layout == "a" and kanji:
            return [kanji]
        return []

    def render_part(
        self,
        symbol: str,
        *,
        visibility: str | None = None,
        extra_class: str = "",
        href: str | None = None,
    ) -> str:
        vis = visibility or self.config.visibility_default
        html = (
            self._part_tpl.replace("{{SYMBOL}}", symbol)
            .replace("{{VISIBILITY}}", vis)
            .replace("{{EXTRA_CLASS}}", extra_class)
        )
        fam = self.config.family_by_symbol.get(symbol, "")
        if fam:
            html = html.replace(
                f'data-part="{symbol}"',
                f'data-part="{symbol}" data-family="{fam}"',
            )
        if symbol in self.config.glossary_hub_symbols:
            html = html.replace('class="kanji-part', 'class="kanji-part glossary-hub', 1)
        if href and self.config.allow_hidden_links:
            html = (
                f'<a href="{href}" class="future-kanji-link" '
                f'data-visibility="{vis}">\n      {html}\n    </a>'
            )
        return html

    def _render_parts_block(
        self, parts: list[str], indent: str = "    ", sep: str = "\n"
    ) -> str:
        lines = []
        for p in parts:
            extra = ""
            href = None
            if p in self.config.hidden_kanji and self.config.allow_hidden_links:
                meta = self.master_by_kanji.get(p, {})
                ln = meta.get("lesson_number", "").strip()
                kw = meta.get("keyword", "").strip() or p
                if ln:
                    href = f"../../book_01/lessons/lesson_{int(ln):02d}.html#kanji-{kw}"
            lines.append(
                indent
                + self.render_part(p, extra_class=extra, href=href).replace(
                    "\n", "\n" + indent
                )
            )
        return sep.join(lines)

    def _outer_enclosure_part(self, symbol: str) -> str:
        return (
            f'    <span class="kanji-part enclosure-part" '
            f'data-visibility="{self.config.visibility_default}" '
            f'data-part="{symbol}">{symbol}</span>'
        )

    def render(
        self,
        row: dict,
        *,
        override_html: str | None = None,
    ) -> RenderResult:
        kanji = (row.get("kanji") or "").strip()
        layout = (row.get("layout_type") or "").strip()

        if override_html is not None:
            return RenderResult(
                kanji=kanji,
                layout_type=layout,
                html=override_html,
                parts=self.resolve_parts(row),
                status="ok",
                message="manual override html",
            )

        if self.should_skip_auto_render(row):
            return RenderResult(
                kanji=kanji,
                layout_type=layout,
                html="",
                parts=[],
                status="skipped_override",
                message="row marked handcrafted / manual override",
            )

        if not layout:
            return RenderResult(
                kanji=kanji,
                layout_type="",
                html="",
                parts=[],
                status="unsupported",
                message="missing layout_type",
            )

        if layout not in LAYOUT_TEMPLATE_MAP:
            return RenderResult(
                kanji=kanji,
                layout_type=layout,
                html="",
                parts=[],
                status="unsupported",
                message=f"unknown layout_type: {layout}",
            )

        parts = self.resolve_parts(row)
        if not parts:
            return RenderResult(
                kanji=kanji,
                layout_type=layout,
                html=(
                    f'<!-- render:incomplete data-kanji="{kanji}" '
                    f'layout="{layout}" -->\n'
                ),
                parts=[],
                status="incomplete",
                message="no kml_primitives / cluster_components",
            )

        try:
            html = self._render_layout(layout, parts, kanji=kanji)
        except (ValueError, KeyError) as e:
            return RenderResult(
                kanji=kanji,
                layout_type=layout,
                html="",
                parts=parts,
                status="error",
                message=str(e),
            )

        return RenderResult(
            kanji=kanji,
            layout_type=layout,
            html=html,
            parts=parts,
            status="ok",
        )

    def _render_layout(self, layout: str, parts: list[str], *, kanji: str = "") -> str:
        tpl = self._layout_template(layout)

        if layout == "a":
            # Anchor = single focal component (whole kanji), not missing decomposition
            focal = parts[0] if len(parts) == 1 else (kanji or parts[0])
            block = self._render_parts_block([focal])
            return tpl.replace("{{PARTS}}", block)

        if layout in ("h", "v"):
            return tpl.replace("{{PARTS}}", self._render_parts_block(parts))

        if layout == "2l":
            if len(parts) < 2:
                raise ValueError("2l requires at least 2 parts")
            left, right = parts[:-1], [parts[-1]]
            return (
                tpl.replace("{{LEFT_PARTS}}", self._render_parts_block(left))
                .replace("{{RIGHT_PARTS}}", self._render_parts_block(right))
            )

        if layout == "2r":
            if len(parts) < 2:
                raise ValueError("2r requires at least 2 parts")
            left, right = [parts[0]], parts[1:]
            return (
                tpl.replace("{{LEFT_PARTS}}", self._render_parts_block(left))
                .replace("{{RIGHT_PARTS}}", self._render_parts_block(right))
            )

        if layout == "2t":
            if len(parts) < 2:
                raise ValueError("2t requires at least 2 parts")
            top, bottom = parts[:-1], [parts[-1]]
            return (
                tpl.replace("{{TOP_PARTS}}", self._render_parts_block(top))
                .replace("{{BOTTOM_PARTS}}", self._render_parts_block(bottom))
            )

        if layout == "2b":
            if len(parts) < 2:
                raise ValueError("2b requires at least 2 parts")
            top, bottom = [parts[0]], parts[1:]
            return (
                tpl.replace("{{TOP_PARTS}}", self._render_parts_block(top))
                .replace("{{BOTTOM_PARTS}}", self._render_parts_block(bottom))
            )

        if layout == "e":
            return tpl.replace("{{OUTER_PART}}", self._outer_enclosure_part(parts[0]))

        if layout == "ei":
            if len(parts) < 2:
                raise ValueError("ei requires outer + inner parts")
            return tpl.replace("{{OUTER_PART}}", self._outer_enclosure_part(parts[0])).replace(
                "{{INNER_PART}}", "      " + self.render_part(parts[1])
            )

        if layout == "3r":
            if len(parts) < 4:
                raise ValueError("3r requires 4 parts (left anchor + 3 vertical)")
            left = self._render_parts_block([parts[0]], indent="      ", sep="\n")
            right = self._render_parts_block(parts[1:4], indent="      ", sep="\n")
            return tpl.replace("{{LEFT_PART}}", left).replace("{{RIGHT_PARTS}}", right)

        raise KeyError(layout)


# --- HTML comparison helpers (validation) ---

BOX_RE = re.compile(
    r'<div\s+class="component-box"[^>]*>(.*?)</div>\s*(?=\n</div>|\n</section>|$)',
    re.DOTALL,
)

LAYOUT_RE = re.compile(r'component-layout\s+([^"]+)"')
PART_RE = re.compile(
    r'<span\s+class="kanji-part"[^>]*>([^<]+)</span>|'
    r'<span\s+class="kanji-part\s+enclosure-part"[^>]*>([^<]+)</span>|'
    r'class="(?:outer-kanji|inner-kanji)"[^>]*>\s*([^<]+)'
)


def normalize_component_box(html: str) -> tuple[str, tuple[str, ...]]:
    """Fingerprint: (layout_code_or_outer, part symbols in order)."""
    if not html:
        return ("", ())
    m = LAYOUT_RE.search(html)
    outer_raw = m.group(1).strip() if m else ""
    outer_tokens = outer_raw.split()
    outer = outer_tokens[0] if outer_tokens else ""

    layout_code = ""
    if "anchor-box" in outer_raw:
        layout_code = "a"
    elif "stack-horizontal" in outer_raw and "kanji-composite" not in outer_raw:
        layout_code = "h"
    elif "stack-vertical" in outer_raw and "kanji-composite" not in outer_raw:
        if "stack-horizontal" in html:
            first_h = html.find("stack-horizontal")
            first_p = html.find("kanji-part")
            layout_code = "2t" if first_h < first_p else "2b"
        else:
            layout_code = "v"
    elif "kanji-composite" in outer_raw or "component-horizontal" in outer_raw:
        if "kanji-left" in html or "component-left" in html:
            left_v = "stack-vertical" in html.split("kanji-right")[0] + html.split(
                "component-right"
            )[0] if "kanji-right" in html else html
            if "kanji-left" in html:
                left_chunk = html.split("kanji-left", 1)[1].split("kanji-right", 1)[0]
            else:
                left_chunk = html.split("component-left", 1)[1].split(
                    "component-right", 1
                )[0]
            right_chunk = (
                html.split("kanji-right", 1)[1]
                if "kanji-right" in html
                else html.split("component-right", 1)[1]
            )
            lv = "stack-vertical" in left_chunk or left_chunk.count("kanji-part") > 1
            rv = "stack-vertical" in right_chunk or right_chunk.count("kanji-part") > 1
            if not lv and rv:
                layout_code = "2r"
            elif lv and not rv:
                layout_code = "2l"
            else:
                layout_code = "h"
        else:
            layout_code = "h"
    elif "enclosure-layout" in outer_raw:
        layout_code = "ei" if "enclosure-inner" in html or "inner-kanji" in html else "e"
    elif "composite-horizontal" in outer_raw:
        layout_code = "h"
    elif "composite-vertical" in outer_raw:
        layout_code = "2t"

    parts: list[str] = []
    for m in PART_RE.finditer(html):
        sym = next((g for g in m.groups() if g), "").strip()
        if sym:
            parts.append(sym)
    return (layout_code or outer, tuple(parts))


def extract_handcrafted_box(section_html: str) -> str:
    m = re.search(
        r'<div\s+class="component-box"[^>]*>.*',
        section_html,
        re.DOTALL,
    )
    if not m:
        return ""
    chunk = m.group(0)
    # clip at section end
    end = chunk.find("</section>")
    if end != -1:
        chunk = chunk[:end]
    return chunk.strip()


def compare_boxes(generated: str, handcrafted: str, csv_layout: str) -> dict:
    gen_fp = normalize_component_box(generated)
    hand_fp = normalize_component_box(handcrafted)
    layout_match = gen_fp[0] == hand_fp[0] == csv_layout or (
        gen_fp[0] == csv_layout and hand_fp[0] == csv_layout
    )
    parts_match = gen_fp[1] == hand_fp[1]
    return {
        "csv_layout": csv_layout,
        "gen_layout": gen_fp[0],
        "hand_layout": hand_fp[0],
        "gen_parts": gen_fp[1],
        "hand_parts": hand_fp[1],
        "layout_match": layout_match,
        "parts_match": parts_match,
        "match": layout_match and parts_match,
    }
