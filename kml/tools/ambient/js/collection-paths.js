/**
 * Collection JSON paths — lesson_01 … lesson_10 subfolders for L1–10 builds.
 */
(function () {
  "use strict";

  const LESSON_FOLDER_OVERRIDES = {
    lessons_1_5_prototype: "lesson_01",
    "lesson_01-05_verses": "lesson_01",
    lessons_6_10_prototype: "lesson_06",
  };

  function lessonFolder(n) {
    return `lesson_${String(n).padStart(2, "0")}`;
  }

  function collectionDirForId(name) {
    if (LESSON_FOLDER_OVERRIDES[name]) return LESSON_FOLDER_OVERRIDES[name];
    if (/^post_elementary_\d+/.test(name)) return "post_elementary";
    if (/^vocabulary_\d+/.test(name)) return "vocabulary";
    if (/^hiragana_song/.test(name)) return "hiragana_song";
    if (/^grade_1/.test(name)) return "grade_1";
    if (/^grade_2/.test(name)) return "grade_2";
    if (/^grade_3/.test(name)) return "grade_3";
    if (/^grade_4/.test(name)) return "grade_4";
    if (/^grade_5/.test(name)) return "grade_5";
    if (/^grade_6/.test(name)) return "grade_6";
    const m = name.match(/^lesson_(\d+)/);
    if (!m) return null;
    const n = parseInt(m[1], 10);
    if (n >= 1 && n <= 10) return lessonFolder(n);
    return null;
  }

  const COLLECTION_ID_ALIASES = {
    lesson_01_assisted_reading: "lesson_01_reading",
    lesson_02_assisted_reading: "lesson_02_reading",
    lesson_03_assisted_reading: "lesson_03_reading",
    lesson_04_assisted_reading: "lesson_04_reading",
    lesson_05_assisted_reading: "lesson_05_reading",
    lesson_06_assisted_reading: "lesson_06_reading",
    lesson_07_assisted_reading: "lesson_07_reading",
    lesson_08_assisted_reading: "lesson_08_reading",
    lesson_09_assisted_reading: "lesson_09_reading",
    lesson_10_assisted_reading: "lesson_10_reading",
    lesson_01_stroke_order: "lesson_01_strokes",
    reading_lesson_01: "lesson_01_reading",
    grade_1_anchor_compounds_prototype: "grade_1_compounds_school",
  };

  function resolveCollectionId(name) {
    if (COLLECTION_ID_ALIASES[name]) return COLLECTION_ID_ALIASES[name];
    if (/_study$/.test(name)) return name.replace(/_study$/, "_foundations");
    if (/_assisted_reading$/.test(name)) return name.replace(/_assisted_reading$/, "_reading");
    if (/_stroke_order$/.test(name)) return name.replace(/_stroke_order$/, "_strokes");
    return name;
  }

  function collectionUrls(name) {
    const urls = [];
    const resolved = resolveCollectionId(name);
    const ids = resolved === name ? [name] : [resolved, name];
    for (const id of ids) {
      const sub = collectionDirForId(id);
      if (sub) urls.push(`./collections/${sub}/${id}.json`);
      urls.push(`./collections/${id}.json`);
    }
    return [...new Set(urls)];
  }

  window.KmlCollectionPaths = {
    collectionUrls,
    collectionDirForId,
    lessonFolder,
    resolveCollectionId,
    COLLECTION_ID_ALIASES,
  };
})();
