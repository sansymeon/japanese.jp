/**
 * Hiragana Song — single-row focus (large fade) + full chart for closing.
 * Display modes: kana (verses 1 & 3) and romaji (verse 2).
 */
(function () {
  "use strict";

  const ROMAJI_BY_KANA = {
    あ: "a",
    い: "i",
    う: "u",
    え: "e",
    お: "o",
    か: "ka",
    き: "ki",
    く: "ku",
    け: "ke",
    こ: "ko",
    さ: "sa",
    し: "shi",
    す: "su",
    せ: "se",
    そ: "so",
    た: "ta",
    ち: "chi",
    つ: "tsu",
    て: "te",
    と: "to",
    な: "na",
    に: "ni",
    ぬ: "nu",
    ね: "ne",
    の: "no",
    は: "ha",
    ひ: "hi",
    ふ: "fu",
    へ: "he",
    ほ: "ho",
    ま: "ma",
    み: "mi",
    む: "mu",
    め: "me",
    も: "mo",
    や: "ya",
    ゆ: "yu",
    よ: "yo",
    ら: "ra",
    り: "ri",
    る: "ru",
    れ: "re",
    ろ: "ro",
    わ: "wa",
    を: "wo",
    ん: "n",
  };

  const ROWS = [
    { id: "a", cells: ["あ", "い", "う", "え", "お"] },
    { id: "ka", cells: ["か", "き", "く", "け", "こ"] },
    { id: "sa", cells: ["さ", "し", "す", "せ", "そ"] },
    { id: "ta", cells: ["た", "ち", "つ", "て", "と"] },
    { id: "na", cells: ["な", "に", "ぬ", "ね", "の"] },
    { id: "ha", cells: ["は", "ひ", "ふ", "へ", "ほ"] },
    { id: "ma", cells: ["ま", "み", "む", "め", "も"] },
    { id: "ya", cells: ["や", null, "ゆ", null, "よ"] },
    { id: "ra", cells: ["ら", "り", "る", "れ", "ろ"] },
    { id: "wa", cells: ["わ", null, "を", null, "ん"] },
  ];

  function cellLabel(kana, mode) {
    if (!kana) return "";
    if (mode === "romaji") return ROMAJI_BY_KANA[kana] || "";
    return kana;
  }

  function buildCell(kana, mode) {
    const el = document.createElement("div");
    el.className = "hiragana-song-cell";
    if (!kana) {
      el.classList.add("is-empty");
      el.setAttribute("aria-hidden", "true");
      return el;
    }
    el.dataset.kana = kana;
    const label = document.createElement("span");
    label.className = "hiragana-song-kana";
    label.lang = mode === "romaji" ? "en" : "ja";
    label.textContent = cellLabel(kana, mode);
    el.appendChild(label);
    return el;
  }

  function buildRow(row, mode) {
    const rowEl = document.createElement("div");
    rowEl.className = "hiragana-song-row";
    rowEl.dataset.rowId = row.id;
    row.cells.forEach((cell) => rowEl.appendChild(buildCell(cell, mode)));
    return rowEl;
  }

  function findRow(rowId) {
    return ROWS.find((row) => row.id === rowId) || null;
  }

  const KmlHiraganaSongChart = {
    ROWS,
    ROMAJI_BY_KANA,

    getDisplayMode(container) {
      return container?.dataset.displayMode === "romaji" ? "romaji" : "kana";
    },

    /** Empty focus stage (no row shown yet). */
    renderFocus(container, mode = "kana") {
      if (!container) return;
      container.innerHTML = "";
      container.dataset.displayMode = mode === "romaji" ? "romaji" : "kana";
      container.dataset.layout = "focus";
      container.classList.add("is-focus");
      container.classList.remove("is-full", "has-active-row", "is-row-visible");
      container.dataset.activeRowId = "";
    },

    /** Full gojūon chart for the instrumental closing. */
    renderFull(container, mode = "kana") {
      if (!container) return;
      const next = mode === "romaji" ? "romaji" : "kana";
      container.innerHTML = "";
      container.dataset.displayMode = next;
      container.dataset.layout = "full";
      container.classList.remove("is-focus", "is-row-visible");
      container.classList.add("is-full");
      ROWS.forEach((row) => container.appendChild(buildRow(row, next)));
      container.classList.remove("has-active-row");
      container.dataset.activeRowId = "";
    },

    setDisplayMode(container, mode) {
      if (!container) return;
      const next = mode === "romaji" ? "romaji" : "kana";
      if (container.dataset.displayMode === next) return;
      const layout = container.dataset.layout || "focus";
      const activeId = container.dataset.activeRowId || "";
      if (layout === "full") {
        this.renderFull(container, next);
        return;
      }
      this.renderFocus(container, next);
      if (activeId) this.setFocusRow(container, activeId);
    },

    /** Swap the single focused row (no fade — caller handles opacity). */
    setFocusRow(container, rowId) {
      if (!container) return;
      const row = findRow(rowId);
      if (!row) return;
      const mode = this.getDisplayMode(container);
      container.innerHTML = "";
      container.appendChild(buildRow(row, mode));
      container.dataset.activeRowId = rowId;
      container.classList.add("has-active-row");
    },

    clearFocus(container) {
      if (!container) return;
      container.innerHTML = "";
      container.dataset.activeRowId = "";
      container.classList.remove("has-active-row", "is-row-visible");
    },

    /** @deprecated alias — prefer clearFocus */
    clearActive(container) {
      this.clearFocus(container);
    },

    setRowVisible(container, on) {
      container?.classList.toggle("is-row-visible", Boolean(on));
    },
  };

  window.KmlHiraganaSongChart = KmlHiraganaSongChart;
})();
