/**
 * Hiragana Origins — man'yōgana → hiragana morph on warm washi.
 * Full gojūon (46): parent kanji ↔ modern hiragana, classical ambient between rows.
 */
(function () {
  "use strict";

  /** @type {ReadonlyArray<{ id: string, kanji: string, hiragana: string, reading: string }>} */
  const A_ROW = [
    { id: "origin_a", kanji: "安", hiragana: "あ", reading: "a" },
    { id: "origin_i", kanji: "以", hiragana: "い", reading: "i" },
    { id: "origin_u", kanji: "宇", hiragana: "う", reading: "u" },
    { id: "origin_e", kanji: "衣", hiragana: "え", reading: "e" },
    { id: "origin_o", kanji: "於", hiragana: "お", reading: "o" },
  ];

  const KA_ROW = [
    { id: "origin_ka", kanji: "加", hiragana: "か", reading: "ka" },
    { id: "origin_ki", kanji: "幾", hiragana: "き", reading: "ki" },
    { id: "origin_ku", kanji: "久", hiragana: "く", reading: "ku" },
    { id: "origin_ke", kanji: "計", hiragana: "け", reading: "ke" },
    { id: "origin_ko", kanji: "己", hiragana: "こ", reading: "ko" },
  ];

  const SA_ROW = [
    { id: "origin_sa", kanji: "左", hiragana: "さ", reading: "sa" },
    { id: "origin_shi", kanji: "之", hiragana: "し", reading: "shi" },
    { id: "origin_su", kanji: "寸", hiragana: "す", reading: "su" },
    { id: "origin_se", kanji: "世", hiragana: "せ", reading: "se" },
    { id: "origin_so", kanji: "曽", hiragana: "そ", reading: "so" },
  ];

  const TA_ROW = [
    { id: "origin_ta", kanji: "太", hiragana: "た", reading: "ta" },
    { id: "origin_chi", kanji: "知", hiragana: "ち", reading: "chi" },
    { id: "origin_tsu", kanji: "川", hiragana: "つ", reading: "tsu" },
    { id: "origin_te", kanji: "天", hiragana: "て", reading: "te" },
    { id: "origin_to", kanji: "止", hiragana: "と", reading: "to" },
  ];

  const NA_ROW = [
    { id: "origin_na", kanji: "奈", hiragana: "な", reading: "na" },
    { id: "origin_ni", kanji: "仁", hiragana: "に", reading: "ni" },
    { id: "origin_nu", kanji: "奴", hiragana: "ぬ", reading: "nu" },
    { id: "origin_ne", kanji: "祢", hiragana: "ね", reading: "ne" },
    { id: "origin_no", kanji: "乃", hiragana: "の", reading: "no" },
  ];

  const HA_ROW = [
    { id: "origin_ha", kanji: "波", hiragana: "は", reading: "ha" },
    { id: "origin_hi", kanji: "比", hiragana: "ひ", reading: "hi" },
    { id: "origin_fu", kanji: "不", hiragana: "ふ", reading: "fu" },
    { id: "origin_he", kanji: "部", hiragana: "へ", reading: "he" },
    { id: "origin_ho", kanji: "保", hiragana: "ほ", reading: "ho" },
  ];

  const MA_ROW = [
    { id: "origin_ma", kanji: "末", hiragana: "ま", reading: "ma" },
    { id: "origin_mi", kanji: "美", hiragana: "み", reading: "mi" },
    { id: "origin_mu", kanji: "武", hiragana: "む", reading: "mu" },
    { id: "origin_me", kanji: "女", hiragana: "め", reading: "me" },
    { id: "origin_mo", kanji: "毛", hiragana: "も", reading: "mo" },
  ];

  const YA_ROW = [
    { id: "origin_ya", kanji: "也", hiragana: "や", reading: "ya" },
    { id: "origin_yu", kanji: "由", hiragana: "ゆ", reading: "yu" },
    { id: "origin_yo", kanji: "与", hiragana: "よ", reading: "yo" },
  ];

  const RA_ROW = [
    { id: "origin_ra", kanji: "良", hiragana: "ら", reading: "ra" },
    { id: "origin_ri", kanji: "利", hiragana: "り", reading: "ri" },
    { id: "origin_ru", kanji: "留", hiragana: "る", reading: "ru" },
    { id: "origin_re", kanji: "礼", hiragana: "れ", reading: "re" },
    { id: "origin_ro", kanji: "呂", hiragana: "ろ", reading: "ro" },
  ];

  const WA_ROW = [
    { id: "origin_wa", kanji: "和", hiragana: "わ", reading: "wa" },
    { id: "origin_wo", kanji: "遠", hiragana: "を", reading: "wo" },
    { id: "origin_n", kanji: "无", hiragana: "ん", reading: "n" },
  ];

  /** Katakana gojūon — parent kanji fragments → modern katakana. */
  const KATAKANA_A_ROW = [
    { id: "origin_a", kanji: "阿", hiragana: "ア", reading: "a" },
    { id: "origin_i", kanji: "伊", hiragana: "イ", reading: "i" },
    { id: "origin_u", kanji: "宇", hiragana: "ウ", reading: "u" },
    { id: "origin_e", kanji: "江", hiragana: "エ", reading: "e" },
    { id: "origin_o", kanji: "於", hiragana: "オ", reading: "o" },
  ];

  const KATAKANA_KA_ROW = [
    { id: "origin_ka", kanji: "加", hiragana: "カ", reading: "ka" },
    { id: "origin_ki", kanji: "幾", hiragana: "キ", reading: "ki" },
    { id: "origin_ku", kanji: "久", hiragana: "ク", reading: "ku" },
    { id: "origin_ke", kanji: "介", hiragana: "ケ", reading: "ke" },
    { id: "origin_ko", kanji: "己", hiragana: "コ", reading: "ko" },
  ];

  const KATAKANA_SA_ROW = [
    { id: "origin_sa", kanji: "散", hiragana: "サ", reading: "sa" },
    { id: "origin_shi", kanji: "之", hiragana: "シ", reading: "shi" },
    { id: "origin_su", kanji: "須", hiragana: "ス", reading: "su" },
    { id: "origin_se", kanji: "世", hiragana: "セ", reading: "se" },
    { id: "origin_so", kanji: "曽", hiragana: "ソ", reading: "so" },
  ];

  const KATAKANA_TA_ROW = [
    { id: "origin_ta", kanji: "多", hiragana: "タ", reading: "ta" },
    { id: "origin_chi", kanji: "千", hiragana: "チ", reading: "chi" },
    { id: "origin_tsu", kanji: "川", hiragana: "ツ", reading: "tsu" },
    { id: "origin_te", kanji: "天", hiragana: "テ", reading: "te" },
    { id: "origin_to", kanji: "止", hiragana: "ト", reading: "to" },
  ];

  const KATAKANA_NA_ROW = [
    { id: "origin_na", kanji: "奈", hiragana: "ナ", reading: "na" },
    { id: "origin_ni", kanji: "二", hiragana: "ニ", reading: "ni" },
    { id: "origin_nu", kanji: "奴", hiragana: "ヌ", reading: "nu" },
    { id: "origin_ne", kanji: "祢", hiragana: "ネ", reading: "ne" },
    { id: "origin_no", kanji: "乃", hiragana: "ノ", reading: "no" },
  ];

  const KATAKANA_HA_ROW = [
    { id: "origin_ha", kanji: "八", hiragana: "ハ", reading: "ha" },
    { id: "origin_hi", kanji: "比", hiragana: "ヒ", reading: "hi" },
    { id: "origin_fu", kanji: "不", hiragana: "フ", reading: "fu" },
    { id: "origin_he", kanji: "部", hiragana: "ヘ", reading: "he" },
    { id: "origin_ho", kanji: "保", hiragana: "ホ", reading: "ho" },
  ];

  const KATAKANA_MA_ROW = [
    { id: "origin_ma", kanji: "万", hiragana: "マ", reading: "ma" },
    { id: "origin_mi", kanji: "三", hiragana: "ミ", reading: "mi" },
    { id: "origin_mu", kanji: "牟", hiragana: "ム", reading: "mu" },
    { id: "origin_me", kanji: "女", hiragana: "メ", reading: "me" },
    { id: "origin_mo", kanji: "毛", hiragana: "モ", reading: "mo" },
  ];

  const KATAKANA_YA_ROW = [
    { id: "origin_ya", kanji: "也", hiragana: "ヤ", reading: "ya" },
    { id: "origin_yu", kanji: "由", hiragana: "ユ", reading: "yu" },
    { id: "origin_yo", kanji: "与", hiragana: "ヨ", reading: "yo" },
  ];

  const KATAKANA_RA_ROW = [
    { id: "origin_ra", kanji: "良", hiragana: "ラ", reading: "ra" },
    { id: "origin_ri", kanji: "利", hiragana: "リ", reading: "ri" },
    { id: "origin_ru", kanji: "流", hiragana: "ル", reading: "ru" },
    { id: "origin_re", kanji: "礼", hiragana: "レ", reading: "re" },
    { id: "origin_ro", kanji: "呂", hiragana: "ロ", reading: "ro" },
  ];

  const KATAKANA_WA_ROW = [
    { id: "origin_wa", kanji: "和", hiragana: "ワ", reading: "wa" },
    { id: "origin_wo", kanji: "乎", hiragana: "ヲ", reading: "wo" },
    { id: "origin_n", kanji: "尓", hiragana: "ン", reading: "n" },
  ];

  /** Gojūon rows in teaching order (modern 46). */
  const GOJUON_ROWS = [
    { id: "a", cells: A_ROW },
    { id: "ka", cells: KA_ROW },
    { id: "sa", cells: SA_ROW },
    { id: "ta", cells: TA_ROW },
    { id: "na", cells: NA_ROW },
    { id: "ha", cells: HA_ROW },
    { id: "ma", cells: MA_ROW },
    { id: "ya", cells: YA_ROW },
    { id: "ra", cells: RA_ROW },
    { id: "wa", cells: WA_ROW },
  ];

  const KATAKANA_GOJUON_ROWS = [
    { id: "a", cells: KATAKANA_A_ROW },
    { id: "ka", cells: KATAKANA_KA_ROW },
    { id: "sa", cells: KATAKANA_SA_ROW },
    { id: "ta", cells: KATAKANA_TA_ROW },
    { id: "na", cells: KATAKANA_NA_ROW },
    { id: "ha", cells: KATAKANA_HA_ROW },
    { id: "ma", cells: KATAKANA_MA_ROW },
    { id: "ya", cells: KATAKANA_YA_ROW },
    { id: "ra", cells: KATAKANA_RA_ROW },
    { id: "wa", cells: KATAKANA_WA_ROW },
  ];

  function hideGlyph(el) {
    if (!el) return;
    el.classList.remove("is-visible");
    el.style.removeProperty("opacity");
  }

  function clearGlyph(el) {
    if (!el) return;
    el.textContent = "";
    hideGlyph(el);
  }

  function clearCalligraphy(wrap, img) {
    wrap?.classList.add("exhibition-hidden");
    wrap?.classList.remove("is-visible");
    if (img) {
      img.removeAttribute("src");
      img.alt = "";
    }
  }

  function clearAmbient(wrap, frame, img) {
    wrap?.classList.add("exhibition-hidden");
    wrap?.classList.remove("is-visible", "is-drifting");
    wrap?.setAttribute("aria-hidden", "true");
    frame?.classList.remove("is-drifting");
    if (img) {
      img.removeAttribute("src");
      img.alt = "";
      img.classList.remove("ken-burns");
    }
  }

  const DEFAULT_PLAQUE = {
    parentTitle: "Origin",
    hiraganaTitle: "Hiragana",
    showHistoricalNote: false,
    historicalNote: "Man'yōgana\nHeian Period",
  };

  function plaqueConfig(display = {}) {
    const custom = display.originsPlaque || display.originsLabels || {};
    return {
      parentTitle: custom.parentTitle || DEFAULT_PLAQUE.parentTitle,
      hiraganaTitle: custom.hiraganaTitle || DEFAULT_PLAQUE.hiraganaTitle,
      showHistoricalNote: Boolean(
        custom.showHistoricalNote ?? display.showOriginsHistoricalNote
      ),
      historicalNote:
        custom.historicalNote ||
        display.originsHistoricalNote ||
        DEFAULT_PLAQUE.historicalNote,
    };
  }

  function clearPlaque(plaque) {
    if (!plaque) return;
    const { root, title, char, note } = plaque;
    root?.classList.remove("is-visible");
    root?.setAttribute("aria-hidden", "true");
    if (title) title.textContent = "";
    if (char) char.textContent = "";
    if (note) {
      note.textContent = "";
      note.classList.add("exhibition-hidden");
    }
  }

  /**
   * @param {{ root: Element, title: Element, char: Element, note: Element }} plaque
   * @param {"parent"|"hiragana"} phase
   * @param {object} scene
   * @param {object} display
   */
  function setPlaqueContent(plaque, phase, scene, display = {}) {
    if (!plaque?.root) return;
    const cfg = plaqueConfig(display);
    const titleText = phase === "hiragana" ? cfg.hiraganaTitle : cfg.parentTitle;
    const charText = phase === "hiragana" ? scene?.hiragana || "" : scene?.kanji || "";
    const noteText =
      scene?.label?.note ||
      scene?.plaqueNote ||
      (cfg.showHistoricalNote ? cfg.historicalNote : "");

    if (plaque.title) plaque.title.textContent = titleText;
    if (plaque.char) plaque.char.textContent = charText;
    if (plaque.note) {
      if (noteText) {
        plaque.note.textContent = noteText;
        plaque.note.classList.remove("exhibition-hidden");
      } else {
        plaque.note.textContent = "";
        plaque.note.classList.add("exhibition-hidden");
      }
    }
  }

  function showPlaque(plaque) {
    if (!plaque?.root) return;
    plaque.root.classList.add("is-visible");
    plaque.root.setAttribute("aria-hidden", "false");
  }

  function hidePlaque(plaque) {
    if (!plaque?.root) return;
    plaque.root.classList.remove("is-visible");
    plaque.root.setAttribute("aria-hidden", "true");
  }

  function setSceneGlyphs(kanjiEl, hiraganaEl, scene) {
    if (kanjiEl) kanjiEl.textContent = scene?.kanji || "";
    if (hiraganaEl) hiraganaEl.textContent = scene?.hiragana || "";
    hideGlyph(kanjiEl);
    hideGlyph(hiraganaEl);
  }

  function setCalligraphy(wrap, img, scene, assetsBase) {
    clearCalligraphy(wrap, img);
    const src = scene?.calligraphy?.image;
    if (!wrap || !img || !src) return false;
    const base = (assetsBase || "").replace(/\/$/, "");
    img.src = base ? `${base}/${src.replace(/^\//, "")}` : src;
    img.alt = scene.calligraphy?.alt || `${scene.kanji} historical calligraphy`;
    return true;
  }

  function setAmbient(wrap, frame, img, imagePath, alt) {
    clearAmbient(wrap, frame, img);
    if (!wrap || !img || !imagePath) return false;
    const clean = String(imagePath).replace(/^\.\//, "");
    img.src = clean.startsWith("http") || clean.startsWith("/") ? clean : `./${clean}`;
    img.alt = alt || "";
    return true;
  }

  function applyTimingCss(timing = {}) {
    const root = document.documentElement;
    const set = (name, ms, fallback) => {
      root.style.setProperty(name, `${timing[ms] ?? fallback}ms`);
    };
    set("--origins-reveal", "originsKanjiRevealMs", 2200);
    set("--origins-morph", "originsMorphMs", 3200);
    set("--origins-fade", "originsExhibitFadeMs", 2400);
    set("--origins-ambient-fade", "originsIntroFadeMs", 3200);
    set("--origins-ken-burns", "originsKenBurnsDurationMs", 48000);
    set("--origins-plaque-fade", "originsLabelFadeMs", 1000);
  }

  function isClassicalAmbientScene(scene) {
    return scene?.kind === "classicalAmbient" || scene?.kind === "ambientImage";
  }

  function isGlyphScene(scene) {
    return Boolean(scene?.kanji && scene?.hiragana) && !isClassicalAmbientScene(scene);
  }

  window.KmlHiraganaOrigins = {
    A_ROW,
    KA_ROW,
    SA_ROW,
    TA_ROW,
    NA_ROW,
    HA_ROW,
    MA_ROW,
    YA_ROW,
    RA_ROW,
    WA_ROW,
    GOJUON_ROWS,
    KATAKANA_A_ROW,
    KATAKANA_KA_ROW,
    KATAKANA_SA_ROW,
    KATAKANA_TA_ROW,
    KATAKANA_NA_ROW,
    KATAKANA_HA_ROW,
    KATAKANA_MA_ROW,
    KATAKANA_YA_ROW,
    KATAKANA_RA_ROW,
    KATAKANA_WA_ROW,
    KATAKANA_GOJUON_ROWS,
    DEFAULT_PLAQUE,
    clearGlyph,
    clearCalligraphy,
    clearAmbient,
    clearPlaque,
    setPlaqueContent,
    showPlaque,
    hidePlaque,
    plaqueConfig,
    setSceneGlyphs,
    setCalligraphy,
    setAmbient,
    applyTimingCss,
    isClassicalAmbientScene,
    isGlyphScene,
  };
})();
