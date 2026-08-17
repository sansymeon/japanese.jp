/**
 * Ask Chat-Sensei — flourish + contextual menu.
 *
 * Heisig entries: section.kanji-entry
 * Start Here / verse bridge: [data-chat-sensei]
 *
 * Gathers lesson/kanji/keyword/verse from the DOM. Does not call ChatGPT.
 * Later: set window.KmlChatSensei.onChoose(promptId, context).
 */
(function () {
  "use strict";

  var FLOURISH_SVG =
    '<svg viewBox="0 0 76 18" aria-hidden="true" focusable="false">' +
    '<path fill="none" stroke="currentColor" stroke-width="2.45" ' +
    'stroke-linecap="round" stroke-linejoin="round" ' +
    'd="M6 9c7.5 0 9.5-5.2 16.5-3.6 3.2.7 3.6 5.4 9.2 3.6"/>' +
    '<path fill="currentColor" d="M36.2 9.7l1.9-1.9 1.9 1.9-1.9 1.9z"/>' +
    '<path fill="none" stroke="currentColor" stroke-width="2.45" ' +
    'stroke-linecap="round" stroke-linejoin="round" ' +
    'd="M70 9c-7.5 0-9.5-5.2-16.5-3.6-3.2.7-3.6 5.4-9.2 3.6"/>' +
    "</svg>";

  var PROMPT_SETS = {
    heisig: [
      { id: "understand-verse", label: "Help me understand this verse" },
      { id: "about-kanji", label: "Tell me about this kanji" },
      { id: "read-japanese", label: "Help me read the Japanese" },
      { id: "explain-grammar", label: "Explain the grammar simply" },
      { id: "known-words", label: "What words do I already know here?" },
      { id: "hint", label: "Give me a hint" },
      { id: "quiz", label: "Quiz me on this" },
    ],
    "already-read": [
      // Future: "understand-verse" should return the existing English
      // translation from KML lesson data. That is the optional meaning
      // door for pathway verses — not a permanent subtitle under the poem.
      { id: "known-words", label: "What can I already read here?" },
      { id: "understand-verse", label: "Help me understand this verse" },
      { id: "hint", label: "Give me a hint" },
    ],
  };

  var PROMPTS = PROMPT_SETS.heisig;

  function lessonNumber() {
    var match = window.location.pathname.match(/lesson_(\d+)\.html/);
    return match ? String(parseInt(match[1], 10)) : "";
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function parseKnownPieces(host) {
    var raw = host.getAttribute("data-known-pieces");
    if (!raw) return [];
    try {
      var parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (err) {
      return [];
    }
  }

  function contextFromHost(host) {
    var article = host.closest("article") || host;
    var jp = article.querySelector(".jp-verse");
    var en = article.querySelector(".en-verse");
    return {
      lesson: host.getAttribute("data-kml-lesson") || "",
      kanji: host.getAttribute("data-kanji") || "",
      slug: host.getAttribute("data-slug") || "",
      keyword: host.getAttribute("data-keyword") || "",
      pathwayRoom: host.getAttribute("data-pathway-room") || "",
      source: host.getAttribute("data-source") || "start-here",
      jpVerse: versePlain(jp),
      jpVerseWithReadings: verseVisible(jp),
      enVerse: verseVisible(en),
      knownPieces: parseKnownPieces(host),
    };
  }

  function formatKnownPieces(context) {
    var pieces = context.knownPieces || [];
    if (!pieces.length) return "";
    return pieces
      .map(function (piece) {
        var jp = escapeHtml(piece.jp || "");
        var note = piece.note ? " — " + escapeHtml(piece.note) : "";
        return "<span lang=\"ja\">" + jp + "</span>" + note;
      })
      .join("<br>");
  }

  function versePlain(el) {
    if (!el) return "";
    var clone = el.cloneNode(true);
    clone.querySelectorAll("rt").forEach(function (rt) {
      rt.remove();
    });
    return clone.textContent.replace(/\s+/g, " ").trim();
  }

  function verseVisible(el) {
    if (!el) return "";
    return el.innerText.replace(/\s+/g, " ").trim();
  }

  function contextFrom(entry) {
    var jp = entry.querySelector(".jp-verse");
    var en = entry.querySelector(".en-verse");
    var keywordEl = entry.querySelector(".kanji-keyword");
    var slug = entry.getAttribute("data-slug") || "";
    return {
      lesson: lessonNumber(),
      kanji: entry.getAttribute("data-kanji") || "",
      slug: slug,
      keyword: keywordEl
        ? keywordEl.textContent.trim()
        : slug.replace(/_/g, " "),
      jpVerse: versePlain(jp),
      jpVerseWithReadings: verseVisible(jp),
      enVerse: verseVisible(en),
    };
  }

  function closeAll() {
    document.querySelectorAll(".chat-sensei.is-open").forEach(function (root) {
      closeOne(root);
    });
  }

  function closeOne(root) {
    var btn = root.querySelector(".chat-sensei-flourish");
    root.classList.remove("is-open", "is-pending");
    if (btn) btn.setAttribute("aria-expanded", "false");
    var pending = root.querySelector(".chat-sensei-pending");
    if (pending) pending.innerHTML = "";
  }

  function openOne(root) {
    closeAll();
    var btn = root.querySelector(".chat-sensei-flourish");
    root.classList.add("is-open");
    if (btn) btn.setAttribute("aria-expanded", "true");
    var first = root.querySelector(".chat-sensei-menu button");
    if (first) first.focus();
  }

  function choosePrompt(root, prompt, context) {
    var api = window.KmlChatSensei || {};
    document.dispatchEvent(
      new CustomEvent("kml:chat-sensei", {
        detail: { promptId: prompt.id, context: context },
      })
    );
    if (typeof api.onChoose === "function") {
      api.onChoose(prompt.id, context);
      return;
    }
    root.classList.add("is-pending");
    var pending = root.querySelector(".chat-sensei-pending");
    if (!pending) return;
    var known = prompt.id === "known-words" ? formatKnownPieces(context) : "";
    if (known) {
      pending.innerHTML =
        "<strong>" + escapeHtml(prompt.label) + "</strong>" + known;
      return;
    }
    pending.innerHTML =
      "<strong>" +
      escapeHtml(prompt.label) +
      "</strong>" +
      escapeHtml(context.kanji || "") +
      (context.keyword ? " · " + escapeHtml(context.keyword) : "") +
      (context.lesson ? " · Lesson " + escapeHtml(context.lesson) : "") +
      (context.pathwayRoom ? " · Room " + escapeHtml(context.pathwayRoom) : "") +
      "<br>Chat-Sensei is not connected yet.";
  }

  function buildWidget(host, options) {
    options = options || {};
    var isEntry = host.matches("section.kanji-entry");
    var context = isEntry ? contextFrom(host) : contextFromHost(host);
    var prompts = PROMPT_SETS[options.promptSet] || PROMPTS;
    var panelId =
      "chat-sensei-panel-" +
      (host.id || context.slug || context.pathwayRoom || "entry");

    var root = isEntry ? document.createElement("div") : host;
    root.classList.add("chat-sensei");
    if (!isEntry) root.classList.add("chat-sensei--bridge");

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chat-sensei-flourish";
    btn.setAttribute(
      "aria-label",
      isEntry ? "Ask Chat-Sensei about this kanji" : "Ask Chat-Sensei about this Japanese"
    );
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-controls", panelId);
    btn.setAttribute("aria-haspopup", "dialog");
    btn.innerHTML = FLOURISH_SVG;

    var panel = document.createElement("div");
    panel.id = panelId;
    panel.className = "chat-sensei-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Ask Chat-Sensei");

    var kicker = document.createElement("p");
    kicker.className = "chat-sensei-kicker";
    kicker.textContent = "Ask Chat-Sensei";

    var menu = document.createElement("ul");
    menu.className = "chat-sensei-menu";

    prompts.forEach(function (prompt) {
      var li = document.createElement("li");
      var item = document.createElement("button");
      item.type = "button";
      item.textContent = prompt.label;
      item.addEventListener("click", function (event) {
        event.stopPropagation();
        choosePrompt(root, prompt, context);
      });
      li.appendChild(item);
      menu.appendChild(li);
    });

    var pending = document.createElement("div");
    pending.className = "chat-sensei-pending";

    panel.appendChild(kicker);
    panel.appendChild(menu);
    panel.appendChild(pending);

    btn.addEventListener("click", function (event) {
      event.stopPropagation();
      if (root.classList.contains("is-open")) closeOne(root);
      else openOne(root);
    });

    root.appendChild(btn);
    root.appendChild(panel);
    if (isEntry) host.appendChild(root);
  }

  document.querySelectorAll("section.kanji-entry").forEach(function (entry) {
    buildWidget(entry, { promptSet: "heisig" });
  });
  document.querySelectorAll("[data-chat-sensei]").forEach(function (host) {
    if (host.closest("section.kanji-entry")) return;
    buildWidget(host, {
      promptSet: host.getAttribute("data-prompt-set") || "already-read",
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    var open = document.querySelector(".chat-sensei.is-open");
    if (!open) return;
    var btn = open.querySelector(".chat-sensei-flourish");
    closeOne(open);
    if (btn) btn.focus();
  });

  document.addEventListener("pointerdown", function (event) {
    var open = document.querySelector(".chat-sensei.is-open");
    if (!open) return;
    if (open.contains(event.target)) return;
    closeOne(open);
  });

  window.KmlChatSensei = window.KmlChatSensei || {};
  window.KmlChatSensei.prompts = PROMPTS;
  window.KmlChatSensei.promptSets = PROMPT_SETS;
  window.KmlChatSensei.contextFrom = contextFrom;
})();
