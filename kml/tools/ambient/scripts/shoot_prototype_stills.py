#!/usr/bin/env python3
"""Shoot full-resolution comparison stills for the prototype editions.

An 8-minute prototype has to be captured in real time, which is too slow to
iterate on typography. This drives the same engine and the same stylesheets,
freezes the presentation, then paints each step's phases directly and
screenshots them — so the pixels are production pixels, in seconds.

  # Everything: both editions × A/B/C × a representative set of slides
  python scripts/shoot_prototype_stills.py

  # Just the portrait typography versions, every slide
  python scripts/shoot_prototype_stills.py --editions mobile --all-steps

Output: collections/prototypes/stills/
  <edition>_<lab>__<NN>_<jp>_<phase>.png     individual frames
  compare_<edition>__<NN>_<jp>_<phase>.png   A | B | C side by side
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
OUT_DIR = ROOT / "collections" / "prototypes" / "stills"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import ensure_deps, load_collection, start_server, stop_server  # noqa: E402

VIEWPORTS = {
    "gallery": {"width": 1920, "height": 1080},
    "mobile": {"width": 1080, "height": 1920},
}

PHASES = ("furigana", "clean", "english")
PARTY_PHASES = ("shock", "reveal", "final")

# "x" means no typeLab param at all — the shipping look, as a control.
CONTROL_LAB = "x"

PRELOAD_FONTS = [
    '400 5rem "Noto Serif JP"',
    '500 5rem "Noto Serif JP"',
    '600 5rem "Noto Serif JP"',
    'italic 500 3rem "Cormorant Garamond"',
]

# Worst-case density, mid-range, and the simple-kanji control group.
DEFAULT_STEPS = (1, 2, 3, 7, 9, 14, 15, 18, 19, 21, 23)

FREEZE_JS = """
() => {
  const p = window.kmlExhibition;
  if (!p) return false;
  // Stall the running sequence at its next await so it stops touching the DOM.
  p.wait = () => new Promise(() => {});
  return true;
}
"""

PAINT_JS = """
({ step, phase }) => {
  const p = window.kmlExhibition;
  const root = document.querySelector('[data-exhibition-root]');
  root.classList.remove('is-initial-black', 'is-compound-reward', 'is-compound-celebration');
  p.setCompoundsStepContent(step);
  const jp = p.els.verseJp;
  const en = p.els.verseEn;
  jp.classList.add('is-visible');
  jp.classList.remove('is-furigana-entering', 'is-furigana-fading');
  jp.classList.toggle('is-furigana-hidden', phase !== 'furigana');
  en.classList.toggle('is-visible', phase === 'english');
  // The reading in 「」 only appears for steps without ruby; keep it consistent.
  jp.querySelector('.kml-compound-reading')?.classList.remove('is-visible');
}
"""

NO_MOTION_CSS = """
*, *::before, *::after {
  transition: none !important;
  animation: none !important;
}
.exhibition-loading, .exhibition-autoplay-gate { display: none !important; }
"""

# Party Kanji reveals its cells through keyframes, which NO_MOTION_CSS cancels —
# so the end state has to be asserted directly.
PARTY_SETTLE_CSS = """
.party-component-cell, .party-kanji-giant, .party-kanji-challenge, .party-kanji-equation {
  opacity: 1 !important;
  transform: none !important;
  filter: none !important;
  visibility: visible !important;
}
"""

PARTY_PAINT_JS = """
({ scene, phase }) => {
  const p = window.kmlExhibition;
  p.els.partyLayer?.classList.remove('exhibition-hidden');
  p.els.partyLayer?.removeAttribute('aria-hidden');
  p.populatePartyKanjiScene(scene);
  document.querySelectorAll('.party-kanji-phase').forEach(el => {
    el.classList.toggle('is-visible', el.dataset.partyPhase === phase);
  });
  p.els.partyChallenge?.classList.remove('party-kanji-challenge--hidden');
  p.els.partyEquation?.classList.remove('party-kanji-equation--hidden');
  document.querySelectorAll('.party-component-cell').forEach(el => el.classList.add('is-arrived'));
  p.els.partyComponentPulse?.classList.add('is-visible');
}
"""


def slug(text: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")


def shoot(*, collection_id: str, editions: list[str], labs: list[str], steps: list[int], port: int):
    from playwright.sync_api import sync_playwright

    collection = load_collection(ROOT, collection_id)
    is_party = (collection.get("display") or {}).get("exhibitProfile") == "partyKanji"
    typography = (collection.get("display") or {}).get("typography") or "mobile-refine"

    if is_party:
        scenes = collection["scenes"]
        chosen = [(i, scenes[i - 1]) for i in steps if 1 <= i <= len(scenes)]
        phases = PARTY_PHASES
        label = lambda scene: scene.get("kanji", "")  # noqa: E731
    else:
        all_steps = collection["scenes"][0]["compounds"]["steps"]
        chosen = [(i, all_steps[i - 1]) for i in steps if 1 <= i <= len(all_steps)]
        phases = PHASES
        label = lambda step: step["jp"]  # noqa: E731

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--autoplay-policy=no-user-gesture-required", "--disable-dev-shm-usage"],
        )
        for edition in editions:
            for lab in labs:
                query = f"collection={collection_id}&typography={typography}"
                if not is_party:
                    query += "&verseMode=sequential"
                else:
                    query += "&skipBookends=1"
                if lab != CONTROL_LAB:
                    query += f"&typeLab={lab}"
                if edition == "mobile":
                    query += "&edition=mobile"
                url = f"http://127.0.0.1:{port}/exhibition.html?{query}"

                context = browser.new_context(
                    viewport=VIEWPORTS[edition], color_scheme="dark"
                )
                page = context.new_page()
                page.goto(url, wait_until="load", timeout=120_000)
                page.wait_for_function("() => window.kmlExhibition", timeout=120_000)
                page.evaluate(
                    "specs => Promise.all(specs.map(s => document.fonts.load(s)))",
                    PRELOAD_FONTS,
                )
                page.wait_for_function(
                    "() => document.fonts && document.fonts.status === 'loaded'",
                    timeout=120_000,
                )
                page.evaluate(FREEZE_JS)
                page.add_style_tag(content=NO_MOTION_CSS)
                if is_party:
                    page.add_style_tag(content=PARTY_SETTLE_CSS)
                page.wait_for_timeout(250)

                for index, item in chosen:
                    for phase in phases:
                        if is_party:
                            page.evaluate(PARTY_PAINT_JS, {"scene": item, "phase": phase})
                        else:
                            page.evaluate(PAINT_JS, {"step": item, "phase": phase})
                        page.wait_for_timeout(60)
                        name = f"{edition}_{lab}__{index:02d}_{slug(label(item))}_{phase}.png"
                        path = OUT_DIR / name
                        page.screenshot(path=str(path))
                        written.append(path)

                context.close()
                print(f"  {edition} / version {lab.upper()}: {len(chosen) * len(phases)} frames")
        browser.close()

    return chosen, written, phases, label


# Where the word actually sits in each frame, for the detail crops.
CROPS = {
    "gallery": {"w": 980, "h": 520, "cy": 0.42},
    "mobile": {"w": 980, "h": 700, "cy": 0.47},
}


def contact_sheets(*, editions: list[str], labs: list[str], chosen, phases, label) -> None:
    """A | B | C side by side — whole frame, plus a 1:1 crop of the word itself.

    Downscaling a 5760px-wide sheet destroys exactly the stroke detail the
    comparison is about, so the crop is the one that answers the question.
    The crop geometry only makes sense for the single centred compound; Party
    Kanji compositions are full-height, so they get the whole-frame sheet only.
    """
    if len(labs) < 2:
        return
    detail = phases == PHASES
    for edition in editions:
        crop = CROPS[edition]
        for index, item in chosen:
            for phase in phases:
                inputs = [
                    OUT_DIR / f"{edition}_{lab}__{index:02d}_{slug(label(item))}_{phase}.png"
                    for lab in labs
                ]
                if not all(p.is_file() for p in inputs):
                    continue
                stem = f"{edition}__{index:02d}_{slug(label(item))}_{phase}"
                sheets = [("compare", f"hstack=inputs={len(inputs)}")]
                if detail:
                    crop_chain = ";".join(
                        f"[{i}:v]crop={crop['w']}:{crop['h']}:"
                        f"(iw-{crop['w']})/2:(ih*{crop['cy']})-{crop['h'] // 2}[c{i}]"
                        for i in range(len(inputs))
                    )
                    stack_in = "".join(f"[c{i}]" for i in range(len(inputs)))
                    sheets.append(
                        ("detail", f"{crop_chain};{stack_in}hstack=inputs={len(inputs)}")
                    )
                for prefix, filters in sheets:
                    cmd = ["ffmpeg", "-y"]
                    for path in inputs:
                        cmd += ["-i", str(path)]
                    cmd += ["-filter_complex", filters, str(OUT_DIR / f"{prefix}_{stem}.png")]
                    subprocess.run(
                        cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )


def write_index(*, collection_id, editions, labs, phases, chosen, label) -> None:
    """Manifest for prototype-editions.html, which flips between versions in place."""
    index_path = OUT_DIR / "index.json"
    existing = {}
    if index_path.is_file():
        existing = json.loads(index_path.read_text("utf-8"))
    existing[collection_id] = {
        "editions": editions,
        "labs": labs,
        "phases": list(phases),
        "frames": [
            {"index": index, "label": label(item), "slug": slug(label(item))}
            for index, item in chosen
        ],
    }
    index_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", "utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", default="proto_typography_lab")
    parser.add_argument("--editions", default="gallery,mobile")
    parser.add_argument("--labs", default="a,b,c")
    parser.add_argument("--steps", default=",".join(str(n) for n in DEFAULT_STEPS))
    parser.add_argument("--all-steps", action="store_true")
    parser.add_argument("--port", type=int, default=9402)
    parser.add_argument("--no-compare", action="store_true")
    args = parser.parse_args()

    ensure_deps()
    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    editions = [e.strip() for e in args.editions.split(",") if e.strip()]
    labs = [x.strip() for x in args.labs.split(",") if x.strip()]

    if args.all_steps:
        data = json.loads(
            (ROOT / "collections" / "prototypes" / f"{args.collection}.json").read_text("utf-8")
        )
        scene = data["scenes"][0]
        count = len(scene["compounds"]["steps"]) if "compounds" in scene else len(data["scenes"])
        steps = list(range(1, count + 1))
    else:
        steps = [int(n) for n in args.steps.split(",") if n.strip()]

    server = start_server(ROOT, args.port)
    try:
        chosen, written, phases, label = shoot(
            collection_id=args.collection,
            editions=editions,
            labs=labs,
            steps=steps,
            port=args.port,
        )
        if not args.no_compare:
            contact_sheets(
                editions=editions, labs=labs, chosen=chosen, phases=phases, label=label
            )
        write_index(
            collection_id=args.collection,
            editions=editions,
            labs=labs,
            phases=phases,
            chosen=chosen,
            label=label,
        )
    finally:
        stop_server(server)

    print(f"\n  {len(written)} stills → {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
