/**
 * Katakana for Foreign Learners — kana data (46 basic katakana only).
 * Data only; rendering logic lives in hiragana-lesson-engine.js.
 * No dakuten, handakuten, small kana, contracted sounds, or historical kana.
 */
(function () {
  "use strict";

  /** Teaching rows, in gojūon order. Romaji is uppercase Hepburn. */
  const katakanaRows = [
    {
      id: "a",
      kana: [
        { kana: "ア", romaji: "A" },
        { kana: "イ", romaji: "I" },
        { kana: "ウ", romaji: "U" },
        { kana: "エ", romaji: "E" },
        { kana: "オ", romaji: "O" },
      ],
    },
    {
      id: "ka",
      kana: [
        { kana: "カ", romaji: "KA" },
        { kana: "キ", romaji: "KI" },
        { kana: "ク", romaji: "KU" },
        { kana: "ケ", romaji: "KE" },
        { kana: "コ", romaji: "KO" },
      ],
    },
    {
      id: "sa",
      kana: [
        { kana: "サ", romaji: "SA" },
        { kana: "シ", romaji: "SHI" },
        { kana: "ス", romaji: "SU" },
        { kana: "セ", romaji: "SE" },
        { kana: "ソ", romaji: "SO" },
      ],
    },
    {
      id: "ta",
      kana: [
        { kana: "タ", romaji: "TA" },
        { kana: "チ", romaji: "CHI" },
        { kana: "ツ", romaji: "TSU" },
        { kana: "テ", romaji: "TE" },
        { kana: "ト", romaji: "TO" },
      ],
    },
    {
      id: "na",
      kana: [
        { kana: "ナ", romaji: "NA" },
        { kana: "ニ", romaji: "NI" },
        { kana: "ヌ", romaji: "NU" },
        { kana: "ネ", romaji: "NE" },
        { kana: "ノ", romaji: "NO" },
      ],
    },
    {
      id: "ha",
      kana: [
        { kana: "ハ", romaji: "HA" },
        { kana: "ヒ", romaji: "HI" },
        { kana: "フ", romaji: "FU" },
        { kana: "ヘ", romaji: "HE" },
        { kana: "ホ", romaji: "HO" },
      ],
    },
    {
      id: "ma",
      kana: [
        { kana: "マ", romaji: "MA" },
        { kana: "ミ", romaji: "MI" },
        { kana: "ム", romaji: "MU" },
        { kana: "メ", romaji: "ME" },
        { kana: "モ", romaji: "MO" },
      ],
    },
    {
      id: "ya",
      kana: [
        { kana: "ヤ", romaji: "YA" },
        { kana: "ユ", romaji: "YU" },
        { kana: "ヨ", romaji: "YO" },
      ],
    },
    {
      id: "ra",
      kana: [
        { kana: "ラ", romaji: "RA" },
        { kana: "リ", romaji: "RI" },
        { kana: "ル", romaji: "RU" },
        { kana: "レ", romaji: "RE" },
        { kana: "ロ", romaji: "RO" },
      ],
    },
    {
      id: "wa",
      kana: [
        { kana: "ワ", romaji: "WA" },
        { kana: "ヲ", romaji: "WO" },
        { kana: "ン", romaji: "N" },
      ],
    },
  ];

  /**
   * Traditional gojūon chart columns for the ending (kana only, no romaji).
   * Read right-to-left by consonant row, top-to-bottom ア→オ within a column.
   * null = the classic empty chart position (ヤ/ワ columns).
   */
  const gojuonChartColumns = [
    { id: "a", cells: ["ア", "イ", "ウ", "エ", "オ"] },
    { id: "ka", cells: ["カ", "キ", "ク", "ケ", "コ"] },
    { id: "sa", cells: ["サ", "シ", "ス", "セ", "ソ"] },
    { id: "ta", cells: ["タ", "チ", "ツ", "テ", "ト"] },
    { id: "na", cells: ["ナ", "ニ", "ヌ", "ネ", "ノ"] },
    { id: "ha", cells: ["ハ", "ヒ", "フ", "ヘ", "ホ"] },
    { id: "ma", cells: ["マ", "ミ", "ム", "メ", "モ"] },
    { id: "ya", cells: ["ヤ", null, "ユ", null, "ヨ"] },
    { id: "ra", cells: ["ラ", "リ", "ル", "レ", "ロ"] },
    { id: "wa", cells: ["ワ", null, "ヲ", null, "ン"] },
  ];

  window.KmlKatakanaLessonData = { katakanaRows, gojuonChartColumns };
})();
