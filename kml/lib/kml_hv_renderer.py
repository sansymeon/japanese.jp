"""KML Phase-1 component renderer: nested Horizontal / Vertical only.

Recognition aid — not dictionary decomposition.
No enclosure, surround, or special structural categories.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Direction = Literal["horizontal", "vertical"]


@dataclass
class Part:
    glyph: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "part", "glyph": self.glyph}


@dataclass
class Group:
    direction: Direction
    children: list[Part | Group] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.direction,
            "children": [c.to_dict() for c in self.children],
        }


Node = Part | Group


def render_node(node: Node, indent: int = 0) -> str:
    """Render a Phase-1 tree to HTML (horizontal / vertical / part only)."""
    pad = "  " * indent
    if isinstance(node, Part):
        return f'{pad}<span class="kml-part">{_esc(node.glyph)}</span>'

    cls = f"kml-group {node.direction}"
    inner = "\n".join(render_node(c, indent + 1) for c in node.children)
    return (
        f'{pad}<div class="{cls}">\n'
        f"{inner}\n"
        f"{pad}</div>"
    )


def render_box(node: Node | None, *, single_glyph: str | None = None) -> str:
    """Wrap a tree (or single glyph anchor) in component-box."""
    if node is None:
        if not single_glyph:
            return '<div class="component-box"></div>'
        inner = f'  <span class="kml-part">{_esc(single_glyph)}</span>'
    else:
        inner = render_node(node, indent=1)
    return f'<div class="component-box">\n{inner}\n</div>'


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# Layout tokens that mean horizontal / vertical in lesson HTML
_H = frozenset(
    {
        "horizontal",
        "stack-horizontal",
        "composite-horizontal",
        "component-horizontal",
    }
)
_V = frozenset(
    {
        "vertical",
        "stack-vertical",
        "composite-vertical",
    }
)
_LEGACY = frozenset(
    {
        "enclosure-layout",
        "anchor-box",
        "kanji-composite",
        "horizontal-layout",
    }
)


def tree_from_parser_node(node: Any) -> tuple[Node | None, list[str]]:
    """Convert html_component_parser tree → Phase-1 H/V tree.

    Returns (tree, issues). Issues non-empty means human edit still needed;
    we do not invent enclosure→H/V mappings.
    """
    issues: list[str] = []

    # PartNode
    if hasattr(node, "glyph") and not hasattr(node, "children"):
        return Part(glyph=node.glyph), issues

    # LayoutNode
    layout = getattr(node, "layout", "") or ""
    children = list(getattr(node, "children", []) or [])

    if layout in _LEGACY or layout == "enclosure-layout":
        if layout == "anchor-box" and len(children) == 1:
            return tree_from_parser_node(children[0])
        issues.append(f"legacy_layout:{layout}")
        return None, issues

    # Unwrap regions / component-box wrappers
    if layout in ("region", "component-box", ""):
        if len(children) == 1:
            return tree_from_parser_node(children[0])
        # Multiple siblings without direction → ambiguous
        if not children:
            return None, issues
        issues.append("undirected_siblings")
        return None, issues

    direction: Direction | None = None
    if layout in _H:
        direction = "horizontal"
    elif layout in _V:
        direction = "vertical"
    elif layout == "kanji-composite":
        # Left/right composite is horizontal grouping of regions —
        # only accept if children are plain H/V/parts (no enclosure).
        direction = "horizontal"
    else:
        issues.append(f"unsupported_layout:{layout}")
        return None, issues

    out_children: list[Node] = []
    for ch in children:
        sub, sub_issues = tree_from_parser_node(ch)
        issues.extend(sub_issues)
        if sub is None:
            continue
        # Flatten undirected single-child wrappers already handled
        out_children.append(sub)

    if issues and any(i.startswith("legacy_") or i.startswith("unsupported_") for i in issues):
        return None, issues

    if not out_children:
        return None, issues or ["empty_group"]

    if len(out_children) == 1 and direction:
        # Single child in a group — keep as-is (still valid)
        return Group(direction=direction, children=out_children), issues

    return Group(direction=direction, children=out_children), issues


def outline(node: Node, indent: int = 0) -> str:
    """Plain-text outline for rapid human review."""
    pad = "  " * indent
    if isinstance(node, Part):
        return f"{pad}{node.glyph}"
    label = "Horizontal" if node.direction == "horizontal" else "Vertical"
    lines = [f"{pad}{label}"]
    for c in node.children:
        lines.append(outline(c, indent + 1))
    return "\n".join(lines)
