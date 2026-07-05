/**
 * Load stroke-order SVG from kml/tools/strokes/pages/*.html
 */
(function (global) {
  const KANJI_FONT_SEL = ".kanji-main-font";
  const STROKE_SVG_SEL = ".stroke-order svg";

  function kanjiFromSvg(svgEl) {
    if (!svgEl) return "";
    const tagged = svgEl.querySelector("[kvg\\:element]");
    return tagged?.getAttribute("kvg:element")?.trim() || "";
  }

  function parseStrokePageHtml(html, fallbackKanji = "") {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const svgEl = doc.querySelector(STROKE_SVG_SEL);
    const kanjiEl = doc.querySelector(KANJI_FONT_SEL);
    const kanji =
      kanjiEl?.textContent?.trim() ||
      kanjiFromSvg(svgEl) ||
      fallbackKanji ||
      "";
    const svg = svgEl?.outerHTML || "";
    const strokeCount = svgEl?.querySelectorAll("path").length || 0;
    return { kanji, svg, strokeCount };
  }

  async function loadStrokePage(url, fallbackKanji = "") {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Stroke page fetch failed (${response.status}): ${url}`);
    }
    const html = await response.text();
    return parseStrokePageHtml(html, fallbackKanji);
  }

  global.KmlStrokePageLoader = {
    parseStrokePageHtml,
    loadStrokePage,
  };
})(window);
