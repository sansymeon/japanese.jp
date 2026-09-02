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

  function fillNav() {
    var prevLink = document.querySelector("[data-room-nav='prev']");
    if (prevLink) {
      if (lesson.prev != null && course.lessons[lesson.prev]) {
        prevLink.href = "../lesson-" + lesson.prev + "/";
        prevLink.textContent = "← Previous Lesson";
        prevLink.hidden = false;
      } else {
        prevLink.removeAttribute("href");
        prevLink.hidden = true;
      }
    }

    var indexLink = document.querySelector("[data-room-nav='index']");
    if (indexLink) {
      indexLink.href = "../rooms/";
      indexLink.textContent = "Index";
    }

    var nextLink = document.querySelector("[data-room-nav='next']");
    if (nextLink) {
      if (lesson.next != null && course.lessons[lesson.next]) {
        nextLink.href = "../lesson-" + lesson.next + "/";
        nextLink.textContent = "Next Lesson →";
        nextLink.hidden = false;
      } else {
        nextLink.removeAttribute("href");
        nextLink.hidden = true;
      }
    }
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
    image.width = 1200;
    image.height = 800;
    image.loading = "eager";
    image.decoding = "async";

    var label = document.createElement("span");
    label.className = "pathway-film-link-label";

    if (lesson.youtubeUrl) {
      hit.href = lesson.youtubeUrl;
      hit.target = "_blank";
      hit.rel = "noopener noreferrer";
      hit.setAttribute("aria-label", "Watch room film on YouTube");
      label.textContent = "Watch on YouTube";
    } else {
      mount.classList.add("is-pending");
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
      titleEl.remove();
    }

    var kanaMount = document.querySelector("[data-static-study-kana]");
    if (kanaMount) {
      kanaMount.replaceChildren();
      var grid = document.createElement("div");
      grid.className = "static-study-kana-grid";
      grid.setAttribute("role", "group");
      grid.setAttribute(
        "aria-label",
        unit.script === "katakana" ? "New katakana" : "New hiragana"
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

  fillNav();
  renderFilmLink();
  renderStudy();
})();
