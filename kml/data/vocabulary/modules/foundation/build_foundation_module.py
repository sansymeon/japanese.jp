#!/usr/bin/env python3
"""Build Foundation Vocabulary F1–F6 exhibition collections.

Reads foundation_module.json and writes vocabulary_f01.json … vocabulary_f06.json
beside the existing Vocabulary series. Does not touch vocabulary_01–22.

Scene artwork in live JSON must reference JPEG web derivatives
(images/vocabulary_N.jpg). PNG masters live in kml/assets/images_png/.
New stills: save the PNG master, then
`python3 kml/scripts/publish_web_jpeg.py kml/assets/images_png/<stem>.png`.

Does not require the master vocabulary database (optional if present on main).

Run: python3 kml/data/vocabulary/modules/foundation/build_foundation_module.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from foundation_context import CONTEXT, LEARNER_NOTE, expansions_for

REPO = HERE.parents[4]
SEED_PATH = HERE / "foundation_module.json"
LESSON_DIR = REPO / "kml/tools/ambient/collections/vocabulary"

SOUNDTRACK_MS = {
    # Start Here rooms 6–11 atmosphere group, each looped 4× to cover the exhibition.
    "audio/lesson-6.mp3": 766642,
    "audio/lesson-7.mp3": 798720,
    "audio/lesson-8.mp3": 716591,
    "audio/lesson-9.mp3": 794854,
    "audio/lesson-10.mp3": 769881,
    "audio/lesson-11.mp3": 753894,
}

RUBY_BW = {
    "言の葉": '<ruby>言<rt>こと</rt></ruby>の<ruby>葉<rt>は</rt></ruby>',
    "団欒": '<ruby>団<rt>だん</rt></ruby><ruby>欒<rt>らん</rt></ruby>',
    "灯火": '<ruby>灯<rt>ともし</rt></ruby><ruby>火<rt>び</rt></ruby>',
    "道草": '<ruby>道<rt>みち</rt></ruby><ruby>草<rt>くさ</rt></ruby>',
    "湯気": '<ruby>湯<rt>ゆ</rt></ruby><ruby>気<rt>げ</rt></ruby>',
    "空模様": '<ruby>空<rt>そら</rt></ruby><ruby>模<rt>も</rt></ruby><ruby>様<rt>よう</rt></ruby>',
}

EXHIBITION = {
    "artworkArrivalMs": 0,
    "artworkArrivalFadeMs": 2800,
    "artworkAloneMs": 1800,
    "exhibitionBlackBeforeMs": 0,
    "compoundsPauseBeforeMs": 3200,
    "compoundsStepRevealMs": 1400,
    "compoundsFuriganaEnterDelayMs": 900,
    "compoundsFuriganaEnterMs": 2200,
    "compoundsFuriganaHoldMs": 3000,
    "compoundsFuriganaFadeMs": 2200,
    "compoundsNativeHoldMs": 2200,
    "compoundsReadingRevealMs": 1200,
    "compoundsReadingHoldMs": 1800,
    "compoundsEnRevealMs": 1200,
    "compoundsEnHoldMs": 3500,
    "compoundsEnFadeMs": 1400,
    "compoundsStepFadeMs": 1400,
    "beautifulWordLabelRevealMs": 1600,
    "beautifulWordLabelHoldMs": 2200,
    "beautifulWordRevealMs": 1600,
    "beautifulWordFuriganaHoldMs": 4500,
    "beautifulWordNativeHoldMs": 3500,
    "beautifulWordEnHoldMs": 5000,
    "beautifulWordFadeMs": 1800,
    "vocabArtworkExhaleMs": 3500,
    "exhibitTransitionMs": 0,
    "kenBurnsDurationMs": 750000,
    "openingBlackBeforeMs": 3000,
    "openingRevealMs": 1800,
    "openingHoldMs": 0,
    "openingExhaleMs": 1800,
    "openingBlackAfterMs": 400,
    "openingSoundtrackDelayMs": 600,
    "closingBlackBeforeMs": 800,
    "closingRevealMs": 3200,
    "closingHoldMs": 2800,
    "closingExhaleMs": 3500,
    "closingSilenceHoldMs": 0,
    "closingBlackAfterMs": 800,
    "closingFadeToBlackMs": 3500,
    "blackHoldMs": 0,
}

# Target headwords are kana: no furigana choreography, no redundant reading beat.
TARGET_STEP_MS = (
    EXHIBITION["compoundsStepRevealMs"]
    + EXHIBITION["compoundsEnRevealMs"]
    + EXHIBITION["compoundsEnHoldMs"]
    + EXHIBITION["compoundsEnFadeMs"]
    + EXHIBITION["compoundsStepFadeMs"]
)
EXPOSURE_STEP_MS = (
    EXHIBITION["compoundsStepRevealMs"]
    + EXHIBITION["compoundsEnRevealMs"]
    + EXHIBITION["compoundsEnHoldMs"]
    + EXHIBITION["compoundsEnFadeMs"]
    + EXHIBITION["compoundsStepFadeMs"]
)

DISPLAY = {
    "loop": False,
    "hideChrome": True,
    "family": "japaneseVocabulary",
    "showKeyword": False,
    "showKanji": False,
    "showEnglish": True,
    "exhibitProfile": "japaneseVocabulary",
    "verseMode": "sequential",
    "typography": "mobile-refine",
    "typographyStyle": "foundations",
    "bookendStyle": "galleryCrest",
    "cameraMotionScale": 1.22,
}


RUBY_MARKUP = re.compile(r"\{([^|{}]+)\|([^|{}]+)\}")

# Spoken readings that should still wrap the same target lemma.
WRAP_ALIASES = {
    "なん": ("なに",),
}


def expand_markup(markup: str) -> tuple[str, str]:
    jp = RUBY_MARKUP.sub(lambda m: m.group(1), markup)
    html = RUBY_MARKUP.sub(
        lambda m: f"<ruby>{m.group(1)}<rt>{m.group(2)}</rt></ruby>", markup
    )
    html = html.replace("\n", "<br>")
    return jp, html


def wrap_target(html: str, target: str) -> str:
    """Keep the target lemma prominent inside contextual Japanese.

    If the lemma is absent, the HTML is returned unchanged so a
    target-linked reply or contrast line can still be exposure.
    """
    if not target or 'class="kml-target-word"' in html:
        return html
    spoken = []
    spans = []  # spoken index → (html_start, html_end)

    i = 0
    n = len(html)
    while i < n:
        if html.startswith("<ruby>", i):
            end = html.find("</ruby>", i)
            if end == -1:
                break
            end += len("</ruby>")
            rt = re.search(r"<rt>([^<]*)</rt>", html[i:end])
            reading = rt.group(1) if rt else ""
            for _ in reading:
                spans.append((i, end))
            spoken.append(reading)
            i = end
            continue
        if html[i] == "<":
            close = html.find(">", i)
            i = close + 1 if close != -1 else i + 1
            continue
        spoken.append(html[i])
        spans.append((i, i + 1))
        i += 1

    spoken_s = "".join(spoken)
    needles = (target,) + WRAP_ALIASES.get(target, ())
    matches: list[tuple[int, int]] = []
    search_from = 0
    while search_from < len(spoken_s):
        at = -1
        needle_len = 0
        for needle in needles:
            found = spoken_s.find(needle, search_from)
            if found == -1:
                continue
            if at == -1 or found < at:
                at = found
                needle_len = len(needle)
        if at == -1:
            break
        matches.append((at, needle_len))
        search_from = at + needle_len
    if not matches and len(target) >= 3 and target[-1] in "うくぐすつぬむるぶ":
        stem = target[:-1]
        at = spoken_s.find(stem)
        if at != -1:
            matches.append((at, len(stem)))
    if not matches:
        return html
    result = html
    for at, needle_len in reversed(matches):
        start = spans[at][0]
        end = spans[at + needle_len - 1][1]
        result = (
            result[:start]
            + f'<span class="kml-target-word">{result[start:end]}</span>'
            + result[end:]
        )
    return result


def target_step(it: dict) -> dict:
    jp = it["jp"]
    return {
        "jp": jp,
        "reading": it["reading"],
        "en": it["en"],
        "jpHtml": f'<span class="kml-target-word">{jp}</span>',
        "coverage": "target",
        "target": jp,
        "curriculumRole": it.get("role", "new"),
        "stop": "valid",
        "optional": False,
    }


def exposure_step(target_jp: str, ctx: dict) -> dict:
    if ctx.get("m"):
        jp, html = expand_markup(ctx["m"])
    else:
        jp = ctx["jp"]
        html = jp
    html = wrap_target(html, target_jp)
    step = {
        "jp": jp,
        "en": ctx["en"],
        "jpHtml": html,
        "coverage": "exposure",
        "target": target_jp,
        "containsTarget": 'class="kml-target-word"' in html,
        "source": ctx.get("source", "expansion"),
        "stop": "valid",
        "optional": True,
    }
    if ctx.get("startHere"):
        step["startHere"] = ctx["startHere"]
    return step


def estimate_runtime_ms(steps: list[dict]) -> int:
    total = 0
    for step in steps:
        if step.get("coverage") == "exposure":
            total += EXPOSURE_STEP_MS
        else:
            total += TARGET_STEP_MS
    return total


def build_collection(seed: dict, ldef: dict) -> dict:
    items = ldef["items"]
    if len(items) != 25:
        raise SystemExit(f"{ldef['collection_id']}: expected 25 items, got {len(items)}")
    bw = ldef["beautiful_word"]
    proverb = ldef["proverb"]
    track = ldef["soundtrack"]
    n = ldef["foundation_lesson"]
    cid = ldef["collection_id"]
    steps = []
    targets = []
    for it in items:
        targets.append(it["jp"])
        steps.append(target_step(it))
        for ctx in expansions_for(it["jp"]):
            steps.append(exposure_step(it["jp"], ctx))
    exposure_n = sum(1 for s in steps if s["coverage"] == "exposure")
    start_here_n = sum(1 for s in steps if s.get("source") == "start-here")
    bw_block = {
        "jp": bw["jp"],
        "jpHtml": RUBY_BW[bw["jp"]],
        "reading": bw["reading"],
        "en": bw["en"],
    }
    reviews = [it["jp"] for it in items if it.get("role") == "review"]
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": cid,
        "title": ldef["title"],
        "notes": (
            f"Japanese Vocabulary Foundation {n} — {ldef['module_title']} "
            f"(Everyday Spoken Japanese, Foundation module). Tea-ceremony intro on "
            f"vocabulary_intro.png: atmosphere → two-column 縦書き proverb → English "
            f"quotation, then lesson. {ldef['scene_theme']}. Beautiful Word "
            f"{bw['jp']}, hold until soundtrack ends → 漢 crest hold → fade out → cut. "
            f"Soundtrack: Start Here atmosphere group lesson-6–11 "
            f"({track.split('/')[-1]}, looped to exhibition length). "
            "Vocabulary in context: each target may be followed by short "
            "Japanese; each line is a valid stopping point. "
            f"{LEARNER_NOTE} "
            "Only coverage=target steps count as taught."
        ),
        "soundtrack": {"main": track},
        "bookends": {
            "mode": "silentCrest",
            "opening": {
                "image": "images/vocabulary_intro.png",
                "startSoundtrackWithImage": True,
                "startSoundtrackAfterImageMs": 600,
                "blackBeforeMs": 3000,
                "revealMs": 2000,
                "atmosphereHoldMs": 5000,
                "jp": proverb["jp"],
                "jpColumns": proverb["columns"],
                "jpRevealMs": 2600,
                "jpHoldMs": 5500,
                "jpFadeMs": 2200,
                "en": proverb["en"],
                "enRevealMs": 2600,
                "enHoldMs": 6000,
                "enFadeMs": 2200,
                "exhaleMs": 2200,
                "blackAfterMs": 600,
            },
            "closing": {
                "image": "images/gold_closing.png",
                "bookendSize": "small",
                "silentAfterSoundtrack": True,
            },
        },
        "beautifulWord": bw_block,
        "exhibition": EXHIBITION,
        "display": DISPLAY,
        "meta": {
            "series": "japanese_vocabulary",
            "curriculum": "japanese_vocabulary",
            "scope": "everyday_spoken_japanese",
            "lesson": ldef["lesson_label"],
            "foundationLesson": n,
            "stage": "vocabulary",
            "format": "spokenTheme",
            "presentation": "vocabulary_in_context",
            "module": "foundation",
            "moduleLesson": n,
            "moduleTitle": ldef["module_title"],
            "prototype": True,
            "sceneCount": 1,
            "compoundCount": 25,
            "targetCount": 25,
            "exposureCount": exposure_n,
            "exhibitCount": len(steps),
            "targetWords": targets,
            "coverageRule": (
                "Only steps with coverage=target receive vocabulary credit. "
                "coverage=exposure is contextual scaffolding (particles, "
                "supporting words, kanji, conjugations, Start Here phrases) "
                "and is not taught. Each step is a valid stopping point; "
                "later expansions are optional invitations. "
                "The bold target is the learner's responsibility; "
                "surrounding Japanese is an invitation and may preview "
                "forms that become targets later."
            ),
            "learnerNote": LEARNER_NOTE,
            "delivery": "interactive-json-exhibition",
            "recordingRole": "promotional-excerpts",
            "previewPrinciple": (
                "Foundation may seed useful Japanese for later recognition "
                "and later targeted study. Exposure never counts as taught."
            ),
            "weight": {
                "target": "prominent",
                "exposure": "regular",
            },
            "soundtrackDurationMs": SOUNDTRACK_MS[track],
            "estimatedContentRuntimeMs": estimate_runtime_ms(steps),
            "ending": "holdFinalSceneUntilSoundtrackEnds",
            "pendingAssets": [ldef["image"]],
            "note": (
                f"Foundation module lesson {n}/6 — everyday spoken Japanese. "
                f"Hiragana/katakana headwords. Does not collide with vocabulary_01–22. "
                f"Deliberate Start Here reviews: {'、'.join(reviews) if reviews else 'none'}. "
                f"Vocabulary in context: {exposure_n} exposure exhibits "
                f"({start_here_n} from Start Here wording). "
                "Ending: crest holds a few seconds after music, then fade out and cut."
            ),
        },
        "scenes": [
            {
                "id": ldef["scene_id"],
                "image": ldef["placeholder_image"],
                "galleryCamera": {
                    "motion": "pull-out",
                    "focus": "48% 58%",
                    "motionScale": 1.22,
                },
                "compounds": {"steps": steps},
                "beautifulWord": bw_block,
                "meta": {
                    "lesson": ldef["lesson_label"],
                    "module": "foundation",
                    "moduleTitle": ldef["module_title"],
                    "atmosphere": ldef["atmosphere"],
                    "prototype": True,
                    "theme": ldef["scene_theme"],
                    "reviewWords": reviews,
                    "targetWords": targets,
                    "targetCount": 25,
                    "exposureCount": exposure_n,
                    "coverageRule": "target vs exposure",
                },
            }
        ],
    }


def main() -> int:
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    LESSON_DIR.mkdir(parents=True, exist_ok=True)
    locked = [jp for lesson in seed["lessons"] for jp in (it["jp"] for it in lesson["items"])]
    unknown_ctx = set(CONTEXT) - set(locked)
    if unknown_ctx:
        raise SystemExit(f"Context keys not in locked curriculum: {sorted(unknown_ctx)}")
    seen_jp: set[str] = set()
    for ldef in seed["lessons"]:
        coll = build_collection(seed, ldef)
        steps = coll["scenes"][0]["compounds"]["steps"]
        targets = [s["jp"] for s in steps if s.get("coverage") == "target"]
        exposures = [s for s in steps if s.get("coverage") == "exposure"]
        if len(targets) != 25:
            raise SystemExit(f"{ldef['collection_id']}: expected 25 targets, got {len(targets)}")
        if len(targets) != len(set(targets)):
            raise SystemExit(f"Duplicate targets in {ldef['collection_id']}")
        overlap = seen_jp.intersection(targets)
        if overlap:
            raise SystemExit(f"Cross-lesson duplicate in {ldef['collection_id']}: {overlap}")
        seen_jp.update(targets)
        for s in exposures:
            if s.get("coverage") != "exposure":
                raise SystemExit("exposure step missing coverage")
            if s.get("target") not in set(targets):
                raise SystemExit(f"exposure not attributed to a target: {s}")
            has_wrap = 'class="kml-target-word"' in (s.get("jpHtml") or "")
            if has_wrap != bool(s.get("containsTarget", has_wrap)):
                raise SystemExit(
                    f"{ldef['collection_id']}: containsTarget mismatch: {s.get('jp')}"
                )
            # Target-linked replies may omit the lemma (contrast, not a wrap failure).
        out = LESSON_DIR / f"{ldef['collection_id']}.json"
        if out.name.startswith("vocabulary_0") or out.name[11:13].isdigit() and "f" not in out.name:
            raise SystemExit(f"Refusing to write {out.name}")
        out.write_text(json.dumps(coll, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        runtime = coll["meta"]["estimatedContentRuntimeMs"]
        music = coll["meta"]["soundtrackDurationMs"]
        print(
            f"wrote {out.relative_to(REPO)} "
            f"(25 targets + {len(exposures)} exposure + BW {ldef['beautiful_word']['jp']}; "
            f"content ~{runtime}ms / soundtrack {music}ms)"
        )
        if runtime + 60_000 > music:
            print(f"  note: content is close to soundtrack length ({runtime} vs {music})")
    print(f"unique target headwords across F1–F6: {len(seen_jp)}")
    try:
        from build_foundation_review import main as build_review
        build_review()
    except Exception as exc:
        print(f"review page not rebuilt: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
