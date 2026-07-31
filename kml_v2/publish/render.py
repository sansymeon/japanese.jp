"""Jinja2 rendering — presentation only."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import paths
from .models import Book, Lesson


def _env(template_dir: Path | None = None) -> Environment:
    directory = template_dir or paths.TEMPLATES
    return Environment(
        loader=FileSystemLoader(str(directory)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_lesson_html(lesson: Lesson, template_dir: Path | None = None) -> str:
    env = _env(template_dir)
    template = env.get_template("lesson.html")
    return template.render(
        lesson=lesson,
        page_title=f"{lesson.title} — Kanji・Music・Landscape",
        site_root=lesson.site_root,
    )


def render_book_html(book: Book, template_dir: Path | None = None) -> str:
    env = _env(template_dir)
    template = env.get_template("book.html")
    return template.render(
        book=book,
        page_title=f"{book.title} — Kanji・Music・Landscape",
        site_root=book.site_root,
    )


def render_bookshelf_html(
    books: list[Book],
    template_dir: Path | None = None,
) -> str:
    env = _env(template_dir)
    template = env.get_template("bookshelf.html")
    return template.render(
        books=books,
        page_title="The Bookshelf — Kanji・Music・Landscape",
        site_root="..",
    )


def render_home_html(
    books: list[Book],
    template_dir: Path | None = None,
) -> str:
    env = _env(template_dir)
    template = env.get_template("home.html")
    return template.render(
        books=books,
        page_title="Kanji・Music・Landscape",
        site_root=".",
    )
