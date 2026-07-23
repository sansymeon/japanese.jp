/**
 * Kana Song — Typography Edition (hiragana / katakana)
 * Gojūon gallery: hero kana → gentle dock into a colored row.
 * Finale: kana snowflakes drift down into a center mound.
 * Romaji edition: Hepburn ruby above each kana + alphabet snow finale.
 */
(function () {
  "use strict";

  const HIRAGANA_ROWS = [
    { id: "a", cells: ["あ", "い", "う", "え", "お"], color: "#FF2D55" },
    { id: "ka", cells: ["か", "き", "く", "け", "こ"], color: "#FF6A00" },
    { id: "sa", cells: ["さ", "し", "す", "せ", "そ"], color: "#FFCC00" },
    { id: "ta", cells: ["た", "ち", "つ", "て", "と"], color: "#22C55E" },
    { id: "na", cells: ["な", "に", "ぬ", "ね", "の"], color: "#1E90FF" },
    { id: "ha", cells: ["は", "ひ", "ふ", "へ", "ほ"], color: "#A855F7" },
    { id: "ma", cells: ["ま", "み", "む", "め", "も"], color: "#FF4D6D" },
    { id: "ya", cells: ["や", "ゆ", "よ"], color: "#00C2C7" },
    { id: "ra", cells: ["ら", "り", "る", "れ", "ろ"], color: "#FF8A1F" },
    { id: "wa", cells: ["わ", "を", "ん"], color: "#7C3AED" },
  ];

  const KATAKANA_ROWS = [
    { id: "a", cells: ["ア", "イ", "ウ", "エ", "オ"], color: "#FF2D55" },
    { id: "ka", cells: ["カ", "キ", "ク", "ケ", "コ"], color: "#FF6A00" },
    { id: "sa", cells: ["サ", "シ", "ス", "セ", "ソ"], color: "#FFCC00" },
    { id: "ta", cells: ["タ", "チ", "ツ", "テ", "ト"], color: "#22C55E" },
    { id: "na", cells: ["ナ", "ニ", "ヌ", "ネ", "ノ"], color: "#1E90FF" },
    { id: "ha", cells: ["ハ", "ヒ", "フ", "ヘ", "ホ"], color: "#A855F7" },
    { id: "ma", cells: ["マ", "ミ", "ム", "メ", "モ"], color: "#FF4D6D" },
    { id: "ya", cells: ["ヤ", "ユ", "ヨ"], color: "#00C2C7" },
    { id: "ra", cells: ["ラ", "リ", "ル", "レ", "ロ"], color: "#FF8A1F" },
    { id: "wa", cells: ["ワ", "ヲ", "ン"], color: "#7C3AED" },
  ];

  /** Standard Hepburn readings, lowercase, keyed by kana (both scripts). */
  const ROMAJI = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "を": "o", "ん": "n",
    "ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o",
    "カ": "ka", "キ": "ki", "ク": "ku", "ケ": "ke", "コ": "ko",
    "サ": "sa", "シ": "shi", "ス": "su", "セ": "se", "ソ": "so",
    "タ": "ta", "チ": "chi", "ツ": "tsu", "テ": "te", "ト": "to",
    "ナ": "na", "ニ": "ni", "ヌ": "nu", "ネ": "ne", "ノ": "no",
    "ハ": "ha", "ヒ": "hi", "フ": "fu", "ヘ": "he", "ホ": "ho",
    "マ": "ma", "ミ": "mi", "ム": "mu", "メ": "me", "モ": "mo",
    "ヤ": "ya", "ユ": "yu", "ヨ": "yo",
    "ラ": "ra", "リ": "ri", "ル": "ru", "レ": "re", "ロ": "ro",
    "ワ": "wa", "ヲ": "o", "ン": "n",
  };

  const ALPHABET = "abcdefghijklmnopqrstuvwxyz".split("");

  /** @deprecated Prefer rowsFor(script) — kept for older callers. */
  const ROWS = HIRAGANA_ROWS;

  function normalizeScript(script) {
    return script === "katakana" ? "katakana" : "hiragana";
  }

  function rowsFor(script) {
    return normalizeScript(script) === "katakana" ? KATAKANA_ROWS : HIRAGANA_ROWS;
  }

  function findRow(rowId, script = "hiragana") {
    return rowsFor(script).find((row) => row.id === rowId) || null;
  }

  function romajiFor(kana) {
    return ROMAJI[kana] || "";
  }

  function allFlakes(script = "hiragana") {
    const flakes = [];
    rowsFor(script).forEach((row) => {
      row.cells.forEach((kana) => {
        flakes.push({ kana, color: row.color, rowId: row.id });
      });
    });
    return flakes;
  }

  /** Lowercase a–z flakes tinted with the rainbow row palette. */
  function alphabetFlakes(script = "hiragana") {
    const palette = rowsFor(script).map((row) => row.color);
    return ALPHABET.map((letter, i) => ({
      kana: letter,
      color: palette[i % palette.length],
      rowId: "alphabet",
    }));
  }

  function shuffleInPlace(list) {
    for (let i = list.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = list[i];
      list[i] = list[j];
      list[j] = tmp;
    }
    return list;
  }

  /** Build a soft triangular mound of landing spots (percent of stage). */
  function moundSlots(count, { preset: presetIn = null, spreadBase = 28, spreadPer = 5.8 } = {}) {
    // Wide low heap — not twin pillars. Exact 46: 12+10+8+6+5+3+2.
    const preset = presetIn || [12, 10, 8, 6, 5, 3, 2];
    const rowCounts = [];
    let remaining = count;
    for (const n of preset) {
      if (remaining <= 0) break;
      const take = Math.min(n, remaining);
      rowCounts.push(take);
      remaining -= take;
    }
    while (remaining > 0) {
      const last = rowCounts[rowCounts.length - 1] || 2;
      const take = Math.min(last, remaining);
      rowCounts.push(take);
      remaining -= take;
    }

    const slots = [];
    const rowGap = 7.5;
    const baseY = 78;
    rowCounts.forEach((n, rowIndex) => {
      const y = baseY - rowIndex * rowGap;
      const spread = spreadBase + n * spreadPer;
      for (let i = 0; i < n; i += 1) {
        const t = n === 1 ? 0.5 : i / (n - 1);
        const x = 50 + (t - 0.5) * spread;
        const jitterX = (Math.random() - 0.5) * 2.4;
        const jitterY = (Math.random() - 0.5) * 2.0;
        slots.push({ x: x + jitterX, y: y + jitterY });
      }
    });
    return slots;
  }

  function clearHero(heroEl) {
    if (!heroEl) return;
    heroEl.textContent = "";
    heroEl.classList.remove("is-visible", "is-docking", "is-settled", "show-romaji");
    delete heroEl.dataset.romaji;
    heroEl.style.removeProperty("transform");
    heroEl.style.removeProperty("opacity");
    heroEl.style.removeProperty("color");
  }

  function clearRow(rowEl) {
    if (!rowEl) return;
    rowEl.innerHTML = "";
    rowEl.classList.remove("is-visible", "is-holding", "is-fading", "is-romaji", "is-static");
    rowEl.style.removeProperty("--typo-row-color");
    rowEl.dataset.rowId = "";
  }

  function clearChart(chartEl) {
    if (!chartEl) return;
    chartEl.innerHTML = "";
    chartEl.classList.remove("is-visible", "is-fading");
  }

  function clearSnow(snowEl) {
    if (!snowEl) return;
    snowEl.classList.remove("is-active", "is-fading");
    snowEl.innerHTML = "";
  }

  function setRowColor(layer, rowEl, color) {
    const value = color || "#FF2D55";
    if (layer) layer.style.setProperty("--typo-row-color", value);
    if (rowEl) {
      rowEl.style.setProperty("--typo-row-color", value);
      rowEl.style.color = value;
    }
  }

  function prepareRow(rowEl, row) {
    if (!rowEl || !row) return;
    clearRow(rowEl);
    rowEl.dataset.rowId = row.id;
    rowEl.style.setProperty("--typo-slot-count", String(row.cells.length));
    setRowColor(null, rowEl, row.color);
    if (row.romaji) rowEl.classList.add("is-romaji");
    row.cells.forEach((kana) => {
      const slot = document.createElement("span");
      slot.className = "hiragana-typo-slot";
      slot.dataset.kana = kana;
      if (row.romaji) slot.dataset.romaji = romajiFor(kana);
      slot.setAttribute("aria-hidden", "true");
      rowEl.appendChild(slot);
    });
    rowEl.classList.add("is-visible");
  }

  /** Final review chart: every row, romaji in ruby position above each kana. */
  function buildChart(chartEl, { script = "hiragana", rowIds = null } = {}) {
    if (!chartEl) return;
    clearChart(chartEl);
    const scriptRows = rowsFor(script);
    const ids = Array.isArray(rowIds) && rowIds.length ? rowIds : scriptRows.map((r) => r.id);
    ids.forEach((id) => {
      const row = findRow(id, script);
      if (!row) return;
      const rowEl = document.createElement("div");
      rowEl.className = "hiragana-typo-chart-row";
      rowEl.style.color = row.color;
      row.cells.forEach((kana) => {
        const cell = document.createElement("span");
        cell.className = "hiragana-typo-chart-cell";
        const ruby = document.createElement("span");
        ruby.className = "hiragana-typo-chart-romaji";
        ruby.textContent = romajiFor(kana);
        const glyph = document.createElement("span");
        glyph.className = "hiragana-typo-chart-kana";
        glyph.textContent = kana;
        cell.appendChild(ruby);
        cell.appendChild(glyph);
        rowEl.appendChild(cell);
      });
      chartEl.appendChild(rowEl);
    });
  }

  function fillSlot(rowEl, index, kana) {
    const slot = rowEl?.children?.[index];
    if (!slot) return null;
    slot.textContent = kana;
    slot.classList.add("is-filled");
    slot.removeAttribute("aria-hidden");
    return slot;
  }

  /**
   * Spawn all gojūon kana as gentle snowflakes that settle into a mound.
   * Returns total animation time in ms (last flake land + small hold).
   */
  function playSnowFinale(
    snowEl,
    { staggerMs = 4500, fallMs = 7000, script = "hiragana", flakeSet = "kana" } = {}
  ) {
    if (!snowEl) return 0;
    clearSnow(snowEl);
    const source = flakeSet === "alphabet" ? alphabetFlakes(script) : allFlakes(script);
    const flakes = shuffleInPlace(source);
    // 26 larger letters need a narrower heap than 46 kana so nothing clips the frame edge.
    const slots =
      flakeSet === "alphabet"
        ? moundSlots(flakes.length, { preset: [9, 7, 5, 3, 2], spreadBase: 22, spreadPer: 5.0 })
        : moundSlots(flakes.length);
    snowEl.classList.add("is-active");

    let maxEnd = 0;
    flakes.forEach((flake, i) => {
      const slot = slots[i] || { x: 50, y: 70 };
      const delay = Math.round((i / Math.max(1, flakes.length - 1)) * staggerMs);
      const duration = fallMs + ((i * 37) % 900) - 200;
      const startX = 6 + Math.random() * 88;
      const sway = (Math.random() - 0.5) * 14;
      const rot = (Math.random() - 0.5) * 48;
      const vh = typeof window !== "undefined" ? window.innerHeight || 1080 : 1080;
      // Lowercase letters carry most of their shape in the x-height, so scale them up.
      const letterBoost = flakeSet === "alphabet" ? 1.25 : 1;
      const sizePx = Math.round(vh * (0.14 + Math.random() * 0.08) * letterBoost); // ~14–22% of frame height
      const el = document.createElement("span");
      el.className = "hiragana-typo-flake";
      if (flakeSet === "alphabet") el.classList.add("is-letter");
      el.textContent = flake.kana;
      el.style.color = flake.color;
      el.style.fontSize = `${sizePx}px`;
      el.style.zIndex = String(10 + i);
      el.style.setProperty("--flake-delay", `${Math.max(0, delay)}ms`);
      el.style.setProperty("--flake-duration", `${Math.max(4200, duration)}ms`);
      el.style.setProperty("--flake-start-x", `${startX}%`);
      el.style.setProperty("--flake-mid-x", `${startX + sway}%`);
      el.style.setProperty("--flake-x", `${slot.x}%`);
      el.style.setProperty("--flake-y", `${slot.y}%`);
      el.style.setProperty("--flake-rot", `${rot}deg`);
      el.style.setProperty("--flake-size", `${sizePx}px`);
      snowEl.appendChild(el);
      maxEnd = Math.max(maxEnd, delay + Math.max(4200, duration));
    });

    // Kick animations on next frame so CSS vars are applied.
    requestAnimationFrame(() => {
      snowEl.querySelectorAll(".hiragana-typo-flake").forEach((el) => {
        el.classList.add("is-falling");
      });
    });

    return maxEnd;
  }

  function buildTimeline({
    soundtrackDurationMs,
    introShare = 0.04,
    finaleMs = 14000,
    finalReviewMs = 0,
    rowIds = null,
    rowHoldMs = 2600,
    finalRowHoldMs = 2800,
    script = "hiragana",
  }) {
    const duration = Math.max(30_000, Number(soundtrackDurationMs) || 214518);
    const scriptRows = rowsFor(script);
    const ids = Array.isArray(rowIds) && rowIds.length ? rowIds : scriptRows.map((r) => r.id);
    const rows = ids.map((id) => findRow(id, script)).filter(Boolean);
    const kanaCount = rows.reduce((n, row) => n + row.cells.length, 0) || 46;

    const introMs = Math.round(duration * introShare);
    const reservedFinale =
      Math.max(10000, Number(finaleMs) || 14000) + Math.max(0, Number(finalReviewMs) || 0);
    const contentEndMs = Math.max(introMs + kanaCount * 900, duration - reservedFinale);
    const budget = Math.max(kanaCount * 1100, contentEndMs - introMs);

    const holdWeights = rows.map((_, i) => (i === rows.length - 1 ? 1.35 : 1));
    const holdWeightSum = holdWeights.reduce((a, b) => a + b, 0);
    const holdBudget = budget * 0.2;
    const kanaBudget = budget - holdBudget;
    const msPerKana = kanaBudget / kanaCount;
    const holdUnit = holdBudget / holdWeightSum;

    let cursor = introMs;
    const events = [];

    rows.forEach((row, rowIndex) => {
      row.cells.forEach((kana, kanaIndex) => {
        events.push({
          type: "kana",
          rowId: row.id,
          color: row.color,
          kana,
          kanaIndex,
          rowCells: row.cells,
          atMs: Math.round(cursor),
          isRowStart: kanaIndex === 0,
        });
        cursor += msPerKana;
      });
      const holdMs = Math.max(
        rowIndex === rows.length - 1 ? finalRowHoldMs : rowHoldMs,
        Math.round(holdUnit * holdWeights[rowIndex])
      );
      events.push({
        type: "rowHold",
        rowId: row.id,
        color: row.color,
        atMs: Math.round(cursor),
        holdMs,
        isFinal: rowIndex === rows.length - 1,
      });
      cursor += holdMs;
    });

    const reviewMs = Math.max(0, Number(finalReviewMs) || 0);
    return {
      soundtrackDurationMs: duration,
      introMs,
      contentEndMs,
      finalReviewStartMs: contentEndMs,
      finalReviewMs: reviewMs,
      finaleStartMs: contentEndMs + reviewMs,
      finaleMs: reservedFinale - reviewMs,
      msPerKana,
      events,
      rows,
      kanaCount,
    };
  }

  const KmlHiraganaSongTypography = {
    ROWS,
    HIRAGANA_ROWS,
    KATAKANA_ROWS,
    ROMAJI,
    ALPHABET,
    normalizeScript,
    rowsFor,
    findRow,
    romajiFor,
    allFlakes,
    alphabetFlakes,
    clearHero,
    clearRow,
    clearChart,
    clearSnow,
    setRowColor,
    prepareRow,
    buildChart,
    fillSlot,
    playSnowFinale,
    buildTimeline,
  };

  window.KmlHiraganaSongTypography = KmlHiraganaSongTypography;
})();
