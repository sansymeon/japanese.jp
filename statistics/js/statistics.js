/**
 * Statistics page — permanent library scope + published progress
 * derived from completed lessons (project_stats.json).
 */
(function () {
  "use strict";

  const PROJECT_STATS_URL = new URL("./data/project_stats.json", window.location.href)
    .href;

  const HERO_ORDER = [
    "kanjiCollection",
    "plannedLessons",
    "lessonsCompleted",
    "kanjiPublished",
    "versesPublished",
    "latestRelease",
  ];

  function fmtInt(n) {
    if (n == null || Number.isNaN(Number(n))) return "—";
    return Number(n).toLocaleString();
  }

  function fmtPercent(n) {
    if (n == null || Number.isNaN(Number(n))) return "—";
    return (
      Number(n).toLocaleString(undefined, {
        maximumFractionDigits: 1,
        minimumFractionDigits: 0,
      }) + "%"
    );
  }

  function fmtOf(covered, total) {
    return fmtInt(covered) + " of " + fmtInt(total);
  }

  function card(value, label, detail, note, textValue) {
    const article = document.createElement("article");
    article.className = "hero-stat-card";
    const valueClass = textValue
      ? "hero-stat-value hero-stat-value--text"
      : "hero-stat-value";
    article.innerHTML =
      '<p class="' +
      valueClass +
      '">' +
      value +
      "</p>" +
      '<p class="hero-stat-label">' +
      label +
      "</p>" +
      (detail ? '<p class="hero-stat-detail">' + detail + "</p>" : "") +
      (note ? '<p class="hero-stat-note">' + note + "</p>" : "");
    return article;
  }

  function detailCard(value, label, detail) {
    const article = document.createElement("article");
    article.className = "detail-stat-card";
    article.innerHTML =
      '<p class="detail-stat-value">' +
      value +
      "</p>" +
      '<p class="detail-stat-label">' +
      label +
      "</p>" +
      (detail ? '<p class="detail-stat-detail">' + detail + "</p>" : "");
    return article;
  }

  function fillGrid(id, items) {
    const grid = document.getElementById(id);
    if (!grid) return;
    grid.innerHTML = "";
    items.forEach(function (item) {
      grid.appendChild(detailCard(item.value, item.label, item.detail || ""));
    });
  }

  function coverageCards(map, order) {
    return order.map(function (key) {
      const item = map[key];
      if (!item) return null;
      return {
        value: fmtPercent(item.percent),
        label: item.label,
        detail: fmtOf(item.covered, item.total),
      };
    }).filter(Boolean);
  }

  function renderHero(hero) {
    const grid = document.getElementById("heroStatGrid");
    if (!grid || !hero) return;
    grid.innerHTML = "";
    HERO_ORDER.forEach(function (key) {
      const item = hero[key];
      if (!item) return;
      const isText = key === "latestRelease" || typeof item.value === "string";
      const value = isText ? String(item.value) : fmtInt(item.value);
      grid.appendChild(
        card(value, item.label, item.detail || "", item.note || "", isText)
      );
    });
  }

  function renderPermanent(permanent, hero) {
    const source = permanent || {
      kanjiCollection: hero && hero.kanjiCollection,
      plannedLessons: hero && hero.plannedLessons,
    };
    const items = [];
    if (source.kanjiCollection) {
      items.push({
        value: fmtInt(source.kanjiCollection.value),
        label: source.kanjiCollection.label,
        detail: source.kanjiCollection.detail || "Total KML library",
      });
    }
    if (source.plannedLessons) {
      items.push({
        value: fmtInt(source.plannedLessons.value),
        label: source.plannedLessons.label,
        detail: source.plannedLessons.detail || "Full lesson curriculum",
      });
    }
    fillGrid("permanentGrid", items);
  }

  function renderPublished(published) {
    if (!published) return;

    fillGrid("progressGrid", [
      {
        value: fmtInt(published.completedLessons),
        label: "Lessons Completed",
        detail: published.highestCompletedLesson
          ? "Through lesson " + published.highestCompletedLesson
          : "",
      },
      {
        value: fmtInt(published.kanjiPublished),
        label: "Kanji Published",
      },
      {
        value: fmtInt(published.versesPublished),
        label: "Verses Published",
      },
      {
        value: fmtInt(published.heroIllustrations),
        label: "Hero Illustrations",
      },
      {
        value: fmtInt(published.verseIllustrations),
        label: "Verse Illustrations",
      },
      {
        value: fmtInt(published.componentsPublished),
        label: "Component Entries",
      },
    ]);

    const coverage = published.coverage || {};
    fillGrid(
      "jlptGrid",
      coverageCards(coverage.jlpt || {}, ["N5", "N4", "N3", "N2", "N1"])
    );
    fillGrid(
      "gradesGrid",
      coverageCards(coverage.grades || {}, [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "S",
      ])
    );

    const joyo = coverage.joyo;
    fillGrid(
      "joyoGrid",
      joyo
        ? [
            {
              value: fmtPercent(joyo.percent),
              label: "Jōyō Coverage",
              detail: fmtOf(joyo.covered, joyo.total),
            },
            {
              value: fmtInt(joyo.covered),
              label: "Jōyō Kanji Published",
              detail: "From completed lessons",
            },
          ]
        : []
    );

    fillGrid("resourcesGrid", [
      {
        value: fmtInt(published.vocabularyPublished),
        label: "Vocabulary Published",
      },
      {
        value: fmtInt(published.compoundEntries),
        label: "Compound Entries",
      },
      {
        value: fmtInt(published.readingEntries),
        label: "Reading Entries",
      },
      {
        value: fmtInt(published.componentsPublished),
        label: "Component Entries",
      },
      {
        value: fmtInt(published.strokeOrderPages),
        label: "Stroke Order Pages",
      },
      {
        value: fmtInt(published.lessonCovers),
        label: "Lesson Covers",
      },
    ]);
  }

  function renderMedia(media) {
    if (!media) return;
    fillGrid("mediaGrid", [
      {
        value: fmtInt(media.galleryExhibitionCount),
        label: "Gallery Exhibitions",
      },
      {
        value: fmtInt(media.ambientCollectionCount),
        label: "Ambient Collections",
      },
      {
        value: fmtInt(media.videos),
        label: "Videos",
      },
      {
        value: fmtInt(media.audioTracks),
        label: "Audio Tracks",
      },
    ]);
  }

  function showError(message) {
    const banner = document.getElementById("statsStatus");
    if (banner) {
      banner.hidden = false;
      banner.textContent =
        message || "Statistics temporarily unavailable.";
    }
  }

  async function load() {
    const res = await fetch(PROJECT_STATS_URL, { cache: "no-cache" });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();

    renderHero(data.hero);
    renderPermanent(data.permanent, data.hero);
    renderPublished(data.published);
    renderMedia(data.media);

    const genEl = document.getElementById("statsGeneratedAt");
    if (genEl && data.generatedAt) {
      const d = new Date(data.generatedAt);
      genEl.textContent = Number.isNaN(d.getTime())
        ? ""
        : "Published progress as of " + d.toLocaleString();
    }
  }

  load().catch(function (err) {
    console.warn("[statistics] load failed:", err);
    showError();
    const grid = document.getElementById("heroStatGrid");
    if (grid) {
      grid.innerHTML =
        '<p class="stats-status">Project statistics temporarily unavailable.</p>';
    }
  });
})();
