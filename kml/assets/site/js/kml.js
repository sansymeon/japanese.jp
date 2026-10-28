// ==============================
// Active Kanji Highlight
// ==============================

(function(){

const sections = document.querySelectorAll(".kanji-entry");
const navLinks = document.querySelectorAll(".anchor-list a");

if (sections.length && navLinks.length) {

  const observer = new IntersectionObserver(entries => {

    entries.forEach(entry => {

      if (entry.isIntersecting) {

        navLinks.forEach(link => link.classList.remove("active"));

        const id = entry.target.getAttribute("id");
        const activeLink = document.querySelector(`.anchor-list a[href="#${id}"]`);

        if (activeLink) activeLink.classList.add("active");

      }

    });

  },{
    rootMargin: "-40% 0px -55% 0px",
    threshold: 0
  });

  sections.forEach(section => observer.observe(section));

}

})();
// ==============================
// KML Reflection + Verse Timing
// ==============================

(function(){

const entries = document.querySelectorAll(".kanji-entry");

if (!entries.length) return;

const observer = new IntersectionObserver((entriesList) => {

  entriesList.forEach(entry => {

    if (!entry.isIntersecting) return;

    const card = entry.target;

    const reflection = card.querySelector(".kml-reflection");
    const verses = card.querySelector(".kml-verses");

    if (!reflection) return;

    // Prevent retrigger
    if (card.dataset.animated) return;
    card.dataset.animated = "true";

    // Step 1: reflection
    setTimeout(() => {
      reflection.classList.add("visible");
    }, 400);

    // Step 2: verses
    if (verses) {
      setTimeout(() => {
        verses.classList.add("visible");
      }, 1200);
    }

  });

},{
  threshold: 0.35
});

entries.forEach(entry => observer.observe(entry));

})();

// ==============================
// KML Primitive Labels
// ==============================

(function(){

const COMPONENT_LABELS = {
  "一": "line",
  "丶": "drop",
  "口": "mouth",
  "日": "sun",
  "月": "moon",
  "田": "field",
  "目": "eye",
  "儿": "two legs",
  "八": "split",
  "十": "ten",
  "卜": "divination",
  "⺈": "hooked cover",
  "貝": "shellfish"
};

const seen = new Set();

document.querySelectorAll("[data-primitive]").forEach(el => {

  const key = el.dataset.primitive;
  const label = COMPONENT_LABELS[key];

  if (!label) return;

  el.title = label;

  if (!seen.has(key)) {
    el.textContent = `${key} (${label})`;
    seen.add(key);
  }

});

})();

// ==============================
// Click-to-reveal verse furigana
// ==============================

(function () {
  document.querySelectorAll(".toggle-reading").forEach((el) => {
    el.addEventListener("click", () => {
      el.classList.toggle("show-reading");
    });
  });
})();

// ==============================
// Kanji lookup
// ==============================

(function () {
  const nav = document.querySelector("nav.anchor-list");
  if (!nav || !document.querySelector(".kanji-entry")) return;

  const wrap = document.createElement("div");
  wrap.className = "kanji-lookup-wrap";
  nav.parentNode.insertBefore(wrap, nav);
  wrap.appendChild(nav);

  const button = document.createElement("button");
  button.type = "button";
  button.className = "kanji-lookup-open";
  button.textContent = "🔍";
  button.setAttribute("aria-label", "Look up a kanji");
  button.setAttribute("aria-expanded", "false");
  button.setAttribute("aria-controls", "kanji-lookup-panel");
  nav.insertBefore(button, nav.firstChild);

  const panel = document.createElement("div");
  panel.className = "kanji-lookup-panel";
  panel.id = "kanji-lookup-panel";
  panel.hidden = true;
  panel.setAttribute("role", "region");
  panel.setAttribute("aria-label", "Kanji lookup");
  panel.innerHTML =
    '<form class="kanji-lookup-form" role="search">' +
      '<label class="kanji-lookup-label" for="kanji-lookup-input">One kanji</label>' +
      '<input id="kanji-lookup-input" type="text" lang="ja" inputmode="text" enterkeyhint="search" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="漢字" maxlength="12">' +
    "</form>" +
    '<div class="kanji-lookup-result" aria-live="polite"></div>';
  wrap.appendChild(panel);

  const form = panel.querySelector("form");
  const input = panel.querySelector("input");
  const result = panel.querySelector(".kanji-lookup-result");
  let lookupPromise = null;
  let composing = false;

  function kanjiCharacters(text) {
    const found = [];
    for (const character of text.trim()) {
      const code = character.codePointAt(0);
      const kanji =
        (code >= 0x3400 && code <= 0x9fff) ||
        (code >= 0xf900 && code <= 0xfaff) ||
        (code >= 0x20000 && code <= 0x3ffff);
      if (kanji) found.push(character);
    }
    return found;
  }

  function loadLookup() {
    if (!lookupPromise) {
      lookupPromise = fetch("/kml/assets/site/data/kanji-lookup.json")
        .then((response) => {
          if (!response.ok) throw new Error("HTTP " + response.status);
          return response.json();
        });
    }
    return lookupPromise;
  }

  function message(text) {
    result.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.className = "kanji-lookup-message";
    paragraph.textContent = text;
    result.appendChild(paragraph);
  }

  function showEntry(character, entry) {
    result.replaceChildren();
    const glyph = document.createElement("p");
    glyph.className = "kanji-lookup-char";
    glyph.lang = "ja";
    glyph.textContent = character;
    result.appendChild(glyph);

    if (entry.m) {
      const meaning = document.createElement("p");
      meaning.className = "kanji-lookup-meaning";
      meaning.lang = "en";
      meaning.textContent = entry.m;
      result.appendChild(meaning);
    }

    const readings = [];
    if (entry.on) readings.push("On: " + entry.on);
    if (entry.kun) readings.push("Kun: " + entry.kun);
    if (readings.length) {
      const line = document.createElement("p");
      line.className = "kanji-lookup-readings";
      line.lang = "ja";
      line.textContent = readings.join(" · ");
      result.appendChild(line);
    }

    const href = typeof entry.href === "string" ? entry.href : "";
    const safe = href.startsWith("/kanken/") || href.startsWith("/kml/");
    if (!safe) {
      message("No reference link is available for this character.");
      return;
    }
    const link = document.createElement("a");
    link.className = "kanji-lookup-link";
    link.href = href;
    link.textContent = entry.kind === "kanken"
      ? "漢検" + (entry.level || "") + " reference"
      : "KML lesson entry";
    result.appendChild(link);
  }

  function search() {
    const characters = kanjiCharacters(input.value);
    if (!input.value.trim()) {
      result.replaceChildren();
      return;
    }
    if (!characters.length) {
      message("Enter one kanji character.");
      return;
    }
    if (characters.length > 1) {
      message("Enter one kanji at a time. Compounds are not searched here.");
      return;
    }
    const character = characters[0];
    message("Looking up " + character + "…");
    loadLookup().then((lookup) => {
      const current = kanjiCharacters(input.value);
      if (current.length !== 1 || current[0] !== character) return;
      const entry = lookup[character];
      if (!entry) {
        message("No entry for " + character + ". It is not in the 漢検 collection, and the KML lessons do not include it.");
        return;
      }
      showEntry(character, entry);
    }).catch(() => {
      lookupPromise = null;
      message("The kanji list could not be loaded.");
    });
  }

  button.addEventListener("click", () => {
    const open = panel.hidden;
    panel.hidden = !open;
    button.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) input.focus();
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    search();
  });

  input.addEventListener("compositionstart", () => {
    composing = true;
  });
  input.addEventListener("compositionend", () => {
    composing = false;
    search();
  });
  input.addEventListener("input", () => {
    if (!composing) search();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) {
      panel.hidden = true;
      button.setAttribute("aria-expanded", "false");
      button.focus();
    }
  });
})();