(function (w) {
  "use strict";
  var script = document.currentScript;
  w.KmlBeginnerRoomBase = script ? new URL(".", script.src).href : "";
  w.KmlBeginnerRoomData = {
  "id": "1",
  "displayName": "日本語が楽しい",
  "roomLabel": "Room 1",
  "mode": "guided-song",
  "romajiDefault": "on",
  "audio": "../../audio/lesson-1.mp3",
  "loop": false,
  "imageCrossfade": 2.8,
  "timing": {
    "status": "listened",
    "audioDuration": 186.6,
    "note": "Vocal timestamps are when image+lyric must already be established. Image changes pre-roll (2.8s after instrumentals; ~0.8–1.2s on tight Q&A). Empty ja clears cards for all instrumental passages. matsuri.png intro + 2:12 wide; taiko.png first interlude; fireworks.png outro only."
  },
  "opening": {
    "image": "../../assets/images/matsuri.png",
    "title": "日本語が楽しい",
    "lead": "A summer evening. A question. A yes.",
    "cta": "Listen & Follow",
    "hint": "げんき, だいじょうぶ, and たのしい can stay whole. You do not need to take them apart."
  },
  "scenes": [
    {
      "id": "intro-grounds",
      "start": 0,
      "image": "../../assets/images/matsuri.png",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "pre-boys",
      "start": 6,
      "image": "../../assets/images/genki_boys_1.png",
      "ja": "",
      "romaji": "",
      "transition": "crossfade",
      "crossfade": 2.8
    },
    {
      "id": "genki-q-1",
      "start": 12,
      "image": "../../assets/images/genki_boys_1.png",
      "ja": "げんきですか。",
      "romaji": "Genki desu ka."
    },
    {
      "id": "pre-boys-2",
      "start": 14,
      "image": "../../assets/images/genki_boys_2.png",
      "ja": "げんきですか。",
      "romaji": "Genki desu ka.",
      "crossfade": 1
    },
    {
      "id": "genki-a-1",
      "start": 15,
      "image": "../../assets/images/genki_boys_2.png",
      "ja": "はい、げんきです。",
      "romaji": "Hai, genki desu."
    },
    {
      "id": "pre-candy-1",
      "start": 18,
      "image": "../../assets/images/cotton_candy_1.png",
      "ja": "はい、げんきです。",
      "romaji": "Hai, genki desu.",
      "crossfade": 1
    },
    {
      "id": "daijobu-q-1",
      "start": 19,
      "image": "../../assets/images/cotton_candy_1.png",
      "ja": "だいじょうぶですか。",
      "romaji": "Daijōbu desu ka."
    },
    {
      "id": "pre-candy-2",
      "start": 20.2,
      "image": "../../assets/images/cotton_candy_2.png",
      "ja": "だいじょうぶですか。",
      "romaji": "Daijōbu desu ka.",
      "crossfade": 0.8
    },
    {
      "id": "daijobu-a-1",
      "start": 21,
      "image": "../../assets/images/cotton_candy_2.png",
      "ja": "はい、だいじょうぶです。",
      "romaji": "Hai, daijōbu desu."
    },
    {
      "id": "pre-goldfish",
      "start": 26.8,
      "image": "../../assets/images/gold_fish.png",
      "ja": "はい、だいじょうぶです。",
      "romaji": "Hai, daijōbu desu.",
      "crossfade": 1.2
    },
    {
      "id": "tanoshii-q-1",
      "start": 28,
      "image": "../../assets/images/gold_fish.png",
      "ja": "たのしいですか。",
      "romaji": "Tanoshii desu ka."
    },
    {
      "id": "pre-tanoshii-1",
      "start": 31.2,
      "image": "../../assets/images/tanoshii_1.png",
      "ja": "たのしいですか。",
      "romaji": "Tanoshii desu ka.",
      "crossfade": 2.8
    },
    {
      "id": "tanoshii-a-1",
      "start": 34,
      "image": "../../assets/images/tanoshii_1.png",
      "ja": "はい、たのしいです。",
      "romaji": "Hai, tanoshii desu."
    },
    {
      "id": "clear-1",
      "start": 37,
      "image": "../../assets/images/tanoshii_2.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "interlude-1b",
      "start": 46,
      "image": "../../assets/images/taiko.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "interlude-1c",
      "start": 55,
      "image": "../../assets/images/shaved_ice_2.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "interlude-1d",
      "start": 61,
      "image": "../../assets/images/tanoshii_1.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "pre-gmother",
      "start": 68.2,
      "image": "../../assets/images/gmother_1.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "genki-q-2",
      "start": 71,
      "image": "../../assets/images/gmother_1.png",
      "ja": "げんきですか。",
      "romaji": "Genki desu ka."
    },
    {
      "id": "pre-gmother-2",
      "start": 72.2,
      "image": "../../assets/images/gmother_2.png",
      "ja": "げんきですか。",
      "romaji": "Genki desu ka.",
      "crossfade": 0.9
    },
    {
      "id": "genki-a-2",
      "start": 73,
      "image": "../../assets/images/gmother_2.png",
      "ja": "はい、げんきです。",
      "romaji": "Hai, genki desu."
    },
    {
      "id": "pre-coins-1",
      "start": 77,
      "image": "../../assets/images/coins_1.png",
      "ja": "はい、げんきです。",
      "romaji": "Hai, genki desu.",
      "crossfade": 1.2
    },
    {
      "id": "daijobu-q-2",
      "start": 78,
      "image": "../../assets/images/coins_1.png",
      "ja": "だいじょうぶですか。",
      "romaji": "Daijōbu desu ka."
    },
    {
      "id": "pre-coins-2",
      "start": 79.2,
      "image": "../../assets/images/coins_2.png",
      "ja": "だいじょうぶですか。",
      "romaji": "Daijōbu desu ka.",
      "crossfade": 0.8
    },
    {
      "id": "daijobu-a-2",
      "start": 80,
      "image": "../../assets/images/coins_2.png",
      "ja": "はい、だいじょうぶです。",
      "romaji": "Hai, daijōbu desu."
    },
    {
      "id": "pre-tanoshii-3",
      "start": 85.5,
      "image": "../../assets/images/tanoshii_3.png",
      "ja": "はい、だいじょうぶです。",
      "romaji": "Hai, daijōbu desu.",
      "crossfade": 1.5
    },
    {
      "id": "tanoshii-q-2",
      "start": 87,
      "image": "../../assets/images/tanoshii_3.png",
      "ja": "たのしいですか。",
      "romaji": "Tanoshii desu ka."
    },
    {
      "id": "pre-tanoshii-4",
      "start": 90,
      "image": "../../assets/images/tanoshii_4.png",
      "ja": "たのしいですか。",
      "romaji": "Tanoshii desu ka.",
      "crossfade": 2
    },
    {
      "id": "tanoshii-a-2",
      "start": 92,
      "image": "../../assets/images/tanoshii_4.png",
      "ja": "はい、たのしいです。",
      "romaji": "Hai, tanoshii desu."
    },
    {
      "id": "clear-2",
      "start": 95,
      "image": "../../assets/images/tanoshii_2.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "interlude-2b",
      "start": 103,
      "image": "../../assets/images/gold_fish.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "interlude-2c",
      "start": 111,
      "image": "../../assets/images/tanoshii_3.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "pre-nihongo",
      "start": 122.2,
      "image": "../../assets/images/tanoshii_4.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "nihongo-1",
      "start": 125,
      "image": "../../assets/images/tanoshii_4.png",
      "ja": "にほんごが たのしい！",
      "romaji": "Nihongo ga tanoshii!"
    },
    {
      "id": "pre-final-wide",
      "start": 129.2,
      "image": "../../assets/images/matsuri.png",
      "ja": "にほんごが たのしい！",
      "romaji": "Nihongo ga tanoshii!",
      "crossfade": 2.8
    },
    {
      "id": "nihongo-2",
      "start": 132,
      "image": "../../assets/images/matsuri.png",
      "ja": "にほんごが たのしい！",
      "romaji": "Nihongo ga tanoshii!"
    },
    {
      "id": "outro-clear",
      "start": 135,
      "image": "../../assets/images/matsuri.png",
      "ja": "",
      "romaji": ""
    },
    {
      "id": "outro-fireworks",
      "start": 152,
      "image": "../../assets/images/fireworks.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    },
    {
      "id": "outro-together",
      "start": 168,
      "image": "../../assets/images/post_matsuri.png",
      "ja": "",
      "romaji": "",
      "crossfade": 2.8
    }
  ]
};
})(window);
