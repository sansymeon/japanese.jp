/**
 * Kana row: render the current gojūon row, then replay KanjiVG stroke order
 * with KmlStrokeOrderPlayer. Timing is kana-only (drawMs 1700, gapMs 950).
 */
(function () {
  "use strict";

  var rows = window.KmlKatakanaRows || window.KmlHiraganaRows || [];
  var scriptName = window.KmlKatakanaRows ? "Katakana" : "Hiragana";
  var slug = document.body.getAttribute("data-kana-row") || "";
  var rowIndex = -1;
  var rowData = null;
  for (var i = 0; i < rows.length; i++) {
    if (rows[i].slug === slug) {
      rowIndex = i;
      rowData = rows[i];
      break;
    }
  }

  function renderExhibits() {
    var list = document.querySelector("[data-kana-exhibits]");
    if (!list || !rowData) return;
    list.replaceChildren();
    list.setAttribute("data-kana-count", String(rowData.kana.length));
    rowData.kana.forEach(function (item) {
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "kana-exhibit";
      btn.setAttribute("data-kana", item.kana);

      var glyph = document.createElement("span");
      glyph.className = "kana-glyph";
      glyph.lang = "ja";
      glyph.textContent = item.kana;

      var romaji = document.createElement("span");
      romaji.className = "kana-romaji";
      romaji.textContent = item.romaji;

      btn.appendChild(glyph);
      btn.appendChild(romaji);
      li.appendChild(btn);
      list.appendChild(li);
    });
  }

  function renderRowTitle() {
    var titleEl = document.querySelector("[data-kana-row-title]");
    if (titleEl && rowData && !titleEl.textContent.trim()) {
      titleEl.lang = "ja";
      titleEl.textContent = rowData.title;
    }
  }

  function renderRowNav() {
    var nav = document.querySelector("[data-kana-row-nav]");
    if (!nav || rowIndex < 0) return;
    nav.replaceChildren();
    nav.setAttribute("aria-label", scriptName + " rows");

    var prev = rows[rowIndex - 1];
    var next = rows[rowIndex + 1];
    if (prev) {
      var prevLink = document.createElement("a");
      prevLink.className = "kana-pathway-next";
      prevLink.href = "../" + prev.slug + "/";
      prevLink.textContent = "Previous row — " + prev.title;
      nav.appendChild(prevLink);
    }
    if (next) {
      var nextLink = document.createElement("a");
      nextLink.className = "kana-pathway-next";
      nextLink.href = "../" + next.slug + "/";
      nextLink.textContent = "Next row — " + next.title;
      nav.appendChild(nextLink);
    }
  }

  renderRowTitle();
  renderExhibits();
  renderRowNav();

  var layer = document.querySelector("[data-kana-stroke]");
  var stage = document.querySelector("[data-kana-stroke-svg]");
  var closeBtn = document.querySelector("[data-kana-stroke-close]");
  var prevBtn = document.querySelector("[data-kana-stroke-prev]");
  var nextBtn = document.querySelector("[data-kana-stroke-next]");
  if (!layer || !stage) return;

  var row = Array.prototype.map.call(
    document.querySelectorAll("[data-kana]"),
    function (btn) {
      return btn.getAttribute("data-kana");
    }
  );
  var currentIndex = 0;

  var cache = {};
  var lastFocus = null;
  var playGeneration = 0;

  function codeToSvgName(ch) {
    return ch.charCodeAt(0).toString(16).padStart(5, "0");
  }

  function svgUrl(ch) {
    return new URL(
      "../../../../data/archive/kanjivg/" + codeToSvgName(ch) + ".svg",
      window.location.href
    ).href;
  }

  function hideNumbers(svg) {
    svg.querySelectorAll('[id^="kvg:StrokeNumbers"]').forEach(function (el) {
      el.setAttribute("display", "none");
    });
  }

  async function loadSvg(ch) {
    if (cache[ch]) return cache[ch];
    var response = await fetch(svgUrl(ch));
    if (!response.ok) throw new Error("Stroke SVG missing");
    var text = await response.text();
    var doc = new DOMParser().parseFromString(text, "image/svg+xml");
    var svg = doc.documentElement;
    if (!svg || svg.nodeName.toLowerCase() !== "svg") {
      throw new Error("Stroke SVG unreadable");
    }
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    hideNumbers(svg);
    cache[ch] = svg;
    return svg;
  }

  function play(svg) {
    var player = window.KmlStrokeOrderPlayer;
    var gen = ++playGeneration;
    if (player) {
      var strokes = player.prepareStrokes(svg, {
        drawColor: "rgba(201, 164, 88, 0.92)",
        finalColor: "rgba(239, 233, 220, 0.96)",
        strokeWidth: 6.5,
      });
      if (!strokes) return;
      strokes.forEach(function (stroke) {
        stroke.style.strokeLinecap = "round";
        stroke.style.strokeLinejoin = "round";
      });
      player.animateStrokes(strokes, {
        drawMs: 1700,
        gapMs: 950,
        finalColor: "rgba(239, 233, 220, 0.96)",
      });
      return;
    }

    var paths = svg.querySelectorAll("path");
    paths.forEach(function (stroke) {
      var length = stroke.getTotalLength();
      stroke.style.fill = "none";
      stroke.style.stroke = "rgba(201, 164, 88, 0.92)";
      stroke.style.strokeWidth = "6.5";
      stroke.style.strokeLinecap = "round";
      stroke.style.strokeLinejoin = "round";
      stroke.style.strokeDasharray = String(length);
      stroke.style.strokeDashoffset = String(length);
      stroke.style.transition = "none";
    });
    paths.forEach(function (stroke, index) {
      window.setTimeout(function () {
        if (gen !== playGeneration) return;
        stroke.style.transition = "stroke-dashoffset 1700ms ease-out, stroke 320ms ease";
        stroke.style.strokeDashoffset = "0";
        window.setTimeout(function () {
          stroke.style.stroke = "rgba(239, 233, 220, 0.96)";
        }, 1560);
      }, index * 950);
    });
  }

  function syncNav() {
    var atStart = currentIndex <= 0;
    var atEnd = currentIndex >= row.length - 1;
    if (prevBtn) {
      prevBtn.disabled = atStart;
      prevBtn.setAttribute("aria-disabled", atStart ? "true" : "false");
    }
    if (nextBtn) {
      nextBtn.disabled = atEnd;
      nextBtn.setAttribute("aria-disabled", atEnd ? "true" : "false");
    }
    var ch = row[currentIndex] || "";
    layer.setAttribute("aria-label", ch ? "Stroke order, " + ch : "Stroke order");
  }

  async function show(ch) {
    var index = row.indexOf(ch);
    if (index < 0) return;
    currentIndex = index;
    syncNav();
    stage.replaceChildren();
    try {
      var svg = (await loadSvg(ch)).cloneNode(true);
      if (row[currentIndex] !== ch) return;
      stage.appendChild(svg);
      play(svg);
    } catch (err) {
      stage.textContent = ch;
      stage.lang = "ja";
    }
  }

  function step(delta) {
    var next = currentIndex + delta;
    if (next < 0 || next >= row.length) return;
    var ch = row[next];
    var exhibit = document.querySelector('[data-kana="' + ch + '"]');
    if (exhibit) lastFocus = exhibit;
    show(ch);
  }

  function close() {
    playGeneration += 1;
    layer.setAttribute("hidden", "");
    layer.setAttribute("aria-hidden", "true");
    document.body.style.removeProperty("overflow");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function open(ch, trigger) {
    lastFocus = trigger || document.activeElement;
    layer.removeAttribute("hidden");
    layer.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    show(ch);
    if (closeBtn) closeBtn.focus();
  }

  document.querySelectorAll("[data-kana]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      open(btn.getAttribute("data-kana"), btn);
    });
  });

  if (closeBtn) closeBtn.addEventListener("click", close);
  if (prevBtn) prevBtn.addEventListener("click", function () { step(-1); });
  if (nextBtn) nextBtn.addEventListener("click", function () { step(1); });

  layer.addEventListener("click", function (event) {
    if (event.target === layer) close();
  });

  document.addEventListener("keydown", function (event) {
    if (layer.hasAttribute("hidden")) return;
    if (event.key === "Escape") {
      close();
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      step(-1);
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      step(1);
    }
  });
})();
