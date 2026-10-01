(function () {
  var root = document.getElementById("compounds-root");
  var hero = document.getElementById("compounds-hero");
  var toggle = document.getElementById("furigana-toggle");
  var source = document.body.getAttribute("data-compounds");
  var assetBase = document.body.getAttribute("data-kml-base") || "";
  var storageKey = "kml-compounds-furigana";

  function furiganaOn() {
    return !document.documentElement.classList.contains("furigana-off");
  }

  function setFurigana(on) {
    document.documentElement.classList.toggle("furigana-off", !on);
    if (!toggle) return;
    toggle.setAttribute("aria-pressed", on ? "true" : "false");
    toggle.setAttribute("aria-label", on ? "Furigana on" : "Furigana off");
    try {
      localStorage.setItem(storageKey, on ? "on" : "off");
    } catch (err) {
      /* private mode */
    }
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setFurigana(!furiganaOn());
    });
  }
  setFurigana(furiganaOn());

  function addText(parent, className, text, lang) {
    var node = document.createElement("p");
    node.className = className;
    if (lang) node.lang = lang;
    node.textContent = text;
    parent.appendChild(node);
    return node;
  }

  function fillRuby(node, segments) {
    segments.forEach(function (segment) {
      if (segment.reading) {
        var ruby = document.createElement("ruby");
        ruby.appendChild(document.createTextNode(segment.text));
        var rt = document.createElement("rt");
        rt.textContent = segment.reading;
        ruby.appendChild(rt);
        node.appendChild(ruby);
      } else {
        node.appendChild(document.createTextNode(segment.text));
      }
    });
  }

  function renderRow(compound) {
    var example = compound.example || {};
    var row = document.createElement("article");
    row.className = "compound-row";

    var entry = document.createElement("div");
    entry.className = "compound-entry";
    addText(entry, "compound-surface", compound.surface || "", "ja");
    addText(entry, "compound-reading", compound.reading || "", "ja");
    addText(entry, "compound-meaning", compound.meaning || "", "en");

    var sample = document.createElement("div");
    sample.className = "compound-example";
    var japanese = document.createElement("p");
    japanese.className = "compound-ja";
    japanese.lang = "ja";
    var ruby = document.createElement("span");
    ruby.className = "ja-ruby";
    var plain = document.createElement("span");
    plain.className = "ja-plain";
    plain.textContent = example.ja || "";
    fillRuby(ruby, example.segments || []);
    japanese.appendChild(ruby);
    japanese.appendChild(plain);
    sample.appendChild(japanese);
    addText(sample, "compound-en", example.en || "", "en");

    row.appendChild(entry);
    row.appendChild(sample);
    return row;
  }

  function renderCharacter(character) {
    var header = document.createElement("header");
    header.className = "compound-group";

    var kanji = document.createElement("span");
    kanji.className = "compound-group-kanji";
    kanji.lang = "ja";
    kanji.textContent = character.kanji || "";

    var readings = document.createElement("span");
    readings.className = "compound-group-reading";
    readings.lang = "ja";
    readings.textContent = character.readings || "";

    var keyword = document.createElement("span");
    keyword.className = "compound-group-keyword";
    keyword.textContent = character.keyword || "";

    header.appendChild(kanji);
    header.appendChild(readings);
    header.appendChild(keyword);
    return header;
  }

  function mountBackground(background) {
    if (!hero) return;
    if (!background || !background.image) {
      hero.hidden = true;
      return;
    }
    var image = document.createElement("img");
    image.alt = background.alt || "";
    image.decoding = "async";
    image.addEventListener("error", function () {
      hero.hidden = true;
      hero.replaceChildren();
    });
    image.src = assetBase + background.image;
    hero.appendChild(image);
    hero.hidden = false;
  }

  function showStatus(message) {
    root.replaceChildren();
    var note = document.createElement("p");
    note.className = "compounds-status";
    note.textContent = message;
    root.appendChild(note);
  }

  if (!root || !source) return;

  fetch(source)
    .then(function (response) {
      if (!response.ok) throw new Error("status " + response.status);
      return response.json();
    })
    .then(function (lesson) {
      mountBackground(lesson.background);
      root.replaceChildren();
      (lesson.characters || []).forEach(function (character) {
        root.appendChild(renderCharacter(character));
        (character.compounds || []).forEach(function (compound) {
          root.appendChild(renderRow(compound));
        });
      });
      if (!root.childNodes.length) showStatus("This lesson has no compounds yet.");
    })
    .catch(function () {
      if (hero) hero.hidden = true;
      showStatus("This lesson could not be loaded.");
    });
})();
