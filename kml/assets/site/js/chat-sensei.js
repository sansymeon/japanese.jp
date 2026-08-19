/**
 * Ask ChatGPT Sensei — flourish + contextual menu + clipboard handoff.
 *
 * Heisig entries: section.kanji-entry
 * Start Here / verse bridge: [data-chat-sensei]
 *
 * Gathers lesson/kanji/keyword/verse from the DOM.
 * Handoff: copy a context-aware prompt, then the learner pastes it into ChatGPT.
 * Does not call the OpenAI API. "known-words" stays local.
 */
(function () {
  "use strict";

  var CHATGPT_URL = "https://chatgpt.com/";

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
      { id: "known-words", label: "What can I already read here?" },
      { id: "understand-verse", label: "Help me understand this verse" },
      { id: "hint", label: "Give me a hint" },
    ],
  };

  var QUESTIONS = {
    "understand-verse":
      "Please explain this verse naturally and simply. Concentrate on how the pieces create the meaning rather than giving an exhaustive grammar lesson.",
    "about-kanji":
      "Please explain this kanji in the context of the current lesson or verse rather than producing an encyclopedic kanji entry.",
    "read-japanese":
      "Please help me read this Japanese. Guide me through it at my current level, using only the material below.",
    "explain-grammar":
      "Please explain the grammar simply, only as it appears in this material. Do not add extra patterns I have not met here.",
    hint:
      "Please give me a hint — not the full answer — so I can keep working with this material myself.",
    quiz:
      "Please give me a short interactive quiz using only the supplied material. Ask one question at a time and wait for my answer before continuing.",
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

  function japaneseFromScope(scope) {
    var jp = scope.querySelector(".jp-verse");
    if (jp) {
      return {
        jpVerse: versePlain(jp),
        jpVerseWithReadings: verseVisible(jp),
        enVerse: verseVisible(scope.querySelector(".en-verse")),
      };
    }

    var texts = [];
    var ens = [];
    scope.querySelectorAll(".jp-kana").forEach(function (el) {
      if (el.hasAttribute("data-guided-ja")) return;
      if (el.closest(".jp-unpack, .guided-lyric")) return;
      var t = el.textContent.replace(/\s+/g, " ").trim();
      if (!t || t.indexOf("＿") !== -1) return;
      if (texts.indexOf(t) === -1) texts.push(t);
      var fig = el.closest("figure");
      var en = fig && fig.querySelector(".jp-en");
      if (!en) return;
      var et = en.textContent.replace(/\s+/g, " ").trim();
      if (et && ens.indexOf(et) === -1) ens.push(et);
    });
    return {
      jpVerse: texts.join(" / "),
      jpVerseWithReadings: "",
      enVerse: ens.join(" / "),
    };
  }

  function contextFromHost(host) {
    var scope =
      host.closest("article, aside.pathway-source") ||
      host.parentElement ||
      host;
    var japanese = japaneseFromScope(scope);
    return {
      lesson: host.getAttribute("data-kml-lesson") || "",
      kanji: host.getAttribute("data-kanji") || "",
      slug: host.getAttribute("data-slug") || "",
      keyword: host.getAttribute("data-keyword") || "",
      pathwayRoom: host.getAttribute("data-pathway-room") || "",
      source: host.getAttribute("data-source") || "start-here",
      jpVerse: japanese.jpVerse,
      jpVerseWithReadings: japanese.jpVerseWithReadings,
      enVerse: japanese.enVerse,
      readings: "",
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
    var readingsEl = entry.querySelector(".kanji-readings");
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
      readings: readingsEl
        ? readingsEl.textContent.replace(/\s+/g, " ").trim()
        : "",
      knownPieces: parseKnownPieces(entry),
    };
  }

  function promptAvailable(prompt, ctx) {
    var hasJapanese = !!(ctx.jpVerse || ctx.jpVerseWithReadings);
    var hasKanji = !!ctx.kanji;
    var hasKnown = !!(ctx.knownPieces && ctx.knownPieces.length);
    switch (prompt.id) {
      case "known-words":
        return hasKnown;
      case "about-kanji":
        return hasKanji;
      case "understand-verse":
      case "read-japanese":
      case "explain-grammar":
        return hasJapanese;
      case "hint":
      case "quiz":
        return hasJapanese || hasKanji;
      default:
        return true;
    }
  }

  function studyingWhere(ctx) {
    if (ctx.pathwayRoom) return "Start Here Room " + ctx.pathwayRoom;
    if (ctx.lesson) return "KML Lesson " + ctx.lesson;
    return "a KML lesson";
  }

  function knownPiecesText(ctx) {
    var pieces = ctx.knownPieces || [];
    if (!pieces.length) return "";
    return pieces
      .map(function (piece) {
        return (piece.jp || "") + (piece.note ? " (" + piece.note + ")" : "");
      })
      .filter(Boolean)
      .join("; ");
  }

  function addLine(lines, label, value) {
    if (value) lines.push(label + ": " + value);
  }

  function relevantContext(promptId, ctx) {
    var lines = [];
    var known = knownPiecesText(ctx);
    var readings =
      ctx.jpVerseWithReadings && ctx.jpVerseWithReadings !== ctx.jpVerse
        ? ctx.jpVerseWithReadings
        : "";

    if (promptId === "about-kanji") {
      addLine(lines, "Kanji", ctx.kanji);
      addLine(lines, "Heisig keyword", ctx.keyword);
      addLine(lines, "Readings", ctx.readings);
      addLine(lines, "Japanese verse", ctx.jpVerse);
      addLine(lines, "Verse with readings", readings);
      return lines.join("\n");
    }

    addLine(lines, "Japanese verse", ctx.jpVerse);
    addLine(lines, "Verse with readings", readings);
    addLine(lines, "Readings", ctx.readings);

    if (promptId === "understand-verse" || promptId === "quiz") {
      addLine(lines, "English verse", ctx.enVerse);
    }

    if (promptId === "quiz" || promptId === "hint") {
      addLine(lines, "Kanji", ctx.kanji);
      addLine(lines, "Heisig keyword", ctx.keyword);
    }

    if (
      known &&
      (promptId === "understand-verse" ||
        promptId === "read-japanese" ||
        promptId === "explain-grammar" ||
        promptId === "hint" ||
        promptId === "quiz")
    ) {
      addLine(lines, "Pieces I can already read", known);
    }

    return lines.join("\n");
  }

  function buildPrompt(promptId, ctx) {
    ctx = ctx || {};
    var question =
      QUESTIONS[promptId] ||
      "Please help me with the specific question implied by this request, using only the material below.";
    var material = relevantContext(promptId, ctx);
    var parts = [
      "I am learning Japanese with KML (Kanji・Music・Landscape). I am currently studying " +
        studyingWhere(ctx) +
        ". Please help me with the specific question below. Keep your explanation appropriate to the material I am studying and avoid overwhelming me with unnecessary grammar or vocabulary.",
      "",
      "Question:",
      question,
    ];
    if (material) {
      parts.push("", "Material:", material);
    }
    return parts.join("\n");
  }

  function copyFallback(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.top = "0";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.focus();
    area.select();
    var ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (err) {
      ok = false;
    }
    document.body.removeChild(area);
    return ok;
  }

  function copyPrompt(text) {
    if (
      window.isSecureContext &&
      navigator.clipboard &&
      typeof navigator.clipboard.writeText === "function"
    ) {
      return navigator.clipboard.writeText(text).then(
        function () {
          return true;
        },
        function () {
          return copyFallback(text);
        }
      );
    }
    return Promise.resolve(copyFallback(text));
  }

  function renderHandoff(pending, promptText, copied) {
    pending.innerHTML = "";

    var title = document.createElement("strong");
    title.textContent = "Your question is ready.";
    pending.appendChild(title);

    var note = document.createElement("p");
    note.className = "chat-sensei-handoff-note";
    note.textContent = copied
      ? "It has been copied. Open ChatGPT and paste it into the conversation."
      : "Copy didn’t work automatically. Select the text below and copy it, then open ChatGPT.";
    pending.appendChild(note);

    if (!copied) {
      var area = document.createElement("textarea");
      area.className = "chat-sensei-prompt";
      area.readOnly = true;
      area.rows = 8;
      area.value = promptText;
      area.setAttribute("aria-label", "Prompt to paste into ChatGPT");
      pending.appendChild(area);
    }

    var actions = document.createElement("div");
    actions.className = "chat-sensei-handoff-actions";

    var open = document.createElement("a");
    open.className = "chat-sensei-open";
    open.href = CHATGPT_URL;
    open.target = "_blank";
    open.rel = "noopener noreferrer";
    open.textContent = "Open ChatGPT";

    var copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "chat-sensei-copy";
    copyBtn.textContent = "Copy again";
    copyBtn.addEventListener("click", function (event) {
      event.stopPropagation();
      copyPrompt(promptText).then(function (ok) {
        renderHandoff(pending, promptText, ok);
        var next = pending.querySelector(".chat-sensei-copy, .chat-sensei-prompt");
        if (next) next.focus();
      });
    });

    actions.appendChild(open);
    actions.appendChild(copyBtn);
    pending.appendChild(actions);
  }

  function defaultOnChoose(promptId, context) {
    var root = document.querySelector(".chat-sensei.is-open");
    if (!root) return;
    var pending = root.querySelector(".chat-sensei-pending");
    if (!pending) return;
    var text = buildPrompt(promptId, context);
    root.classList.add("is-pending");
    copyPrompt(text).then(function (ok) {
      renderHandoff(pending, text, ok);
    });
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

  function showKnownWords(root, prompt, context) {
    root.classList.add("is-pending");
    var pending = root.querySelector(".chat-sensei-pending");
    if (!pending) return;
    var known = formatKnownPieces(context);
    pending.innerHTML =
      "<strong>" +
      escapeHtml(prompt.label) +
      "</strong>" +
      (known || "Nothing from this passage is marked as already readable.");
  }

  function choosePrompt(root, prompt, context) {
    var api = window.KmlChatSensei || {};
    document.dispatchEvent(
      new CustomEvent("kml:chat-sensei", {
        detail: { promptId: prompt.id, context: context },
      })
    );
    if (prompt.id === "known-words") {
      showKnownWords(root, prompt, context);
      return;
    }
    if (typeof api.onChoose === "function") {
      api.onChoose(prompt.id, context);
      return;
    }
    defaultOnChoose(prompt.id, context);
  }

  function buildWidget(host, options) {
    options = options || {};
    var isEntry = host.matches("section.kanji-entry");
    var context = isEntry ? contextFrom(host) : contextFromHost(host);
    var prompts = (PROMPT_SETS[options.promptSet] || PROMPTS).filter(
      function (prompt) {
        return promptAvailable(prompt, context);
      }
    );
    if (!prompts.length) return;
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
      isEntry
        ? "Ask ChatGPT Sensei about this kanji"
        : "Ask ChatGPT Sensei about this Japanese"
    );
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-controls", panelId);
    btn.setAttribute("aria-haspopup", "dialog");
    btn.innerHTML = FLOURISH_SVG;

    var panel = document.createElement("div");
    panel.id = panelId;
    panel.className = "chat-sensei-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Ask ChatGPT Sensei");

    var kicker = document.createElement("p");
    kicker.className = "chat-sensei-kicker";
    kicker.textContent = "Ask ChatGPT Sensei";

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
  window.KmlChatSensei.buildPrompt = buildPrompt;
  if (typeof window.KmlChatSensei.onChoose !== "function") {
    window.KmlChatSensei.onChoose = defaultOnChoose;
  }
})();
