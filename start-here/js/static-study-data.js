/**
 * Static study track for Start Here rooms.
 *
 * One ordered sequence of study units. Content length is independent of
 * how many Start Here rooms exist — rooms point into this track via
 * `staticStudy` on the room registry.
 *
 * After the hiragana gojūon sequence, the same track continues into
 * katakana (same unit shape: script + kana + vocabulary). Katakana
 * units are not authored yet; progression will be decided after the
 * hiragana prototype review.
 *
 * Basic gojūon only in the opening set — no dakuten, handakuten, or ゃゅょ.
 */
(function (global) {
  "use strict";

  var units = {
    "h-a": {
      id: "h-a",
      script: "hiragana",
      label: "あ行",
      pronunciationNote: "Think Spanish rather than English.",
      kana: [
        { kana: "あ", romaji: "a" },
        { kana: "い", romaji: "i" },
        { kana: "う", romaji: "u" },
        { kana: "え", romaji: "e" },
        { kana: "お", romaji: "o" }
      ],
      vocabulary: [
        { word: "あい", romaji: "ai", meaning: "love" },
        { word: "いえ", romaji: "ie", meaning: "house" },
        { word: "うえ", romaji: "ue", meaning: "above" },
        { word: "あお", romaji: "ao", meaning: "blue" }
      ]
    },
    "h-ka": {
      id: "h-ka",
      script: "hiragana",
      label: "か行",
      kana: [
        { kana: "か", romaji: "ka" },
        { kana: "き", romaji: "ki" },
        { kana: "く", romaji: "ku" },
        { kana: "け", romaji: "ke" },
        { kana: "こ", romaji: "ko" }
      ],
      vocabulary: [
        { word: "かお", meaning: "face" },
        { word: "えき", meaning: "station" },
        { word: "いけ", meaning: "pond" },
        { word: "こえ", meaning: "voice" },
        { word: "ここ", meaning: "here" }
      ]
    },
    "h-sa": {
      id: "h-sa",
      script: "hiragana",
      label: "さ行",
      kana: [
        { kana: "さ", romaji: "sa" },
        { kana: "し", romaji: "shi" },
        { kana: "す", romaji: "su" },
        { kana: "せ", romaji: "se" },
        { kana: "そ", romaji: "so" }
      ],
      vocabulary: [
        { word: "すし", meaning: "sushi" },
        { word: "いす", meaning: "chair" },
        { word: "かさ", meaning: "umbrella" },
        { word: "そこ", meaning: "there" },
        { word: "すき", meaning: "like" }
      ]
    },
    "h-ta": {
      id: "h-ta",
      script: "hiragana",
      label: "た行",
      kana: [
        { kana: "た", romaji: "ta" },
        { kana: "ち", romaji: "chi" },
        { kana: "つ", romaji: "tsu" },
        { kana: "て", romaji: "te" },
        { kana: "と", romaji: "to" }
      ],
      vocabulary: [
        { word: "した", meaning: "below" },
        { word: "くつ", meaning: "shoes" },
        { word: "つくえ", meaning: "desk" },
        { word: "とけい", meaning: "clock" },
        { word: "たこ", meaning: "octopus" }
      ]
    },
    "h-na": {
      id: "h-na",
      script: "hiragana",
      label: "な行",
      kana: [
        { kana: "な", romaji: "na" },
        { kana: "に", romaji: "ni" },
        { kana: "ぬ", romaji: "nu" },
        { kana: "ね", romaji: "ne" },
        { kana: "の", romaji: "no" }
      ],
      vocabulary: [
        { word: "ねこ", meaning: "cat" },
        { word: "いぬ", meaning: "dog" },
        { word: "なつ", meaning: "summer" },
        { word: "にく", meaning: "meat" },
        { word: "なに", meaning: "what" }
      ]
    },
    "h-ha": {
      id: "h-ha",
      script: "hiragana",
      label: "は行",
      kana: [
        { kana: "は", romaji: "ha" },
        { kana: "ひ", romaji: "hi" },
        { kana: "ふ", romaji: "fu" },
        { kana: "へ", romaji: "he" },
        { kana: "ほ", romaji: "ho" }
      ],
      vocabulary: [
        { word: "はな", meaning: "flower" },
        { word: "ひと", meaning: "person" },
        { word: "ふね", meaning: "boat" },
        { word: "ほし", meaning: "star" },
        { word: "はし", meaning: "bridge" }
      ]
    },
    "h-ma": {
      id: "h-ma",
      script: "hiragana",
      label: "ま行",
      kana: [
        { kana: "ま", romaji: "ma" },
        { kana: "み", romaji: "mi" },
        { kana: "む", romaji: "mu" },
        { kana: "め", romaji: "me" },
        { kana: "も", romaji: "mo" }
      ],
      vocabulary: [
        { word: "みせ", meaning: "shop" },
        { word: "みみ", meaning: "ears" },
        { word: "まえ", meaning: "front" },
        { word: "あめ", meaning: "rain" },
        { word: "もの", meaning: "thing" }
      ]
    },
    "h-ya": {
      id: "h-ya",
      script: "hiragana",
      label: "や行",
      kana: [
        { kana: "や", romaji: "ya" },
        { kana: "ゆ", romaji: "yu" },
        { kana: "よ", romaji: "yo" }
      ],
      vocabulary: [
        { word: "やま", meaning: "mountain" },
        { word: "ゆき", meaning: "snow" },
        { word: "よる", meaning: "night" },
        { word: "やさい", meaning: "vegetables" },
        { word: "ゆめ", meaning: "dream" }
      ]
    },
    "h-ra": {
      id: "h-ra",
      script: "hiragana",
      label: "ら行",
      kana: [
        { kana: "ら", romaji: "ra" },
        { kana: "り", romaji: "ri" },
        { kana: "る", romaji: "ru" },
        { kana: "れ", romaji: "re" },
        { kana: "ろ", romaji: "ro" }
      ],
      vocabulary: [
        { word: "そら", meaning: "sky" },
        { word: "さくら", meaning: "cherry blossom" },
        { word: "くるま", meaning: "car" },
        { word: "とり", meaning: "bird" },
        { word: "ひる", meaning: "daytime" }
      ]
    },
    "h-wa": {
      id: "h-wa",
      script: "hiragana",
      label: "わ行・ん",
      kana: [
        { kana: "わ", romaji: "wa" },
        { kana: "を", romaji: "o" },
        { kana: "ん", romaji: "n" }
      ],
      vocabulary: [
        { word: "かわ", meaning: "river" },
        { word: "ほん", meaning: "book" },
        { word: "にわ", meaning: "garden" },
        { word: "わたし", meaning: "I" },
        { word: "こんにちは", meaning: "hello" }
      ]
    }
    /* Katakana continues in the same units map, e.g.:
     * "k-a": { id: "k-a", script: "katakana", label: "ア行", kana: [...], vocabulary: [...] }
     * Append those ids to `sequence` after the hiragana block.
     */
  };

  global.KmlStaticStudy = {
    units: units,
    /* Planned track order. Only units that exist are listed.
       Extend with katakana ids when those units are authored. */
    sequence: [
      "h-a",
      "h-ka",
      "h-sa",
      "h-ta",
      "h-na",
      "h-ha",
      "h-ma",
      "h-ya",
      "h-ra",
      "h-wa"
    ]
  };
})(window);
