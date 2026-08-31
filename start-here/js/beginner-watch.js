/**
 * Start Here — Read / Watch mode chrome.
 *
 * When a room declares watchYoutubeId (or watchModes including "watch"),
 * show a quiet Read | Watch & Listen toggle. Watch embeds unlisted YouTube
 * (Room 39 pattern). Read keeps the existing page body.
 *
 * Rooms without a YouTube id keep current behavior. Guided-song rooms that
 * set watchYoutubeId prefer the embed as the primary film and leave the
 * after-listen web section in place; the local guided stage is hidden but
 * not deleted from the HTML (fallback / rollback).
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
    /* Still allow explicit dual-mode rooms awaiting upload. */
    if (!(modes && modes.indexOf("read") !== -1 && modes.indexOf("watch") !== -1)) {
      return;
    }
  }

  var storageKey = (course.watchStorageKey || "kml-beginner-watch-mode") + ":" + lessonId;
  var guidedStage = document.querySelector("[data-guided-song]");
  var after = document.querySelector("[data-guided-after]");
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

  function revealAfterForYoutube() {
    if (!after) return;
    after.removeAttribute("hidden");
    document.body.classList.add("is-guided-complete");
    document.body.classList.add("is-watch-youtube");
    after.querySelectorAll(".reveal").forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  function applyGuidedYoutubePrimary() {
    if (!youtubeId) return false;
    if (!guidedStage && !filmMount) return false;

    ensureFilm(youtubeId);
    document.body.classList.add("is-watch-youtube");

    if (guidedStage) {
      guidedStage.setAttribute("hidden", "");
      guidedStage.setAttribute("aria-hidden", "true");
    }

    var ytSection = document.querySelector("[data-watch-youtube-primary]");
    if (ytSection) {
      ytSection.removeAttribute("hidden");
    }

    var guidedViews = document.querySelector("[data-guided-view-list]");
    var staticViews = document.querySelector("[data-static-verse-list]");
    if (guidedViews) guidedViews.setAttribute("hidden", "");
    if (staticViews) staticViews.removeAttribute("hidden");

    revealAfterForYoutube();

    /* Static verse toggles in after — do not depend on guided-song replay. */
    document.querySelectorAll("[data-static-verse-select]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var view = btn.getAttribute("data-static-verse-select") || "none";
        document.querySelectorAll("[data-static-verse]").forEach(function (panel) {
          var match = panel.getAttribute("data-static-verse") === view;
          panel.hidden = view === "none" ? true : !match;
        });
        document.querySelectorAll("[data-static-verse-select]").forEach(function (b) {
          b.setAttribute(
            "aria-pressed",
            b.getAttribute("data-static-verse-select") === view ? "true" : "false"
          );
        });
      });
    });

    return true;
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

    /* Study music belongs to Read. Pause when switching to Watch. */
    if (next === "watch") {
      var musicBtn = document.querySelector("[data-study-music]");
      if (musicBtn && musicBtn.getAttribute("aria-pressed") === "true") {
        musicBtn.click();
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

    /* Watch may be selected before upload — show pending copy instead of an embed. */
    if (!youtubeId) {
      var pending = document.querySelector("[data-watch-pending]");
      if (pending) pending.hidden = false;
    }
  }

  /* Guided-song rooms with a YouTube id → primary embed path. */
  if (lesson.mode === "guided-song" && youtubeId) {
    applyGuidedYoutubePrimary();
    return;
  }

  /* Study rooms with dual modes → Read / Watch toggle. */
  if (lesson.mode === "study-room" && modes && modes.indexOf("watch") !== -1) {
    bindStudyToggle();
    var initial = storedMode() || lesson.watchDefault || "read";
    applyStudyDualMode(initial);
  }
})();
