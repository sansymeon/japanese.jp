/**
 * Guided-song player.
 *
 * MP3 = soundtrack. JSON = timing/conductor. HTML/CSS = presentation.
 *
 * Room data: start-here/data/rooms/{id}.js (loaded as a script; .json is the
 * same object for editing). Asset paths are relative to that data file.
 *   id, displayName, roomLabel, mode: "guided-song",
 *   imageCrossfade?: seconds (image dissolve; lyrics are not delayed)
 *   opening { image, title, lead, cta, hint? },
 *   film[] { id?, start, image, transition?, crossfade?, crop? }
 *     Optional. When present, paintings are a master visual sequence
 *     independent of any lyric overlay. crop is an object-position
 *     (e.g. "62% 40%") applied to the incoming layer.
 *   lyrics[] { id?, start, ja, romaji, overlay?, align? }
 *     Optional. Timed independently of film. Empty = listen only.
 *     When both film and lyrics are present, the clock applies both.
 *     guided-stage--interlude is listen-only (empty lyrics), not a
 *     singing room that happens to use film.
 *   Film rooms may also offer whole-piece text views via
 *   [data-guided-view] / [data-verse-panel]. Those are not timed
 *   karaoke and must not change the film.
 *   scenes[] { id?, start (seconds), image, ja, romaji,
 *              transition?: "crossfade"|"cut", overlay?: "default"|"none",
 *              align?: "center"|"start"|"end",
 *              crossfade?: seconds for this image change only }
 *     Used when film is absent (Rooms 0, 1, 3, 5).
 *
 * State is derived from audio.currentTime. Seek and pause stay in sync
 * because the view only follows the soundtrack clock.
 *
 * [data-guided-skip] ("Skip listening") stops audio and calls revealAfter()
 * so the learner stays in this room. It does not navigate away.
 */
(function () {
  "use strict";

  var course = window.KmlBeginnerCourse;
  if (!course) return;

  var mount = document.querySelector("[data-guided-song]");
  if (!mount) return;

  var root = document.querySelector("[data-beginner-lesson]");
  var lessonId = root ? String(root.getAttribute("data-beginner-lesson") || "") : "";
  var lesson = course.lessons[lessonId];
  if (!lesson || lesson.mode !== "guided-song" || !lesson.dataSrc) return;

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var dataUrl = null;
  var audio = new Audio();
  audio.preload = "auto";
  var scenes = [];
  var film = [];
  var lyrics = [];
  var filmMode = false;
  var config = null;
  var currentSceneId = null;
  var currentFilmId = null;
  var currentLyricId = null;
  var activeLayer = 0;
  var raf = 0;
  var seeking = false;
  var started = false;
  var completed = false;
  var ready = false;
  var pendingStart = false;
  var playGeneration = 0;
  var currentView = "none";
  var heardOnce = false;

  var layers = mount.querySelectorAll(".guided-layer");
  var welcome = mount.querySelector("[data-guided-welcome]");
  var lyric = mount.querySelector("[data-guided-lyric]");
  var jaEl = mount.querySelector("[data-guided-ja]");
  var romajiEl = mount.querySelector("[data-guided-romaji]");
  var startBtn = mount.querySelector("[data-guided-start]");
  var transport = mount.querySelector("[data-guided-transport]");
  var pauseBtn = mount.querySelector("[data-guided-pause]");
  var seekEl = mount.querySelector("[data-guided-seek]");
  var timeEl = mount.querySelector("[data-guided-time]");
  var after = document.querySelector("[data-guided-after]");

  function pageDirHref() {
    var href = window.location.href.split("#")[0].split("?")[0];
    if (/\.html?$/i.test(href)) return href.replace(/[^/]+$/, "");
    if (href.charAt(href.length - 1) !== "/") return href + "/";
    return href;
  }

  function roomDataUrl() {
    if (window.KmlBeginnerRoomBase) return new URL(window.KmlBeginnerRoomBase);
    return new URL(lesson.dataSrc, pageDirHref());
  }

  function resolveUrl(path) {
    if (!path) return "";
    return new URL(path, dataUrl).href;
  }

  function itemAt(list, time) {
    var found = list[0] || null;
    var i;
    for (i = 0; i < list.length; i += 1) {
      if (list[i].start <= time) found = list[i];
      else break;
    }
    return found;
  }

  function sceneAt(time) {
    return itemAt(scenes, time);
  }

  function preload(src) {
    if (!src) return;
    var img = new Image();
    img.src = src;
  }

  function setLayerSrc(layer, src) {
    if (!layer || !src) return;
    if (layer.getAttribute("src") !== src) layer.setAttribute("src", src);
  }

  function showImage(src, transition, duration, crop) {
    if (!layers.length) return;
    var current = layers[activeLayer];
    if (current && current.getAttribute("src") === src) {
      if (crop) current.style.objectPosition = crop;
      return;
    }

    if (typeof duration === "number" && duration >= 0) {
      mount.style.setProperty("--guided-crossfade", duration + "s");
    }

    var nextIndex = layers.length > 1 ? 1 - activeLayer : 0;
    var next = layers[nextIndex];
    setLayerSrc(next, src);
    if (crop) next.style.objectPosition = crop;
    else next.style.objectPosition = "";
    next.removeAttribute("hidden");

    if (layers.length < 2 || reduceMotion || transition === "cut" || duration === 0) {
      if (current && current !== next) current.classList.remove("is-active");
      next.classList.add("is-active");
      activeLayer = nextIndex;
      return;
    }

    next.classList.add("is-active");
    if (current) current.classList.remove("is-active");
    activeLayer = nextIndex;
  }

  function setLyric(scene) {
    if (!lyric || !jaEl) return;
    var text = scene && scene.ja ? scene.ja : "";
    var romaji = scene && scene.romaji ? scene.romaji : "";
    var hide = !text || (scene && scene.overlay === "none");

    if (hide) {
      lyric.hidden = true;
      jaEl.textContent = "";
      if (romajiEl) romajiEl.textContent = "";
      return;
    }

    lyric.hidden = false;
    lyric.dataset.align = scene.align || "center";
    jaEl.textContent = text;
    if (romajiEl) romajiEl.textContent = romaji;
  }

  function applyScene(scene, force) {
    if (!scene) return;
    var id = scene.id || String(scene.start);
    if (!force && id === currentSceneId) return;
    currentSceneId = id;
    showImage(
      scene.image,
      scene.transition || "crossfade",
      scene.crossfade,
      scene.crop
    );
    setLyric(scene);
  }

  function applyFilm(item, force, cut) {
    if (!item) return;
    var id = item.id || String(item.start);
    if (!force && id === currentFilmId) return;
    currentFilmId = id;
    mount.dataset.guidedFilm = id;
    showImage(
      item.image,
      cut ? "cut" : item.transition || "crossfade",
      cut ? 0 : item.crossfade,
      item.crop
    );
  }

  function applyLyric(item, force) {
    var id = item ? item.id || String(item.start) : "none";
    if (!force && id === currentLyricId) return;
    currentLyricId = id;
    setLyric(item);
  }

  function applyView() {
    var panels = mount.querySelectorAll("[data-verse-panel]");
    if (!panels.length) return;
    var show = currentView && currentView !== "none";
    if (lyric) lyric.hidden = !show;
    mount.classList.toggle("is-showing-verse", show);
    panels.forEach(function (panel) {
      if (panel.getAttribute("data-verse-panel") === currentView) {
        panel.removeAttribute("hidden");
      } else {
        panel.setAttribute("hidden", "");
      }
    });
  }

  function formatTime(seconds) {
    if (!isFinite(seconds) || seconds < 0) seconds = 0;
    var total = Math.floor(seconds);
    var m = Math.floor(total / 60);
    var s = total % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  function syncTransport() {
    var duration = audio.duration || 0;
    var t = audio.currentTime || 0;
    if (seekEl && duration && !seeking) {
      seekEl.value = String(Math.round((t / duration) * 1000));
    }
    if (timeEl) {
      timeEl.textContent = formatTime(t) + (duration ? " / " + formatTime(duration) : "");
    }
    if (pauseBtn) {
      pauseBtn.setAttribute("aria-pressed", audio.paused ? "false" : "true");
      pauseBtn.textContent = audio.paused ? "Play" : "Pause";
    }
  }

  function syncTo(time) {
    if (filmMode) {
      applyFilm(itemAt(film, time), false, seeking);
      if (lyrics.length) applyLyric(itemAt(lyrics, time), false);
    } else {
      applyScene(sceneAt(time), false);
    }
    syncTransport();
  }

  function tick() {
    if (!seeking) syncTo(audio.currentTime || 0);
    if (!audio.paused && !audio.ended) {
      raf = window.requestAnimationFrame(tick);
    }
  }

  function startClock() {
    window.cancelAnimationFrame(raf);
    raf = window.requestAnimationFrame(tick);
  }

  function revealAfter() {
    if (completed) return;
    completed = true;
    document.body.classList.add("is-guided-complete");
    var continueEl = mount.querySelector("[data-guided-continue]");
    if (continueEl) continueEl.removeAttribute("hidden");
    if (after) {
      after.removeAttribute("hidden");
      after.querySelectorAll(".reveal").forEach(function (el) {
        el.classList.add("is-visible");
      });
      if (!filmMode || lyrics.length || heardOnce) {
        window.requestAnimationFrame(function () {
          after.scrollIntoView({
            behavior: reduceMotion ? "auto" : "smooth",
            block: "start",
          });
        });
      }
    }
    if (filmMode) heardOnce = true;
  }

  function stopAudio() {
    pendingStart = false;
    playGeneration += 1;
    window.cancelAnimationFrame(raf);
    audio.pause();
  }

  function skipListening() {
    stopAudio();
    revealAfter();
  }

  function enterPlayingChrome() {
    started = true;
    mount.classList.add("is-playing");
    if (welcome) welcome.hidden = true;
    if (transport) transport.hidden = false;
  }

  function playFrom(time) {
    var gen = ++playGeneration;
    enterPlayingChrome();
    if (typeof time === "number") audio.currentTime = time;
    else if (audio.ended) audio.currentTime = 0;
    if (filmMode) {
      currentFilmId = null;
      applyFilm(itemAt(film, audio.currentTime || 0), true, true);
      if (lyrics.length) {
        currentLyricId = null;
        applyLyric(itemAt(lyrics, audio.currentTime || 0), true);
      }
      applyView();
    }
    var playPromise = audio.play();
    if (playPromise && playPromise.then) {
      playPromise
        .then(function () {
          if (gen !== playGeneration) audio.pause();
        })
        .catch(function () {
          /* click-to-play blocked — stay paused */
        });
    }
  }

  function playView(view) {
    currentView = view || "none";
    completed = false;
    document.body.classList.remove("is-guided-complete");
    var continueEl = mount.querySelector("[data-guided-continue]");
    if (continueEl) continueEl.setAttribute("hidden", "");
    applyView();
    playFrom(0);
    mount.scrollIntoView({
      behavior: reduceMotion ? "auto" : "smooth",
      block: "start",
    });
  }

  function requestStart() {
    if (!ready) {
      pendingStart = true;
      return;
    }
    playFrom(started ? audio.currentTime : 0);
  }

  function bind() {
    if (pauseBtn) {
      pauseBtn.addEventListener("click", function () {
        if (audio.paused) playFrom();
        else audio.pause();
      });
    }

    if (seekEl) {
      seekEl.addEventListener("pointerdown", function () {
        seeking = true;
      });
      seekEl.addEventListener("pointerup", function () {
        seeking = false;
        syncTo(audio.currentTime || 0);
      });
      seekEl.addEventListener("input", function () {
        var duration = audio.duration || 0;
        if (!duration) return;
        audio.currentTime = (Number(seekEl.value) / 1000) * duration;
        syncTo(audio.currentTime);
      });
    }

    audio.addEventListener("play", function () {
      enterPlayingChrome();
      if (pauseBtn) {
        pauseBtn.setAttribute("aria-pressed", "true");
        pauseBtn.textContent = "Pause";
      }
      startClock();
    });

    audio.addEventListener("pause", function () {
      window.cancelAnimationFrame(raf);
      if (pauseBtn) {
        pauseBtn.setAttribute("aria-pressed", "false");
        pauseBtn.textContent = "Play";
      }
      syncTo(audio.currentTime || 0);
    });

    audio.addEventListener("ended", function () {
      window.cancelAnimationFrame(raf);
      syncTo(audio.duration || audio.currentTime || 0);
      if (pauseBtn) {
        pauseBtn.setAttribute("aria-pressed", "false");
        pauseBtn.textContent = "Play";
      }
      revealAfter();
    });

    audio.addEventListener("seeked", function () {
      syncTo(audio.currentTime || 0);
    });

    audio.addEventListener("loadedmetadata", syncTransport);

    audio.addEventListener("error", function () {
      mount.classList.add("is-audio-error");
      if (startBtn) {
        startBtn.disabled = true;
        startBtn.textContent = "Audio unavailable";
      }
      revealAfter();
    });

    document.querySelectorAll("[data-guided-replay]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        playFrom(0);
      });
    });

    document.querySelectorAll("[data-guided-view]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        playView(btn.getAttribute("data-guided-view") || "none");
      });
    });

    document.querySelectorAll("[data-guided-skip]").forEach(function (btn) {
      btn.addEventListener("click", skipListening);
    });
  }

  function applyOpening(opening) {
    if (!opening) return;
    var title = mount.querySelector("[data-guided-title]");
    var lead = mount.querySelector("[data-guided-lead]");
    var hint = mount.querySelector("[data-guided-hint]");
    if (title && opening.title) title.textContent = opening.title;
    if (lead && opening.lead) lead.textContent = opening.lead;
    if (startBtn && opening.cta) {
      startBtn.innerHTML =
        '<span class="guided-start-icon" aria-hidden="true">▶</span>' +
        opening.cta.replace(/^▶\s*/, "");
    }
    if (hint) {
      if (opening.hint) hint.textContent = opening.hint;
      else hint.hidden = true;
    }
    if (opening.image && layers[0] && !layers[0].getAttribute("src")) {
      setLayerSrc(layers[0], opening.image);
    }
  }

  function init(data) {
    config = data || {};
    audio.loop = false;
    audio.src = resolveUrl(config.audio);

    var fade = Number(config.imageCrossfade);
    if (fade > 0) {
      mount.style.setProperty("--guided-crossfade", fade + "s");
    }

    applyOpening(config.opening);

    film = (config.film || [])
      .map(function (item) {
        return {
          id: item.id || String(item.start),
          start: Number(item.start) || 0,
          image: resolveUrl(item.image || (config.opening && config.opening.image) || ""),
          transition: item.transition || "crossfade",
          crossfade:
            item.crossfade != null ? Number(item.crossfade) : undefined,
          crop: item.crop || "",
        };
      })
      .sort(function (a, b) {
        return a.start - b.start;
      });

    lyrics = (config.lyrics || [])
      .map(function (item) {
        return {
          id: item.id || String(item.start),
          start: Number(item.start) || 0,
          ja: item.ja || "",
          romaji: item.romaji || "",
          overlay: item.overlay || "default",
          align: item.align || "center",
        };
      })
      .sort(function (a, b) {
        return a.start - b.start;
      });

    filmMode = film.length > 0;
    if (filmMode && !lyrics.length) mount.classList.add("guided-stage--interlude");

    scenes = (config.scenes || [])
      .map(function (scene) {
        return {
          id: scene.id || String(scene.start),
          start: Number(scene.start) || 0,
          image: resolveUrl(scene.image || (config.opening && config.opening.image) || ""),
          ja: scene.ja || "",
          romaji: scene.romaji || "",
          transition: scene.transition || "crossfade",
          overlay: scene.overlay || "default",
          align: scene.align || "center",
          crop: scene.crop || "",
          crossfade:
            scene.crossfade != null ? Number(scene.crossfade) : undefined,
        };
      })
      .sort(function (a, b) {
        return a.start - b.start;
      });

    var seen = {};
    (filmMode ? film : scenes).forEach(function (item) {
      if (item.image && !seen[item.image]) {
        seen[item.image] = true;
        preload(item.image);
      }
    });

    if (after) after.setAttribute("hidden", "");
    bind();
    if (filmMode) {
      applyFilm(itemAt(film, 0), true, true);
      if (lyrics.length) applyLyric(itemAt(lyrics, 0), true);
      applyView();
    } else {
      applyScene(sceneAt(0), true);
    }
    ready = true;
    if (pendingStart) playFrom(0);
  }

  if (startBtn) {
    startBtn.addEventListener("click", requestStart);
  }

  function fail(message) {
    mount.classList.add("is-audio-error");
    document.body.classList.add("is-guided-complete");
    if (startBtn) {
      startBtn.disabled = true;
      startBtn.textContent = message || "Room data unavailable";
    }
    if (after) after.removeAttribute("hidden");
  }

  dataUrl = roomDataUrl();
  if (window.KmlBeginnerRoomData) {
    init(window.KmlBeginnerRoomData);
  } else {
    fetch(dataUrl.href)
      .then(function (response) {
        if (!response.ok) throw new Error("Room data missing");
        return response.json();
      })
      .then(init)
      .catch(function () {
        fail("Room data unavailable");
      });
  }
})();
