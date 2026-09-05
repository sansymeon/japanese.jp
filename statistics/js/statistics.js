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
    "verses",
    "plannedLessons",
    "lessonsCompleted",
    "kanjiPublished",
    "youtubeVideos",
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
      const isText = typeof item.value === "string";
      const value = isText ? String(item.value) : fmtInt(item.value);
      grid.appendChild(
        card(value, item.label, item.detail || "", item.note || "", isText)
      );
    });
  }

  function renderPermanent(permanent, hero) {
    const source = permanent || {};
    const order = source.order || [
      "kanjiCollection",
      "verses",
      "strokeOrderPages",
      "plannedLessons",
      "vocabularyUnique",
      "compoundsUnique",
      "components",
    ];
    const items = [];
    order.forEach(function (key) {
      const card = source[key];
      if (!card || card.value == null) return;
      items.push({
        value: fmtInt(card.value),
        label: card.label,
        detail: card.detail || "",
      });
    });
    if (!items.length && hero && hero.kanjiCollection) {
      items.push({
        value: fmtInt(hero.kanjiCollection.value),
        label: hero.kanjiCollection.label,
        detail: hero.kanjiCollection.detail || "",
      });
    }
    fillGrid("permanentGrid", items);
  }

  function renderPublished(published) {
    if (!published) return;

    const scope = published.curriculumScope || "Completed lessons";

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
        label: "Lesson Kanji Published",
        detail: scope,
      },
      {
        value: fmtInt(published.versesPublished),
        label: "Lesson Verses Published",
        detail: scope,
      },
      {
        value: fmtInt(published.heroIllustrations),
        label: "Hero Illustrations",
        detail: scope,
      },
      {
        value: fmtInt(published.verseIllustrations),
        label: "Verse Illustrations",
        detail: scope,
      },
      {
        value: fmtInt(published.componentsPublished),
        label: "Component Entries",
        detail: scope,
      },
    ]);

    const coverage = published.coverage || {};
    const jlptCards = coverageCards(coverage.jlpt || {}, [
      "N5",
      "N4",
      "N3",
      "N2",
      "N1",
    ]).map(function (item) {
      return {
        value: item.value,
        label: item.label,
        detail: item.detail + " · " + scope,
      };
    });
    fillGrid("jlptGrid", jlptCards);
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
      ]).map(function (item) {
        return {
          value: item.value,
          label: item.label,
          detail: item.detail + " · " + scope,
        };
      })
    );

    const joyo = coverage.joyo;
    fillGrid(
      "joyoGrid",
      joyo
        ? [
            {
              value: fmtPercent(joyo.percent),
              label: "Jōyō Coverage",
              detail: fmtOf(joyo.covered, joyo.total) + " · " + scope,
            },
            {
              value: fmtInt(joyo.covered),
              label: "Jōyō Kanji Published",
              detail: scope,
            },
          ]
        : []
    );
  }

  function fmtResourceItems(items) {
    return (items || [])
      .filter(function (item) {
        return item && item.value != null;
      })
      .map(function (item) {
        return {
          value: fmtInt(item.value),
          label: item.label,
          detail: item.detail || "",
        };
      });
  }

  function curriculumResourceCards(published, scope) {
    return [
      {
        value: fmtInt(published.vocabularyPublished),
        label: "Lesson Vocabulary",
        detail: scope,
      },
      {
        value: fmtInt(published.compoundEntries),
        label: "Lesson Compounds",
        detail: scope,
      },
      {
        value: fmtInt(published.readingEntries),
        label: "Lesson Readings",
        detail: scope,
      },
      {
        value: fmtInt(published.componentsPublished),
        label: "Lesson Components",
        detail: scope,
      },
      {
        value: fmtInt(published.strokeOrderPages),
        label: "Lesson Stroke Pages",
        detail: scope,
      },
      {
        value: fmtInt(published.lessonCovers),
        label: "Lesson Covers",
        detail: scope,
      },
    ];
  }

  function renderResources(data) {
    const published = data.published || {};
    const scope = published.curriculumScope || "Completed lessons";
    const resources = data.resources || {};
    fillGrid(
      "resourcesGrid",
      resources.curriculum && resources.curriculum.length
        ? fmtResourceItems(resources.curriculum)
        : curriculumResourceCards(published, scope)
    );
    fillGrid("ecosystemResourcesGrid", fmtResourceItems(resources.ecosystem));
  }

  function renderMedia(media) {
    if (!media) return;
    const youtube = media.youtube || {};
    fillGrid("mediaGrid", [
      {
        value: fmtInt(youtube.value),
        label: youtube.label || "YouTube Videos",
        detail:
          youtube.note ||
          youtube.detail ||
          (youtube.asOf ? "Channel total as of " + youtube.asOf : ""),
      },
      {
        value: fmtInt(media.videoCollectionCount),
        label: "Video Collections",
        detail: media.videoCollectionDetail || "Website playlist galleries",
      },
      {
        value: fmtInt(media.galleryExhibitionCount),
        label: "Gallery Exhibitions",
        detail: media.galleryDetail || "Published exhibition films",
      },
      {
        value: fmtInt(media.ambientCollectionCount),
        label: "Ambient Collections",
        detail: media.ambientDetail || "Published ambient collections",
      },
      {
        value: fmtInt(media.audioTracks),
        label: "Audio Tracks",
        detail: media.audioDetail || "Website soundtrack files",
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
    renderResources(data);
    renderMedia(data.media);

    const genEl = document.getElementById("statsGeneratedAt");
    if (genEl && data.generatedAt) {
      const d = new Date(data.generatedAt);
      genEl.textContent = Number.isNaN(d.getTime())
        ? ""
        : "Curriculum figures as of " + d.toLocaleString();
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
