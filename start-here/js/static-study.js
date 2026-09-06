/**
 * Renders the static study block inside Start Here rooms.
 *
 * Rooms opt in with `staticStudy` (a unit id from KmlStaticStudy).
 * The same renderer serves hiragana and later katakana units.
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

  function unitTitle(unitData) {
    return unitData.kana
      .map(function (item) {
        return item.kana;
      })
      .join("　");
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
    }

    if (lesson.displayName) {
      document.title =
        lesson.roomLabel +
        " — " +
        lesson.displayName +
        " — Kanji・Music・Landscape";
    }

    var titleEl = document.querySelector("[data-static-study-title]");
    if (titleEl) {
      titleEl.lang = "ja";
      titleEl.textContent = unitTitle(unit);
    }

    var kanaMount = document.querySelector("[data-static-study-kana]");
    if (kanaMount) {
      kanaMount.replaceChildren();
      var grid = document.createElement("div");
      grid.className = "static-study-kana-grid";
      grid.setAttribute("role", "group");
      grid.setAttribute(
        "aria-label",
        lessonId === "0"
          ? "Hiragana you will meet in this room"
          : unit.script === "katakana"
            ? "New katakana"
            : "New hiragana"
      );

      unit.kana.forEach(function (item) {
        var cell = document.createElement("div");
        cell.className = "static-study-kana-cell";

        var glyph = document.createElement("span");
        glyph.className = "static-study-kana-glyph";
        glyph.lang = "ja";
        glyph.textContent = item.kana;

        var romaji = document.createElement("span");
        romaji.className = "static-study-kana-romaji";
        romaji.textContent = item.romaji;

        cell.appendChild(glyph);
        cell.appendChild(romaji);
        grid.appendChild(cell);
      });

      kanaMount.appendChild(grid);
    }

    var vocabMount = document.querySelector("[data-static-study-vocab]");
    if (vocabMount) {
      vocabMount.replaceChildren();
      var list = document.createElement("ul");
      list.className = "static-study-vocab-list";

      unit.vocabulary.forEach(function (item) {
        var li = document.createElement("li");
        li.className = "static-study-vocab-item";

        var word = document.createElement("p");
        word.className = "static-study-vocab-word";
        word.lang = "ja";
        word.textContent = item.word;

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
  if (typeof course.installPathwayRomaji === "function") {
    course.installPathwayRomaji();
  }
})();
