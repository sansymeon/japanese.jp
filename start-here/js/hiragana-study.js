/**
 * Renders conventional hiragana study content inside Start Here rooms.
 * Expects data-beginner-lesson on body and hiraganaStudy on the room registry entry.
 */
(function () {
  "use strict";

  var course = window.KmlBeginnerCourse;
  var study = window.KmlHiraganaStudy;
  if (!course || !study) return;

  var lessonId = document.body.getAttribute("data-beginner-lesson");
  var lesson = lessonId ? course.lessons[lessonId] : null;
  if (!lesson || !lesson.hiraganaStudy) return;

  var row = study.rows[lesson.hiraganaStudy];
  if (!row) return;

  function rowTitle(rowData) {
    return rowData.kana.map(function (item) {
      return item.kana;
    }).join("　");
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
    var titleEl = document.querySelector("[data-hiragana-study-title]");
    if (titleEl) {
      titleEl.lang = "ja";
      titleEl.textContent = rowTitle(row);
    }

    var kanaMount = document.querySelector("[data-hiragana-study-kana]");
    if (kanaMount) {
      kanaMount.replaceChildren();
      var grid = document.createElement("div");
      grid.className = "hiragana-study-kana-grid";
      grid.setAttribute("role", "group");
      grid.setAttribute("aria-label", "New kana");

      row.kana.forEach(function (item) {
        var cell = document.createElement("div");
        cell.className = "hiragana-study-kana-cell";

        var glyph = document.createElement("span");
        glyph.className = "hiragana-study-kana-glyph";
        glyph.lang = "ja";
        glyph.textContent = item.kana;

        var romaji = document.createElement("span");
        romaji.className = "hiragana-study-kana-romaji";
        romaji.textContent = item.romaji;

        cell.appendChild(glyph);
        cell.appendChild(romaji);
        grid.appendChild(cell);
      });

      kanaMount.appendChild(grid);
    }

    var vocabMount = document.querySelector("[data-hiragana-study-vocab]");
    if (vocabMount) {
      vocabMount.replaceChildren();
      var list = document.createElement("ul");
      list.className = "hiragana-study-vocab-list";

      row.vocabulary.forEach(function (item) {
        var li = document.createElement("li");
        li.className = "hiragana-study-vocab-item";

        var word = document.createElement("p");
        word.className = "hiragana-study-vocab-word";
        word.lang = "ja";
        word.textContent = item.word;

        var meaning = document.createElement("p");
        meaning.className = "hiragana-study-vocab-meaning";
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
