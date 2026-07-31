"""HTTP helpers for the stdlib server (framework-agnostic)."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, quote


def send(
    handler: BaseHTTPRequestHandler,
    code: int,
    body: bytes,
    content_type: str = "text/html; charset=utf-8",
) -> None:
    handler.send_response(code)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def redirect(handler: BaseHTTPRequestHandler, location: str) -> None:
    handler.send_response(303)
    handler.send_header("Location", location)
    handler.end_headers()


def read_form(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    length = int(handler.headers.get("Content-Length", 0))
    raw = handler.rfile.read(length) if length else b""
    parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
    return {k: (v[0] if v else "") for k, v in parsed.items()}


def flash_redirect(handler: BaseHTTPRequestHandler, path: str, flash: str) -> None:
    sep = "&" if "?" in path else "?"
    redirect(handler, f"{path}{sep}flash={quote(flash)}")
