/**
 * SanSymeon homepage — live curriculum headlines + URL wiring.
 * Fetches analytics once per visit; does not poll.
 */
(function () {
  "use strict";

  /* =========================================================================
   * CONFIGURABLE URLS
   * Fill in YouTube channel / playlist URLs when known.
   * Do not invent YouTube links — leave null until verified.
   * ========================================================================= */
  const SITE_CONFIG = {
    /** @type {string|null} Official KML / SanSymeon YouTube channel */
    youtubeChannelUrl: null, // PLACEHOLDER: set when channel URL is confirmed

    /** Curriculum overview (book / learning paths on-site) */
    curriculumUrl: "./kml/index.html",

    /** Deployed analytics dashboard */
    analyticsDashboardUrl: "./kml/analytics/dashboard/",

    /**
     * Public analytics JSON (generated under output/; dashboard ./data symlinks here).
     * Homepage reads summary.* only; never modifies this file.
     * Prefer output/ over dashboard/data so deploy hosts need not resolve the symlink.
     */
    analyticsJsonUrl: "./kml/analytics/output/kml_channel_learning.json",

    /**
     * Playlist URLs keyed by learning-path card id.
     * null = no verified playlist; button falls back to curriculumUrl.
     */
    playlistUrls: {
      kana: null, // PLACEHOLDER
      elementaryKanji: null, // PLACEHOLDER
      elementaryCompounds: null, // PLACEHOLDER
      postElementaryKanji: null, // PLACEHOLDER
      postElementaryCompounds: null, // PLACEHOLDER
      japaneseVocabulary: null, // PLACEHOLDER
      spokenJapanese: null, // PLACEHOLDER
    },

    /**
     * Featured lessons — thumbnails are local; watchUrl null until verified.
     * Prefer thumbnails + links over many iframes.
     */
    featuredLessons: [
      {
        id: "grade1-kanji",
        title: "Grade 1 Kanji Soundtrack",
        description:
          "Begin with elementary school kanji through calm imagery and music.",
        type: "Elementary Kanji",
        thumbnail: "./kml/assets/youtube_thumbnails/grade_1_.png",
        watchUrl: null, // PLACEHOLDER
      },
      {
        id: "vocabulary",
        title: "Japanese Vocabulary",
        description:
          "High-frequency spoken vocabulary presented in natural contexts.",
        type: "Spoken Vocabulary",
        thumbnail: "./kml/assets/youtube_thumbnails/gallery.png",
        watchUrl: null, // PLACEHOLDER
      },
      {
        id: "foundations",
        title: "Foundations (Heisig Path)",
        description:
          "Story-driven foundations that prepare the eye and memory for kanji.",
        type: "Foundations",
        thumbnail: "./kml/assets/youtube_thumbnails/foundations.png",
        watchUrl: null, // PLACEHOLDER
      },
      {
        id: "grade2-compounds",
        title: "Grade 2 School Compounds",
        description:
          "Build reading fluency with school-grade compound words.",
        type: "Elementary Compounds",
        thumbnail: "./kml/assets/youtube_thumbnails/grade_2_jukugo_1.png",
        watchUrl: null, // PLACEHOLDER
      },
    ],
  };

  window.SANSYMEON_SITE_CONFIG = SITE_CONFIG;

  /* ---------- helpers ---------- */

  function fmtInt(n) {
    if (n == null || Number.isNaN(Number(n))) return "—";
    return Number(n).toLocaleString("en-US");
  }

  function fmtPercent(n, digits) {
    if (n == null || Number.isNaN(Number(n))) return "—";
    return Number(n).toFixed(digits == null ? 2 : digits) + "%";
  }

  function formatGeneratedAt(iso) {
    if (!iso) return "";
    try {
      const d = new Date(iso);
      if (Number.isNaN(d.getTime())) return iso;
      return d.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZoneName: "short",
      });
    } catch (_) {
      return iso;
    }
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function wireHref(selector, url, options) {
    const opts = options || {};
    document.querySelectorAll(selector).forEach((el) => {
      if (url) {
        el.setAttribute("href", url);
        el.removeAttribute("aria-disabled");
        el.classList.remove("is-placeholder");
        if (opts.external) {
          el.setAttribute("target", "_blank");
          el.setAttribute("rel", "noopener noreferrer");
        }
      } else {
        el.setAttribute("href", opts.fallback || "#");
        el.classList.add("is-placeholder");
        if (!opts.fallback) {
          el.setAttribute("aria-disabled", "true");
          el.setAttribute("tabindex", "-1");
          el.addEventListener("click", (e) => e.preventDefault());
        }
        if (opts.placeholderTitle) {
          el.setAttribute("title", opts.placeholderTitle);
        }
      }
    });
  }

  /* ---------- header / nav ---------- */

  function initNav() {
    const toggle = document.getElementById("navToggle");
    const nav = document.getElementById("siteNav");
    if (!toggle || !nav) return;

    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    nav.querySelectorAll("a").forEach((a) => {
      a.addEventListener("click", () => {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- configurable links ---------- */

  function applyConfigLinks() {
    const c = SITE_CONFIG;
    const ytTitle =
      "YouTube channel URL not set yet — update SITE_CONFIG.youtubeChannelUrl in assets/js/homepage.js";

    wireHref("[data-link='youtube']", c.youtubeChannelUrl, {
      external: true,
      placeholderTitle: ytTitle,
    });

    wireHref("[data-link='curriculum']", c.curriculumUrl);
    wireHref("[data-link='analytics']", c.analyticsDashboardUrl);

    document.querySelectorAll("[data-playlist]").forEach((el) => {
      const key = el.getAttribute("data-playlist");
      const playlist = c.playlistUrls[key] || null;
      if (playlist) {
        el.setAttribute("href", playlist);
        el.setAttribute("target", "_blank");
        el.setAttribute("rel", "noopener noreferrer");
        el.textContent = el.getAttribute("data-label-playlist") || "Open Playlist";
        el.classList.remove("is-placeholder");
      } else {
        el.setAttribute("href", c.curriculumUrl);
        el.removeAttribute("target");
        el.textContent =
          el.getAttribute("data-label-fallback") || "Explore Curriculum";
        el.classList.add("is-placeholder");
        el.setAttribute(
          "title",
          "Playlist URL pending — opens on-site curriculum. Set SITE_CONFIG.playlistUrls." +
            key
        );
      }
    });
  }

  /* ---------- featured lessons ---------- */

  function renderFeatured() {
    const root = document.getElementById("featuredLessons");
    if (!root) return;

    root.innerHTML = "";
    SITE_CONFIG.featuredLessons.forEach((lesson) => {
      const article = document.createElement("article");
      article.className = "feature-card";

      const img = document.createElement("img");
      img.src = lesson.thumbnail;
      img.alt = "";
      img.loading = "lazy";
      img.width = 640;
      img.height = 360;

      const body = document.createElement("div");
      body.className = "feature-card-body";

      const type = document.createElement("p");
      type.className = "feature-type";
      type.textContent = lesson.type;

      const h3 = document.createElement("h3");
      h3.textContent = lesson.title;

      const desc = document.createElement("p");
      desc.textContent = lesson.description;

      const btn = document.createElement("a");
      btn.className = "btn btn-secondary";
      if (lesson.watchUrl) {
        btn.href = lesson.watchUrl;
        btn.target = "_blank";
        btn.rel = "noopener noreferrer";
        btn.textContent = "Watch";
      } else {
        btn.href = SITE_CONFIG.curriculumUrl;
        btn.classList.add("is-placeholder");
        btn.textContent = "View Curriculum";
        btn.title =
          "Watch URL pending — update featuredLessons in assets/js/homepage.js";
      }

      body.append(type, h3, desc, btn);
      article.append(img, body);
      root.appendChild(article);
    });
  }

  /* ---------- analytics ---------- */

  function showStatsError(message) {
    const banner = document.getElementById("statsStatus");
    if (banner) {
      banner.hidden = false;
      banner.textContent =
        message || "Curriculum statistics temporarily unavailable.";
    }
    document.querySelectorAll("[data-stat]").forEach((el) => {
      el.textContent = "—";
    });
    setText("statsGeneratedAt", "");
  }

  function applySummary(summary, generatedAt) {
    const banner = document.getElementById("statsStatus");
    if (banner) {
      banner.hidden = true;
      banner.textContent = "";
    }

    setText("statVideos", fmtInt(summary.global_videos));
    setText("statPaths", fmtInt(summary.independent_paths));
    setText("statVocab", fmtInt(summary.global_unique_vocabulary));
    setText("statKanji", fmtInt(summary.global_unique_kanji));
    setText("statJoyo", fmtPercent(summary.global_joyo_percent));

    setText("factJoyo", fmtPercent(summary.global_joyo_percent));
    setText("factMultiContext", fmtInt(summary.vocab_multiple_contexts));
    setText("factJoyo3", fmtPercent(summary.joyo_at_least_3_percent));
    setText("factVocabTotal", fmtInt(summary.global_unique_vocabulary));

    const genEl = document.getElementById("statsGeneratedAt");
    if (genEl) {
      const label = formatGeneratedAt(generatedAt);
      genEl.textContent = label ? "Analytics generated " + label : "";
    }
  }

  async function loadAnalytics() {
    const url = SITE_CONFIG.analyticsJsonUrl;
    try {
      // Once per visit; no-cache so redeployed JSON is picked up without polling.
      const res = await fetch(url, { cache: "no-cache" });
      if (!res.ok) {
        throw new Error("HTTP " + res.status);
      }
      const data = await res.json();
      if (!data || !data.summary) {
        throw new Error("Missing summary");
      }
      applySummary(data.summary, data.generated_at);
    } catch (err) {
      console.warn("[homepage] analytics load failed:", err);
      showStatsError("Curriculum statistics temporarily unavailable.");
    }
  }

  /* ---------- footer year ---------- */

  function setCopyrightYear() {
    const el = document.getElementById("copyrightYear");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  /* ---------- init ---------- */

  document.addEventListener("DOMContentLoaded", () => {
    initNav();
    applyConfigLinks();
    renderFeatured();
    setCopyrightYear();
    loadAnalytics();
  });
})();
