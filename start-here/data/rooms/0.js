(function (w) {
  "use strict";
  var script = document.currentScript;
  w.KmlBeginnerRoomBase = script ? new URL(".", script.src).href : "";
  w.KmlBeginnerRoomData = {
  "id": "0",
  "displayName": "The Genkan",
  "roomLabel": "Room 0",
  "mode": "guided-song",
  "romajiDefault": "on",
  "audio": "../../audio/lesson-0.mp3",
  "loop": false,
  "imageCrossfade": 2.8,
  "timing": {
    "status": "listened",
    "audioDuration": 199.7,
    "note": "Sung lyric wins over a clean instrumental boundary. なるほど at 1:01 stays on piano.png until window.png at 1:15. Instrumental is five ~14s holds; piano_score.png sits at 1:29 between window and tanoshii. Final あいうえお at 2:37; overlay clears as outro.png begins at 2:40. Departure 2:40 outro.png → 2:51 outro_2.png → 3:04 outro_3.png, all text-free."
  },
  "opening": {
    "image": "../../assets/images/intro.jpg",
    "title": "The Genkan",
    "lead": "Welcome to your Japanese journey.",
    "cta": "Listen & Follow",
    "hint": "Relax your mouth. Listen first. Then imitate the singer."
  },
  "scenes": [
    {
      "id": "arrive",
      "start": 0,
      "image": "../../assets/images/intro.jpg",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "ah-soudesuka",
      "start": 8,
      "image": "../../assets/images/ah_soudesuka.jpg",
      "ja": "あー、そうですか。",
      "romaji": "Ā, sō desu ka."
    },
    {
      "id": "iine",
      "start": 12,
      "image": "../../assets/images/iine.jpg",
      "ja": "いいね！",
      "romaji": "Ii ne!"
    },
    {
      "id": "uu-kawaii",
      "start": 16,
      "image": "../../assets/images/uu_kawaii.jpg",
      "ja": "うー、かわいい。",
      "romaji": "Ū, kawaii."
    },
    {
      "id": "eh-honto",
      "start": 19,
      "image": "../../assets/images/eh_honto.jpg",
      "ja": "えー？ほんとう？",
      "romaji": "Ē? Hontō?"
    },
    {
      "id": "oh-naruhodo",
      "start": 23,
      "image": "../../assets/images/oh_naruhodo.jpg",
      "ja": "おー、なるほど。",
      "romaji": "Ō, naruhodo."
    },
    {
      "id": "iidesune",
      "start": 26,
      "image": "../../assets/images/iidesune.jpg",
      "ja": "いいですね。",
      "romaji": "Ii desu ne."
    },
    {
      "id": "chorus-long",
      "start": 34,
      "image": "../../assets/images/ah_soudesuka.jpg",
      "ja": "あー　いー　うー　えー　おー",
      "romaji": "ā　ī　ū　ē　ō"
    },
    {
      "id": "chorus-short",
      "start": 42,
      "image": "../../assets/images/ah_soudesuka.jpg",
      "ja": "あ　い　う　え　お",
      "romaji": "a　i　u　e　o"
    },
    {
      "id": "ah-soudesuka-2",
      "start": 51,
      "image": "../../assets/images/ah_soudesuka.jpg",
      "ja": "あー、そうですか。",
      "romaji": "Ā, sō desu ka."
    },
    {
      "id": "iine-2",
      "start": 53,
      "image": "../../assets/images/ah_soudesuka.jpg",
      "ja": "いいね！",
      "romaji": "Ii ne!"
    },
    {
      "id": "uu-kawaii-2",
      "start": 54,
      "image": "../../assets/images/ah_soudesuka.jpg",
      "ja": "うー、かわいい。",
      "romaji": "Ū, kawaii."
    },
    {
      "id": "eh-honto-2",
      "start": 57,
      "image": "../../assets/images/ah_soudesuka.jpg",
      "ja": "えー？ほんとう？",
      "romaji": "Ē? Hontō?"
    },
    {
      "id": "oh-naruhodo-2",
      "start": 61,
      "image": "../../assets/images/piano.jpg",
      "ja": "おー、なるほど。",
      "romaji": "Ō, naruhodo.",
      "transition": "crossfade"
    },
    {
      "id": "look-window",
      "start": 75,
      "image": "../../assets/images/window.jpg",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "look-piano-score",
      "start": 89,
      "image": "../../assets/images/piano_score.jpg",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "look-tanoshii",
      "start": 103,
      "image": "../../assets/images/tanoshii.jpg",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "look-iine",
      "start": 117,
      "image": "../../assets/images/iine.jpg",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "return-soudesuka",
      "start": 132,
      "image": "../../assets/images/iine.jpg",
      "ja": "あー、そうですか。",
      "romaji": "Ā, sō desu ka."
    },
    {
      "id": "return-iine",
      "start": 134,
      "image": "../../assets/images/iine.jpg",
      "ja": "いいね！",
      "romaji": "Ii ne!"
    },
    {
      "id": "return-kawaii",
      "start": 138,
      "image": "../../assets/images/window.jpg",
      "ja": "うー、かわいい。",
      "romaji": "Ū, kawaii."
    },
    {
      "id": "return-honto",
      "start": 140,
      "image": "../../assets/images/window.jpg",
      "ja": "えー？ほんとう？",
      "romaji": "Ē? Hontō?"
    },
    {
      "id": "return-naruhodo",
      "start": 145,
      "image": "../../assets/images/window.jpg",
      "ja": "おー、なるほど。",
      "romaji": "Ō, naruhodo."
    },
    {
      "id": "chorus-long-2",
      "start": 152,
      "image": "../../assets/images/tanoshii.jpg",
      "ja": "あー　いー　うー　えー　おー",
      "romaji": "ā　ī　ū　ē　ō"
    },
    {
      "id": "chorus-short-2",
      "start": 157,
      "image": "../../assets/images/tanoshii.jpg",
      "ja": "あ　い　う　え　お",
      "romaji": "a　i　u　e　o"
    },
    {
      "id": "leave-sign",
      "start": 160,
      "image": "../../assets/images/outro.jpg",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "leave-walk",
      "start": 171,
      "image": "../../assets/images/outro_2.jpg",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    },
    {
      "id": "leave-street",
      "start": 184,
      "image": "../../assets/images/outro_3.jpg",
      "ja": "",
      "romaji": "",
      "transition": "crossfade"
    }
  ]
};
})(window);
