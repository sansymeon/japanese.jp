(function (w) {
  "use strict";
  var script = document.currentScript;
  w.KmlBeginnerRoomBase = script ? new URL(".", script.src).href : "";
  w.KmlBeginnerRoomData = {
  "id": "24",
  "displayName": "竹の音",
  "roomLabel": "Room 24",
  "mode": "guided-song",
  "romajiDefault": "on",
  "audio": "../../audio/竹の音.mp3",
  "loop": false,
  "imageCrossfade": 2.8,
  "timing": {
    "status": "listened",
    "audioDuration": 167.47,
    "note": "Landmarks are musical, not karaoke cuts. Lyrics appear 1s before vocal onsets (0:13 / 0:17 / 0:20 and 1:51 / 1:55 / 1:59). Image dissolves are independent: the next landscape begins arriving during the previous line (~2.8s). Long instrumental 0:24–1:51 is unlabeled landscape (3.6s dissolves), not a drill. Reprise pre-rolls the grove before 1:51. Fade stays at the horizon."
  },
  "opening": {
    "image": "../../assets/images/lesson_24/bamboo_2.png",
    "title": "竹の音",
    "lead": "Listen.",
    "cta": "Listen & Follow"
  },
  "scenes": [
    {
      "id": "intro-grove",
      "start": 0,
      "image": "../../assets/images/lesson_24/bamboo_2.png",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "v1-take",
      "start": 12,
      "image": "../../assets/images/lesson_24/bamboo_2.png",
      "ja": "たけのおと",
      "romaji": "Take no oto"
    },
    {
      "id": "v1-yama-arrive",
      "start": 14.2,
      "image": "../../../kml/assets/ambient_japan_4_seasons/mt_fuji_2.png",
      "ja": "たけのおと",
      "romaji": "Take no oto",
      "crossfade": 2.8
    },
    {
      "id": "v1-yama",
      "start": 16,
      "image": "../../../kml/assets/ambient_japan_4_seasons/mt_fuji_2.png",
      "ja": "やまのこえ",
      "romaji": "Yama no koe"
    },
    {
      "id": "v1-hate-arrive",
      "start": 17.2,
      "image": "../../../kml/assets/ambient_japan_4_seasons/dawn.png",
      "ja": "やまのこえ",
      "romaji": "Yama no koe",
      "crossfade": 2.8
    },
    {
      "id": "v1-hate",
      "start": 19,
      "image": "../../../kml/assets/ambient_japan_4_seasons/dawn.png",
      "ja": "はてまで",
      "romaji": "Hate made"
    },
    {
      "id": "interlude-horizon",
      "start": 24,
      "image": "../../../kml/assets/ambient_japan_4_seasons/dawn.png",
      "ja": "",
      "romaji": ""
    },
    {
      "id": "interlude-scenery",
      "start": 40,
      "image": "../../../kml/assets/ambient_japan_4_seasons/scenery.png",
      "ja": "",
      "romaji": "",
      "crossfade": 3.6
    },
    {
      "id": "interlude-radiance",
      "start": 56,
      "image": "../../../kml/assets/ambient_japan_4_seasons/radiance.png",
      "ja": "",
      "romaji": "",
      "crossfade": 3.6
    },
    {
      "id": "interlude-raizan",
      "start": 72,
      "image": "../../../kml/assets/ambient_japan_4_seasons/raizan.png",
      "ja": "",
      "romaji": "",
      "crossfade": 3.6
    },
    {
      "id": "interlude-grove",
      "start": 88,
      "image": "../../../kml/assets/ambient_japan_4_seasons/bamboo_forest.png",
      "ja": "",
      "romaji": "",
      "crossfade": 3.6
    },
    {
      "id": "reprise-take-preroll",
      "start": 104,
      "image": "../../assets/images/lesson_24/bamboo_2.png",
      "ja": "",
      "romaji": "",
      "crossfade": 3.6
    },
    {
      "id": "v2-take",
      "start": 110,
      "image": "../../assets/images/lesson_24/bamboo_2.png",
      "ja": "たけのおと",
      "romaji": "Take no oto"
    },
    {
      "id": "v2-yama-arrive",
      "start": 112.2,
      "image": "../../../kml/assets/ambient_japan_4_seasons/mt_fuji_2.png",
      "ja": "たけのおと",
      "romaji": "Take no oto",
      "crossfade": 2.8
    },
    {
      "id": "v2-yama",
      "start": 114,
      "image": "../../../kml/assets/ambient_japan_4_seasons/mt_fuji_2.png",
      "ja": "やまのこえ",
      "romaji": "Yama no koe"
    },
    {
      "id": "v2-hate-arrive",
      "start": 116.2,
      "image": "../../../kml/assets/ambient_japan_4_seasons/dawn.png",
      "ja": "やまのこえ",
      "romaji": "Yama no koe",
      "crossfade": 2.8
    },
    {
      "id": "v2-hate",
      "start": 118,
      "image": "../../../kml/assets/ambient_japan_4_seasons/dawn.png",
      "ja": "はてまで",
      "romaji": "Hate made"
    },
    {
      "id": "outro-horizon",
      "start": 125,
      "image": "../../../kml/assets/ambient_japan_4_seasons/dawn.png",
      "ja": "",
      "romaji": ""
    },
    {
      "id": "outro-radiance",
      "start": 145,
      "image": "../../../kml/assets/ambient_japan_4_seasons/radiance.png",
      "ja": "",
      "romaji": "",
      "crossfade": 3.6
    }
  ]
};
})(window);
