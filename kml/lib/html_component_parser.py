"""Parse KML lesson HTML component-box trees.

Lesson HTML is the canonical source for decompositions and layout
relationships. This module preserves structure; it does not normalize
or invent parts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Outer / region class tokens we care about
LAYOUT_TYPES = frozenset(
    {
        "stack-horizontal",
        "stack-vertical",
        "enclosure-layout",
        "anchor-box",
        "kanji-composite",
        "composite-horizontal",
        "composite-vertical",
        "component-horizontal",
        "horizontal-layout",
    }
)

REGION_ROLES = (
    ("kanji-left", "left"),
    ("component-left", "left"),
    ("kanji-right", "right"),
    ("component-right", "right"),
    ("component-top", "top"),
    ("component-bottom", "bottom"),
    ("bottom-section", "bottom"),
    ("top-section", "top"),
    ("enclosure-inner", "inner"),
    ("enclosure-part", "enclosure"),
    ("inner-part", "inner"),
    ("outer-kanji", "enclosure"),
    ("inner-kanji", "inner"),
)


@dataclass
class PartNode:
    glyph: str
    role: str | None = None  # enclosure-part, etc.
    family: str | None = None
    visibility: str | None = None
    data_part: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": "part", "glyph": self.glyph}
        if self.role:
            d["role"] = self.role
        if self.family:
            d["family"] = self.family
        if self.visibility:
            d["visibility"] = self.visibility
        if self.data_part and self.data_part != self.glyph:
            d["dataPart"] = self.data_part
        return d


@dataclass
class LayoutNode:
    layout: str
    role: str | None = None
    children: list[PartNode | LayoutNode] = field(default_factory=list)
    render_layout: str | None = None  # data-render-layout on component-box

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": "layout",
            "layout": self.layout,
            "children": [c.to_dict() for c in self.children],
        }
        if self.role:
            d["role"] = self.role
        if self.render_layout:
            d["renderLayout"] = self.render_layout
        return d


@dataclass
class KanjiDecomposition:
    kanji: str
    keyword: str
    slug: str
    lesson: int
    tree: LayoutNode | PartNode | None
    parts_flat: list[str]
    layout_type: str
    layout_code: str
    render_layout: str | None
    has_box: bool
    source: str  # html | absent
    raw_box: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kanji": self.kanji,
            "keyword": self.keyword,
            "slug": self.slug,
            "lesson": self.lesson,
            "source": self.source,
            "hasBox": self.has_box,
            "layoutType": self.layout_type,
            "layoutCode": self.layout_code,
            "renderLayout": self.render_layout,
            "partsFlat": self.parts_flat,
            "tree": self.tree.to_dict() if self.tree else None,
            "notes": self.notes,
        }


def _attrs(tag_open: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in re.finditer(r'([^\s=]+)="([^"]*)"', tag_open):
        out[m.group(1)] = m.group(2)
    for m in re.finditer(r"([^\s=]+)='([^']*)'", tag_open):
        out.setdefault(m.group(1), m.group(2))
    return out


def _classes(tag_open: str) -> list[str]:
    return (_attrs(tag_open).get("class") or "").split()


def extract_balanced_div(html: str, start: int) -> tuple[str, int] | None:
    """Return (outer_html_including_div, end_index) for the div at start."""
    if not html.startswith("<div", start):
        m = re.search(r"<div\b", html[start:])
        if not m:
            return None
        start = start + m.start()

    i = start
    depth = 0
    while i < len(html):
        if html.startswith("<!--", i):
            end = html.find("-->", i + 4)
            i = len(html) if end < 0 else end + 3
            continue
        if html.startswith("</div>", i):
            depth -= 1
            i += 6
            if depth == 0:
                return html[start:i], i
            continue
        if html.startswith("<div", i) and (
            i + 4 >= len(html) or html[i + 4] in " \t\n\r>/"
        ):
            # opening or self-closing
            gt = html.find(">", i)
            if gt < 0:
                break
            if html[gt - 1] != "/":
                depth += 1
            i = gt + 1
            continue
        i += 1
    return None


def extract_component_box(section: str) -> tuple[str, str | None]:
    """Return (box_html, data-render-layout)."""
    m = re.search(r'<div\s+class="component-box[^"]*"[^>]*>', section)
    if not m:
        return "", None
    got = extract_balanced_div(section, m.start())
    if not got:
        # fallback: clip at section end
        chunk = section[m.start() :]
        end = chunk.find("</section>")
        if end >= 0:
            chunk = chunk[:end]
        attrs = _attrs(m.group(0))
        return chunk.strip(), attrs.get("data-render-layout")
    box, _ = got
    attrs = _attrs(m.group(0))
    return box.strip(), attrs.get("data-render-layout")


def _find_layout_token(classes: list[str]) -> str | None:
    for c in classes:
        if c in LAYOUT_TYPES:
            return c
    # e.g. "stack-horizontal top-section"
    for c in classes:
        base = c.split()[0] if " " in c else c
        if base in LAYOUT_TYPES:
            return base
    return None


def _region_role(classes: list[str]) -> str | None:
    joined = " ".join(classes)
    for token, role in REGION_ROLES:
        if token in classes or token in joined:
            return role
    return None


def _parse_nodes(html: str) -> list[PartNode | LayoutNode]:
    """Parse a fragment into a list of part/layout nodes (siblings)."""
    nodes: list[PartNode | LayoutNode] = []
    i = 0
    while i < len(html):
        if html.startswith("<!--", i):
            end = html.find("-->", i + 4)
            i = len(html) if end < 0 else end + 3
            continue

        # nested component-box
        if html.startswith("<div", i):
            gt = html.find(">", i)
            if gt < 0:
                break
            open_tag = html[i : gt + 1]
            classes = _classes(open_tag)

            if "component-box" in classes:
                got = extract_balanced_div(html, i)
                if not got:
                    break
                box, end = got
                inner = _strip_outer_div(box)
                children = _parse_nodes(inner)
                # unwrap single layout child
                if len(children) == 1:
                    nodes.append(children[0])
                elif children:
                    nodes.append(
                        LayoutNode(layout="component-box", children=children)
                    )
                i = end
                continue

            layout = _find_layout_token(classes)
            role = _region_role(classes)
            # region wrappers without layout token still matter
            if layout or role or any(
                c.startswith(("kanji-", "component-", "enclosure-", "bottom-", "top-", "inner-", "outer-"))
                for c in classes
            ):
                got = extract_balanced_div(html, i)
                if not got:
                    break
                block, end = got
                inner = _strip_outer_div(block)
                children = _parse_nodes(inner)

                # Some enclosure variants put the glyph as direct text in
                # div.enclosure-part / div.inner-part / div.kanji-part
                # (no span.kanji-part).
                if not children and (
                    role in ("enclosure", "inner") or "kanji-part" in classes
                ):
                    text = re.sub(r"<[^>]+>", "", inner).strip()
                    if text:
                        children = [
                            PartNode(
                                glyph=text,
                                role="enclosure" if role == "enclosure" else None,
                            )
                        ]

                layout_name = layout or (
                    next((c for c in classes if c in LAYOUT_TYPES), None)
                )
                # If region has stack-vertical in class list alongside role
                if not layout_name:
                    for c in classes:
                        if c in LAYOUT_TYPES:
                            layout_name = c
                            break
                    if "stack-vertical" in classes:
                        layout_name = "stack-vertical"
                    elif "stack-horizontal" in classes:
                        layout_name = "stack-horizontal"
                if layout_name or role or children:
                    nodes.append(
                        LayoutNode(
                            layout=layout_name or "region",
                            role=role,
                            children=children,
                        )
                    )
                else:
                    nodes.extend(children)
                i = end
                continue

            # unknown div — descend
            got = extract_balanced_div(html, i)
            if not got:
                i = gt + 1
                continue
            block, end = got
            inner = _strip_outer_div(block)
            nodes.extend(_parse_nodes(inner))
            i = end
            continue

        # kanji-part span
        if html.startswith("<span", i):
            gt = html.find(">", i)
            if gt < 0:
                break
            open_tag = html[i : gt + 1]
            classes = _classes(open_tag)
            attrs = _attrs(open_tag)
            close = html.find("</span>", gt + 1)
            if close < 0:
                break
            text = html[gt + 1 : close].strip()
            if "kanji-part" in classes and text:
                role = "enclosure" if "enclosure-part" in classes else None
                nodes.append(
                    PartNode(
                        glyph=text,
                        role=role,
                        family=attrs.get("data-family"),
                        visibility=attrs.get("data-visibility"),
                        data_part=attrs.get("data-part"),
                    )
                )
            i = close + len("</span>")
            continue

        # legacy outer/inner-kanji divs with direct text
        if html.startswith("<div", i):
            pass  # handled above

        i += 1
    return nodes


def _strip_outer_div(block: str) -> str:
    m = re.match(r"<div\b[^>]*>", block)
    if not m:
        return block
    if not block.endswith("</div>"):
        return block[m.end() :]
    return block[m.end() : -len("</div>")]


def flatten_parts(node: PartNode | LayoutNode | None) -> list[str]:
    if node is None:
        return []
    if isinstance(node, PartNode):
        return [node.glyph]
    out: list[str] = []
    for c in node.children:
        out.extend(flatten_parts(c))
    return out


def primary_layout_type(node: PartNode | LayoutNode | None) -> str:
    if node is None:
        return ""
    if isinstance(node, PartNode):
        return "anchor-box"
    if node.layout and node.layout not in ("region", "component-box"):
        return node.layout
    for c in node.children:
        if isinstance(c, LayoutNode):
            t = primary_layout_type(c)
            if t:
                return t
    return node.layout or ""


def layout_code_for(tree: PartNode | LayoutNode | None, render_layout: str | None) -> str:
    """Map tree + optional data-render-layout to a short layout code."""
    if render_layout:
        return render_layout
    if tree is None:
        return ""
    if isinstance(tree, PartNode):
        return "a"
    lt = primary_layout_type(tree)
    if lt == "anchor-box":
        return "a"
    if lt in ("stack-horizontal", "composite-horizontal", "component-horizontal"):
        return "h"
    if lt == "enclosure-layout":
        return "e"
    if lt in ("stack-vertical", "composite-vertical"):
        # detect 2t/2b from children roles
        roles = {c.role for c in tree.children if isinstance(c, LayoutNode)}
        if "top" in roles and "bottom" in roles:
            return "2t"
        if "bottom" in roles:
            return "2b"
        return "v"
    if lt == "kanji-composite":
        left = next(
            (
                c
                for c in tree.children
                if isinstance(c, LayoutNode) and c.role == "left"
            ),
            None,
        )
        right = next(
            (
                c
                for c in tree.children
                if isinstance(c, LayoutNode) and c.role == "right"
            ),
            None,
        )

        def side_vertical(n: LayoutNode | None) -> bool:
            if n is None:
                return False
            if n.layout == "stack-vertical":
                return True
            return len(flatten_parts(n)) > 1 and n.layout != "stack-horizontal"

        lv = side_vertical(left)
        rv = side_vertical(right)
        if not lv and rv:
            return "2r"
        if lv and not rv:
            return "2l"
        return "h"
    return lt[:8] if lt else ""


def parse_component_box(box: str, render_layout: str | None = None) -> LayoutNode | PartNode | None:
    if not box:
        return None
    # Prefer parsing inside the outer component-box
    if box.lstrip().startswith("<div"):
        inner = _strip_outer_div(box)
    else:
        inner = box
    children = _parse_nodes(inner)
    if not children:
        return None
    if len(children) == 1:
        node = children[0]
        if isinstance(node, LayoutNode) and render_layout:
            node.render_layout = render_layout
        return node
    return LayoutNode(
        layout="component-box",
        children=children,
        render_layout=render_layout,
    )


def parse_lesson_html(path: str | Any, lesson: int) -> list[KanjiDecomposition]:
    from pathlib import Path

    p = Path(path)
    return parse_lesson_text(p.read_text(encoding="utf-8"), lesson)


def parse_lesson_text(text: str, lesson: int) -> list[KanjiDecomposition]:
    out: list[KanjiDecomposition] = []
    # Split on kanji-entry sections
    for chunk in re.split(r'<section\s+class="kanji-entry"', text)[1:]:
        # attrs are before first '>'
        gt = chunk.find(">")
        if gt < 0:
            continue
        open_attrs = chunk[:gt]
        body = chunk[gt + 1 :]
        end = body.find("</section>")
        if end >= 0:
            body = body[:end]
        attrs = _attrs("<x " + open_attrs + ">")
        kanji = (attrs.get("data-kanji") or "").strip()
        slug = (attrs.get("data-slug") or "").strip()
        if not kanji:
            continue
        kw_m = re.search(
            r'<span class="kanji-keyword">([^<]+)</span>',
            body,
        )
        keyword = kw_m.group(1).strip() if kw_m else slug.replace("_", " ")

        box, render_layout = extract_component_box(body)
        notes: list[str] = []
        if not box:
            out.append(
                KanjiDecomposition(
                    kanji=kanji,
                    keyword=keyword,
                    slug=slug,
                    lesson=lesson,
                    tree=None,
                    parts_flat=[],
                    layout_type="",
                    layout_code="",
                    render_layout=None,
                    has_box=False,
                    source="absent",
                    notes=["no_component_box"],
                )
            )
            continue

        tree = parse_component_box(box, render_layout)
        parts = flatten_parts(tree)
        layout_type = primary_layout_type(tree)
        layout_code = layout_code_for(tree, render_layout)

        # Self-reference leftovers are placeholder scaffolding, not approved
        # editorial decompositions. True anchors (parts == [kanji]) are fine.
        if kanji in parts and len(parts) > 1:
            notes.append("placeholder_self_reference")
            if set(parts) == {kanji}:
                notes.append("placeholder_self_only")
        if not parts:
            notes.append("empty_parts")
        if box.count("component-layout") > 1:
            notes.append("nested_component_layout")

        out.append(
            KanjiDecomposition(
                kanji=kanji,
                keyword=keyword,
                slug=slug,
                lesson=lesson,
                tree=tree,
                parts_flat=parts,
                layout_type=layout_type,
                layout_code=layout_code,
                render_layout=render_layout,
                has_box=True,
                source="html",
                raw_box=box,
                notes=notes,
            )
        )
    return out
