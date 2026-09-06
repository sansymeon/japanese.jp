/**
 * Beginner pathway — room registry.
 *
 * Learner-facing name is "Room". URLs stay /start-here/lesson-N/.
 * Room 0 is The Genkan (romaji only — no げんかん / 玄関).
 *
 * mode:
 *   "guided-song" — historically Listen & Follow JSON; room film is YouTube
 *   "study-room"  — learner-paced study below the YouTube doorway
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
 * Room 40 is すらすら言える / Hiragana in Rhythm. Room 41 is 言葉が咲く |
 * Words in Bloom (production Room 40 lower lesson, under the film).
 * Room 42 is Shiba-kun Overture, the Start Here terminus.
 *
 * Slice: Rooms 0–42. Opening song order:
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
 *   40 すらすら言える / Hiragana in Rhythm. Continues to Room 41.
 *   41 ことばが さく / Words in Bloom — production Room 40 lower lesson
 *       under the film. Continues to Room 42.
 *   42 Shiba-kun Overture. Start Here terminus. No Room 43.
 *       Pathway nav is previous + Room Map only.
 *
 * Reading: you don't have to understand everything to understand something.
 * Help learners notice known pieces and signals. Unknown material can wait.
 * Do not repeat this as a slogan on every page.
 *
 * Static study track (simplified rooms):
 *   Room pages may mount conventional kana study via `staticStudy`
 *   (a unit id from start-here/js/static-study-data.js). That track is
 *   ordered by content — hiragana, then later katakana — and is not
 *   sized to the number of Start Here rooms. Prototype: Room 0 only
 *   (h-a). Do not wire remaining rooms until review.
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
  var L41 = L40;
  var L42 = L41;


  var lessons = {
    "0": {
      id: "0",
      roomLabel: "Room 0",
      displayName: "The Genkan",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: false,
      showReferenceChart: false,
      encounteredKana: L0,
      newKana: L0,
      staticStudy: "h-a",
      dataSrc: "../data/rooms/0.json",
      filmImage: "../assets/images/room_00.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=hdMZBbYnY_U",
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
      filmImage: "../assets/images/room_01.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=wMzT4WbGbpY",
      prev: "0",
      next: "2",
    },
    "2": {
      id: "2",
      roomLabel: "Room 2",
      displayName: "Begin seeing Japanese",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L2,
      newKana: ["は", "す", "か", "し"],
      filmImage: "../assets/images/room_02.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=bOIWwSUSuVU",
      prev: "1",
      next: "3",
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
      filmImage: "../assets/images/room_03.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=nl8vBOgPLjE",
      prev: "2",
      next: "4",
    },
    "4": {
      id: "4",
      roomLabel: "Room 4",
      displayName: "Reading names",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L4,
      newKana: ["な", "ま", "ん", "さ", "こ"],
      filmImage: "../assets/images/room_04.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=YHwmkzt1xzs",
      prev: "3",
      next: "5",
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
      filmImage: "../assets/images/room_05.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=H09lWLQY9Rg",
      prev: "4",
      next: "6",
    },
    "6": {
      id: "6",
      roomLabel: "Room 6",
      displayName: "This is sushi",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L6,
      newKana: ["れ"],
      filmImage: "../assets/images/room_06.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=eugosPkh6lw",
      prev: "5",
      next: "7",
    },
    "7": {
      id: "7",
      roomLabel: "Room 7",
      displayName: "Four pictures",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L7,
      newKana: ["ほ", "ね", "や", "ぬ"],
      filmImage: "../assets/images/room_07.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=xPnZZiNakEQ",
      prev: "6",
      next: "8",
    },
    "8": {
      id: "8",
      roomLabel: "Room 8",
      displayName: "これは ねこですか",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L8,
      newKana: [],
      filmImage: "../assets/images/room_08.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=ndd6DTzSArM",
      prev: "7",
      next: "9",
    },
    "9": {
      id: "9",
      roomLabel: "Room 9",
      displayName: "これは なんですか",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L9,
      newKana: [],
      filmImage: "../assets/images/room_09.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=JVDY9WuwVAE",
      prev: "8",
      next: "10",
    },
    "10": {
      id: "10",
      roomLabel: "Room 10",
      displayName: "ねこが います",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L10,
      newKana: [],
      filmImage: "../assets/images/room_10.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=uRvdyJLWRus",
      prev: "9",
      next: "11",
    },
    "11": {
      id: "11",
      roomLabel: "Room 11",
      displayName: "いすが あります",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L11,
      newKana: ["り"],
      filmImage: "../assets/images/room_11.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=O_mGmOI7OxY",
      prev: "10",
      next: "12",
    },
    "12": {
      id: "12",
      roomLabel: "Room 12",
      displayName: "しずか",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L12,
      newKana: [],
      filmImage: "../assets/images/room_12.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=eEYuKSTxEVQ",
      prev: "11",
      next: "13",
    },
    "13": {
      id: "13",
      roomLabel: "Room 13",
      displayName: "ひかり",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L13,
      newKana: ["ひ"],
      filmImage: "../assets/images/room_13.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=fl4Ei1ae0c4",
      prev: "12",
      next: "14",
    },
    "14": {
      id: "14",
      roomLabel: "Room 14",
      displayName: "はしに",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L14,
      newKana: ["に"],
      filmImage: "../assets/images/room_14.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=JCKDaBA6v4c",
      prev: "13",
      next: "15",
    },
    "15": {
      id: "15",
      roomLabel: "Room 15",
      displayName: "つりがね",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L15,
      newKana: ["つ"],
      filmImage: "../assets/images/room_15.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=ehG3GfBtsPM",
      prev: "14",
      next: "16",
    },
    "16": {
      id: "16",
      roomLabel: "Room 16",
      displayName: "つくえ",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L16,
      newKana: ["く"],
      filmImage: "../assets/images/room_16.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=Z3sbTWtAMng",
      prev: "15",
      next: "17",
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
      filmImage: "../assets/images/room_17.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=bCEEh4vydVI",
      prev: "16",
      next: "18",
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
      filmImage: "../assets/images/room_18.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=Ap9sX9cwa1g",
      prev: "17",
      next: "19",
    },
    "19": {
      id: "19",
      roomLabel: "Room 19",
      displayName: "いしを こえ",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L19,
      newKana: [],
      filmImage: "../assets/images/room_19.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=OZht_7jxSlg",
      prev: "18",
      next: "20",
    },
    "20": {
      id: "20",
      roomLabel: "Room 20",
      displayName: "かわ",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L20,
      newKana: ["わ"],
      filmImage: "../assets/images/room_20.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=QY9dQia1wqM",
      prev: "19",
      next: "21",
    },
    "21": {
      id: "21",
      roomLabel: "Room 21",
      displayName: "おと",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L21,
      newKana: ["と"],
      filmImage: "../assets/images/room_21.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=1dnFc8gnqtk",
      prev: "20",
      next: "22",
    },
    "22": {
      id: "22",
      roomLabel: "Room 22",
      displayName: "まど",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L22,
      newKana: [],
      filmImage: "../assets/images/room_22.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=XL3GdJsIC70",
      prev: "21",
      next: "23",
    },
    "23": {
      id: "23",
      roomLabel: "Room 23",
      displayName: "かねひとつ",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L23,
      newKana: [],
      filmImage: "../assets/images/room_23.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=bEt2ANdYl6k",
      prev: "22",
      next: "24",
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
      filmImage: "../assets/images/room_24.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=DyrWcHptIck",
      prev: "23",
      next: "25",
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
      filmImage: "../assets/images/room_25.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=s-MtpLw_Jzo",
      prev: "24",
      next: "26",
    },
    "26": {
      id: "26",
      roomLabel: "Room 26",
      displayName: "げんき",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L26,
      newKana: ["き"],
      filmImage: "../assets/images/room_26.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=WB3HRfXg13U",
      prev: "25",
      next: "27",
    },
    "27": {
      id: "27",
      roomLabel: "Room 27",
      displayName: "こんにちは",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L27,
      newKana: ["ち"],
      filmImage: "../assets/images/room_27.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=qjLhfXWJEu0",
      prev: "26",
      next: "28",
    },
    "28": {
      id: "28",
      roomLabel: "Room 28",
      displayName: "へや",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L28,
      newKana: ["へ"],
      filmImage: "../assets/images/room_28.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=EuQffj738xw",
      prev: "27",
      next: "29",
    },
    "29": {
      id: "29",
      roomLabel: "Room 29",
      displayName: "しあわせ",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L29,
      newKana: ["せ"],
      filmImage: "../assets/images/room_29.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=FDaYx57khhM",
      prev: "28",
      next: "30",
    },
    "30": {
      id: "30",
      roomLabel: "Room 30",
      displayName: "みず",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L30,
      newKana: ["み"],
      filmImage: "../assets/images/room_30.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=xwAGvYsMre4",
      prev: "29",
      next: "31",
    },
    "31": {
      id: "31",
      roomLabel: "Room 31",
      displayName: "さくら",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L31,
      newKana: ["ら"],
      filmImage: "../assets/images/room_31.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=74gwg2yCZxU",
      prev: "30",
      next: "32",
    },
    "32": {
      id: "32",
      roomLabel: "Room 32",
      displayName: "そら",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L32,
      newKana: ["そ"],
      filmImage: "../assets/images/room_32.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=LIcZXG1qqv0",
      prev: "31",
      next: "33",
    },
    "33": {
      id: "33",
      roomLabel: "Room 33",
      displayName: "くも",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L33,
      newKana: ["も"],
      filmImage: "../assets/images/room_33.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=Oh1aMNPjnYM",
      prev: "32",
      next: "34",
    },
    "34": {
      id: "34",
      roomLabel: "Room 34",
      displayName: "ゆめ",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L34,
      newKana: ["ゆ", "め"],
      filmImage: "../assets/images/room_34.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=z7R5kUhBxOM",
      prev: "33",
      next: "35",
    },
    "35": {
      id: "35",
      roomLabel: "Room 35",
      displayName: "ねむる",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L35,
      newKana: ["む", "る"],
      filmImage: "../assets/images/room_35.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=g6OBP7LkSLc",
      prev: "34",
      next: "36",
    },
    "36": {
      id: "36",
      roomLabel: "Room 36",
      displayName: "ふゆ",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L36,
      newKana: ["ふ"],
      filmImage: "../assets/images/room_36.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=9giwZaUPRVU",
      prev: "35",
      next: "37",
    },
    "37": {
      id: "37",
      roomLabel: "Room 37",
      displayName: "静かな部屋に",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L37,
      newKana: [],
      filmImage: "../assets/images/room_37.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=aZWBy2dnvbw",
      prev: "36",
      next: "38",
    },
    "38": {
      id: "38",
      roomLabel: "Room 38",
      displayName: "よろしく",
      mode: "study-room",
      romajiDefault: "on",
      showPuzzle: true,
      showReferenceChart: false,
      encounteredKana: L38,
      newKana: ["よ", "ろ"],
      filmImage: "../assets/images/room_38.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=Ay7Wig4Xtbk",
      prev: "37",
      next: "39",
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
      filmImage: "../assets/images/room_39.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=uUIChxBhkCc",
      prev: "38",
      next: "40",
    },
    "40": {
      id: "40",
      roomLabel: "Room 40",
      displayName: "すらすら言える / Hiragana in Rhythm",
      mode: "study-room",
      romajiDefault: "off",
      showPuzzle: false,
      showReferenceChart: true,
      encounteredKana: L40,
      newKana: [],
      filmImage: "../assets/images/room_40.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=XKzuVYryXrU",
      prev: "39",
      next: "41",
    },
    "41": {
      id: "41",
      roomLabel: "Room 41",
      displayName: "言葉が咲く | Words in Bloom",
      mode: "study-room",
      romajiDefault: "off",
      showPuzzle: false,
      showReferenceChart: true,
      encounteredKana: L41,
      newKana: [],
      filmImage: "../assets/images/room_41.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=fGc3HnpN8jA",
      prev: "40",
      next: "42",
    },
    "42": {
      id: "42",
      roomLabel: "Room 42",
      displayName: "Shiba-kun Overture",
      mode: "study-room",
      romajiDefault: "off",
      showPuzzle: false,
      showReferenceChart: true,
      encounteredKana: L42,
      newKana: [],
      filmImage: "../assets/images/room_42.jpg",
      youtubeUrl: "https://www.youtube.com/watch?v=VqCrT25rCl4",
      prev: "41",
      next: null,
    },
  };

  function teachingContainer() {
    return document.querySelector(
      ".room-section--film-top + .room-section .room-container"
    );
  }

  function lessonHref(id) {
    return "../lesson-" + id + "/";
  }

  function asNavAnchor(el, className, role) {
    var anchor = el;
    if (!anchor || anchor.tagName !== "A") {
      anchor = document.createElement("a");
      if (el) el.replaceWith(anchor);
    }
    anchor.className = className;
    anchor.setAttribute("data-room-nav", role);
    return anchor;
  }

  function normalizeNav(nav) {
    nav.setAttribute("aria-label", "Room sequence");

    var back =
      nav.querySelector("[data-room-nav='prev']") ||
      nav.querySelector(".pathway-nav-back");
    var next =
      nav.querySelector("[data-room-nav='next']") ||
      nav.querySelector(".pathway-nav-next");
    var index =
      nav.querySelector("[data-room-nav='index']") ||
      nav.querySelector(".pathway-nav-index");
    var status =
      nav.querySelector("[data-room-nav='current']") ||
      nav.querySelector(".pathway-nav-status");

    back = asNavAnchor(back, "pathway-nav-back", "prev");
    if (!back.parentNode) nav.insertBefore(back, nav.firstChild);

    if (!index) {
      index = document.createElement("a");
      if (status) status.replaceWith(index);
      else if (next) nav.insertBefore(index, next);
      else nav.appendChild(index);
    }
    index = asNavAnchor(index, "pathway-nav-index", "index");
    if (status && status.parentNode) status.remove();

    next = asNavAnchor(next, "pathway-nav-next", "next");
    if (!next.parentNode) nav.appendChild(next);
  }

  function removeTopRoomNav(lesson) {
    var n = parseInt(lesson.id, 10);
    if (!(n >= 1 && n <= 42)) return;
    document
      .querySelectorAll(
        ".room-section:not(.room-section--film-top) .pathway-nav--top"
      )
      .forEach(function (nav) {
        nav.remove();
      });
  }

  function fillRoomNav(lesson) {
    document.querySelectorAll(".pathway-nav").forEach(normalizeNav);

    document.querySelectorAll("[data-room-nav='prev']").forEach(function (prevLink) {
      if (lesson.prev != null && lessons[lesson.prev]) {
        var prev = lessons[lesson.prev];
        prevLink.href = lessonHref(prev.id);
        prevLink.hidden = false;
        prevLink.textContent = "← " + prev.roomLabel;
      } else {
        prevLink.removeAttribute("href");
        prevLink.hidden = true;
        prevLink.textContent = "";
      }
    });

    document.querySelectorAll("[data-room-nav='index']").forEach(function (indexLink) {
      indexLink.href = "../rooms/";
      indexLink.hidden = false;
      indexLink.textContent = "Room Map";
    });

    document.querySelectorAll("[data-room-nav='next']").forEach(function (nextLink) {
      if (lesson.next != null && lessons[lesson.next]) {
        var next = lessons[lesson.next];
        nextLink.href = lessonHref(next.id);
        nextLink.hidden = false;
        nextLink.textContent = "Continue to " + next.roomLabel + " →";
      } else {
        nextLink.removeAttribute("href");
        nextLink.hidden = true;
        nextLink.textContent = "";
      }
    });
  }

  function isRedundantRoomControl(anchor, lessonNum) {
    var text = String(anchor.textContent || "").replace(/\s+/g, " ").trim();
    if (/^Watch the film again$/i.test(text)) return true;
    if (/^Continue to Room\s+\d+/i.test(text)) return true;
    if (/^Previous:/i.test(text)) return true;
    if (/^←\s+Room\s+\d+/i.test(text)) return true;
    if (/^←\s+The Genkan$/i.test(text)) return true;
    if (text === "Room Map") return true;
    if (/^(Next Lesson|← Previous Lesson)/i.test(text)) return true;
    if (/^Continue the KML Journey$/i.test(text)) return true;
    if (/^Ambient Kanji Gallery$/i.test(text)) return true;
    if (/^Back to Start Here$/i.test(text)) return true;
    return false;
  }

  function installBottomRoomNav(lesson) {
    var n = parseInt(lesson.id, 10);
    if (!(n >= 1 && n <= 42)) return;

    var teaching = teachingContainer();
    if (!teaching) return;

    var extras = [];
    teaching
      .querySelectorAll(
        ".room-actions a, .pathway-close-actions a, .pathway-close-back a"
      )
      .forEach(function (anchor) {
        if (isRedundantRoomControl(anchor, n)) anchor.remove();
        else extras.push(anchor);
      });

    var nav = teaching.querySelector(".pathway-nav--bottom");
    if (!nav) {
      nav = document.createElement("nav");
      nav.className = "pathway-nav pathway-nav--bottom";
      nav.innerHTML =
        '<a class="pathway-nav-back" data-room-nav="prev"></a>' +
        '<a class="pathway-nav-index" data-room-nav="index" href="../rooms/">Room Map</a>' +
        '<a class="pathway-nav-next" data-room-nav="next"></a>';
    }

    var host =
      teaching.querySelector(".room-forward, .pathway-close") || teaching;
    host.appendChild(nav);

    var extrasWrap = host.querySelector(".room-actions");
    if (extras.length) {
      if (!extrasWrap) {
        extrasWrap = document.createElement("div");
        extrasWrap.className = "room-actions";
      }
      extras.forEach(function (anchor) {
        extrasWrap.appendChild(anchor);
      });
      nav.insertAdjacentElement("afterend", extrasWrap);
    } else if (extrasWrap && !extrasWrap.querySelector("a, button")) {
      extrasWrap.remove();
    }

    teaching.querySelectorAll(".pathway-close-back, .pathway-close-actions").forEach(
      function (el) {
        if (!el.querySelector("a, button")) el.remove();
      }
    );

    unwrapEmptyNavHost(host, nav);
  }

  function unwrapEmptyNavHost(host, nav) {
    if (!host || !nav || host === teachingContainer()) return;
    if (
      !host.classList.contains("room-forward") &&
      !host.classList.contains("pathway-close")
    ) {
      return;
    }
    var leftover = false;
    Array.prototype.forEach.call(host.children, function (child) {
      if (child === nav) return;
      leftover = true;
    });
    if (leftover) return;
    host.replaceWith(nav);
  }

  function stripFooterRoomNav(lesson) {
    var n = parseInt(lesson.id, 10);
    document.querySelectorAll(".museum-footer nav a").forEach(function (anchor) {
      var href = String(anchor.getAttribute("href") || "");
      var text = String(anchor.textContent || "").replace(/\s+/g, " ").trim();
      if (/lesson-\d+\/?$/.test(href)) anchor.remove();
      if (text === "Room Map") anchor.remove();
      if (n >= 1 && n <= 42 && text !== "Home" && text !== "Start Here") {
        anchor.remove();
      }
    });
  }

  function kanaToRomaji(input) {
    var EXCEPTIONS = {
      こんにちは: "konnichiwa",
      こんばんは: "konbanwa",
      です: "desu",
      ですか: "desu ka",
    };
    var DIGRAPH = {
      きゃ: "kya",
      きゅ: "kyu",
      きょ: "kyo",
      しゃ: "sha",
      しゅ: "shu",
      しょ: "sho",
      ちゃ: "cha",
      ちゅ: "chu",
      ちょ: "cho",
      にゃ: "nya",
      にゅ: "nyu",
      にょ: "nyo",
      ひゃ: "hya",
      ひゅ: "hyu",
      ひょ: "hyo",
      みゃ: "mya",
      みゅ: "myu",
      みょ: "myo",
      りゃ: "rya",
      りゅ: "ryu",
      りょ: "ryo",
      ぎゃ: "gya",
      ぎゅ: "gyu",
      ぎょ: "gyo",
      じゃ: "ja",
      じゅ: "ju",
      じょ: "jo",
      びゃ: "bya",
      びゅ: "byu",
      びょ: "byo",
      ぴゃ: "pya",
      ぴゅ: "pyu",
      ぴょ: "pyo",
    };
    var MONO = {
      あ: "a",
      い: "i",
      う: "u",
      え: "e",
      お: "o",
      か: "ka",
      き: "ki",
      く: "ku",
      け: "ke",
      こ: "ko",
      さ: "sa",
      し: "shi",
      す: "su",
      せ: "se",
      そ: "so",
      た: "ta",
      ち: "chi",
      つ: "tsu",
      て: "te",
      と: "to",
      な: "na",
      に: "ni",
      ぬ: "nu",
      ね: "ne",
      の: "no",
      は: "ha",
      ひ: "hi",
      ふ: "fu",
      へ: "he",
      ほ: "ho",
      ま: "ma",
      み: "mi",
      む: "mu",
      め: "me",
      も: "mo",
      や: "ya",
      ゆ: "yu",
      よ: "yo",
      ら: "ra",
      り: "ri",
      る: "ru",
      れ: "re",
      ろ: "ro",
      わ: "wa",
      を: "o",
      ん: "n",
      が: "ga",
      ぎ: "gi",
      ぐ: "gu",
      げ: "ge",
      ご: "go",
      ざ: "za",
      じ: "ji",
      ず: "zu",
      ぜ: "ze",
      ぞ: "zo",
      だ: "da",
      ぢ: "ji",
      づ: "zu",
      で: "de",
      ど: "do",
      ば: "ba",
      び: "bi",
      ぶ: "bu",
      べ: "be",
      ぼ: "bo",
      ぱ: "pa",
      ぴ: "pi",
      ぷ: "pu",
      ぺ: "pe",
      ぽ: "po",
      ぁ: "a",
      ぃ: "i",
      ぅ: "u",
      ぇ: "e",
      ぉ: "o",
    };
    var PARTICLES = { は: "wa", へ: "e", を: "o" };

    function convertWord(word) {
      if (EXCEPTIONS[word]) return EXCEPTIONS[word];
      if (PARTICLES[word]) return PARTICLES[word];
      var out = "";
      var i = 0;
      while (i < word.length) {
        var ch = word.charAt(i);
        if (ch === "っ" || ch === "ッ") {
          var next = word.slice(i + 1, i + 3);
          var pair = DIGRAPH[next] || MONO[word.charAt(i + 1)] || "";
          out += pair.charAt(0) || "";
          i += 1;
          continue;
        }
        var two = word.slice(i, i + 2);
        if (DIGRAPH[two]) {
          out += DIGRAPH[two];
          i += 2;
          continue;
        }
        if (ch === "ー" && out) {
          var last = out.charAt(out.length - 1);
          if ("aiueo".indexOf(last) >= 0) out += last;
          i += 1;
          continue;
        }
        if (ch === "＿") {
          out += "__";
          i += 1;
          continue;
        }
        if (ch === "。") {
          out += ".";
          i += 1;
          continue;
        }
        if (ch === "？" || ch === "?") {
          out += "?";
          i += 1;
          continue;
        }
        if (ch === "！" || ch === "!") {
          out += "!";
          i += 1;
          continue;
        }
        if (MONO[ch]) {
          out += MONO[ch];
          i += 1;
          continue;
        }
        out += ch;
        i += 1;
      }
      return out;
    }

    return String(input || "")
      .split(/(\n)/)
      .map(function (chunk) {
        if (chunk === "\n") return "\n";
        return chunk
          .split(/([ 　]+)/)
          .map(function (part) {
            if (/^[ 　]+$/.test(part)) return " ";
            return convertWord(part);
          })
          .join("");
      })
      .join("");
  }

  function romajiForKanaLine(ja) {
    return kanaToRomaji(ja);
  }

  function indexJaKey(value) {
    return String(value || "")
      .replace(/[。．.？?！!、，,]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function rememberRomaji(map, ja, romaji) {
    var key = String(ja || "").replace(/\s+/g, " ").trim();
    var ro = String(romaji || "").replace(/\s+/g, " ").trim();
    if (!key || !ro) return;
    map[key] = ro;
    map[indexJaKey(key)] = ro;
  }

  function pageRomajiMap() {
    var map = {};
    document.querySelectorAll(".jp-kana").forEach(function (jaEl) {
      var roEl = jaEl.nextElementSibling;
      if (!roEl || !roEl.classList.contains("jp-romaji")) {
        var block = jaEl.closest(".jp-block");
        roEl = block ? block.querySelector(".jp-romaji") : null;
      }
      if (!roEl) return;
      rememberRomaji(map, jaEl.textContent, roEl.textContent);
    });
    document.querySelectorAll(".jp-verse").forEach(function (verse) {
      var roEl = verse.nextElementSibling;
      if (!roEl || !roEl.classList.contains("jp-romaji")) return;
      rememberRomaji(map, verse.textContent, roEl.textContent);
    });
    return map;
  }

  function pageKanjiReadings() {
    var map = {};
    document.querySelectorAll("ruby").forEach(function (ruby) {
      var rt = ruby.querySelector("rt");
      if (!rt) return;
      var reading = String(rt.textContent || "").replace(/\s+/g, "").trim();
      var clone = ruby.cloneNode(true);
      Array.prototype.forEach.call(clone.querySelectorAll("rt, rp"), function (node) {
        node.remove();
      });
      var written = String(clone.textContent || "").replace(/\s+/g, "").trim();
      if (written && reading) map[written] = reading;
    });
    return map;
  }

  function lookupRomaji(map, jaKey, reading) {
    var keys = [jaKey, indexJaKey(jaKey), reading, indexJaKey(reading)];
    var i;
    for (i = 0; i < keys.length; i += 1) {
      if (keys[i] && map[keys[i]]) return map[keys[i]];
    }
    var compact = indexJaKey(jaKey).replace(/ /g, "");
    for (var key in map) {
      if (!Object.prototype.hasOwnProperty.call(map, key)) continue;
      if (indexJaKey(key).replace(/ /g, "") === compact) return map[key];
    }
    return "";
  }

  function verseReadingKana(verse, kanjiMap) {
    var words = [];
    var buf = "";
    var particles = "にがのをはへも";
    kanjiMap = kanjiMap || {};

    function flush() {
      if (buf) words.push(buf);
      buf = "";
    }

    function appendReading(reading) {
      if (!reading) return;
      buf += reading;
    }

    var lastWasRuby = false;

    function walkText(text, allowParticleSplit) {
      var i = 0;
      while (i < text.length) {
        var ch = text.charAt(i);
        if (ch === "\n") {
          flush();
          words.push("\n");
          lastWasRuby = false;
          i += 1;
          continue;
        }
        if (ch === " " || ch === "　") {
          flush();
          words.push(" ");
          lastWasRuby = false;
          i += 1;
          continue;
        }
        if ("。．.？?！!、，,".indexOf(ch) >= 0) {
          flush();
          words.push(ch);
          lastWasRuby = false;
          i += 1;
          continue;
        }
        if (ch === "＿" || ch === "_") {
          flush();
          var blank = "";
          while (i < text.length && (text.charAt(i) === "＿" || text.charAt(i) === "_")) {
            blank += text.charAt(i);
            i += 1;
          }
          words.push(blank);
          lastWasRuby = false;
          continue;
        }
        var mapped = "";
        var len = 2;
        while (len >= 1) {
          var slice = text.slice(i, i + len);
          if (kanjiMap[slice]) {
            mapped = kanjiMap[slice];
            i += len;
            break;
          }
          len -= 1;
        }
        if (mapped) {
          appendReading(mapped);
          lastWasRuby = false;
          continue;
        }
        if (allowParticleSplit && particles.indexOf(ch) >= 0 && buf) {
          flush();
          words.push(ch);
        } else {
          buf += ch;
        }
        lastWasRuby = false;
        i += 1;
      }
    }

    function walk(node) {
      if (!node) return;
      if (node.nodeType === 3) {
        var text = node.nodeValue || "";
        if (/^\s*$/.test(text)) return;
        walkText(text, true);
        return;
      }
      if (node.nodeType !== 1) return;
      var tag = node.tagName;
      if (tag === "BR") {
        flush();
        words.push("\n");
        lastWasRuby = false;
        return;
      }
      if (tag === "RT" || tag === "RP") return;
      if (tag === "RUBY") {
        if (buf && !lastWasRuby) flush();
        appendReading(rtReading(node));
        lastWasRuby = true;
        return;
      }
      Array.prototype.forEach.call(node.childNodes, walk);
    }

    walk(verse);
    flush();
    return words;
  }

  function wordsToRomaji(words) {
    var parts = [];
    (words || []).forEach(function (word) {
      if (word === "\n") {
        parts.push("\n");
        return;
      }
      if (word === " ") return;
      var converted = kanaToRomaji(word);
      if (!converted) return;
      if (parts.length && parts[parts.length - 1] !== "\n") parts.push(" ");
      parts.push(converted);
    });
    return parts
      .join("")
      .replace(/[ \t]+\n/g, "\n")
      .replace(/\n[ \t]+/g, "\n")
      .replace(/ +([.?!])/g, "$1")
      .trim();
  }

  function rtReading(ruby) {
    var rt = ruby.querySelector("rt");
    return rt ? String(rt.textContent || "") : String(ruby.textContent || "");
  }

  function sentenceCaseRomaji(romaji, ja) {
    var text = String(romaji || "").trim();
    if (!text) return text;
    if (!/[。．.？?！!]|です/.test(String(ja || ""))) return text;
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function hostAlreadyHasRomaji(host) {
    if (host.querySelector(":scope > .jp-verse-line > .jp-romaji")) return true;
    var sib = host.nextElementSibling;
    return !!(sib && sib.classList.contains("jp-romaji"));
  }

  function romajiIsComplete(romaji) {
    var text = String(romaji || "").trim();
    if (!text) return false;
    return !/[\u3040-\u30ff\u4e00-\u9fff]/.test(text);
  }

  function isJapaneseLessonText(text) {
    var compact = String(text || "").replace(/\s+/g, "");
    if (!compact) return false;
    var jp = (compact.match(/[\u3040-\u30ff\u4e00-\u9fff＿]/g) || []).length;
    return jp > 0 && jp >= compact.length * 0.6;
  }

  function shouldSkipRomajiHost(host) {
    if (!host || host.closest(".kana-puzzle, [data-kana-puzzle], [data-kana-chart-full]")) {
      return true;
    }
    if (host.closest(".museum-header, .museum-footer, .museum-nav, .pathway-nav, .room-actions")) {
      return true;
    }
    if (host.closest(".static-study-kana")) return true;
    if (host.classList.contains("static-study-title")) return true;
    if (host.classList.contains("jp-romaji") || host.classList.contains("jp-en")) return true;
    return false;
  }

  function readingForHost(host, map, kanjiMap) {
    var jaKey = String(host.textContent || "").replace(/\s+/g, " ").trim();
    var words = verseReadingKana(host, kanjiMap);
    var reading = words
      .filter(function (w) {
        return w !== "\n" && w !== " ";
      })
      .join(" ");
    var mapped = lookupRomaji(map, jaKey, reading);
    if (mapped) return mapped;
    if (!/\s/.test(jaKey) && /^[\u3041-\u3096ー]+$/.test(jaKey)) {
      return kanaToRomaji(jaKey);
    }
    return sentenceCaseRomaji(
      wordsToRomaji(words) || kanaToRomaji(jaKey),
      jaKey
    );
  }

  function verseLinesFromBr(verse) {
    var lines = [[]];
    Array.prototype.forEach.call(Array.prototype.slice.call(verse.childNodes), function (node) {
      if (node.nodeType === 1 && node.tagName === "BR") {
        lines.push([]);
        return;
      }
      if (node.nodeType === 3 && /^\s*$/.test(node.nodeValue || "")) return;
      lines[lines.length - 1].push(node);
    });
    return lines.filter(function (nodes) {
      return nodes.length > 0;
    });
  }

  function pairVerseLineRomaji(verse, map, kanjiMap) {
    if (verse.querySelector(".jp-verse-line")) return;
    var sibling = verse.nextElementSibling;
    if (sibling && sibling.classList.contains("jp-romaji")) sibling.remove();
    var lines = verseLinesFromBr(verse);
    if (lines.length <= 1) {
      attachRomajiToHost(verse, map, kanjiMap);
      return;
    }
    var frag = document.createDocumentFragment();
    lines.forEach(function (nodes) {
      var row = document.createElement("span");
      row.className = "jp-verse-line";
      var ja = document.createElement("span");
      ja.className = "jp-verse-ja";
      ja.lang = "ja";
      nodes.forEach(function (node) {
        ja.appendChild(node);
      });
      row.appendChild(ja);
      var romaji = readingForHost(ja, map, kanjiMap);
      if (romajiIsComplete(romaji)) {
        var ro = document.createElement("span");
        ro.className = "jp-romaji";
        ro.textContent = romaji;
        row.appendChild(ro);
        rememberRomaji(map, ja.textContent, romaji);
      } else {
        ja.setAttribute("data-romaji-missing", "");
      }
      frag.appendChild(row);
    });
    verse.replaceChildren(frag);
  }

  function attachRomajiToHost(host, map, kanjiMap) {
    if (!host || hostAlreadyHasRomaji(host) || shouldSkipRomajiHost(host)) return;
    var romaji = readingForHost(host, map, kanjiMap);
    if (!romajiIsComplete(romaji)) {
      host.setAttribute("data-romaji-missing", "");
      return;
    }
    host.removeAttribute("data-romaji-missing");
    var el = document.createElement("p");
    el.className = "jp-romaji";
    el.textContent = romaji;
    host.insertAdjacentElement("afterend", el);
    rememberRomaji(map, host.textContent, romaji);
  }

  function japaneseHeadingHosts() {
    var out = [];
    document
      .querySelectorAll(
        ".room-section:not(.room-section--film-top) h1, .room-section:not(.room-section--film-top) h2, .room-section:not(.room-section--film-top) h3"
      )
      .forEach(function (heading) {
        if (shouldSkipRomajiHost(heading)) return;
        if (heading.id === "puzzle-heading" || heading.id === "source-heading" || heading.id === "map-heading") {
          return;
        }
        if (!isJapaneseLessonText(heading.textContent)) return;
        out.push(heading);
      });
    return out;
  }

  function installPathwayRomaji() {
    var kanjiMap = pageKanjiReadings();
    var map = pageRomajiMap();
    document.querySelectorAll(".jp-verse").forEach(function (verse) {
      if (verse.querySelector("br")) pairVerseLineRomaji(verse, map, kanjiMap);
      else attachRomajiToHost(verse, map, kanjiMap);
    });
    map = pageRomajiMap();
    document.querySelectorAll(".jp-kana, .static-study-vocab-word").forEach(function (host) {
      attachRomajiToHost(host, map, kanjiMap);
    });
    japaneseHeadingHosts().forEach(function (heading) {
      attachRomajiToHost(heading, map, kanjiMap);
    });
  }

  function uniqueLyricLines(config) {
    var rows = [];
    if (config && config.scenes && config.scenes.length) rows = config.scenes;
    else if (config && config.lyrics && config.lyrics.length) rows = config.lyrics;
    var seen = {};
    var out = [];
    rows.forEach(function (row) {
      var ja = String((row && row.ja) || "").replace(/\s+/g, " ").trim();
      if (!ja || seen[ja]) return;
      seen[ja] = true;
      out.push({
        ja: String(row.ja).trim(),
        romaji: String((row && row.romaji) || "").trim(),
      });
    });
    return out;
  }

  function englishByJaFromPage() {
    var map = {};
    document.querySelectorAll(".jp-block").forEach(function (block) {
      var jaEl = block.querySelector(".jp-kana");
      var enEl = block.querySelector(".jp-en");
      if (!jaEl || !enEl) return;
      var key = String(jaEl.textContent || "").replace(/\s+/g, " ").trim();
      var en = String(enEl.textContent || "").replace(/\s+/g, " ").trim();
      if (key && en) map[key] = en;
    });
    return map;
  }

  function placeSongLyricsSection(section) {
    var teaching = teachingContainer();
    if (!teaching) return;
    var after = teaching.querySelector(".pathway-learner-controls");
    if (after) {
      after.insertAdjacentElement("afterend", section);
      return;
    }
    var before = teaching.querySelector(
      ".static-study, .room-section-head, .jp-block, .beginner-exhibit"
    );
    if (before) teaching.insertBefore(section, before);
    else teaching.insertBefore(section, teaching.firstChild);
  }

  function renderSongLyricLines(lines) {
    if (!lines.length || document.querySelector("[data-song-lyrics]")) return;
    var english = englishByJaFromPage();
    var section = document.createElement("section");
    section.className = "beginner-song";
    section.setAttribute("data-song-lyrics", "");
    section.setAttribute("aria-label", "Song lyrics");

    var label = document.createElement("p");
    label.className = "beginner-song-label";
    label.textContent = "Lyrics";
    section.appendChild(label);

    lines.forEach(function (line) {
      var figure = document.createElement("figure");
      figure.className = "jp-block jp-block--solo";

      var ja = document.createElement("p");
      ja.className = "jp-kana";
      ja.lang = "ja";
      ja.textContent = line.ja;
      figure.appendChild(ja);

      var romajiText = line.romaji || romajiForKanaLine(line.ja);
      if (romajiText) {
        var romaji = document.createElement("p");
        romaji.className = "jp-romaji";
        romaji.textContent = romajiText;
        figure.appendChild(romaji);
      }

      var enText = english[String(line.ja).replace(/\s+/g, " ").trim()];
      if (enText) {
        var en = document.createElement("p");
        en.className = "jp-en";
        en.textContent = enText;
        figure.appendChild(en);
      }

      section.appendChild(figure);
    });

    placeSongLyricsSection(section);
  }

  var songLyricsRequested = false;

  function installSongLyrics() {
    var lessonId = document.body.getAttribute("data-beginner-lesson");
    var lesson = lessonId != null ? lessons[lessonId] : null;
    if (!lesson) return;

    var n = parseInt(lesson.id, 10);
    if (n === 17 || n === 25) return;
    if (songLyricsRequested || document.querySelector("[data-song-lyrics]")) return;

    var src = lesson.dataSrc;
    if (!src) return;
    if (!(n === 0 || n === 1 || n === 3 || n === 5)) return;

    songLyricsRequested = true;
    fetch(src)
      .then(function (res) {
        if (!res.ok) throw new Error("lyrics");
        return res.json();
      })
      .then(function (config) {
        renderSongLyricLines(uniqueLyricLines(config));
        if (typeof installPathwayRomaji === "function") installPathwayRomaji();
      })
      .catch(function () {
        /* keep teaching content if lyrics file is unavailable */
      });
  }

  function installRoomNavigation() {
    var lessonId = document.body.getAttribute("data-beginner-lesson");
    var lesson = lessonId != null ? lessons[lessonId] : null;
    if (!lesson) return;
    removeTopRoomNav(lesson);
    installBottomRoomNav(lesson);
    stripFooterRoomNav(lesson);
    fillRoomNav(lesson);
  }

  window.KmlBeginnerCourse = {
    romajiStorageKey: "kml-beginner-romaji",
    gojuonColumns: GOJUON_COLUMNS,
    boxCount: 46,
    lessons: lessons,
    installRoomNavigation: installRoomNavigation,
    installSongLyrics: installSongLyrics,
    installPathwayRomaji: installPathwayRomaji,
  };
})();
