/**
 * Shared compound-word layout — scale long anchor/compound strings to one line.
 */
(function () {
  "use strict";

  function anchorWordLength(word) {
    return [...String(word || "")].length;
  }

  /**
   * Scale factor for multi-character compounds at stroke-order-sized type.
   * 1–2 chars: full size · 3: modest reduction · 4+: stronger (e.g. 虫めがね)
   */
  function anchorWordScale(word) {
    const n = anchorWordLength(word);
    if (n <= 2) return 1;
    if (n === 3) return 0.74;
    if (n === 4) return 0.56;
    return 0.48;
  }

  function applyCompoundWordScale(element, word) {
    if (!element) return 1;
    const scale = anchorWordScale(word);
    element.style.setProperty("--kml-compound-word-scale", String(scale));
    return scale;
  }

  function clearCompoundWordScale(element) {
    element?.style.removeProperty("--kml-compound-word-scale");
  }

  window.KmlAnchorCompoundsLayout = {
    anchorWordLength,
    anchorWordScale,
    applyCompoundWordScale,
    clearCompoundWordScale,
  };
})();
