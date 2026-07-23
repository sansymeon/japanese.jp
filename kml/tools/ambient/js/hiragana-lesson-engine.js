/**
 * Kana for Foreign Learners — prototype engine (hiragana & katakana).
 *
 * Ambient kana-recognition lesson built on the Japanese Vocabulary Lesson 1
 * atmosphere (background, soundtrack, ivory brush typography, slow camera).
 *
 * Timeline is generated programmatically from the kana data files and the
 * central `timing` object in collections/<id>/<id>.json. The collection's
 * `script` field ("hiragana" default, or "katakana") selects the kana set.
 *
 * URL params:
 *   ?collection=katakana_lesson   collection id (page default: hiragana_lesson)
 *   ?scope=test         opening + first row + review + transition into row 2
 *   ?scope=full         complete 46-kana lesson + gojūon chart ending
 *   &timingScale=0.05   speed multiplier for QA
 */
(function () {
  "use strict";

  const params = new URLSearchParams(location.search);
  const timingScale = Math.max(0.01, parseFloat(params.get("timingScale")) || 1);

  function collectionId() {
    return (
      params.get("collection") ||
      document.querySelector("[data-hl-collection]")?.dataset.hlCollection ||
      "hiragana_lesson"
    );
  }

  const state = {
    presentationEnded: false,
    scope: "full",
    config: null,
  };
  window.kmlExhibition = state;

  const $ = (sel) => document.querySelector(sel);

  function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms * timingScale));
  }

  /** Set an element's opacity transition duration (scaled) and toggle visibility. */
  function setFade(el, ms) {
    el.style.transitionDuration = `${Math.round(ms * timingScale)}ms`;
  }

  async function fadeIn(el, ms) {
    setFade(el, ms);
    // Force a style flush so the transition always runs.
    void el.offsetWidth;
    el.classList.add("is-visible");
    await wait(ms);
  }

  async function fadeOut(el, ms) {
    setFade(el, ms);
    void el.offsetWidth;
    el.classList.remove("is-visible");
    await wait(ms);
  }

  function applyConfigCss(config) {
    const root = document.documentElement;
    const typo = config.typography || {};
    const bg = config.background || {};
    const set = (name, value) => {
      if (value !== undefined && value !== null) root.style.setProperty(name, String(value));
    };
    set("--hl-kana-size", typo.kanaSize);
    set("--hl-kana-color", typo.kanaColor);
    set("--hl-romaji-size", typo.romajiSize);
    set("--hl-romaji-color", typo.romajiColor);
    set("--hl-romaji-tracking", typo.romajiTracking);
    set("--hl-romaji-gap", typo.romajiGap);
    set("--hl-review-kana-size", typo.reviewKanaSize);
    set("--hl-review-gap", typo.reviewGap);
    set("--hl-chart-kana-size", typo.chartKanaSize);
    set("--hl-chart-column-gap", typo.chartColumnGap);
    set("--hl-chart-row-gap", typo.chartRowGap);
    set("--hl-title-size", typo.titleSize);
    set("--hl-title-tracking", typo.titleTracking);
    set("--hl-title-sub-size", typo.titleSubSize);
    set("--hl-title-sub-tracking", typo.titleSubTracking);
    set("--hl-overlay-opacity", bg.overlayOpacity ?? 0.34);
    const push = bg.pushIn || {};
    set("--hl-push-from", push.scaleFrom ?? 1.04);
    set("--hl-push-to", push.scaleTo ?? 1.14);
    set("--hl-push-duration", `${Math.round((push.durationMs ?? 600000) * timingScale)}ms`);
    const t = config.timing || {};
    set("--hl-chart-highlight-fade", `${Math.round((t.chartHighlightFadeMs ?? 1200) * timingScale)}ms`);
  }

  function setupBackground(config) {
    const img = $("[data-hl-background-img]");
    const bg = config.background || {};
    img.src = bg.image;
    img.style.objectPosition = bg.focus || "center center";
  }

  function startSoundtrackPreview(config, delayMs) {
    // Live-browser preview only; the recording pipeline muxes the soundtrack
    // with ffmpeg (adelay) exactly like the Vocabulary Lesson 1 export.
    const src = config.soundtrack?.main;
    if (!src) return;
    const audio = new Audio(src);
    audio.preload = "auto";
    setTimeout(() => {
      audio.play().catch(() => {});
    }, delayMs * timingScale);
  }

  function buildReviewRow(row) {
    const wrap = $("[data-hl-review]");
    wrap.innerHTML = "";
    row.kana.forEach((cell) => {
      const el = document.createElement("span");
      el.className = "hl-review-kana";
      el.lang = "ja";
      el.textContent = cell.kana;
      wrap.appendChild(el);
    });
  }

  function buildChart(columns) {
    const chart = $("[data-hl-chart]");
    chart.innerHTML = "";
    columns.forEach((column) => {
      const colEl = document.createElement("div");
      colEl.className = "hl-chart-column";
      colEl.dataset.rowId = column.id;
      column.cells.forEach((kana) => {
        const cell = document.createElement("span");
        cell.className = "hl-chart-cell";
        if (kana) {
          cell.lang = "ja";
          cell.textContent = kana;
        } else {
          cell.classList.add("is-empty");
          cell.setAttribute("aria-hidden", "true");
        }
        colEl.appendChild(cell);
      });
      chart.appendChild(colEl);
    });
  }

  /** One kana: fade in → alone → romaji in → together → romaji out → alone → fade out. */
  async function playKana(cell, t) {
    const stage = $("[data-hl-kana-stage]");
    const kanaEl = $("[data-hl-kana]");
    const romajiEl = $("[data-hl-romaji]");
    kanaEl.textContent = cell.kana;
    romajiEl.textContent = cell.romaji;

    await fadeIn(stage, t.kanaFadeInMs);
    await wait(t.kanaAloneMs);
    await fadeIn(romajiEl, t.romajiFadeInMs);
    await wait(t.kanaRomajiHoldMs);
    await fadeOut(romajiEl, t.romajiFadeOutMs);
    await wait(t.kanaAloneAfterMs);
    await fadeOut(stage, t.kanaFadeOutMs);
    await wait(t.kanaGapMs);
  }

  /** Kana-only row review: fade in as one row, hold, fade out. */
  async function playReview(row, t) {
    const review = $("[data-hl-review]");
    buildReviewRow(row);
    await wait(t.reviewBeforeMs);
    await fadeIn(review, t.reviewFadeInMs);
    await wait(t.reviewHoldMs);
    await fadeOut(review, t.reviewFadeOutMs);
    await wait(t.reviewAfterMs);
  }

  async function playOpening(config, t) {
    const veil = $("[data-hl-veil]");
    const bgWrap = $("[data-hl-background]");
    const title = $("[data-hl-title]");
    $("[data-hl-title-main]").textContent = config.opening?.titleMain || "HIRAGANA";
    $("[data-hl-title-sub]").textContent =
      config.opening?.titleSub || "46 Basic Japanese Characters";

    await wait(t.recordingBlackBeforeMs);
    startSoundtrackPreview(config, t.soundtrackDelayAfterImageMs ?? 0);
    bgWrap.classList.add("is-pushing");
    setFade(veil, t.backgroundFadeInMs);
    veil.classList.add("is-clear");
    await wait(t.backgroundFadeInMs);
    await wait(t.backgroundAloneMs);

    await fadeIn(title, t.titleFadeInMs);
    await wait(t.titleHoldMs);
    await fadeOut(title, t.titleFadeOutMs);
    await wait(t.titleAfterMs);
  }

  async function playChartEnding(columns, t) {
    const chart = $("[data-hl-chart]");
    buildChart(columns);
    await wait(t.chartBeforeMs);
    await fadeIn(chart, t.chartFadeInMs);
    await wait(t.chartHoldMs);

    for (const column of columns) {
      chart.classList.add("is-highlighting");
      chart
        .querySelectorAll(".hl-chart-column")
        .forEach((el) => el.classList.toggle("is-highlight", el.dataset.rowId === column.id));
      await wait(t.chartHighlightFadeMs + t.chartHighlightHoldMs);
    }
    chart.classList.remove("is-highlighting");
    chart.querySelectorAll(".hl-chart-column").forEach((el) => el.classList.remove("is-highlight"));
    await wait(t.chartHighlightFadeMs + t.chartUnhighlightHoldMs);

    await fadeOut(chart, t.chartFadeOutMs);
  }

  async function playEnding(config, t) {
    const veil = $("[data-hl-veil]");
    await wait(t.endBackgroundHoldMs);
    setFade(veil, t.endFadeToBlackMs);
    veil.classList.remove("is-clear");
    await wait(t.endFadeToBlackMs);

    // Silent 漢 crest on black — same closing convention as the KML
    // vocabulary videos (music has already faded with the background).
    const crestSrc = config.crest?.image;
    if (crestSrc) {
      const crest = $("[data-hl-crest]");
      $("[data-hl-crest-img]").src = crestSrc;
      await wait(t.crestBlackBeforeMs ?? 800);
      await fadeIn(crest, t.crestFadeInMs ?? 3200);
      await wait(t.crestHoldMs ?? 2800);
      await fadeOut(crest, t.crestFadeOutMs ?? 3500);
      await wait(t.crestBlackAfterMs ?? 800);
    }

    await wait(400);
    state.presentationEnded = true;
  }

  async function run() {
    const id = collectionId();
    const config = await fetch(`collections/${id}/${id}.json`).then((r) => r.json());
    state.config = config;
    state.scope = params.get("scope") || config.display?.scope || "full";

    const katakana = config.script === "katakana";
    const source = katakana ? window.KmlKatakanaLessonData : window.KmlHiraganaLessonData;
    const data = {
      rows: katakana ? source.katakanaRows : source.hiraganaRows,
      gojuonChartColumns: source.gojuonChartColumns,
    };
    const t = config.timing;
    applyConfigCss(config);
    setupBackground(config);

    await new Promise((resolve) => {
      if (document.readyState === "complete") resolve();
      else window.addEventListener("load", resolve, { once: true });
    });
    try {
      await document.fonts.ready;
    } catch (_) {
      /* fonts optional */
    }

    await playOpening(config, t);

    const isTest = state.scope === "test";
    const rows = isTest ? data.rows.slice(0, 1) : data.rows;

    for (const row of rows) {
      for (const cell of row.kana) await playKana(cell, t);
      await playReview(row, t);
    }

    if (isTest) {
      // Transition into the second row — enough to judge pacing and flow.
      await playKana(data.rows[1].kana[0], t);
    } else {
      await playChartEnding(data.gojuonChartColumns, t);
    }

    await playEnding(config, t);
  }

  run().catch((err) => {
    console.error("hiragana lesson failed:", err);
    const errEl = $("[data-hl-error]");
    if (errEl) {
      errEl.textContent = String(err);
      errEl.classList.add("is-visible");
    }
  });
})();
