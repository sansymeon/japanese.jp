"""KML Studio — local web app entry (stdlib HTTP + Jinja2).

Option A: Python standard library HTTP server.
No Flask/Django. Framework-agnostic handlers in handlers.py.
Publishing Engine stays independent; Studio calls publish.* APIs only.
"""

from __future__ import annotations

import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from publish import paths

from . import handlers, httputil


class StudioHandler(BaseHTTPRequestHandler):
    server_version = "KMLStudio/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[studio] {self.address_string()} {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802
        try:
            handlers.handle_get(self)
        except Exception:
            httputil.send(
                self,
                500,
                f"<pre>{traceback.format_exc()}</pre>".encode(),
            )

    def do_POST(self) -> None:  # noqa: N802
        try:
            handlers.handle_post(self)
        except Exception:
            httputil.send(
                self,
                500,
                f"<pre>{traceback.format_exc()}</pre>".encode(),
            )


def run(host: str = "127.0.0.1", port: int = 8787) -> None:
    server = ThreadingHTTPServer((host, port), StudioHandler)
    print(f"KML Studio → http://{host}:{port}/")
    print(f"Site root:  {paths.ROOT}")
    print("Stack:      stdlib http.server + Jinja2 (no web framework)")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()
