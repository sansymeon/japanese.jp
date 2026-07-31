"""python -m studio — start KML Studio (local-first web app)."""

from .app import run


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="KML Studio — local authoring control center (stdlib HTTP + Jinja2)"
    )
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8787)
    args = p.parse_args()
    run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
