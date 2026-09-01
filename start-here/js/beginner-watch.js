/**
 * Start Here — Read / Watch mode chrome for dual-mode rooms.
 *
 * Rooms with watchModes embed YouTube directly in HTML (Room 39 pattern).
 * This script toggles visibility between Read and Watch panels. No autoplay.
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

  var modes = lesson.watchModes || null;
  if (!(modes && modes.indexOf("watch") !== -1 && modes.indexOf("read") !== -1)) {
    return;
  }

  var storageKey = (course.watchStorageKey || "kml-beginner-watch-mode") + ":" + lessonId;
  var readPanel = document.querySelector("[data-watch-read]");
  var watchPanel = document.querySelector("[data-watch-watch]");
  var modeRoot = document.querySelector("[data-watch-mode]");

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
    if (next !== "read" && next !== "watch") next = "watch";

    document.body.classList.toggle("is-watch-mode", next === "watch");
    document.body.classList.toggle("is-read-mode", next === "read");
    setToggleState(next);
    persistMode(next);

    if (readPanel) {
      if (next === "read") readPanel.removeAttribute("hidden");
      else readPanel.setAttribute("hidden", "");
    }
    if (watchPanel) {
      if (next === "watch") watchPanel.removeAttribute("hidden");
      else watchPanel.setAttribute("hidden", "");
    }
  }

  if (!modeRoot) return;
  modeRoot.hidden = false;
  modeRoot.querySelectorAll("[data-watch-select]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      applyStudyDualMode(btn.getAttribute("data-watch-select") || "watch");
    });
  });

  var initial = storedMode() || lesson.watchDefault || "watch";
  applyStudyDualMode(initial);
})();
