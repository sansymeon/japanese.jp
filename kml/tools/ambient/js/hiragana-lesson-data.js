/**
 * Hiragana for Foreign Learners — kana data (46 basic hiragana only).
 * Data only; rendering logic lives in hiragana-lesson-engine.js.
 * No dakuten, handakuten, small kana, contracted sounds, or historical kana.
 */
(function () {
  "use strict";

  /** Teaching rows, in gojūon order. Romaji is uppercase Hepburn. */
  const hiraganaRows = [
    {
      id: "a",
      kana: [
        { kana: "あ", romaji: "A" },
        { kana: "い", romaji: "I" },
        { kana: "う", romaji: "U" },
        { kana: "え", romaji: "E" },
        { kana: "お", romaji: "O" },
      ],
    },
    {
      id: "ka",
      kana: [
        { kana: "か", romaji: "KA" },
        { kana: "き", romaji: "KI" },
        { kana: "く", romaji: "KU" },
        { kana: "け", romaji: "KE" },
        { kana: "こ", romaji: "KO" },
      ],
    },
    {
      id: "sa",
      kana: [
        { kana: "さ", romaji: "SA" },
        { kana: "し", romaji: "SHI" },
        { kana: "す", romaji: "SU" },
        { kana: "せ", romaji: "SE" },
        { kana: "そ", romaji: "SO" },
      ],
    },
    {
      id: "ta",
      kana: [
        { kana: "た", romaji: "TA" },
        { kana: "ち", romaji: "CHI" },
        { kana: "つ", romaji: "TSU" },
        { kana: "て", romaji: "TE" },
        { kana: "と", romaji: "TO" },
      ],
    },
    {
      id: "na",
      kana: [
        { kana: "な", romaji: "NA" },
        { kana: "に", romaji: "NI" },
        { kana: "ぬ", romaji: "NU" },
        { kana: "ね", romaji: "NE" },
        { kana: "の", romaji: "NO" },
      ],
    },
    {
      id: "ha",
      kana: [
        { kana: "は", romaji: "HA" },
        { kana: "ひ", romaji: "HI" },
        { kana: "ふ", romaji: "FU" },
        { kana: "へ", romaji: "HE" },
        { kana: "ほ", romaji: "HO" },
      ],
    },
    {
      id: "ma",
      kana: [
        { kana: "ま", romaji: "MA" },
        { kana: "み", romaji: "MI" },
        { kana: "む", romaji: "MU" },
        { kana: "め", romaji: "ME" },
        { kana: "も", romaji: "MO" },
      ],
    },
    {
      id: "ya",
      kana: [
        { kana: "や", romaji: "YA" },
        { kana: "ゆ", romaji: "YU" },
        { kana: "よ", romaji: "YO" },
      ],
    },
    {
      id: "ra",
      kana: [
        { kana: "ら", romaji: "RA" },
        { kana: "り", romaji: "RI" },
        { kana: "る", romaji: "RU" },
        { kana: "れ", romaji: "RE" },
        { kana: "ろ", romaji: "RO" },
      ],
    },
    {
      id: "wa",
      kana: [
        { kana: "わ", romaji: "WA" },
        { kana: "を", romaji: "WO" },
        { kana: "ん", romaji: "N" },
      ],
    },
  ];

  /**
   * Traditional gojūon chart columns for the ending (kana only, no romaji).
   * Read right-to-left by consonant row, top-to-bottom あ→お within a column.
   * null = the classic empty chart position (や/わ columns).
   */
  const gojuonChartColumns = [
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

  window.KmlHiraganaLessonData = { hiraganaRows, gojuonChartColumns };
})();
