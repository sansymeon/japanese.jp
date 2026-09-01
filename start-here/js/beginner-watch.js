/**
 * Start Here — Read / Watch mode chrome for study rooms.
 *
 * When a room declares watchYoutubeId (or watchModes including "watch"),
 * show a quiet Read | Watch & Listen toggle. Watch embeds unlisted YouTube
 * (Room 39 pattern). Read keeps the existing page body.
 *
 * Guided-song rooms with YouTube use a static embed in HTML (no local MP3).
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

  var youtubeId = String(lesson.watchYoutubeId || "").trim();
  var modes = lesson.watchModes || null;
  var wantsWatch = Boolean(youtubeId) || (modes && modes.indexOf("watch") !== -1);
  if (!wantsWatch && !youtubeId) {
    if (!(modes && modes.indexOf("read") !== -1 && modes.indexOf("watch") !== -1)) {
      return;
    }
  }

  var storageKey = (course.watchStorageKey || "kml-beginner-watch-mode") + ":" + lessonId;
  var readPanel = document.querySelector("[data-watch-read]");
  var watchPanel = document.querySelector("[data-watch-watch]");
  var modeRoot = document.querySelector("[data-watch-mode]");
  var filmMount = document.querySelector("[data-watch-film]");

  function storedMode() {
    try {
      var value = localStorage.getItem(storageKey);
      if (value === "read" || value === "watch") return value;
    } catch (err) {
      /* private mode */
    }
    return null;
  }

  function persistMode(value) {
    try {
      localStorage.setItem(storageKey, value);
    } catch (err) {
      /* private mode */
    }
  }

  function embedUrl(id) {
    return (
      "https://www.youtube.com/embed/" +
      encodeURIComponent(id) +
      "?rel=0&modestbranding=1"
    );
  }

  function ensureFilm(id) {
    if (!filmMount || !id) return;
    if (filmMount.querySelector("iframe")) return;
    var wrap = document.createElement("div");
    wrap.className = "pathway-film";
    var iframe = document.createElement("iframe");
    iframe.src = embedUrl(id);
    iframe.title = (lesson.displayName || "Start Here") + " — Watch & Listen";
    iframe.setAttribute(
      "allow",
      "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    );
    iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
    iframe.setAttribute("allowfullscreen", "");
    wrap.appendChild(iframe);
    filmMount.appendChild(wrap);
  }

  function setToggleState(mode) {
    if (!modeRoot) return;
    modeRoot.querySelectorAll("[data-watch-select]").forEach(function (btn) {
      var on = btn.getAttribute("data-watch-select") === mode;
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      btn.classList.toggle("is-active", on);
    });
  }

  function applyStudyDualMode(mode) {
    if (!readPanel && !watchPanel) return;

    var next = mode;
    if (next !== "read" && next !== "watch") next = "read";

    document.body.classList.toggle("is-watch-mode", next === "watch");
    document.body.classList.toggle("is-read-mode", next === "read");
    setToggleState(next);
    persistMode(next);

    if (readPanel) {
      if (next === "read") readPanel.removeAttribute("hidden");
      else readPanel.setAttribute("hidden", "");
    }
    if (watchPanel) {
      if (next === "watch") {
        watchPanel.removeAttribute("hidden");
        if (youtubeId) ensureFilm(youtubeId);
      } else {
        watchPanel.setAttribute("hidden", "");
      }
    }
  }

  function bindStudyToggle() {
    if (!modeRoot) return;
    modeRoot.hidden = false;
    modeRoot.querySelectorAll("[data-watch-select]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyStudyDualMode(btn.getAttribute("data-watch-select") || "read");
      });
    });

    if (!youtubeId) {
      var pending = document.querySelector("[data-watch-pending]");
      if (pending) pending.hidden = false;
    }
  }

  if (lesson.mode === "study-room" && modes && modes.indexOf("watch") !== -1) {
    bindStudyToggle();
    var initial = storedMode() || lesson.watchDefault || "read";
    applyStudyDualMode(initial);
  }
})();
