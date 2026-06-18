/**
 * Exhibition / capture verse formatting.
 * Authored lines: each <br> in source → one non-wrapping display line.
 * Fallback: verses without <br> use legacyFormatter (browser wrap).
 */
(function () {
  "use strict";

  const BR_SPLIT = /<br\s*\/?>/gi;
  const HAS_BR = /<br\b/i;

  function legacyFormatter(jpHtml) {
    if (!jpHtml) return "";
    return jpHtml.replace(/<br\s*\/?>\s+/gi, "<br>");
  }

  function usesAuthoredLines(jpHtml) {
    return Boolean(jpHtml && HAS_BR.test(jpHtml));
  }

  function formatAuthoredVerseHtml(jpHtml) {
    if (!jpHtml) return "";
    if (!usesAuthoredLines(jpHtml)) {
      return legacyFormatter(jpHtml);
    }
    return jpHtml
      .split(BR_SPLIT)
      .map((chunk) => chunk.trim())
      .filter(Boolean)
      .map((chunk) => `<span class="kml-verse-line">${chunk}</span>`)
      .join("");
  }

  window.KmlVerseDisplay = {
    legacyFormatter,
    formatAuthoredVerseHtml,
    usesAuthoredLines,
  };
})();
