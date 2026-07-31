"""Studio UI rendering (Jinja2 — shared with Publishing Engine, no web framework)."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

STUDIO_ROOT = Path(__file__).resolve().parent
TEMPLATES = STUDIO_ROOT / "templates"
STATIC = STUDIO_ROOT / "static"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(name: str, **ctx) -> bytes:
    return _env.get_template(name).render(**ctx).encode("utf-8")
