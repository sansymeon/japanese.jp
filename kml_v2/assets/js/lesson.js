/**
 * KML V2 — lesson page helpers (hydrate from lesson pack)
 */

(function (global) {
  const KML = (global.KML = global.KML || {});

  function renderNav(nav) {
    const prev = nav.getAttribute("data-prev");
    const next = nav.getAttribute("data-next");
    const prevLabel = nav.getAttribute("data-prev-label") || "Previous";
    const nextLabel = nav.getAttribute("data-next-label") || "Next";

    const prevHtml = prev
      ? `<a href="${prev}">← ${prevLabel}</a>`
      : `<span aria-disabled="true">← ${prevLabel}</span>`;

    const nextHtml = next
      ? `<a href="${next}">${nextLabel} →</a>`
      : `<span aria-disabled="true">${nextLabel} →</span>`;

    nav.innerHTML = `${prevHtml}${nextHtml}`;
  }

  function fill(sel, value) {
    const el = document.querySelector(sel);
    if (el && value != null && value !== "") el.textContent = value;
  }

  function renderKanjiRoster(kanjiDoc) {
    const host = document.querySelector("[data-lesson-kanji]");
    if (!host || !kanjiDoc || !Array.isArray(kanjiDoc.items)) return;

    host.innerHTML = kanjiDoc.items
      .map((k) => {
        const on = (k.readings && k.readings.on && k.readings.on[0]) || "";
        return `<li class="lesson-card" style="cursor:default">
          <span class="lesson-card-label"><span lang="ja">${k.character}</span> · ${k.keyword}</span>
          <span class="lesson-card-meta">${on || "—"} · H${k.heisig_number ?? k.ord}</span>
        </li>`;
      })
      .join("");
  }

  async function hydrate(lessonId) {
    if (!KML.data) throw new Error("KML.data required (load data.js first)");
    const pack = await KML.data.lessonPack(lessonId);
    const { lesson, kanji, vocabulary, phrases, compounds, youtube, assets } =
      pack;

    document.title = `${lesson.title || lesson.id} — Kanji・Music・Landscape`;
    fill('[data-lesson-field="title"]', lesson.title);
    fill('[data-lesson-field="subtitle"]', lesson.subtitle);
    fill('[data-lesson-field="summary"]', lesson.summary);

    const opening =
      (lesson.focus && lesson.focus.opening_character) ||
      (kanji && kanji.items && kanji.items[0] && kanji.items[0].character) ||
      "字";
    fill('[data-lesson-field="kanji"]', opening);
    fill(
      '[data-lesson-field="keyword"]',
      (lesson.focus && lesson.focus.primary_keyword) ||
        (kanji && kanji.items && kanji.items[0] && kanji.items[0].keyword) ||
        lesson.title
    );

    const note = document.querySelector('[data-lesson-field="status-note"]');
    if (note) {
      const kCount =
        (lesson.focus && lesson.focus.kanji_count) ||
        (kanji && kanji.count) ||
        (kanji && kanji.items && kanji.items.length) ||
        "?";
      const vCount =
        (vocabulary && vocabulary.count) ||
        (vocabulary && vocabulary.items && vocabulary.items.length) ||
        0;
      const pCount =
        (phrases && phrases.count) ||
        (phrases && phrases.items && phrases.items.length) ||
        0;
      const cCount =
        (compounds && compounds.count) ||
        (compounds && compounds.items && compounds.items.length) ||
        0;
      note.textContent = `Status: ${lesson.status} · ${lesson.id} · ${kCount} kanji · ${vCount} vocab · ${pCount} phrases · ${cCount} compounds · YouTube: ${
        (youtube && youtube.id) || "unpublished"
      }`;
    }

    renderKanjiRoster(kanji);

    const nav = document.querySelector("[data-lesson-nav]");
    if (nav && lesson.navigation) {
      const n = lesson.navigation;
      if (n.prev_href) nav.setAttribute("data-prev", n.prev_href);
      if (n.next_href) nav.setAttribute("data-next", n.next_href);
      if (n.prev_label) nav.setAttribute("data-prev-label", n.prev_label);
      if (n.next_label) nav.setAttribute("data-next-label", n.next_label);
    }

    document.dispatchEvent(
      new CustomEvent("kml:lesson-ready", { detail: { pack, assets } })
    );
    return pack;
  }

  function initNav() {
    document.querySelectorAll("[data-lesson-nav]").forEach(renderNav);
  }

  KML.lesson = { hydrate, renderNav: initNav };

  function boot() {
    initNav();
    const host = document.querySelector("[data-lesson-id]");
    if (host && host.getAttribute("data-lesson-id")) {
      hydrate(host.getAttribute("data-lesson-id"))
        .then(initNav)
        .catch((err) => console.error(err));
    }
  }

  document.addEventListener("kml:includes-ready", boot);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    queueMicrotask(boot);
  }
})(window);
