/**
 * Static study track for Start Here rooms.
 *
 * One ordered sequence of study units. Content length is independent of
 * how many Start Here rooms exist — rooms point into this track via
 * `staticStudy` on the room registry.
 *
 * After the hiragana gojūon sequence, the same track continues into
 * katakana (same unit shape: script + kana + vocabulary).
 * Katakana units are encounter-only: no teaching prose in the data.
 */
(function (global) {
  "use strict";

  var units = {
    "h-a": {
      id: "h-a",
      script: "hiragana",
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
    },
    "k-a": {
      id: "k-a",
      script: "katakana",
      label: "ア行",
      kana: [
        { kana: "ア", romaji: "a" },
        { kana: "イ", romaji: "i" },
        { kana: "ウ", romaji: "u" },
        { kana: "エ", romaji: "e" },
        { kana: "オ", romaji: "o" }
      ],
      vocabulary: [
        { word: "エア", meaning: "air" }
      ]
    },
    "k-ka": {
      id: "k-ka",
      script: "katakana",
      label: "カ行",
      kana: [
        { kana: "カ", romaji: "ka" },
        { kana: "キ", romaji: "ki" },
        { kana: "ク", romaji: "ku" },
        { kana: "ケ", romaji: "ke" },
        { kana: "コ", romaji: "ko" }
      ],
      vocabulary: [
        { word: "イカ", meaning: "squid" },
        { word: "キウイ", meaning: "kiwi" },
        { word: "ココア", meaning: "cocoa" },
        { word: "カカオ", meaning: "cacao" }
      ]
    },
    "k-sa": {
      id: "k-sa",
      script: "katakana",
      label: "サ行",
      kana: [
        { kana: "サ", romaji: "sa" },
        { kana: "シ", romaji: "shi" },
        { kana: "ス", romaji: "su" },
        { kana: "セ", romaji: "se" },
        { kana: "ソ", romaji: "so" }
      ],
      vocabulary: [
        { word: "アイス", meaning: "ice cream" },
        { word: "キス", meaning: "kiss" },
        { word: "スイス", meaning: "Switzerland" },
        { word: "スカイ", meaning: "sky" }
      ]
    },
    "k-ta": {
      id: "k-ta",
      script: "katakana",
      label: "タ行",
      kana: [
        { kana: "タ", romaji: "ta" },
        { kana: "チ", romaji: "chi" },
        { kana: "ツ", romaji: "tsu" },
        { kana: "テ", romaji: "te" },
        { kana: "ト", romaji: "to" }
      ],
      vocabulary: [
        { word: "テスト", meaning: "test" },
        { word: "タコス", meaning: "tacos" },
        { word: "テキスト", meaning: "text" },
        { word: "サイト", meaning: "site" },
        { word: "コスト", meaning: "cost" }
      ]
    },
    "k-na": {
      id: "k-na",
      script: "katakana",
      label: "ナ行",
      kana: [
        { kana: "ナ", romaji: "na" },
        { kana: "ニ", romaji: "ni" },
        { kana: "ヌ", romaji: "nu" },
        { kana: "ネ", romaji: "ne" },
        { kana: "ノ", romaji: "no" }
      ],
      vocabulary: [
        { word: "ネコ", meaning: "cat" },
        { word: "テニス", meaning: "tennis" },
        { word: "ネクタイ", meaning: "necktie" },
        { word: "ナイス", meaning: "nice" },
        { word: "ナイト", meaning: "night" }
      ]
    },
    "k-ha": {
      id: "k-ha",
      script: "katakana",
      label: "ハ行",
      kana: [
        { kana: "ハ", romaji: "ha" },
        { kana: "ヒ", romaji: "hi" },
        { kana: "フ", romaji: "fu" },
        { kana: "ヘ", romaji: "he" },
        { kana: "ホ", romaji: "ho" }
      ],
      vocabulary: [
        { word: "ヘア", meaning: "hair" },
        { word: "ホスト", meaning: "host" },
        { word: "オフ", meaning: "off" },
        { word: "ハイ", meaning: "hi" }
      ]
    },
    "k-ma": {
      id: "k-ma",
      script: "katakana",
      label: "マ行",
      kana: [
        { kana: "マ", romaji: "ma" },
        { kana: "ミ", romaji: "mi" },
        { kana: "ム", romaji: "mu" },
        { kana: "メ", romaji: "me" },
        { kana: "モ", romaji: "mo" }
      ],
      vocabulary: [
        { word: "トマト", meaning: "tomato" },
        { word: "マスク", meaning: "mask" },
        { word: "キムチ", meaning: "kimchi" },
        { word: "マイク", meaning: "mic" },
        { word: "メキシコ", meaning: "Mexico" }
      ]
    },
    "k-ya": {
      id: "k-ya",
      script: "katakana",
      label: "ヤ行",
      kana: [
        { kana: "ヤ", romaji: "ya" },
        { kana: "ユ", romaji: "yu" },
        { kana: "ヨ", romaji: "yo" }
      ],
      vocabulary: [
        { word: "タイヤ", meaning: "tire" },
        { word: "マヨ", meaning: "mayo" },
        { word: "ヤシ", meaning: "palm" }
      ]
    },
    "k-ra": {
      id: "k-ra",
      script: "katakana",
      label: "ラ行",
      kana: [
        { kana: "ラ", romaji: "ra" },
        { kana: "リ", romaji: "ri" },
        { kana: "ル", romaji: "ru" },
        { kana: "レ", romaji: "re" },
        { kana: "ロ", romaji: "ro" }
      ],
      vocabulary: [
        { word: "ホテル", meaning: "hotel" },
        { word: "カメラ", meaning: "camera" },
        { word: "カラオケ", meaning: "karaoke" },
        { word: "トイレ", meaning: "toilet" },
        { word: "ミルク", meaning: "milk" }
      ]
    },
    "k-wa": {
      id: "k-wa",
      script: "katakana",
      label: "ワ行・ン",
      kana: [
        { kana: "ワ", romaji: "wa" },
        { kana: "ヲ", romaji: "o" },
        { kana: "ン", romaji: "n" }
      ],
      vocabulary: [
        { word: "レモン", meaning: "lemon" },
        { word: "フロント", meaning: "front desk" },
        { word: "エアコン", meaning: "air conditioner" },
        { word: "ワイン", meaning: "wine" },
        { word: "ハワイ", meaning: "Hawaii" }
      ]
    },
    "k-choon": {
      id: "k-choon",
      script: "katakana",
      label: "ー",
      kana: [{ kana: "ー", romaji: "" }],
      vocabulary: [
        { word: "コーヒー", meaning: "coffee" },
        { word: "ラーメン", meaning: "ramen" },
        { word: "ケーキ", meaning: "cake" },
        { word: "タクシー", meaning: "taxi" },
        { word: "カレー", meaning: "curry" }
      ]
    },
    "k-dakuten": {
      id: "k-dakuten",
      script: "katakana",
      label: "゛゜",
      kana: [
        { kana: "ガ", romaji: "ga" },
        { kana: "ギ", romaji: "gi" },
        { kana: "グ", romaji: "gu" },
        { kana: "ゲ", romaji: "ge" },
        { kana: "ゴ", romaji: "go" },
        { kana: "ザ", romaji: "za" },
        { kana: "ジ", romaji: "ji" },
        { kana: "ズ", romaji: "zu" },
        { kana: "ゼ", romaji: "ze" },
        { kana: "ゾ", romaji: "zo" },
        { kana: "ダ", romaji: "da" },
        { kana: "ヂ", romaji: "ji" },
        { kana: "ヅ", romaji: "zu" },
        { kana: "デ", romaji: "de" },
        { kana: "ド", romaji: "do" },
        { kana: "バ", romaji: "ba" },
        { kana: "ビ", romaji: "bi" },
        { kana: "ブ", romaji: "bu" },
        { kana: "ベ", romaji: "be" },
        { kana: "ボ", romaji: "bo" },
        { kana: "パ", romaji: "pa" },
        { kana: "ピ", romaji: "pi" },
        { kana: "プ", romaji: "pu" },
        { kana: "ペ", romaji: "pe" },
        { kana: "ポ", romaji: "po" }
      ],
      vocabulary: [
        { word: "パン", meaning: "bread" },
        { word: "ドア", meaning: "door" },
        { word: "テレビ", meaning: "TV" },
        { word: "バス", meaning: "bus" },
        { word: "コンビニ", meaning: "convenience store" }
      ]
    },
    "k-sokuon": {
      id: "k-sokuon",
      script: "katakana",
      label: "ッ",
      kana: [{ kana: "ッ", romaji: "" }],
      vocabulary: [
        { word: "ベッド", meaning: "bed" },
        { word: "カップ", meaning: "cup" },
        { word: "グッド", meaning: "good" },
        { word: "ホットドッグ", meaning: "hot dog" }
      ]
    },
    "k-youon": {
      id: "k-youon",
      script: "katakana",
      label: "ャュョ",
      kana: [
        { kana: "ャ", romaji: "" },
        { kana: "ュ", romaji: "" },
        { kana: "ョ", romaji: "" }
      ],
      vocabulary: [
        { word: "メニュー", meaning: "menu" },
        { word: "ジュース", meaning: "juice" },
        { word: "チョコレート", meaning: "chocolate" },
        { word: "シャワー", meaning: "shower" },
        { word: "ニュース", meaning: "news" }
      ]
    },
    "k-reading": {
      id: "k-reading",
      script: "katakana",
      gloss: "english",
      lead: "You know the katakana now. How many of these words can you read?",
      close: "Ready to hear them?",
      kana: [],
      vocabulary: [
        { word: "カフェ", meaning: "café" },
        { word: "コーヒー", meaning: "coffee" },
        { word: "ミルク", meaning: "milk" },
        { word: "ウインナー", meaning: "wiener" },
        { word: "サラダ", meaning: "salad" },
        { word: "シチュー", meaning: "stew" },
        { word: "エビフライ", meaning: "fried shrimp" },
        { word: "ハンバーガー", meaning: "hamburger" },
        { word: "アイスクリーム", meaning: "ice cream" },
        { word: "ケーキ", meaning: "cake" },
        { word: "メロン", meaning: "melon" },
        { word: "マンゴー", meaning: "mango" },
        { word: "タルト", meaning: "tart" },
        { word: "モンブラン", meaning: "Mont Blanc" },
        { word: "ヌードル", meaning: "noodles" },
        { word: "ソーセージ", meaning: "sausage" },
        { word: "ホットドッグ", meaning: "hot dog" },
        { word: "ワッフル", meaning: "waffle" },
        { word: "ヨーグルト", meaning: "yogurt" },
        { word: "オムレツ", meaning: "omelet" },
        { word: "セロリ", meaning: "celery" },
        { word: "ニンジン", meaning: "carrot" },
        { word: "ネギトロ", meaning: "negitoro" },
        { word: "テーブル", meaning: "table" },
        { word: "クッキー", meaning: "cookie" },
        { word: "カタカナ", meaning: "katakana" }
      ]
    }
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
      "h-wa",
      "k-a",
      "k-ka",
      "k-sa",
      "k-ta",
      "k-na",
      "k-ha",
      "k-ma",
      "k-ya",
      "k-ra",
      "k-wa",
      "k-choon",
      "k-dakuten",
      "k-sokuon",
      "k-youon",
      "k-reading"
    ]
  };
})(window);
