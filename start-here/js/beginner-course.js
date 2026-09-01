/**
 * Beginner pathway — room registry.
 *
 * Learner-facing name is "Room". URLs stay /start-here/lesson-N/.
 * Room 0 is The Genkan (romaji only — no げんかん / 玄関).
 *
 * mode:
 *   "guided-song" — Listen & Follow; JSON scenes follow audio time; no loop
 *   "study-room"  — learner-paced; optional looping atmosphereAudio,
 *                   or atmospherePool (shuffle; no single-file loop)
 *
 * romajiDefault is per room ("on" | "off"). The learner's explicit toggle
 * is stored separately and, once set, overrides the room default.
 * Lesson 9 is the current *proposed* switch to default off; that is data,
 * not a hard-coded rule in the toggle.
 *
 * encounteredKana: target kana only (gojūon boxes). Scenery / unopened
 * chunks do not belong here. Dakuten are not separate boxes.
 *
 * Acquisition does not require isolated drilling. If the learner has
 * repeatedly heard, understood, and sung a word, its kana may join.
 *
 * Gold is a temporary visual cue, not a particle legend.
 * .jp-signal (gold) means: pay attention to this signal right now.
 * Use it in the room that introduces a signal, and optionally in the
 * immediately following supported-recognition room. After that, ordinary
 * Japanese. Do not gold-code の・が・を・に・は merely because they are
 * particles. Authentic KML verses stay unannotated.
 * Current: を is gold in Rooms 18–19 only. Room 20 onward: normal.
 *
 * After Room 25: no more teaching songs before 46/46. Ordinary rooms only.
 * Do not change the approved 31/46 → 46/46 vocabulary path to make a finale.
 *
 * Room 40 is the hiragana reading epilogue after 46/46. Not a teaching
 * lesson, not an appendix, not a mashup. Hiragana-only song; no new kana.
 * Timed lyrics preserve sung Japanese exactly (みちても). No Room 41.
 *
 * YouTube media layer (prototypes Rooms 17 + 28):
 *   watchYoutubeId — unlisted embed id; empty keeps local delivery
 *   watchModes     — study-room dual UI: ["read","watch"]
 *   watchDefault   — "read" | "watch"
 * See start-here/js/beginner-watch.js. Do not delete local AV until dual
 * delivery is verified on production.
 *
 * Slice: Rooms 0–40. Opening song order:
 *   0 conversational あいうえお jazz (guided-song)
 *   1 日本語が楽しい
 *   3–4 What’s your name?
 *   5 Japanese food is good (guided-song)
 *   8 yes/no on Room 7 pictures (0 new kana)
 *   9 これは なんですか — retrieve untaught words (0 new kana)
 *   10 ねこが います — scenes; が is dakuten, not a box
 *   11 いすが あります — り joins (22/46)
 *   12 しずか — verse-native word; first authentic KML verse (0 new kana)
 *   13 ひかり — ひ joins (23/46); same 胃 verse, 光 now readable
 *   14 はしに — に joins (24/46); Lesson 1 九; first fully readable authentic line
 *   15 つりがね — つ joins (25/46); Lesson 2 唱. 九 is not shown.
 *   16 つくえ — く joins (26/46); 九 returns, now fully readable. No song.
 *   17 濡れた橋 — first interlude; listen-only film of the 九 poem. 0 new kana.
 *       After listen: “Where this came from” doorway to #kanji-nine
 *       (complete authentic verse only — not fragments).
 *   18 すしを たべます — playful food song; を joins (27/46). べ stays scenery.
 *       After the song, を is named as a little signal (not “direct object”).
 *   19 いしを こえ — quiet recognition; 0 new kana. Lesson 1 田, first line only.
 *   20 かわ — arrival at the mountain river; わ joins (28/46). Lesson 7 川, first line only.
 *   21 おと — still at the river; と joins (29/46). かわの おと. No 川 line 2,
 *       no だけが / ていた, no source doorway. こえ (越え) is not おと (音).
 *   22 まど — interior looking out; 0 new kana (29/46). Lesson 41 窓, first line only.
 *       とおい ひかり. Do not reteach ひかり. Do not pre-teach うつす.
 *   23 かねひとつ — quiet recognition; 0 new kana (29/46). Lesson 26 音, first line only.
 *       Do not reteach つりがね. No line 2. No source doorway. No 川 song.
 *   24 竹の音 — guided-song landscape; け and て join (31/46).
 *       け from たけ, て from はて. Do not teach だけが / ていた.
 *       Do not show 川. The 川 recording stays backstage.
 *   25 山の川 — second interlude; listen-only film of the complete 川 verse.
 *       0 new kana (31/46). river.png alone. Doorway to Lesson 7 #kanji-river.
 *   26 げんき — quiet unpacking; き joins (32/46). Word from Room 1, not new
 *       vocabulary. Do not replay the song. Do not teach 元気. Do not show 田.
 *   27 こんにちは — quiet unpacking; ち joins (33/46). Greeting from Rooms 3–4,
 *       not new vocabulary. Room 4 already unpacked it; に has since joined.
 *       Do not replay the name song. Do not explain は. Do not show よろしく.
 *   28 へや — ordinary picture room; へ joins (34/46). Do not replay たべます.
 *       Do not show 胃. Do not teach 部屋 as kanji. No doorway.
 *       Picture-noun labels: no Japanese 。 and no romaji period.
 *       Utterances / sentences keep normal punctuation.
 *   29 しあわせ — ordinary picture room; せ joins (35/46). Visual: part.png
 *       only. Do not show 分 / 分ける / わける / the verse / a doorway.
 *       Do not explain the lamps or sharing.
 *   30 みず — ordinary picture room; み joins (36/46). Visual: spring.png.
 *       Water itself, not かわ / うみ. Do not show 水 or 泉. Do not teach うみ.
 *   31 さくら — ordinary picture room; ら joins (37/46). Visual:
 *       train_cherry_blossoms.png. Do not show 桜. Do not preview そら.
 *   32 そら — ordinary picture room; そ joins (38/46). Visual: open_sea.png.
 *       Do not show 空. Do not teach うみ. Do not preview くも.
 *   33 くも — ordinary picture room; も joins (39/46). Visual: cloud.png.
 *       Do not show 雲. No weather lesson. No rain. No そら review.
 *       Do not teach もり. No verse. No doorway. No song. No extra kana.
 *   34 ゆめ — ordinary picture room; ゆ and め join together (41/46).
 *       Visual: dream.png. Do not show 夢. Do not teach ねむる / よる /
 *       あめ / ゆき. No verse. No doorway. No song.
 *   35 ねむる — ordinary picture room; む and る join together (43/46).
 *       Visual: bed.png. Do not show 眠 / 眠る. Not a grammar lesson.
 *       Do not review ゆめ. Do not introduce よる. No verse. No doorway.
 *   36 ふゆ — ordinary picture room; ふ joins (44/46). Visual: winter.png.
 *       Do not show 冬. Do not teach ゆき. Do not review ねむる.
 *       No verse. No doorway. No song.
 *   37 静かな部屋に — recognition; 0 new kana (44/46). Return to the
 *       Rooms 12–13 胃 verse, now readable. Visual: stomach.png.
 *       Exact original verse. No English/romaji under the verse.
 *       No vocabulary breakdown. No 胃 lesson. Doorway to Lesson 2
 *       #kanji-stomach.
 *   38 よろしく — quiet unpacking; よ and ろ join together (46/46).
 *       Word from Rooms 3–4, not new vocabulary. Visual: maria_bows.png.
 *       Do not show 宜しく. Do not explain the meaning. No verse.
 *       No doorway. No song.
 *   39 listen — curtain call after 46/46. YouTube Hiragana/Romaji film
 *       is the content. Continues to Room 40. 0 new kana. No puzzle.
 *   40 ことばが さく — hiragana reading epilogue. Guided-song, hiragana
 *       only. 0 new kana. After listen: hiragana from the sung lyrics.
 *       Terminus.
 *       Outward doors to Start Here, Room Index, Kanji Studies, and
 *       Ambient Kanji Gallery. No Room 41.
 *
 * Reading: you don't have to understand everything to understand something.
 * Help learners notice known pieces and signals. Unknown material can wait.
 * Do not repeat this as a slogan on every page.
 */
(function () {
  "use strict";

  var GOJUON_COLUMNS = [
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

  var L0 = ["あ", "い", "う", "え", "お"];
  var L1 = L0.concat(["は", "す", "か", "し", "た", "の"]);
  var L2 = L1;
  var L4 = L2.concat(["な", "ま", "ん", "さ", "こ"]);
  var L5 = L4;
  var L6 = L5.concat(["れ"]);
  var L7 = L6.concat(["ほ", "ね", "や", "ぬ"]);
  var L8 = L7;
  var L9 = L8;
  var L10 = L9;
  var L11 = L10.concat(["り"]);
  var L12 = L11;
  var L13 = L12.concat(["ひ"]);
  var L14 = L13.concat(["に"]);
  var L15 = L14.concat(["つ"]);
  var L16 = L15.concat(["く"]);
  var L17 = L16;
  var L18 = L17.concat(["を"]);
  var L19 = L18;
  var L20 = L19.concat(["わ"]);
  var L21 = L20.concat(["と"]);
  var L22 = L21;
  var L23 = L22;
  var L24 = L23.concat(["け", "て"]);
  var L25 = L24;
  var L26 = L25.concat(["き"]);
  var L27 = L26.concat(["ち"]);
  var L28 = L27.concat(["へ"]);
  var L29 = L28.concat(["せ"]);
  var L30 = L29.concat(["み"]);
  var L31 = L30.concat(["ら"]);
  var L32 = L31.concat(["そ"]);
  var L33 = L32.concat(["も"]);
  var L34 = L33.concat(["ゆ", "め"]);
  var L35 = L34.concat(["む", "る"]);
  var L36 = L35.concat(["ふ"]);
  var L37 = L36;
  var L38 = L37.concat(["よ", "ろ"]);
  var L39 = L38;
  var L40 = L39;

  var ATMOSPHERE_6_11 = [
    "../audio/lesson-6.mp3",
    "../audio/lesson-7.mp3",
    "../audio/lesson-8.mp3",
    "../audio/lesson-9.mp3",
    "../audio/lesson-10.mp3",
    "../audio/lesson-11.mp3",
  ];

  var lessons = {
    "0": {
      id: "0",
      roomLabel: "Room 0",
      displayName: "The Genkan",
      mode: "guided-song",
      dataSrc: "../data/rooms/0.json",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L0,
      newKana: L0,
      prev: null,
      next: "1",
    },
    "1": {
      id: "1",
      roomLabel: "Room 1",
      displayName: "日本語が楽しい",
      mode: "guided-song",
      dataSrc: "../data/rooms/1.json",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L1,
      newKana: ["は", "す", "か", "し", "た", "の"],
      prev: "0",
      next: "2",
      /* Unlisted YouTube: https://youtu.be/wMzT4WbGbpY */
      watchYoutubeId: "wMzT4WbGbpY",
    },
    "2": {
      id: "2",
      roomLabel: "Room 2",
      displayName: "Begin seeing Japanese",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-2.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L2,
      newKana: ["は", "す", "か", "し"],
      prev: "1",
      next: "3",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/bOIWwSUSuVU */
      watchYoutubeId: "bOIWwSUSuVU",
    },
    "3": {
      id: "3",
      roomLabel: "Room 3",
      displayName: "What’s your name?",
      mode: "guided-song",
      dataSrc: "../data/rooms/3.json",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L2,
      newKana: [],
      prev: "2",
      next: "4",
      /* Unlisted YouTube: https://youtu.be/nl8vBOgPLjE */
      watchYoutubeId: "nl8vBOgPLjE",
    },
    "4": {
      id: "4",
      roomLabel: "Room 4",
      displayName: "Reading names",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-4.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L4,
      newKana: ["な", "ま", "ん", "さ", "こ"],
      prev: "3",
      next: "5",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/YHwmkzt1xzs */
      watchYoutubeId: "YHwmkzt1xzs",
    },
    "5": {
      id: "5",
      roomLabel: "Room 5",
      displayName: "Japanese food is good",
      mode: "guided-song",
      dataSrc: "../data/rooms/5.json",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L5,
      newKana: [],
      prev: "4",
      next: "6",
      /* Unlisted YouTube: https://youtu.be/H09lWLQY9Rg */
      watchYoutubeId: "H09lWLQY9Rg",
    },
    "6": {
      id: "6",
      roomLabel: "Room 6",
      displayName: "This is sushi",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-6.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L6,
      newKana: ["れ"],
      prev: "5",
      next: "7",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/eugosPkh6lw */
      watchYoutubeId: "eugosPkh6lw",
    },
    "7": {
      id: "7",
      roomLabel: "Room 7",
      displayName: "Four pictures",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-7.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L7,
      newKana: ["ほ", "ね", "や", "ぬ"],
      prev: "6",
      next: "8",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/xPnZZiNakEQ */
      watchYoutubeId: "xPnZZiNakEQ",
    },
    "8": {
      id: "8",
      roomLabel: "Room 8",
      displayName: "これは ねこですか",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-8.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L8,
      newKana: [],
      prev: "7",
      next: "9",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/ndd6DTzSArM */
      watchYoutubeId: "ndd6DTzSArM",
    },
    "9": {
      id: "9",
      roomLabel: "Room 9",
      displayName: "これは なんですか",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-9.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L9,
      newKana: [],
      prev: "8",
      next: "10",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/JVDY9WuwVAE */
      watchYoutubeId: "JVDY9WuwVAE",
    },
    "10": {
      id: "10",
      roomLabel: "Room 10",
      displayName: "ねこが います",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-10.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L10,
      newKana: [],
      prev: "9",
      next: "11",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/uRvdyJLWRus */
      watchYoutubeId: "uRvdyJLWRus",
    },
    "11": {
      id: "11",
      roomLabel: "Room 11",
      displayName: "いすが あります",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-11.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L11,
      newKana: ["り"],
      prev: "10",
      next: "12",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/O_mGmOI7OxY */
      watchYoutubeId: "O_mGmOI7OxY",
    },
    "12": {
      id: "12",
      roomLabel: "Room 12",
      displayName: "しずか",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-7.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L12,
      newKana: [],
      prev: "11",
      next: "13",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/eEYuKSTxEVQ */
      watchYoutubeId: "eEYuKSTxEVQ",
    },
    "13": {
      id: "13",
      roomLabel: "Room 13",
      displayName: "ひかり",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-8.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L13,
      newKana: ["ひ"],
      prev: "12",
      next: "14",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/fl4Ei1ae0c4 */
      watchYoutubeId: "fl4Ei1ae0c4",
    },
    "14": {
      id: "14",
      roomLabel: "Room 14",
      displayName: "はしに",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-9.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L14,
      newKana: ["に"],
      prev: "13",
      next: "15",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/JCKDaBA6v4c */
      watchYoutubeId: "JCKDaBA6v4c",
    },
    "15": {
      id: "15",
      roomLabel: "Room 15",
      displayName: "つりがね",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-6.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L15,
      newKana: ["つ"],
      prev: "14",
      next: "16",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/ehG3GfBtsPM */
      watchYoutubeId: "ehG3GfBtsPM",
    },
    "16": {
      id: "16",
      roomLabel: "Room 16",
      displayName: "つくえ",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-11.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L16,
      newKana: ["く"],
      prev: "15",
      next: "17",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/Z3sbTWtAMng */
      watchYoutubeId: "Z3sbTWtAMng",
    },
    "17": {
      id: "17",
      roomLabel: "Room 17",
      displayName: "濡れた橋",
      mode: "guided-song",
      dataSrc: "../data/rooms/17.json",
      romajiDefault: "off",
      showPuzzle: false,
      showReferenceChart: false,
      encounteredKana: L17,
      newKana: [],
      prev: "16",
      next: "18",
      /* Unlisted YouTube: https://youtu.be/bCEEh4vydVI */
      watchYoutubeId: "bCEEh4vydVI",
    },
    "18": {
      id: "18",
      roomLabel: "Room 18",
      displayName: "すしを たべます",
      mode: "guided-song",
      dataSrc: "../data/rooms/18.json",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L18,
      newKana: ["を"],
      prev: "17",
      next: "19",
      /* Unlisted YouTube: https://youtu.be/Ap9sX9cwa1g */
      watchYoutubeId: "Ap9sX9cwa1g",
    },
    "19": {
      id: "19",
      roomLabel: "Room 19",
      displayName: "いしを こえ",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L19,
      newKana: [],
      prev: "18",
      next: "20",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/OZht_7jxSlg */
      watchYoutubeId: "OZht_7jxSlg",
    },
    "20": {
      id: "20",
      roomLabel: "Room 20",
      displayName: "かわ",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L20,
      newKana: ["わ"],
      prev: "19",
      next: "21",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/QY9dQia1wqM */
      watchYoutubeId: "QY9dQia1wqM",
    },
    "21": {
      id: "21",
      roomLabel: "Room 21",
      displayName: "おと",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L21,
      newKana: ["と"],
      prev: "20",
      next: "22",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/1dnFc8gnqtk */
      watchYoutubeId: "1dnFc8gnqtk",
    },
    "22": {
      id: "22",
      roomLabel: "Room 22",
      displayName: "まど",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L22,
      newKana: [],
      prev: "21",
      next: "23",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/XL3GdJsIC70 */
      watchYoutubeId: "XL3GdJsIC70",
    },
    "23": {
      id: "23",
      roomLabel: "Room 23",
      displayName: "かねひとつ",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L23,
      newKana: [],
      prev: "22",
      next: "24",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/bEt2ANdYl6k */
      watchYoutubeId: "bEt2ANdYl6k",
    },
    "24": {
      id: "24",
      roomLabel: "Room 24",
      displayName: "竹の音",
      mode: "guided-song",
      dataSrc: "../data/rooms/24.json",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L24,
      newKana: ["け", "て"],
      prev: "23",
      next: "25",
      /* Unlisted YouTube: https://youtu.be/DyrWcHptIck */
      watchYoutubeId: "DyrWcHptIck",
    },
    "25": {
      id: "25",
      roomLabel: "Room 25",
      displayName: "山の川",
      mode: "guided-song",
      dataSrc: "../data/rooms/25.json",
      romajiDefault: "off",
      showPuzzle: false,
      showReferenceChart: false,
      encounteredKana: L25,
      newKana: [],
      prev: "24",
      next: "26",
      /* Unlisted YouTube: https://youtu.be/s-MtpLw_Jzo */
      watchYoutubeId: "s-MtpLw_Jzo",
    },
    "26": {
      id: "26",
      roomLabel: "Room 26",
      displayName: "げんき",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L26,
      newKana: ["き"],
      prev: "25",
      next: "27",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/WB3HRfXg13U */
      watchYoutubeId: "WB3HRfXg13U",
    },
    "27": {
      id: "27",
      roomLabel: "Room 27",
      displayName: "こんにちは",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L27,
      newKana: ["ち"],
      prev: "26",
      next: "28",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/qjLhfXWJEu0 */
      watchYoutubeId: "qjLhfXWJEu0",
    },
    "28": {
      id: "28",
      roomLabel: "Room 28",
      displayName: "へや",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L28,
      newKana: ["へ"],
      prev: "27",
      next: "29",
      /* Prototype: Read page / Watch & Listen film (unlisted YouTube). */
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/EuQffj738xw */
      watchYoutubeId: "EuQffj738xw",
    },
    "29": {
      id: "29",
      roomLabel: "Room 29",
      displayName: "しあわせ",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L29,
      newKana: ["せ"],
      prev: "28",
      next: "30",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/FDaYx57khhM */
      watchYoutubeId: "FDaYx57khhM",
    },
    "30": {
      id: "30",
      roomLabel: "Room 30",
      displayName: "みず",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L30,
      newKana: ["み"],
      prev: "29",
      next: "31",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/xwAGvYsMre4 */
      watchYoutubeId: "xwAGvYsMre4",
    },
    "31": {
      id: "31",
      roomLabel: "Room 31",
      displayName: "さくら",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L31,
      newKana: ["ら"],
      prev: "30",
      next: "32",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/74gwg2yCZxU */
      watchYoutubeId: "74gwg2yCZxU",
    },
    "32": {
      id: "32",
      roomLabel: "Room 32",
      displayName: "そら",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L32,
      newKana: ["そ"],
      prev: "31",
      next: "33",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/LIcZXG1qqv0 */
      watchYoutubeId: "LIcZXG1qqv0",
    },
    "33": {
      id: "33",
      roomLabel: "Room 33",
      displayName: "くも",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L33,
      newKana: ["も"],
      prev: "32",
      next: "34",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/Oh1aMNPjnYM */
      watchYoutubeId: "Oh1aMNPjnYM",
    },
    "34": {
      id: "34",
      roomLabel: "Room 34",
      displayName: "ゆめ",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L34,
      newKana: ["ゆ", "め"],
      prev: "33",
      next: "35",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/z7R5kUhBxOM */
      watchYoutubeId: "z7R5kUhBxOM",
    },
    "35": {
      id: "35",
      roomLabel: "Room 35",
      displayName: "ねむる",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L35,
      newKana: ["む", "る"],
      prev: "34",
      next: "36",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/g6OBP7LkSLc */
      watchYoutubeId: "g6OBP7LkSLc",
    },
    "36": {
      id: "36",
      roomLabel: "Room 36",
      displayName: "ふゆ",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L36,
      newKana: ["ふ"],
      prev: "35",
      next: "37",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/9giwZaUPRVU */
      watchYoutubeId: "9giwZaUPRVU",
    },
    "37": {
      id: "37",
      roomLabel: "Room 37",
      displayName: "静かな部屋に",
      mode: "study-room",
      atmosphereAudio: "../audio/lesson-7.mp3",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L37,
      newKana: [],
      prev: "36",
      next: "38",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/aZWBy2dnvbw */
      watchYoutubeId: "aZWBy2dnvbw",
    },
    "38": {
      id: "38",
      roomLabel: "Room 38",
      displayName: "よろしく",
      mode: "study-room",
      atmospherePool: ATMOSPHERE_6_11,
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L38,
      newKana: ["よ", "ろ"],
      prev: "37",
      next: "39",
      watchModes: ["read", "watch"],
      watchDefault: "read",
      /* Unlisted YouTube: https://youtu.be/Ay7Wig4Xtbk */
      watchYoutubeId: "Ay7Wig4Xtbk",
    },
    "39": {
      id: "39",
      roomLabel: "Room 39",
      displayName: "Listen",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: false,
      showReferenceChart: false,
      encounteredKana: L39,
      newKana: [],
      prev: "38",
      next: "40",
    },
    "40": {
      id: "40",
      roomLabel: "Room 40",
      displayName: "ことばが さく",
      mode: "guided-song",
      dataSrc: "../data/rooms/40.json",
      romajiDefault: "off",
      showPuzzle: false,
      showReferenceChart: true,
      encounteredKana: L40,
      newKana: [],
      prev: "39",
      next: null,
      /* Unlisted YouTube: https://youtu.be/VqCrT25rCl4 */
      watchYoutubeId: "VqCrT25rCl4",
    },
  };

  window.KmlBeginnerCourse = {
    romajiStorageKey: "kml-beginner-romaji",
    musicStorageKey: "kml-beginner-study-music",
    watchStorageKey: "kml-beginner-watch-mode",
    gojuonColumns: GOJUON_COLUMNS,
    boxCount: 46,
    lessons: lessons,
  };
})();
