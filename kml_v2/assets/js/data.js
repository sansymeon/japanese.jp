/**
 * KML V2 — metadata access layer
 *
 * Approved lesson pack (reference: lesson_001):
 *   lesson, kanji, vocabulary, phrases, compounds, gallery, youtube, assets
 */

(function (global) {
  const KML = (global.KML = global.KML || {});

  function siteRoot() {
    return (
      document.documentElement.getAttribute("data-site-root") || "."
    ).replace(/\/$/, "") || ".";
  }

  function url(path) {
    const clean = String(path).replace(/^\//, "");
    return `${siteRoot()}/${clean}`;
  }

  async function loadJson(path) {
    const res = await fetch(url(path), { cache: "no-cache" });
    if (!res.ok) {
      throw new Error(`Metadata load failed: ${path} (${res.status})`);
    }
    return res.json();
  }

  function lessonId(idOrNumber) {
    if (typeof idOrNumber === "number") {
      return `lesson_${String(idOrNumber).padStart(3, "0")}`;
    }
    const s = String(idOrNumber);
    if (/^lesson_\d+$/.test(s)) {
      const n = parseInt(s.replace("lesson_", ""), 10);
      return `lesson_${String(n).padStart(3, "0")}`;
    }
    if (/^\d+$/.test(s)) {
      return `lesson_${String(parseInt(s, 10)).padStart(3, "0")}`;
    }
    return s;
  }

  function lessonPackBase(id) {
    return `data/lessons/${lessonId(id)}`;
  }

  async function optionalJson(path) {
    const res = await fetch(url(path), { cache: "no-cache" });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`Metadata load failed: ${path} (${res.status})`);
    return res.json();
  }

  const PACK_FILES = [
    "lesson",
    "kanji",
    "vocabulary",
    "phrases",
    "compounds",
    "gallery",
    "youtube",
    "assets",
  ];

  async function lessonPack(id) {
    const base = lessonPackBase(id);
    const entries = await Promise.all(
      PACK_FILES.map(async (name) => {
        const required = name === "lesson" || name === "kanji";
        const path = `${base}/${name}.json`;
        const data = required ? await loadJson(path) : await optionalJson(path);
        return [name, data];
      })
    );
    return Object.fromEntries(entries);
  }

  KML.data = {
    url,
    loadJson,
    lessonId,
    lessonPackBase,
    PACK_FILES,
    booksIndex: () => loadJson("data/books/index.json"),
    book: (id) => loadJson(`data/books/${id}.json`),
    lessonsIndex: () => loadJson("data/lessons/index.json"),
    lesson: (id) => loadJson(`${lessonPackBase(id)}/lesson.json`),
    lessonKanji: (id) => loadJson(`${lessonPackBase(id)}/kanji.json`),
    lessonVocabulary: (id) => loadJson(`${lessonPackBase(id)}/vocabulary.json`),
    lessonPhrases: (id) => loadJson(`${lessonPackBase(id)}/phrases.json`),
    lessonCompounds: (id) => loadJson(`${lessonPackBase(id)}/compounds.json`),
    lessonGallery: (id) => loadJson(`${lessonPackBase(id)}/gallery.json`),
    lessonYoutube: (id) => loadJson(`${lessonPackBase(id)}/youtube.json`),
    lessonAssets: (id) => loadJson(`${lessonPackBase(id)}/assets.json`),
    lessonPack,
    playlistsIndex: () => loadJson("data/playlists/index.json"),
    playlist: (id) => loadJson(`data/playlists/${id}.json`),
    galleryIndex: () => loadJson("data/gallery/index.json"),
    ambientIndex: () => loadJson("data/ambient/index.json"),
    youtubeIndex: () => loadJson("data/youtube/index.json"),
    sitemap: () => loadJson("data/site/sitemap.json"),
    navigation: () => loadJson("data/site/navigation.json"),
  };
})(window);
