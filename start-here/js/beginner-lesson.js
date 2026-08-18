/**
 * Beginner lesson chrome: Romaji ON/OFF + Your Hiragana puzzle + study-room music.
 *
 * Romaji and the puzzle are independent. The puzzle only fills.
 * Romaji is a global line under Japanese, never mixed per-kana ruby.
 *
 * Study-room atmosphere audio loops only after an explicit press.
 * It never autoplays. Preference is remembered; the next room still
 * waits for a click.
 */
(function () {
  "use strict";

  var course = window.KmlBeginnerCourse;
  if (!course) return;

  var root = document.querySelector("[data-beginner-lesson]");
  if (!root) return;

  var lessonId = String(root.getAttribute("data-beginner-lesson") || "");
  var lesson = course.lessons[lessonId];
  if (!lesson) return;

  function storedRomaji() {
    try {
      var value = localStorage.getItem(course.romajiStorageKey);
      if (value === "on" || value === "off") return value;
    } catch (err) {
      /* private mode */
    }
    return null;
  }

  function persistRomaji(value) {
    try {
      localStorage.setItem(course.romajiStorageKey, value);
    } catch (err) {
      /* private mode */
    }
  }

  function persistMusic(value) {
    try {
      localStorage.setItem(course.musicStorageKey, value);
    } catch (err) {
      /* private mode */
    }
  }

  function romajiIsOn() {
    var stored = storedRomaji();
    if (stored) return stored === "on";
    return (lesson.romajiDefault || "on") === "on";
  }

  function applyRomaji(on) {
    document.documentElement.classList.toggle("is-romaji-on", on);
    document.documentElement.classList.toggle("is-romaji-off", !on);
    var buttons = document.querySelectorAll("[data-romaji-toggle]");
    buttons.forEach(function (btn) {
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      btn.textContent = on ? "Romaji: ON" : "Romaji: OFF";
    });
  }

  function bindToggle() {
    document.querySelectorAll("[data-romaji-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var next = !document.documentElement.classList.contains("is-romaji-on");
        persistRomaji(next ? "on" : "off");
        applyRomaji(next);
      });
    });
  }

  function cellEl(kana, encountered, isNew, emptySlot) {
    var el = document.createElement("span");
    el.className = "kana-puzzle-cell";
    if (emptySlot) {
      el.classList.add("is-void");
      el.setAttribute("aria-hidden", "true");
      return el;
    }
    if (encountered[kana]) {
      el.textContent = kana;
      el.lang = "ja";
      if (isNew) el.classList.add("is-new");
    } else {
      el.classList.add("is-empty");
      el.setAttribute("aria-hidden", "true");
    }
    return el;
  }

  function renderGrid(container, fillSet, newSet, mode) {
    if (!container) return;
    container.innerHTML = "";
    container.classList.add("kana-puzzle");
    if (mode) container.classList.add("kana-puzzle--" + mode);

    var encountered = {};
    (fillSet || []).forEach(function (k) {
      encountered[k] = true;
    });
    var news = {};
    (newSet || []).forEach(function (k) {
      news[k] = true;
    });

    course.gojuonColumns.forEach(function (column) {
      var col = document.createElement("div");
      col.className = "kana-puzzle-col";
      col.dataset.rowId = column.id;
      column.cells.forEach(function (kana) {
        if (kana === null) {
          col.appendChild(cellEl(null, encountered, false, true));
        } else if (mode === "reference") {
          var all = {};
          all[kana] = true;
          col.appendChild(cellEl(kana, all, false, false));
        } else {
          col.appendChild(cellEl(kana, encountered, Boolean(news[kana]), false));
        }
      });
      container.appendChild(col);
    });
  }

  function renderPuzzle() {
    var mount = document.querySelector("[data-kana-puzzle]");
    if (!mount || !lesson.showPuzzle) return;
    renderGrid(mount, lesson.encounteredKana, lesson.newKana, "learner");

    var countEl = document.querySelector("[data-kana-puzzle-count]");
    if (countEl) {
      var n = (lesson.encounteredKana || []).length;
      countEl.textContent = n
        ? "Hiragana: " + n + " / " + course.boxCount
        : "Hiragana: 0 / " + course.boxCount;
    }
  }

  function hiraganaFromLyrics(lyrics) {
    var present = {};
    (lyrics || []).forEach(function (item) {
      String((item && item.ja) || "").split("").forEach(function (ch) {
        if (ch === "っ") return;
        if (ch >= "ぁ" && ch <= "ゖ") present[ch] = true;
      });
    });
    return present;
  }

  function gojuonBoxes() {
    var boxes = {};
    course.gojuonColumns.forEach(function (column) {
      column.cells.forEach(function (kana) {
        if (kana) boxes[kana] = true;
      });
    });
    return boxes;
  }

  function renderVoicedExtras(afterEl, extras) {
    var parent = afterEl.parentNode;
    var existing = parent.querySelector("[data-kana-chart-voiced]");
    if (existing) existing.remove();
    if (!extras.length) return;

    var order =
      "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゃゅょ";
    var present = {};
    extras.forEach(function (kana) {
      present[kana] = true;
    });
    var row = document.createElement("div");
    row.className = "kana-puzzle-voiced";
    row.setAttribute("data-kana-chart-voiced", "");
    row.lang = "ja";
    order.split("").forEach(function (kana) {
      if (!present[kana]) return;
      row.appendChild(cellEl(kana, present, false, false));
      present[kana] = false;
    });
    extras.forEach(function (kana) {
      if (present[kana]) row.appendChild(cellEl(kana, present, false, false));
    });
    afterEl.insertAdjacentElement("afterend", row);
  }

  function renderLyricKana(container, lyrics) {
    var present = hiraganaFromLyrics(lyrics);
    var boxes = gojuonBoxes();
    var basic = [];
    var extras = [];
    Object.keys(present).forEach(function (kana) {
      if (boxes[kana]) basic.push(kana);
      else extras.push(kana);
    });
    renderGrid(container, basic, [], "learner");
    renderVoicedExtras(container, extras);
  }

  function renderReference() {
    var mount = document.querySelector("[data-kana-chart-full]");
    if (!mount || !lesson.showReferenceChart) return;
    var data = window.KmlBeginnerRoomData;
    if (data && data.lyrics && data.lyrics.length) {
      renderLyricKana(mount, data.lyrics);
      return;
    }
    renderGrid(mount, null, null, "reference");
  }

  function fillNav() {
    var status = document.querySelector("[data-room-nav='current']");
    if (status) status.textContent = lesson.roomLabel || ("Room " + lesson.id);

    var prevLink = document.querySelector("[data-room-nav='prev']");
    if (prevLink && lesson.prev != null && course.lessons[lesson.prev]) {
      var prev = course.lessons[lesson.prev];
      var prevName = prev.id === "0" ? prev.displayName : prev.roomLabel;
      prevLink.textContent = "← " + prevName;
    }

    var nextLink = document.querySelector("[data-room-nav='next']");
    if (nextLink && lesson.next != null && course.lessons[lesson.next]) {
      var next = course.lessons[lesson.next];
      nextLink.textContent = "Continue to " + next.roomLabel + " →";
    }
  }

  function bindAudio() {
    document.querySelectorAll("[data-beginner-audio]").forEach(function (audio) {
      function hide() {
        audio.hidden = true;
      }
      audio.addEventListener("error", hide);
      if (audio.error) hide();
    });
  }

  function bindStudyMusic() {
    if (lesson.mode !== "study-room") return;
    var pool = lesson.atmospherePool;
    var single = lesson.atmosphereAudio;
    if ((!pool || !pool.length) && !single) return;
    var btn = document.querySelector("[data-study-music]");
    if (!btn) return;

    var audio = new Audio();
    audio.preload = "metadata";
    var currentSrc = "";
    var shuffle = pool && pool.length > 1;

    function pickNext() {
      if (!shuffle) return single;
      var choices = pool.filter(function (src) {
        return src !== currentSrc;
      });
      if (!choices.length) choices = pool.slice();
      return choices[Math.floor(Math.random() * choices.length)];
    }

    function loadNext() {
      currentSrc = pickNext();
      audio.src = currentSrc;
    }

    if (shuffle) {
      audio.loop = false;
      loadNext();
      audio.addEventListener("ended", function () {
        if (btn.getAttribute("aria-pressed") !== "true") return;
        loadNext();
        audio.play().catch(function () {
          setPlaying(false);
        });
      });
    } else {
      audio.loop = true;
      audio.src = single;
    }

    btn.hidden = false;

    function setPlaying(on) {
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      btn.textContent = on ? "♪ Room music on" : "♪ Play room music";
    }

    setPlaying(false);

    btn.addEventListener("click", function () {
      if (audio.paused) {
        audio
          .play()
          .then(function () {
            persistMusic("on");
            setPlaying(true);
          })
          .catch(function () {
            setPlaying(false);
          });
      } else {
        audio.pause();
        persistMusic("off");
        setPlaying(false);
      }
    });
  }

  applyRomaji(romajiIsOn());
  bindToggle();
  bindAudio();
  bindStudyMusic();
  fillNav();
  renderPuzzle();
  renderReference();
})();
