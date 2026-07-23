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
    /** Official KML Japan YouTube channel */
    youtubeChannelUrl: "https://www.youtube.com/@ambientkanji",

    /** Curriculum overview (book / learning paths on-site) */
    curriculumUrl: "kml/index.html",

    /** Deployed analytics dashboard */
    analyticsDashboardUrl: "kml/analytics/dashboard/",

    /**
     * Public analytics JSON (generated under output/; dashboard ./data symlinks here).
     * Homepage reads summary.* only; never modifies this file.
     * Prefer output/ over dashboard/data so deploy hosts need not resolve the symlink.
     * Paths are relative to the site root; resolved with <html data-base> when needed.
     */
    analyticsJsonUrl: "kml/analytics/output/kml_channel_learning.json",

    /**
     * Gallery entrance playlists.
     * Set playlistUrl when known; null falls back to youtubeChannelUrl
     * unless comingSoon is true (no outbound link yet).
     * To swap artwork later, change only the <img src> in index.html
     * (or image fields below if you choose to drive src from JS).
     */
    galleryEntrances: {
      vocabulary: {
        playlistUrl:
          "https://www.youtube.com/playlist?list=PLJemcdjLRw4w",
        image: "kml/assets/youtube_thumbnails/vocabulary.png",
      },
      postElementaryKanji: {
        playlistUrl:
          "https://www.youtube.com/playlist?list=PLI-ULFjSKz58",
        image: "kml/assets/youtube_thumbnails/jr_high_image.png",
      },
      rememberingKanji: {
        playlistUrl:
          "https://www.youtube.com/playlist?list=PLBv0xLsm4RBo",
        image: "kml/assets/youtube_thumbnails/foundations.png",
      },
      elementaryKanji: {
        playlistUrl:
          "https://www.youtube.com/playlist?list=PLZocopP--8p0",
        image: "kml/assets/youtube_thumbnails/grade_1_.png",
      },
      kanaPreschool: {
        playlistUrl:
          "https://www.youtube.com/playlist?list=PLIX7jswPySk0",
        image: "kml/assets/images/kana_song_image.png",
      },
      postJoyoKanji: {
        playlistUrl: null,
        comingSoon: true,
        image: "kml/assets/images/post_joyo_coming_soon.png",
      },
      ambientJapan: {
        playlistUrl:
          "https://www.youtube.com/playlist?list=PLdjO5D7Hu6TU",
        image: "kml/assets/youtube_thumbnails/ambient_japan.png",
      },
    },

    /**
     * Playlist URLs keyed by learning-path card id.
     * null = no verified playlist; button falls back to curriculumUrl.
     */
    playlistUrls: {
      kana: "https://www.youtube.com/playlist?list=PLIX7jswPySk0",
      elementaryKanji:
        "https://www.youtube.com/playlist?list=PLZocopP--8p0",
      elementaryCompounds: null, // PLACEHOLDER
      postElementaryKanji:
        "https://www.youtube.com/playlist?list=PLI-ULFjSKz58",
      postElementaryCompounds: null, // PLACEHOLDER
      japaneseVocabulary:
        "https://www.youtube.com/playlist?list=PLJemcdjLRw4w",
      spokenJapanese: null, // PLACEHOLDER
      ambientJapan:
        "https://www.youtube.com/playlist?list=PLdjO5D7Hu6TU",
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

  function assetBase() {
    const raw = document.documentElement.getAttribute("data-base");
    if (raw == null || raw === "" || raw === ".") return "";
    return String(raw).replace(/\/$/, "");
  }

  function resolveAsset(path) {
    if (!path) return path;
    if (/^(https?:|mailto:|tel:|#|\/\/)/i.test(path)) return path;
    const cleaned = String(path).replace(/^\.\//, "");
    const base = assetBase();
    return base ? base + "/" + cleaned : cleaned;
  }

  function pageLocale() {
    const lang = (document.documentElement.lang || "en").toLowerCase();
    return lang.startsWith("ja") ? "ja" : "en";
  }

  function fmtInt(n) {
    if (n == null || Number.isNaN(Number(n))) return "—";
    return Number(n).toLocaleString(pageLocale() === "ja" ? "ja-JP" : "en-US");
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
      const locale = pageLocale() === "ja" ? "ja-JP" : undefined;
      return d.toLocaleString(locale, {
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

    wireHref("[data-link='curriculum']", resolveAsset(c.curriculumUrl));
    wireHref("[data-link='analytics']", resolveAsset(c.analyticsDashboardUrl));

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
        el.setAttribute("href", resolveAsset(c.curriculumUrl));
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

    // Gallery entrance frames: playlist when set, otherwise channel
    // (unless comingSoon — keep the frame as a quiet placeholder).
    document.querySelectorAll("[data-gallery]").forEach((el) => {
      const key = el.getAttribute("data-gallery");
      const entry = (c.galleryEntrances && c.galleryEntrances[key]) || null;
      const comingSoon = !!(entry && entry.comingSoon);
      const href = comingSoon
        ? "#"
        : (entry && entry.playlistUrl) || c.youtubeChannelUrl || "#";

      el.setAttribute("href", href);

      if (comingSoon) {
        el.removeAttribute("target");
        el.removeAttribute("rel");
        el.classList.add("is-placeholder", "is-coming-soon");
        el.setAttribute("aria-disabled", "true");
        el.setAttribute("title", "Coming soon");
        return;
      }

      el.removeAttribute("aria-disabled");
      el.classList.remove("is-coming-soon");

      if (href && href !== "#") {
        el.setAttribute("target", "_blank");
        el.setAttribute("rel", "noopener noreferrer");
        el.classList.remove("is-placeholder");
      }

      if (entry && entry.playlistUrl == null && c.youtubeChannelUrl) {
        el.setAttribute(
          "title",
          "Playlist URL pending — opens KML Japan channel. Set SITE_CONFIG.galleryEntrances." +
            key +
            ".playlistUrl"
        );
      } else {
        el.removeAttribute("title");
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
      img.src = resolveAsset(lesson.thumbnail);
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
      if (!label) {
        genEl.textContent = "";
      } else if (pageLocale() === "ja") {
        genEl.textContent = "分析生成日時 " + label;
      } else {
        genEl.textContent = "Analytics generated " + label;
      }
    }
  }

  async function loadAnalytics() {
    const url = resolveAsset(SITE_CONFIG.analyticsJsonUrl);
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
      showStatsError(
        pageLocale() === "ja"
          ? "カリキュラム統計を一時的に表示できません。"
          : "Curriculum statistics temporarily unavailable."
      );
    }
  }

  /* ---------- footer year ---------- */

  function setCopyrightYear() {
    const el = document.getElementById("copyrightYear");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  /* ---------- museum section reveals ---------- */

  function initReveals() {
    const nodes = document.querySelectorAll(".reveal");
    if (!nodes.length) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      nodes.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    if (!("IntersectionObserver" in window)) {
      nodes.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    // threshold 0: tall sections (e.g. gallery hall) must reveal as soon as
    // any part enters view — a high % threshold left the mid-page blank.
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0, rootMargin: "0px 0px -6% 0px" }
    );

    nodes.forEach((el) => observer.observe(el));
  }

  /* ---------- init ---------- */

  document.addEventListener("DOMContentLoaded", () => {
    initNav();
    applyConfigLinks();
    renderFeatured();
    setCopyrightYear();
    initReveals();
    loadAnalytics();
  });
})();
