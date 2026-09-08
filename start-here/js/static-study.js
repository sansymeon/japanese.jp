/**
 * Renders the static study block inside Start Here rooms.
 *
 * Rooms opt in with `staticStudy` (a unit id from KmlStaticStudy).
 * The same renderer serves hiragana and later katakana units.
 * Katakana glyphs and words are playable via the browser's Japanese voice.
 */
(function () {
  "use strict";

  var course = window.KmlBeginnerCourse;
  var study = window.KmlStaticStudy;
  if (!course || !study) return;

  var lessonId = document.body.getAttribute("data-beginner-lesson");
  var lesson = lessonId ? course.lessons[lessonId] : null;
  if (!lesson || !lesson.staticStudy) return;

  var unit = study.units[lesson.staticStudy];
  if (!unit) return;

  var isKatakana = unit.script === "katakana";

  function unitTitle(unitData) {
    return unitData.kana
      .map(function (item) {
        return item.kana;
      })
      .join("　");
  }

  function japaneseVoice() {
    if (!window.speechSynthesis) return null;
    var voices = window.speechSynthesis.getVoices() || [];
    var i;
    for (i = 0; i < voices.length; i += 1) {
      if ((voices[i].lang || "").toLowerCase().indexOf("ja") === 0) {
        return voices[i];
      }
    }
    return null;
  }

  function speak(text) {
    if (!window.speechSynthesis || !text) return;
    window.speechSynthesis.cancel();
    var utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "ja-JP";
    utterance.rate = 0.9;
    var voice = japaneseVoice();
    if (voice) utterance.voice = voice;
    window.speechSynthesis.speak(utterance);
  }

  function bindSpeak(el, text) {
    el.addEventListener("click", function () {
      speak(text);
    });
  }

  function renderFilmLink() {
    var mount = document.querySelector("[data-room-film]");
    if (!mount || !lesson.filmImage) return;

    mount.replaceChildren();
    mount.classList.remove("is-pending");

    var hit = document.createElement(lesson.youtubeUrl ? "a" : "div");
    hit.className = "pathway-film-link-hit";

    var image = document.createElement("img");
    image.src = lesson.filmImage;
    image.alt = "";
    image.width = 1672;
    image.height = 941;
    image.loading = "eager";
    image.decoding = "async";

    var label = document.createElement("span");
    label.setAttribute("aria-hidden", "true");

    if (lesson.youtubeUrl) {
      hit.href = lesson.youtubeUrl;
      hit.target = "_blank";
      hit.rel = "noopener noreferrer";
      hit.setAttribute("aria-label", "Watch on YouTube");
      label.className = "pathway-film-affordance";
      label.innerHTML =
        '<span class="pathway-film-affordance-icon">▶</span> Watch on YouTube';
    } else {
      mount.classList.add("is-pending");
      label.className = "pathway-film-link-label";
      label.textContent = "Film coming soon";
    }

    hit.appendChild(image);
    hit.appendChild(label);
    mount.appendChild(hit);
  }

  function renderStudy() {
    var section = document.querySelector("[data-static-study]");
    if (section) {
      section.setAttribute("data-script", unit.script || "");
      if (unit.gloss) section.setAttribute("data-gloss", unit.gloss);
    }

    if (lesson.displayName) {
      document.title =
        lesson.roomLabel +
        " — " +
        lesson.displayName +
        " — Kanji・Music・Landscape";
    }

    var titleEl = document.querySelector("[data-static-study-title]");
    if (titleEl && lesson.displayName) {
      if (unit.kana && unit.kana.length && isKatakana) {
        titleEl.lang = "ja";
        titleEl.textContent = lesson.displayName;
      } else if (unit.kana && unit.kana.length) {
        titleEl.lang = "ja";
        titleEl.textContent = unitTitle(unit);
      } else {
        titleEl.removeAttribute("lang");
        titleEl.textContent = lesson.displayName;
      }
    }

    var leadEl = document.querySelector("[data-static-study-lead]");
    if (leadEl && unit.lead && !leadEl.textContent.trim()) {
      leadEl.textContent = unit.lead;
    }

    var closeEl = document.querySelector("[data-static-study-close]");
    if (closeEl && unit.close && !closeEl.textContent.trim()) {
      closeEl.textContent = unit.close;
    }

    var kanaMount = document.querySelector("[data-static-study-kana]");
    if (kanaMount) {
      if (!unit.kana || !unit.kana.length) {
        kanaMount.hidden = true;
        kanaMount.replaceChildren();
      } else {
      kanaMount.hidden = false;
      kanaMount.replaceChildren();
      var grid = document.createElement("div");
      grid.className = "static-study-kana-grid";
      grid.setAttribute("role", "group");
      grid.setAttribute("aria-label", unitTitle(unit));

      unit.kana.forEach(function (item) {
        var cell = document.createElement(isKatakana ? "button" : "div");
        cell.className = "static-study-kana-cell";
        if (isKatakana) {
          cell.type = "button";
          cell.setAttribute("aria-label", item.kana);
          bindSpeak(cell, item.kana);
        }

        var glyph = document.createElement("span");
        glyph.className = "static-study-kana-glyph";
        glyph.lang = "ja";
        glyph.textContent = item.kana;
        cell.appendChild(glyph);

        if (item.romaji) {
          var romaji = document.createElement("span");
          romaji.className = "static-study-kana-romaji";
          romaji.textContent = item.romaji;
          cell.appendChild(romaji);
        }

        grid.appendChild(cell);
      });

      kanaMount.appendChild(grid);
      }
    }

    var vocabMount = document.querySelector("[data-static-study-vocab]");
    if (vocabMount) {
      vocabMount.replaceChildren();
      var words = unit.vocabulary || [];
      if (!words.length) {
        vocabMount.hidden = true;
        return;
      }
      vocabMount.hidden = false;
      var list = document.createElement("ul");
      list.className = "static-study-vocab-list";
      if (unit.gloss === "english") {
        list.classList.add("static-study-vocab-list--reading");
      }

      words.forEach(function (item) {
        var li = document.createElement("li");
        li.className = "static-study-vocab-item";
        if (unit.gloss === "english") {
          li.classList.add("static-study-vocab-item--reading");
        }

        var word = document.createElement(isKatakana ? "button" : "p");
        word.className = "static-study-vocab-word";
        word.lang = "ja";
        word.textContent = item.word;
        if (isKatakana) {
          word.type = "button";
          word.setAttribute("aria-label", item.word);
          bindSpeak(word, item.word);
        }

        var meaning = document.createElement("p");
        meaning.className = "static-study-vocab-meaning";
        meaning.textContent = item.meaning;

        li.appendChild(word);
        li.appendChild(meaning);
        list.appendChild(li);
      });

      vocabMount.appendChild(list);
    }
  }

  if (typeof course.installRoomNavigation === "function") {
    course.installRoomNavigation();
  }
  if (typeof course.installSongLyrics === "function") {
    course.installSongLyrics();
  }
  renderFilmLink();
  renderStudy();
  if (window.speechSynthesis && isKatakana) {
    window.speechSynthesis.getVoices();
  }
  if (typeof course.installPathwayRomaji === "function") {
    course.installPathwayRomaji();
  }
})();
