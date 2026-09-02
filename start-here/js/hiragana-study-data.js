/**
 * Conventional hiragana row content for Start Here rooms.
 * Linked from beginner-course.js via hiraganaStudy id (1–10).
 * Basic gojūon only — no dakuten, handakuten, or ゃゅょ.
 */
(function (global) {
  "use strict";

  global.KmlHiraganaStudy = {
    rows: {
      "1": {
        id: "1",
        label: "あ行",
        kana: [
          { kana: "あ", romaji: "a" },
          { kana: "い", romaji: "i" },
          { kana: "う", romaji: "u" },
          { kana: "え", romaji: "e" },
          { kana: "お", romaji: "o" }
        ],
        vocabulary: [
          { word: "あい", meaning: "love" },
          { word: "いえ", meaning: "house" },
          { word: "うえ", meaning: "above" },
          { word: "あお", meaning: "blue" }
        ]
      },
      "2": {
        id: "2",
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
      "3": {
        id: "3",
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
      "4": {
        id: "4",
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
      "5": {
        id: "5",
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
      "6": {
        id: "6",
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
      "7": {
        id: "7",
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
      "8": {
        id: "8",
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
      "9": {
        id: "9",
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
      "10": {
        id: "10",
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
    }
  };
})(window);
