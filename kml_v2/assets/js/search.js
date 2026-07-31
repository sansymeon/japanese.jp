/**
 * KML V2 — search helpers (index-backed; no page-specific logic)
 *
 * Future: filter lessons/books/gallery from metadata indexes.
 * Phase 2 ships the API surface only.
 */

(function (global) {
  const KML = (global.KML = global.KML || {});

  function normalize(s) {
    return String(s || "")
      .toLowerCase()
      .normalize("NFKC")
      .trim();
  }

  function matchRecord(record, query) {
    const q = normalize(query);
    if (!q) return true;
    const hay = normalize(
      [
        record.id,
        record.title,
        record.subtitle,
        record.keyword,
        record.description,
        ...(record.tags || []),
      ].join(" ")
    );
    return hay.includes(q);
  }

  async function searchLessons(query) {
    const index = await KML.data.lessonsIndex();
    const items = index.lessons || index.items || [];
    return items.filter((item) => matchRecord(item, query));
  }

  async function searchBooks(query) {
    const index = await KML.data.booksIndex();
    const items = index.books || index.items || [];
    return items.filter((item) => matchRecord(item, query));
  }

  KML.search = { matchRecord, searchLessons, searchBooks };
})(window);
