/**
 * Beginner lesson chrome: Romaji ON/OFF + Your Hiragana puzzle.
 *
 * Romaji and the puzzle are independent. The puzzle only fills.
 * Romaji is a global line under Japanese, never mixed per-kana ruby.
 *
 * Room film is the YouTube doorway. Local MP3 atmosphere is not a
 * page control (files remain on disk). Visitor-facing song/audio
 * download links are stripped; YouTube remains the listening path.
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

    var newcomers = lesson.newKana || [];
    var meetEl = document.querySelector("[data-kana-meet]");
    if (newcomers.length) {
      if (!meetEl) {
        meetEl = document.createElement("p");
        meetEl.className = "kana-meet-label";
        meetEl.setAttribute("data-kana-meet", "");
        mount.parentNode.insertBefore(meetEl, mount);
      }
      meetEl.hidden = false;
      meetEl.textContent = "In this room, you’ll meet:";
    } else if (meetEl) {
      meetEl.hidden = true;
    }

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

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function splitHeroTitle(text) {
    var t = String(text || "").replace(/\s+/g, " ").trim();
    var m = t.match(/^(Room\s+\d+)\s*[—–-]\s*(.+)$/);
    if (m) return { room: m[1], title: m[2] };
    return { room: t, title: "" };
  }

  function youtubeWatchFromEmbed(src) {
    var m = String(src || "").match(/embed\/([^?&/]+)/);
    return m ? "https://www.youtube.com/watch?v=" + m[1] : "";
  }

  function pathwayRoomNumber() {
    var n = parseInt(lessonId, 10);
    return n >= 1 && n <= 42 ? n : null;
  }

  var WATCH_ON_YOUTUBE = "Watch on YouTube";

  function convertHeroFilmToDoorway() {
    var hero = document.querySelector(".room-hero");
    if (!hero || document.querySelector(".room-section--film-top")) return;
    var film = hero.querySelector("a.room-hero-film");
    var img = hero.querySelector(".room-hero-media img");
    var h1 = hero.querySelector("h1");
    if (!img || !h1) return;
    var href = film ? film.getAttribute("href") : "";
    if (!href) {
      var iframe = document.querySelector("iframe[src*='youtube.com/embed']");
      if (iframe) href = youtubeWatchFromEmbed(iframe.getAttribute("src"));
    }
    if (!href) return;

    var parts = splitHeroTitle(h1.textContent || "");
    var roomKicker = "Room " + (pathwayRoomNumber() != null ? pathwayRoomNumber() : lessonId);
    var titleText = parts.title;
    if (!titleText) {
      var raw = (h1.textContent || "").replace(/\s+/g, " ").trim();
      if (!/^Room\s+\d+$/i.test(raw)) titleText = raw;
      else titleText = parts.room;
    }
    var section = document.createElement("section");
    section.className = "room-section room-section--film-top";
    section.id = "film";
    section.setAttribute("aria-label", "Room film");
    section.innerHTML =
      '<div class="room-container">' +
      '<header class="room-film-heading">' +
      '<p class="room-film-room">' +
      escapeHtml(roomKicker) +
      "</p>" +
      "<h1>" +
      escapeHtml(titleText) +
      "</h1>" +
      "</header>" +
      '<div class="pathway-film-link">' +
      '<a class="pathway-film-link-hit" href="' +
      escapeHtml(href) +
      '" target="_blank" rel="noopener noreferrer" aria-label="' +
      WATCH_ON_YOUTUBE +
      '">' +
      img.outerHTML +
      "</a></div></div>";
    hero.replaceWith(section);

    document.querySelectorAll(".pathway-film-exhibit").forEach(function (el) {
      el.remove();
    });
    var skip = document.querySelector(".skip-link");
    if (skip) {
      skip.setAttribute("href", "#film");
      skip.textContent = "Skip to film";
    }
  }

  function normalizeFilmHeading() {
    var n = pathwayRoomNumber();
    if (n == null) return;
    var heading = document.querySelector(
      ".room-section--film-top .room-film-heading"
    );
    if (!heading) return;

    var roomLabel = "Room " + n;
    var h1 = heading.querySelector("h1");
    var kicker = heading.querySelector(".room-film-room");
    var titleText = "";

    if (h1) {
      var h1Text = (h1.textContent || "").replace(/\s+/g, " ").trim();
      if (!/^Room\s+\d+$/i.test(h1Text)) titleText = h1Text;
    }
    if (!titleText) {
      var extra = heading.querySelector("p:not(.room-film-room)");
      if (extra) titleText = extra.textContent.replace(/\s+/g, " ").trim();
    }

    if (!kicker) {
      kicker = document.createElement("p");
      kicker.className = "room-film-room";
    }
    kicker.textContent = roomLabel;

    if (!h1) {
      h1 = document.createElement("h1");
    }
    if (titleText) h1.textContent = titleText;

    heading.innerHTML = "";
    heading.appendChild(kicker);
    heading.appendChild(h1);
  }

  function stripFilmTopExtras() {
    if (pathwayRoomNumber() == null) return;
    var top = document.querySelector(".room-section--film-top .room-container");
    if (!top) return;
    Array.prototype.slice.call(top.children).forEach(function (el) {
      if (el.classList.contains("room-film-heading")) return;
      if (el.classList.contains("pathway-film-link")) return;
      el.remove();
    });
  }

  function setWatchAffordance(hit) {
    hit.setAttribute("aria-label", WATCH_ON_YOUTUBE);
    var badge = hit.querySelector(
      ".pathway-film-affordance, .pathway-film-link-label"
    );
    if (!badge) {
      badge = document.createElement("span");
      hit.appendChild(badge);
    }
    badge.className = "pathway-film-affordance";
    badge.setAttribute("aria-hidden", "true");
    badge.innerHTML =
      '<span class="pathway-film-affordance-icon">▶</span> ' + WATCH_ON_YOUTUBE;
  }

  function enhanceFilmDoorways() {
    var scope =
      pathwayRoomNumber() != null
        ? ".room-section--film-top .pathway-film-link-hit"
        : ".pathway-film-link-hit";
    document.querySelectorAll(scope).forEach(function (hit) {
      if (pathwayRoomNumber() != null) {
        setWatchAffordance(hit);
        return;
      }
      if (hit.querySelector(".pathway-film-affordance, .pathway-film-link-label")) {
        return;
      }
      setWatchAffordance(hit);
    });
    document.querySelectorAll(".room-doorway-hint").forEach(function (el) {
      el.remove();
    });
  }

  function removeStudyMusicControls() {
    document.querySelectorAll("[data-study-music]").forEach(function (el) {
      el.remove();
    });
    document.querySelectorAll("a[href*='.mp3']").forEach(function (el) {
      el.remove();
    });
    document.querySelectorAll(".interlude-keep").forEach(function (el) {
      if (!el.querySelector("a, button")) el.remove();
    });
    document.querySelectorAll(".beginner-assist").forEach(function (el) {
      if (!el.querySelector("button, a")) el.remove();
    });
  }

  function installRomajiControl() {
    var n = parseInt(lessonId, 10);
    if (!(n >= 0 && n <= 42)) return;

    document
      .querySelectorAll(".room-section--film-top .pathway-learner-controls")
      .forEach(function (el) {
        el.remove();
      });

    var teaching = document.querySelector(
      ".room-section--film-top + .room-section .room-container"
    );
    if (!teaching) return;

    var bar = teaching.querySelector(".pathway-learner-controls");
    if (!bar) {
      bar = document.createElement("div");
      bar.className = "pathway-learner-controls";
      bar.innerHTML =
        '<button type="button" data-romaji-toggle aria-pressed="true">Romaji: ON</button>';
    }
    teaching.insertBefore(bar, teaching.firstChild);

    document.querySelectorAll("[data-romaji-toggle]").forEach(function (btn) {
      if (!btn.closest(".pathway-learner-controls")) btn.remove();
    });
    document.querySelectorAll(".beginner-assist").forEach(function (el) {
      if (!el.querySelector("button, a")) el.remove();
    });
  }

  function installPathwayShell() {
    convertHeroFilmToDoorway();
    normalizeFilmHeading();
    stripFilmTopExtras();
    enhanceFilmDoorways();
    removeStudyMusicControls();
    if (typeof course.installRoomNavigation === "function") {
      course.installRoomNavigation();
    }
    installRomajiControl();
    if (typeof course.installSongLyrics === "function") {
      course.installSongLyrics();
    }
    if (typeof course.installPathwayRomaji === "function") {
      course.installPathwayRomaji();
    }
  }

  installPathwayShell();
  applyRomaji(romajiIsOn());
  bindToggle();
  renderPuzzle();
  renderReference();
})();
