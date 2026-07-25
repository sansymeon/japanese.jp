#!/usr/bin/env python3
"""Compare live computed typography: Lesson 5 (master) vs Lesson 33.

Probes exhibition/index at 1920×1080 recording viewport. Ignores artwork.
Reports CSS values AND the actually resolved font face (not merely the stack).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 9066
VIEWPORT = {"width": 1920, "height": 1080}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    launch_recording_browser,
    new_recording_context,
)

PROPS = [
    "fontFamily",
    "fontSize",
    "fontWeight",
    "fontStyle",
    "lineHeight",
    "letterSpacing",
    "color",
    "textShadow",
    "opacity",
    "marginTop",
    "marginBottom",
    "paddingTop",
    "paddingBottom",
    "width",
    "maxWidth",
    "top",
    "left",
    "transform",
]

PROBE_JS = r"""
async ({ sample, selectors }) => {
  await document.fonts.ready;
  const out = {
    htmlClasses: [...document.documentElement.classList].sort(),
    rootClasses: [],
    cssVars: {},
    faces: [],
    nodes: {},
    resolved: {},
  };

  const root = document.querySelector('.exhibition-root, .ambient-root');
  if (root) out.rootClasses = [...root.classList].sort();

  const style = getComputedStyle(document.documentElement);
  for (const v of [
    '--kml-font-kanji-main',
    '--kml-font-heart-verse-jp',
    '--kml-font-heart-voice',
    '--kml-size-verse-jp',
    '--kml-size-verse-en',
    '--kml-size-keyword',
    '--kml-compounds-jp',
    '--kml-compounds-en',
    '--kml-compounds-reading',
    '--kml-compounds-target',
    '--kml-assisted-verse-jp',
    '--kml-assisted-verse-en',
    '--kml-foundations-exhibition-verse-jp',
    '--kml-foundations-exhibition-verse-en',
    '--kml-kanji-letter-spacing',
    '--kml-color-kanji',
    '--kml-color-verse-jp',
    '--kml-color-verse-en',
  ]) {
    out.cssVars[v] = style.getPropertyValue(v).trim();
  }

  out.faces = [...document.fonts]
    .filter(f => /Noto Serif JP|Yuji Syuku|Cormorant|Noto Sans/i.test(f.family))
    .map(f => ({
      family: f.family,
      weight: String(f.weight),
      style: f.style,
      status: f.status,
      // Chromium exposes the loaded source when available
      unicodeRange: f.unicodeRange || '',
    }));

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  function measure(family, weight, sizePx, text) {
    ctx.font = `${weight} ${sizePx}px ${family}`;
    const m = ctx.measureText(text);
    return {
      width: +m.width.toFixed(3),
      actualBoundingBoxAscent: m.actualBoundingBoxAscent
        ? +m.actualBoundingBoxAscent.toFixed(3) : null,
      actualBoundingBoxDescent: m.actualBoundingBoxDescent
        ? +m.actualBoundingBoxDescent.toFixed(3) : null,
    };
  }

  // Which face actually paints this CSS font shorthand?
  function resolvedFace(cssFont, sampleText) {
    const check = (name) => document.fonts.check(cssFont.replace(/"[^"]+"|'[^']+'|[^,]+/, `"${name}"`), sampleText);
    // Prefer parsing family from cssFont
    const famMatch = cssFont.match(/["']([^"']+)["']|,\s*([^,]+)\s*$/);
    const primary = (cssFont.match(/["']([^"']+)["']/) || [])[1] || '';
    const stack = [...cssFont.matchAll(/["']([^"']+)["']/g)].map(m => m[1]);
    const ok = {};
    for (const name of stack.length ? stack : [primary]) {
      ok[name] = document.fonts.check(
        cssFont.replace(/^(.*?)\d+px/, (all) => all).includes(name)
          ? cssFont
          : cssFont.replace(/["'][^"']+["']/, `"${name}"`),
        sampleText
      );
      // simpler: check weight+size+family
      const weight = (cssFont.match(/^\s*(\d{3}|normal|bold)/) || ['','400'])[1];
      const size = (cssFont.match(/(\d+(?:\.\d+)?)px/) || ['','82'])[1];
      ok[name] = document.fonts.check(`${weight} ${size}px "${name}"`, sampleText);
    }
    return { primary, stack, check: ok };
  }

  for (const [key, sel] of Object.entries(selectors)) {
    const el = document.querySelector(sel);
    if (!el) {
      out.nodes[key] = null;
      continue;
    }
    // Force visible so computed styles aren't display:none artifacts
    el.classList.add('is-visible');
    const cs = getComputedStyle(el);
    const node = {};
    for (const p of %PROPS%) node[p] = cs[p];
    node.text = (el.textContent || '').trim().slice(0, 40);
    node.tag = el.tagName.toLowerCase();
    node.className = el.className;
    out.nodes[key] = node;

    const fam = cs.fontFamily;
    const weight = cs.fontWeight;
    const size = parseFloat(cs.fontSize);
    const probeText = sample[key] || node.text || '静';
    const cssFont = `${weight} ${size}px ${fam}`;
    out.resolved[key] = {
      cssFont,
      fontsCheckPrimary: document.fonts.check(
        `${weight} ${size}px ${fam.split(',')[0].trim()}`,
        probeText
      ),
      faceChecks: Object.fromEntries(
        ['Noto Serif JP', 'Yuji Syuku', 'Cormorant Garamond', 'Noto Sans JP', 'Noto Sans CJK JP']
          .map(n => [n, document.fonts.check(`${weight} ${size}px "${n}"`, probeText)])
      ),
      metrics: {
        onNotoSerifJP: measure('"Noto Serif JP"', weight, size, probeText),
        onYujiSyuku: measure('"Yuji Syuku"', weight, size, probeText),
        onNotoSansJP: measure('"Noto Sans JP"', weight, size, probeText),
        onStack: measure(fam, weight, size, probeText),
      },
    };
  }

  // Detect whether local OTF or Google webfont is serving "Noto Serif JP"
  const notoFaces = [...document.fonts].filter(
    f => f.family.replace(/['"]/g, '') === 'Noto Serif JP'
  );
  out.notoSerifJP = notoFaces.map(f => ({
    weight: String(f.weight),
    status: f.status,
    // In Chromium, FontFace has no public URL; use presence of multiple weights
    // and compare glyph metrics vs a known CJK OTF sample.
  }));

  // Glyph fingerprint: width of distinctive characters at fixed size
  const fpChars = ['工', '静', '忘', '恵', 'あ', 'の', 'M', 'g'];
  out.glyphFingerprint = {};
  for (const ch of fpChars) {
    out.glyphFingerprint[ch] = {
      serifJP: measure('"Noto Serif JP"', '400', 82, ch).width,
      yuji: measure('"Yuji Syuku"', '400', 82, ch).width,
      sansJP: measure('"Noto Sans JP"', '400', 82, ch).width,
    };
  }

  return out;
}
""".replace("%PROPS%", json.dumps(PROPS))


CASES = [
    {
        "id": "compounds",
        "urls": {
            "L5": f"http://127.0.0.1:{PORT}/exhibition.html?collection=lesson_05_compounds&typography=mobile-refine&verseMode=sequential&capture=1",
            "L33": f"http://127.0.0.1:{PORT}/exhibition.html?collection=lesson_33_compounds&typography=mobile-refine&verseMode=sequential&capture=1",
        },
        "wait_engine": "kmlExhibition",
        "selectors": {
            "compoundJp": ".kml-compound-jp, .exhibition-verse-jp .kml-compound-jp, [class*='compound'] .kml-compound-jp",
            "compoundEn": ".kml-compound-en, .exhibition-verse-en",
            "furiganaRt": "ruby rt, .kml-compound-jp rt",
            "targetKanji": ".kml-compounds-target, .exhibition-kanji",
            "verseJp": ".exhibition-verse-jp",
            "verseEn": ".exhibition-verse-en",
        },
        "sample": {
            "compoundJp": "工房",
            "compoundEn": "workshop",
            "furiganaRt": "こう",
            "targetKanji": "工",
            "verseJp": "静",
            "verseEn": "quiet",
        },
        "advance": """async () => {
          const ex = window.kmlExhibition;
          if (!ex) return;
          // Start and jump into first compound step with text visible
          if (ex.ensureAudioUnlocked) await ex.ensureAudioUnlocked();
          // Force-show compound layers if present
          document.querySelectorAll('.kml-compound-jp, .kml-compound-en, .exhibition-verse-jp, .exhibition-verse-en, .exhibition-kanji, .kml-compounds-target, ruby rt')
            .forEach(el => el.classList.add('is-visible'));
          // Also reveal furigana opacity if CSS hides it
          document.querySelectorAll('ruby rt').forEach(rt => { rt.style.opacity = '1'; });
        }""",
    },
    {
        "id": "reading",
        "urls": {
            "L5": f"http://127.0.0.1:{PORT}/exhibition.html?collection=lesson_05_reading&typography=mobile-refine&verseMode=sequential&capture=1",
            "L33": f"http://127.0.0.1:{PORT}/exhibition.html?collection=lesson_33_reading&typography=mobile-refine&verseMode=sequential&capture=1",
        },
        "wait_engine": "kmlExhibition",
        "selectors": {
            "verseJp": ".exhibition-verse-jp",
            "verseEn": ".exhibition-verse-en",
            "furiganaRt": ".exhibition-verse-jp ruby rt",
            "keyword": ".exhibition-keyword",
        },
        "sample": {
            "verseJp": "静",
            "verseEn": "quiet",
            "furiganaRt": "しず",
            "keyword": "craft",
        },
        "advance": """async () => {
          document.querySelectorAll('.exhibition-verse-jp, .exhibition-verse-en, .exhibition-keyword, ruby rt')
            .forEach(el => el.classList.add('is-visible'));
          document.querySelectorAll('ruby rt').forEach(rt => { rt.style.opacity = '1'; });
        }""",
    },
    {
        "id": "foundations",
        "urls": {
            "L5": f"http://127.0.0.1:{PORT}/index.html?collection=lesson_05_foundations&typography=mobile-refine&capture=1",
            "L33": f"http://127.0.0.1:{PORT}/index.html?collection=lesson_33_foundations&typography=mobile-refine&capture=1",
        },
        "wait_engine": "kmlAmbient",
        "selectors": {
            "kanji": ".ambient-kanji",
            "keyword": ".ambient-keyword",
            "verseJp": ".ambient-verse-jp",
            "furiganaRt": ".ambient-verse-jp ruby rt",
        },
        "sample": {
            "kanji": "工",
            "keyword": "craft",
            "verseJp": "静",
            "furiganaRt": "しず",
        },
        "advance": """async () => {
          document.querySelectorAll('.ambient-kanji, .ambient-keyword, .ambient-verse-jp, ruby rt')
            .forEach(el => el.classList.add('is-visible'));
          document.querySelectorAll('ruby rt').forEach(rt => { rt.style.opacity = '1'; });
        }""",
    },
]


def probe(page, case: dict) -> dict:
    page.wait_for_function(
        f"() => window.{case['wait_engine']}",
        timeout=120_000,
    )
    page.wait_for_function(
        "() => document.fonts && document.fonts.status === 'loaded'",
        timeout=120_000,
    )
    page.wait_for_timeout(800)
    page.evaluate(case["advance"])
    page.wait_for_timeout(400)
    # Broaden selectors: try multiple fallbacks
    selectors = dict(case["selectors"])
    # Discover actual compound selectors present
    discovered = page.evaluate(
        """() => {
          const pick = (cands) => cands.find(s => document.querySelector(s)) || null;
          return {
            compoundJp: pick(['.kml-compound-jp','.exhibition-notes .kml-compound-jp','[data-compound-jp]','.kml-vocab-jp']),
            compoundEn: pick(['.kml-compound-en','.exhibition-verse-en']),
            furiganaRt: pick(['.kml-compound-jp rt','ruby rt','.exhibition-verse-jp rt']),
            targetKanji: pick(['.kml-compounds-target','.exhibition-kanji','.kml-target-kanji']),
            verseJp: pick(['.exhibition-verse-jp','.ambient-verse-jp']),
            verseEn: pick(['.exhibition-verse-en','.ambient-verse-en']),
            keyword: pick(['.exhibition-keyword','.ambient-keyword']),
            kanji: pick(['.ambient-kanji','.exhibition-kanji']),
          };
        }"""
    )
    for k, v in discovered.items():
        if v and k in selectors:
            selectors[k] = v
        elif v and k not in selectors:
            selectors[k] = v
    return page.evaluate(PROBE_JS, {"sample": case["sample"], "selectors": selectors})


def diff_dicts(a, b, path=""):
    diffs = []
    if type(a) is not type(b):
        return [(path or "$", a, b)]
    if isinstance(a, dict):
        keys = sorted(set(a) | set(b))
        for k in keys:
            p = f"{path}.{k}" if path else k
            if k not in a:
                diffs.append((p, "<missing>", b[k]))
            elif k not in b:
                diffs.append((p, a[k], "<missing>"))
            else:
                diffs.extend(diff_dicts(a[k], b[k], p))
        return diffs
    if a != b:
        return [(path or "$", a, b)]
    return []


def main() -> int:
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.0)

    from playwright.sync_api import sync_playwright

    report = {}
    try:
        with sync_playwright() as p:
            browser = launch_recording_browser(p, headless=True)
            for case in CASES:
                report[case["id"]] = {}
                for label, url in case["urls"].items():
                    context = new_recording_context(browser, viewport=VIEWPORT)
                    page = context.new_page()
                    print(f"Probe {case['id']} {label}: {url}")
                    page.goto(url, wait_until="load", timeout=120_000)
                    # click gate if present
                    try:
                        gate = page.locator("[data-ambient-autoplay-gate], [data-exhibition-autoplay-gate]")
                        if gate.count() and gate.first.is_visible():
                            gate.first.click()
                    except Exception:
                        page.mouse.click(960, 540)
                    data = probe(page, case)
                    report[case["id"]][label] = data
                    context.close()

                # Compare L5 vs L33
                l5 = report[case["id"]]["L5"]
                l33 = report[case["id"]]["L33"]
                print(f"\n======== {case['id'].upper()} ========")
                print(f"html classes L5:  {l5['htmlClasses']}")
                print(f"html classes L33: {l33['htmlClasses']}")
                print(f"root classes L5:  {l5['rootClasses']}")
                print(f"root classes L33: {l33['rootClasses']}")

                print("-- CSS vars --")
                for k in sorted(set(l5["cssVars"]) | set(l33["cssVars"])):
                    a, b = l5["cssVars"].get(k), l33["cssVars"].get(k)
                    mark = "OK" if a == b else "DIFF"
                    if a != b:
                        print(f"  [{mark}] {k}\n    L5:  {a}\n    L33: {b}")
                    else:
                        print(f"  [{mark}] {k} = {a}")

                print("-- node computed styles --")
                for key in sorted(set(l5["nodes"]) | set(l33["nodes"])):
                    n5, n33 = l5["nodes"].get(key), l33["nodes"].get(key)
                    if n5 is None and n33 is None:
                        continue
                    if n5 is None or n33 is None:
                        print(f"  [{key}] MISSING on {'L5' if n5 is None else 'L33'}")
                        continue
                    print(f"  [{key}] text L5={n5.get('text')!r} L33={n33.get('text')!r}")
                    for prop in PROPS:
                        a, b = n5.get(prop), n33.get(prop)
                        if a != b:
                            print(f"    DIFF {prop}: L5={a!r}  L33={b!r}")
                    r5, r33 = l5["resolved"].get(key, {}), l33["resolved"].get(key, {})
                    print(f"    cssFont L5:  {r5.get('cssFont')}")
                    print(f"    cssFont L33: {r33.get('cssFont')}")
                    print(f"    faceChecks L5:  {r5.get('faceChecks')}")
                    print(f"    faceChecks L33: {r33.get('faceChecks')}")
                    m5 = (r5.get("metrics") or {}).get("onStack")
                    m33 = (r33.get("metrics") or {}).get("onStack")
                    print(f"    stack metrics L5={m5} L33={m33}")
                    # Compare Noto Serif metrics at this size — if CSS says Noto Serif JP
                    # but metrics match Sans, we're on the wrong face.
                    ns5 = (r5.get("metrics") or {}).get("onNotoSerifJP")
                    ns33 = (r33.get("metrics") or {}).get("onNotoSerifJP")
                    sans5 = (r5.get("metrics") or {}).get("onNotoSansJP")
                    sans33 = (r33.get("metrics") or {}).get("onNotoSansJP")
                    if m5 and ns5 and sans5:
                        closer = "serif" if abs(m5["width"] - ns5["width"]) <= abs(m5["width"] - sans5["width"]) else "SANS"
                        print(f"    L5 painted face ~ {closer} (stack={m5['width']} serif={ns5['width']} sans={sans5['width']})")
                    if m33 and ns33 and sans33:
                        closer = "serif" if abs(m33["width"] - ns33["width"]) <= abs(m33["width"] - sans33["width"]) else "SANS"
                        print(f"    L33 painted face ~ {closer} (stack={m33['width']} serif={ns33['width']} sans={sans33['width']})")

                print("-- glyph fingerprint (400 82px) --")
                for ch in sorted(set(l5["glyphFingerprint"]) | set(l33["glyphFingerprint"])):
                    a, b = l5["glyphFingerprint"][ch], l33["glyphFingerprint"][ch]
                    if a != b:
                        print(f"  DIFF '{ch}': L5={a} L33={b}")
                    else:
                        print(f"  OK   '{ch}': {a}")

                print("-- loaded Noto/Yuji/Cormorant faces --")
                def face_summary(faces):
                    return sorted({(f["family"], f["weight"], f["status"]) for f in faces})
                print(f"  L5:  {face_summary(l5['faces'])}")
                print(f"  L33: {face_summary(l33['faces'])}")

            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except Exception:
            server.kill()

    out = ROOT / "collections" / "typography_compare_l5_l33.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
