"""Request handlers — thin adapters over studio.services → publish engine.

No business logic here. Keep framework-agnostic so a future web stack
could call the same service functions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from publish import paths

from . import httputil, services, views

STATIC = views.STATIC


def handle_get(handler) -> None:
    parsed = urlparse(handler.path)
    path = parsed.path.rstrip("/") or "/"
    qs = parse_qs(parsed.query)

    if path.startswith("/static/"):
        return _static(handler, path)

    if path == "/":
        return _dashboard(handler, qs)

    m = re.fullmatch(r"/lessons/(lesson_\d+)", path)
    if m:
        return _lesson(handler, m.group(1), qs)

    if path == "/api/status":
        payload = json.dumps(services.dashboard(run_validate=False), default=str).encode()
        return httputil.send(handler, 200, payload, "application/json")

    httputil.send(handler, 404, b"Not found")


def handle_post(handler) -> None:
    parsed = urlparse(handler.path)
    path = parsed.path.rstrip("/") or "/"
    form = httputil.read_form(handler)

    if path == "/actions/create":
        lid = (form.get("lesson_id") or "").strip() or services.suggest_next_lesson_id()
        result = services.action_create(lid)
        flash = f"Created {lid}" if result["ok"] else f"Create failed ({result.get('code')})"
        target = f"/lessons/{lid}" if result["ok"] else "/"
        return httputil.flash_redirect(handler, target, flash)

    if path == "/actions/validate":
        lid = form.get("lesson_id", "").strip()
        result = services.action_validate(lid)
        flash = "Valid" if result["ok"] else f"Invalid ({len(result['errors'])} issues)"
        return httputil.flash_redirect(handler, f"/lessons/{lid}", flash)

    if path == "/actions/build-lesson":
        lid = form.get("lesson_id", "").strip()
        result = services.action_build_lesson(lid)
        flash = (
            f"Built {result.get('path')}"
            if result["ok"]
            else "Build failed: " + "; ".join(result.get("errors") or [])
        )
        return httputil.flash_redirect(handler, f"/lessons/{lid}", flash)

    if path == "/actions/build-book":
        bid = form.get("book_id", "book_01").strip()
        result = services.action_build_book(bid)
        flash = (
            f"Built {result.get('path')}"
            if result["ok"]
            else "Book build failed: " + "; ".join(result.get("errors") or [])
        )
        return httputil.flash_redirect(handler, "/", flash)

    if path == "/actions/build-site":
        result = services.action_build_site()
        flash = (
            "Site built: " + ", ".join(result.get("paths") or [])
            if result["ok"]
            else "Site build failed"
        )
        return httputil.flash_redirect(handler, "/", flash)

    if path == "/actions/build-all":
        result = services.action_build_all()
        flash = "Build all succeeded" if result["ok"] else "Build all finished with errors"
        return httputil.flash_redirect(handler, "/?validate=1", flash)

    httputil.send(handler, 404, b"Unknown action")


def _static(handler, path: str) -> None:
    rel = path[len("/static/") :]
    file_path = (STATIC / rel).resolve()
    if not str(file_path).startswith(str(STATIC.resolve())) or not file_path.is_file():
        httputil.send(handler, 404, b"Not found")
        return
    data = file_path.read_bytes()
    ctype = "text/css" if file_path.suffix == ".css" else "application/octet-stream"
    httputil.send(handler, 200, data, ctype)


def _dashboard(handler, qs: dict) -> None:
    validate = (qs.get("validate") or ["0"])[0] == "1"
    dash = services.dashboard(run_validate=validate)
    flash = (qs.get("flash") or [""])[0]
    body = views.render(
        "dashboard.html",
        dash=dash,
        flash=flash,
        next_id=services.suggest_next_lesson_id(),
        validate=validate,
        site_root=str(paths.ROOT),
    )
    httputil.send(handler, 200, body)


def _lesson(handler, lesson_id: str, qs: dict) -> None:
    try:
        detail = services.lesson_detail(lesson_id)
    except FileNotFoundError:
        httputil.send(handler, 404, b"Lesson not found")
        return
    flash = (qs.get("flash") or [""])[0]
    body = views.render("lesson.html", detail=detail, flash=flash)
    httputil.send(handler, 200, body)
