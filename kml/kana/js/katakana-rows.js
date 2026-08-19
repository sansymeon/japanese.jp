/**
 * Basic katakana pathway — 46 gojūon only.
 * Slugs match /kml/kana/katakana/{slug}/ (Hepburn row head, as /a/).
 */
(function (global) {
  "use strict";

  global.KmlKatakanaRows = [
    {
      slug: "a",
      title: "アイウエオ",
      kana: [
        { kana: "ア", romaji: "a" },
        { kana: "イ", romaji: "i" },
        { kana: "ウ", romaji: "u" },
        { kana: "エ", romaji: "e" },
        { kana: "オ", romaji: "o" }
      ]
    },
    {
      slug: "ka",
      title: "カキクケコ",
      kana: [
        { kana: "カ", romaji: "ka" },
        { kana: "キ", romaji: "ki" },
        { kana: "ク", romaji: "ku" },
        { kana: "ケ", romaji: "ke" },
        { kana: "コ", romaji: "ko" }
      ]
    },
    {
      slug: "sa",
      title: "サシスセソ",
      kana: [
        { kana: "サ", romaji: "sa" },
        { kana: "シ", romaji: "shi" },
        { kana: "ス", romaji: "su" },
        { kana: "セ", romaji: "se" },
        { kana: "ソ", romaji: "so" }
      ]
    },
    {
      slug: "ta",
      title: "タチツテト",
      kana: [
        { kana: "タ", romaji: "ta" },
        { kana: "チ", romaji: "chi" },
        { kana: "ツ", romaji: "tsu" },
        { kana: "テ", romaji: "te" },
        { kana: "ト", romaji: "to" }
      ]
    },
    {
      slug: "na",
      title: "ナニヌネノ",
      kana: [
        { kana: "ナ", romaji: "na" },
        { kana: "ニ", romaji: "ni" },
        { kana: "ヌ", romaji: "nu" },
        { kana: "ネ", romaji: "ne" },
        { kana: "ノ", romaji: "no" }
      ]
    },
    {
      slug: "ha",
      title: "ハヒフヘホ",
      kana: [
        { kana: "ハ", romaji: "ha" },
        { kana: "ヒ", romaji: "hi" },
        { kana: "フ", romaji: "fu" },
        { kana: "ヘ", romaji: "he" },
        { kana: "ホ", romaji: "ho" }
      ]
    },
    {
      slug: "ma",
      title: "マミムメモ",
      kana: [
        { kana: "マ", romaji: "ma" },
        { kana: "ミ", romaji: "mi" },
        { kana: "ム", romaji: "mu" },
        { kana: "メ", romaji: "me" },
        { kana: "モ", romaji: "mo" }
      ]
    },
    {
      slug: "ya",
      title: "ヤユヨ",
      kana: [
        { kana: "ヤ", romaji: "ya" },
        { kana: "ユ", romaji: "yu" },
        { kana: "ヨ", romaji: "yo" }
      ]
    },
    {
      slug: "ra",
      title: "ラリルレロ",
      kana: [
        { kana: "ラ", romaji: "ra" },
        { kana: "リ", romaji: "ri" },
        { kana: "ル", romaji: "ru" },
        { kana: "レ", romaji: "re" },
        { kana: "ロ", romaji: "ro" }
      ]
    },
    {
      slug: "wa",
      title: "ワヲ",
      kana: [
        { kana: "ワ", romaji: "wa" },
        { kana: "ヲ", romaji: "o" }
      ]
    },
    {
      slug: "n",
      title: "ン",
      kana: [
        { kana: "ン", romaji: "n" }
      ]
    }
  ];
})(window);
