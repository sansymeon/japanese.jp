(function (w) {
  "use strict";
  var script = document.currentScript;
  w.KmlBeginnerRoomBase = script ? new URL(".", script.src).href : "";
  w.KmlBeginnerRoomData = {
  "id": "25",
  "displayName": "山の川",
  "roomLabel": "Room 25",
  "mode": "guided-song",
  "romajiDefault": "off",
  "audio": "../../audio/山の川が 石を越え.mp3",
  "loop": false,
  "presentation": "listen",
  "timing": {
    "status": "listened",
    "audioDuration": 237.4,
    "note": "Single still: river.png for the whole piece. The song is the event; do not add a slideshow. Vocals at 0:18 / 0:23 and 2:50 / 2:56. Master film has no lyrics. Later text views replay the same still."
  },
  "vocals": [
    { "start": 18, "text": "山の川が　石を越え" },
    { "start": 23, "text": "絶えぬ音だけが　谷に響いていた" },
    { "start": 170, "text": "山の川が　石を越え" },
    { "start": 176, "text": "絶えぬ音だけが　谷に響いていた" }
  ],
  "opening": {
    "image": "../../../kml/assets/studies/river.png",
    "title": "山の川",
    "lead": "Listen.",
    "cta": "Listen"
  },
  "film": [
    {
      "id": "river",
      "start": 0,
      "image": "../../../kml/assets/studies/river.png"
    }
  ],
  "lyrics": []
};
})(window);
