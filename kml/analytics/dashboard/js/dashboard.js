/**
 * KML Curriculum Dashboard v1.0
 * Read-only visualization of ../output/kml_channel_learning.json
 * Never touches production lesson files.
 */
(() => {
  "use strict";

  const DASHBOARD_VERSION = "1.0";
  const DATA_URL = new URL("./data/kml_channel_learning.json", window.location.href).href;
  const POLL_MS = 30000;

  const ROLE_COLORS = {
    introduction: "var(--intro)",
    balanced: "var(--balanced)",
    consolidation: "var(--consol)",
    light: "var(--light-role)",
    empty: "var(--light-role)",
  };

  const BAND_COLORS = {
    introduced: "#7a9e8f",
    reinforced: "#4a6fa5",
    familiar: "#a67c52",
    strong: "#6b5b95",
    core: "#2f5d50",
    unseen: "#c4bbb0",
  };

  const PATH_LABELS = {
    japanese_vocabulary: "Spoken Vocabulary",
    grade_1_kanji: "Grade 1",
    grade_2_kanji: "Grade 2",
    grade_3_kanji: "Grade 3",
    grade_4_kanji: "Grade 4",
    grade_5_kanji: "Grade 5",
    grade_6_kanji: "Grade 6",
    grade_1_compounds: "Grade 1 Compounds",
    grade_2_compounds: "Grade 2 Compounds",
    grade_3_compounds: "Grade 3 Compounds",
    grade_4_compounds: "Grade 4 Compounds",
    grade_5_compounds: "Grade 5 Compounds",
    grade_6_compounds: "Grade 6 Compounds",
    post_elementary_kanji: "Post-Elementary",
    post_elementary_compounds: "Post-Elementary Compounds",
    foundations: "Foundations",
    channel_global: "Complete Channel",
  };

  /** @type {any} */
  let DATA = null;
  /** @type {string|null} */
  let lastGeneratedAt = null;
  /** @type {Record<string, any>} */
  const charts = {};
  let filters = {
    playlist: "all",
    jlpt: "all",
    kind: "all",
    role: "all",
    lesson: "",
  };

  // --------------------------------------------------------------------------
  // Utilities
  // --------------------------------------------------------------------------

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  function fmt(n, digits = 0) {
    if (n == null || Number.isNaN(n)) return "—";
    return Number(n).toLocaleString(undefined, {
      maximumFractionDigits: digits,
      minimumFractionDigits: digits,
    });
  }

  function pct(n) {
    if (n == null) return "—";
    return `${fmt(n, 1)}%`;
  }

  function pathName(id) {
    return PATH_LABELS[id] || id || "—";
  }

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function chartDefaults() {
    const ink = cssVar("--ink-secondary") || "#5c564c";
    const grid = cssVar("--stroke") || "#ddd6c8";
    Chart.defaults.color = ink;
    Chart.defaults.borderColor = grid;
    Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
    Chart.defaults.plugins.legend.labels.boxWidth = 10;
    Chart.defaults.plugins.legend.labels.boxHeight = 10;
    Chart.defaults.elements.line.tension = 0.25;
    Chart.defaults.elements.point.radius = 0;
    Chart.defaults.elements.point.hoverRadius = 4;
  }

  function destroyChart(id) {
    if (charts[id]) {
      charts[id].destroy();
      delete charts[id];
    }
  }

  function makeChart(id, config) {
    destroyChart(id);
    const canvas = document.getElementById(id);
    if (!canvas) return null;
    charts[id] = new Chart(canvas, config);
    return charts[id];
  }

  function independentPaths() {
    return Object.values(DATA.paths).filter((p) => p.path_id !== "channel_global");
  }

  function globalPath() {
    return DATA.paths.channel_global;
  }

  function filteredLessons() {
    const g = globalPath();
    return (g.per_lesson || []).filter((L) => {
      const lv = L.learning_value || {};
      const role = (lv.educational_role || {}).id || "";
      if (filters.playlist !== "all" && (L.source_path || "") !== filters.playlist) return false;
      if (filters.kind !== "all" && (L.kind || "") !== filters.kind) return false;
      if (filters.role !== "all" && role !== filters.role) return false;
      if (filters.lesson) {
        const q = filters.lesson.toLowerCase();
        const hay = `${L.label} ${L.title} ${L.id}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  function filteredProgress() {
    const orders = new Set(filteredLessons().map((L) => L.order));
    return (globalPath().progress || []).filter((p) => orders.has(p.after_order));
  }

  // --------------------------------------------------------------------------
  // Data load
  // --------------------------------------------------------------------------

  async function loadData({ silent = false } = {}) {
    const status = $("#statusBanner");
    if (!silent && status) {
      status.hidden = false;
      status.className = "status-banner loading";
      status.textContent = "Loading curriculum analytics…";
    }
    try {
      const res = await fetch(DATA_URL, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status} loading ${DATA_URL}`);
      const json = await res.json();
      if (!json.paths || !json.summary) {
        throw new Error("Unexpected analytics schema — missing paths/summary.");
      }
      const changed = json.generated_at !== lastGeneratedAt;
      DATA = json;
      lastGeneratedAt = json.generated_at;
      if (status) status.hidden = true;
      if (changed || !silent) renderAll();
      return changed;
    } catch (err) {
      console.error(err);
      if (status) {
        status.hidden = false;
        status.className = "status-banner error";
        status.textContent =
          `Could not load analytics JSON. Serve from kml/analytics/dashboard/ ` +
          `(./serve.sh) and regenerate with analyze_channel_learning.py. ${err.message}`;
      }
      return false;
    }
  }

  // --------------------------------------------------------------------------
  // Header / summary
  // --------------------------------------------------------------------------

  function renderHeader() {
    const s = DATA.summary;
    $("#generatedAt").textContent = formatTimestamp(DATA.generated_at);
    $("#schemaVersion").textContent =
      `schema v${DATA.schema_version ?? "?"} · dashboard v${DASHBOARD_VERSION}`;
    $("#genMeta").textContent = DATA.generator || "";

    const cards = [
      { label: "Videos", value: fmt(s.global_videos), sub: "global learning path" },
      { label: "Learning paths", value: fmt(s.independent_paths), sub: "independent playlists" },
      { label: "Unique vocabulary", value: fmt(s.global_unique_vocabulary), sub: "distinct words" },
      { label: "Unique kanji", value: fmt(s.global_unique_kanji), sub: "distinct characters" },
      { label: "Joyo coverage", value: pct(s.global_joyo_percent), sub: "of 2,136 joyo" },
      {
        label: "Multi-context vocab",
        value: fmt(s.vocab_multiple_contexts),
        sub: "appeared in 2+ videos",
      },
      {
        label: "Avg learning value",
        value: fmt(globalPath().learning_values?.average_total_learning_value, 1),
        sub: "new + reinforced / video",
      },
      {
        label: "Avg reinforcement",
        value: fmt(globalPath().learning_values?.average_reinforced, 1),
        sub: "reinforced items / video",
      },
    ];
    $("#summaryCards").innerHTML = cards
      .map(
        (c) => `
      <article class="card stat-card">
        <div class="stat-label">${c.label}</div>
        <div class="stat-value">${c.value}</div>
        <div class="stat-sub">${c.sub}</div>
      </article>`
      )
      .join("");
  }

  function formatTimestamp(iso) {
    if (!iso) return "—";
    try {
      const d = new Date(iso);
      return d.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso;
    }
  }

  // --------------------------------------------------------------------------
  // Growth charts
  // --------------------------------------------------------------------------

  function progressTooltip(ctx) {
    const p = filteredProgress()[ctx.dataIndex];
    if (!p) return "";
    const lv = p.learning_value || {};
    return [
      p.after_lesson_label,
      `Playlist: ${pathName(p.source_path)}`,
      `New vocab: ${p.new_vocabulary ?? 0} · Reinforced vocab: ${p.reviewed_vocabulary ?? 0}`,
      `New kanji: ${p.new_kanji ?? 0} · Reinforced kanji: ${p.reviewed_kanji ?? 0}`,
      `Learning value: ${lv.total_learning_value ?? "—"} ${lv.stars || ""}`,
    ];
  }

  function renderGrowthCharts() {
    const progress = filteredProgress();
    const labels = progress.map((p) => String(p.after_order));
    const commonOpts = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: true },
        tooltip: {
          callbacks: {
            title: (items) => {
              const p = progress[items[0].dataIndex];
              return p ? p.after_lesson_label : "";
            },
            afterBody: (items) => progressTooltip(items[0]),
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "Global video #" },
          ticks: { maxTicksLimit: 12 },
        },
        y: { beginAtZero: true },
      },
    };

    makeChart("chartVocabGrowth", {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Unique vocabulary",
            data: progress.map((p) => p.unique_vocabulary),
            borderColor: cssVar("--info"),
            backgroundColor: "transparent",
          },
        ],
      },
      options: commonOpts,
    });

    makeChart("chartKanjiGrowth", {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Unique kanji",
            data: progress.map((p) => p.unique_kanji),
            borderColor: cssVar("--success"),
            backgroundColor: "transparent",
          },
        ],
      },
      options: commonOpts,
    });

    makeChart("chartJoyoGrowth", {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Joyo coverage %",
            data: progress.map((p) => p.joyo_coverage?.percent ?? 0),
            borderColor: cssVar("--accent"),
            backgroundColor: "transparent",
          },
        ],
      },
      options: {
        ...commonOpts,
        scales: {
          ...commonOpts.scales,
          y: { beginAtZero: true, max: 100, title: { display: true, text: "%" } },
        },
      },
    });

    makeChart("chartJlptWords", {
      type: "line",
      data: {
        labels,
        datasets: ["N5", "N4", "N3", "N2", "N1"].map((lv, i) => ({
          label: lv,
          data: progress.map((p) => p.jlpt_word_coverage?.[lv]?.percent ?? 0),
          borderColor: ["#2f5d50", "#4a6fa5", "#a67c52", "#6b5b95", "#9b3d3d"][i],
          backgroundColor: "transparent",
        })),
      },
      options: {
        ...commonOpts,
        scales: {
          ...commonOpts.scales,
          y: { beginAtZero: true, title: { display: true, text: "% of list" } },
        },
      },
    });

    makeChart("chartSpoken", {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Top 1000 %",
            data: progress.map((p) => p.spoken_frequency_coverage?.top_1000?.percent ?? 0),
            borderColor: cssVar("--info"),
            backgroundColor: "transparent",
          },
          {
            label: "Top 2000 %",
            data: progress.map((p) => p.spoken_frequency_coverage?.top_2000?.percent ?? 0),
            borderColor: cssVar("--warning"),
            backgroundColor: "transparent",
          },
          {
            label: "Top 500 %",
            data: progress.map((p) => p.spoken_frequency_coverage?.top_500?.percent ?? 0),
            borderColor: cssVar("--success"),
            backgroundColor: "transparent",
          },
          {
            label: "Top 5000 %",
            data: progress.map((p) => p.spoken_frequency_coverage?.top_5000?.percent ?? 0),
            borderColor: cssVar("--light-role"),
            backgroundColor: "transparent",
          },
        ],
      },
      options: {
        ...commonOpts,
        scales: {
          ...commonOpts.scales,
          y: { beginAtZero: true, title: { display: true, text: "% of band" } },
        },
      },
    });

    makeChart("chartReview", {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Vocab due for review",
            data: progress.map((p) => p.review_opportunities?.vocabulary_due ?? 0),
            borderColor: cssVar("--warning"),
            backgroundColor: "transparent",
          },
          {
            label: "Kanji due for review",
            data: progress.map((p) => p.review_opportunities?.kanji_due ?? 0),
            borderColor: cssVar("--info"),
            backgroundColor: "transparent",
          },
        ],
      },
      options: commonOpts,
    });
  }

  // --------------------------------------------------------------------------
  // Learning value timeline
  // --------------------------------------------------------------------------

  function renderLearningValue() {
    const lessons = filteredLessons();
    const roleIds = ["introduction", "balanced", "consolidation", "light"];
    const roleLabels = ["Introduction", "Balanced", "Consolidation", "Light touch"];
    const roleVars = ["--intro", "--balanced", "--consol", "--light-role"];

    makeChart("chartLearningValue", {
      type: "scatter",
      data: {
        datasets: roleIds.map((role, i) => ({
          label: roleLabels[i],
          data: lessons
            .filter((L) => (L.learning_value?.educational_role?.id || "light") === role)
            .map((L) => ({
              x: L.order,
              y: L.learning_value?.total_learning_value ?? 0,
              lesson: L,
            })),
          backgroundColor: cssVar(roleVars[i]),
          pointRadius: 5,
          pointHoverRadius: 7,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              title: (items) => items[0]?.raw?.lesson?.label || "",
              label: (item) => {
                const L = item.raw.lesson;
                const lv = L.learning_value || {};
                return [
                  `Playlist: ${pathName(L.source_path)}`,
                  `New: ${lv.new_total} · Reinforced: ${lv.reinforced_total}`,
                  `Value: ${lv.total_learning_value} ${lv.stars || ""}`,
                  `Role: ${lv.educational_role?.label || "—"}`,
                ];
              },
            },
          },
        },
        scales: {
          x: { title: { display: true, text: "Global video #" }, type: "linear" },
          y: { title: { display: true, text: "Learning value" }, beginAtZero: true },
        },
      },
    });

    const tbody = lessons
      .slice()
      .sort(
        (a, b) =>
          (b.learning_value?.total_learning_value || 0) -
          (a.learning_value?.total_learning_value || 0)
      )
      .slice(0, 40)
      .map((L) => {
        const lv = L.learning_value || {};
        const role = lv.educational_role?.id || "";
        return `<tr>
          <td>${escapeHtml(L.label)}</td>
          <td>${escapeHtml(pathName(L.source_path))}</td>
          <td>${lv.new_total ?? 0}</td>
          <td>${lv.reinforced_total ?? 0}</td>
          <td>${lv.total_learning_value ?? 0}</td>
          <td>${lv.stars || ""}</td>
          <td><span class="pill ${role}">${escapeHtml(lv.educational_role?.label || "")}</span></td>
          <td>${lv.jlpt_gain?.combined ?? 0}</td>
          <td>${lv.spoken_frequency_gain?.headline_top_1000 ?? 0}</td>
        </tr>`;
      })
      .join("");
    $("#learningValueTable").innerHTML = tbody;
  }

  // --------------------------------------------------------------------------
  // Playlist cards
  // --------------------------------------------------------------------------

  function renderPlaylists() {
    const paths = independentPaths().filter((p) => {
      if (filters.playlist !== "all" && p.path_id !== filters.playlist) return false;
      return true;
    });
    $("#playlistCards").innerHTML = paths
      .map((p) => {
        const f = p.final || {};
        const lv = p.learning_values || {};
        const n5 = f.jlpt_word_coverage?.N5?.percent ?? 0;
        const t1k = f.spoken_frequency_coverage?.top_1000?.percent ?? 0;
        return `<article class="card playlist-card" data-path="${p.path_id}">
          <h3>${escapeHtml(pathName(p.path_id))}</h3>
          <div class="playlist-meta">
            <div><span>Videos</span><br><strong>${p.lessons_in_path}</strong></div>
            <div><span>Role</span><br><strong>${escapeHtml(p.role)}</strong></div>
            <div><span>Vocabulary</span><br><strong>${fmt(f.unique_vocabulary)}</strong></div>
            <div><span>Kanji</span><br><strong>${fmt(f.unique_kanji)}</strong></div>
            <div><span>Joyo</span><br><strong>${pct(f.joyo_coverage?.percent)}</strong></div>
            <div><span>N5 words</span><br><strong>${pct(n5)}</strong></div>
            <div><span>Top 1000</span><br><strong>${pct(t1k)}</strong></div>
            <div><span>Avg learning value</span><br><strong>${fmt(lv.average_total_learning_value, 1)}</strong></div>
          </div>
        </article>`;
      })
      .join("");
  }

  // --------------------------------------------------------------------------
  // Exposure
  // --------------------------------------------------------------------------

  function renderExposure() {
    const ex = globalPath().exposure || {};
    const bands = DATA.summary.exposure_bands || [];
    const order = bands.map((b) => b.id);

    function stackHtml(title, bandObj, includeUnseen) {
      const keys = includeUnseen ? [...order, "unseen"] : order;
      const total = keys.reduce((s, k) => s + (bandObj?.[k]?.count || 0), 0) || 1;
      const segs = keys
        .map((k) => {
          const c = bandObj?.[k]?.count || 0;
          if (!c) return "";
          const color = BAND_COLORS[k] || "#999";
          const w = (100 * c) / total;
          const label = bandObj?.[k]?.label || k;
          return `<div class="stack-seg" style="width:${w}%;background:${color}" title="${label}: ${c}"></div>`;
        })
        .join("");
      return `<div class="stack-row">
        <div>${title}</div>
        <div class="stack-track">${segs}</div>
        <div class="section-note">${fmt(total === 1 ? 0 : total)}</div>
      </div>`;
    }

    const legend = [...order, "unseen"]
      .map((k) => {
        const label =
          bands.find((b) => b.id === k)?.label ||
          (k === "unseen" ? "Unseen" : k);
        return `<span><i style="background:${BAND_COLORS[k]}"></i>${label}</span>`;
      })
      .join("");

    $("#exposureStacks").innerHTML = `
      <div class="legend">${legend}</div>
      <div class="stack-bars">
        ${stackHtml("Vocabulary", ex.vocabulary?.bands, false)}
        ${stackHtml("Kanji (seen)", ex.kanji?.bands, false)}
        ${stackHtml("Joyo", ex.joyo?.bands, true)}
      </div>`;

    // Donut charts
    const vocabData = order.map((k) => ex.vocabulary?.bands?.[k]?.count || 0);
    const joyoData = [...order, "unseen"].map((k) => ex.joyo?.bands?.[k]?.count || 0);

    makeChart("chartExposureVocab", {
      type: "doughnut",
      data: {
        labels: order.map((k) => bands.find((b) => b.id === k)?.label || k),
        datasets: [{ data: vocabData, backgroundColor: order.map((k) => BAND_COLORS[k]) }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
      },
    });

    makeChart("chartExposureJoyo", {
      type: "doughnut",
      data: {
        labels: [...order, "unseen"].map(
          (k) => bands.find((b) => b.id === k)?.label || (k === "unseen" ? "Unseen" : k)
        ),
        datasets: [
          {
            data: joyoData,
            backgroundColor: [...order, "unseen"].map((k) => BAND_COLORS[k]),
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
      },
    });
  }

  // --------------------------------------------------------------------------
  // JLPT
  // --------------------------------------------------------------------------

  function renderJlpt() {
    const ex = globalPath().exposure || {};
    const f = globalPath().final || {};
    const levels = ["N5", "N4", "N3", "N2", "N1"];

    makeChart("chartJlptCoverage", {
      type: "bar",
      data: {
        labels: levels,
        datasets: [
          {
            label: "Word-list coverage %",
            data: levels.map((lv) => f.jlpt_word_coverage?.[lv]?.percent ?? 0),
            backgroundColor: cssVar("--info"),
          },
          {
            label: "Kanji coverage %",
            data: levels.map((lv) => f.jlpt_kanji_coverage?.[lv]?.percent ?? 0),
            backgroundColor: cssVar("--success"),
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: "%" } } },
      },
    });

    makeChart("chartJlptEncounters", {
      type: "bar",
      data: {
        labels: levels,
        datasets: [
          {
            label: "Avg encounters (kanji, among seen)",
            data: levels.map(
              (lv) => ex.jlpt_kanji?.[lv]?.average_encounters_among_seen ?? 0
            ),
            backgroundColor: cssVar("--warning"),
          },
          {
            label: "Avg encounters (vocab in curriculum)",
            data: levels.map(
              (lv) => ex.jlpt_words?.[lv]?.average_encounters_among_curriculum ?? 0
            ),
            backgroundColor: cssVar("--info"),
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true, title: { display: true, text: "encounters" } } },
      },
    });
  }

  // --------------------------------------------------------------------------
  // Heatmaps
  // --------------------------------------------------------------------------

  function renderHeatmaps() {
    const paths = independentPaths();
    const levels = ["N5", "N4", "N3", "N2", "N1"];
    const bands = [500, 1000, 2000, 5000];

    function heat(containerId, cols, getValue, format = (v) => fmt(v, 0)) {
      const values = paths.flatMap((p) => cols.map((c) => getValue(p, c)));
      const max = Math.max(...values, 0.0001);
      const head = `<div class="heatmap-row" style="--cols:${cols.length}">
        <div></div>${cols.map((c) => `<div class="heatmap-head">${c}</div>`).join("")}
      </div>`;
      const rows = paths
        .map((p) => {
          const cells = cols
            .map((c) => {
              const v = getValue(p, c);
              const t = Math.min(1, v / max);
              const bg = `color-mix(in srgb, ${cssVar("--accent")} ${Math.round(t * 85)}%, ${cssVar("--bg-muted")})`;
              return `<div class="heatmap-cell" style="background:${bg}" title="${pathName(p.path_id)} / ${c}: ${format(v)}">${format(v)}</div>`;
            })
            .join("");
          return `<div class="heatmap-row" style="--cols:${cols.length}">
            <div class="heatmap-label">${escapeHtml(pathName(p.path_id))}</div>${cells}
          </div>`;
        })
        .join("");
      $(containerId).innerHTML = `<div class="heatmap">${head}${rows}</div>`;
    }

    heat(
      "#heatJlpt",
      levels,
      (p, lv) => p.final?.jlpt_word_coverage?.[lv]?.percent ?? 0,
      (v) => fmt(v, 0)
    );
    heat(
      "#heatFreq",
      bands.map((b) => `Top ${b}`),
      (p, label) => {
        const b = Number(label.replace("Top ", ""));
        return p.final?.spoken_frequency_coverage?.[`top_${b}`]?.percent ?? 0;
      },
      (v) => fmt(v, 0)
    );
    heat(
      "#heatValue",
      ["Avg value", "Avg new", "Avg reinforced"],
      (p, col) => {
        const lv = p.learning_values || {};
        if (col === "Avg value") return lv.average_total_learning_value || 0;
        if (col === "Avg new") return lv.average_new || 0;
        return lv.average_reinforced || 0;
      },
      (v) => fmt(v, 0)
    );
    heat(
      "#heatRoles",
      ["Introduction", "Balanced", "Consolidation"],
      (p, col) => {
        const id = col.toLowerCase();
        return p.learning_values?.role_counts?.[id] || 0;
      },
      (v) => fmt(v, 0)
    );
  }

  // --------------------------------------------------------------------------
  // Milestones
  // --------------------------------------------------------------------------

  function renderMilestones() {
    const g = globalPath();
    const statements = [...(g.milestone_statements || [])];
    const progress = g.progress || [];
    const extras = [];

    // Derived milestone-style achievements
    for (const p of progress) {
      if (p.unique_vocabulary >= 1000 && !extras.find((e) => e.key === "vocab1000")) {
        extras.push({
          key: "vocab1000",
          title: "1,000 unique vocabulary",
          detail: `${p.after_lesson_label} · ${pathName(p.source_path)}`,
        });
      }
      if (p.unique_kanji >= 2000 && !extras.find((e) => e.key === "kanji2000")) {
        extras.push({
          key: "kanji2000",
          title: "2,000 unique kanji",
          detail: `${p.after_lesson_label} · ${pathName(p.source_path)}`,
        });
      }
      if (
        (p.review_opportunities?.vocabulary_due || 0) >= 100 &&
        !extras.find((e) => e.key === "review100")
      ) {
        extras.push({
          key: "review100",
          title: "100 reinforcement-candidate words",
          detail: `${p.after_lesson_label} · ${pathName(p.source_path)}`,
        });
      }
    }

    const fromStatements = statements
      .filter((s) =>
        /90% of Joyo|50% of JLPT N5|75% of Top 1000|100% of JLPT N5 Kanji|25% of Top 1000|50% of Joyo/.test(
          s
        )
      )
      .map((s) => ({ title: s.replace(/\.$/, ""), detail: "Coverage milestone" }));

    const items = [...fromStatements, ...extras].slice(0, 24);
    $("#milestoneList").innerHTML = items
      .map(
        (m) => `<div class="milestone"><strong>${escapeHtml(m.title)}</strong><span>${escapeHtml(m.detail)}</span></div>`
      )
      .join("");
  }

  // --------------------------------------------------------------------------
  // Search
  // --------------------------------------------------------------------------

  function renderSearch(query = "") {
    const si = globalPath().search_index;
    const box = $("#searchResults");
    if (!si) {
      box.innerHTML = `<tr><td colspan="7">Search index not present in analytics JSON.</td></tr>`;
      return;
    }
    const q = query.trim().toLowerCase();
    if (!q) {
      box.innerHTML = `<tr><td colspan="7">Type a kanji, word, reading, lesson, or playlist.</td></tr>`;
      return;
    }

    let jlptFilter = filters.jlpt;
    const vocabHits = (si.vocabulary || [])
      .filter((w) => {
        if (jlptFilter !== "all" && w.jlpt !== jlptFilter) return false;
        const hay = `${w.jp} ${w.reading || ""} ${w.en || ""} ${w.first_lesson || ""} ${pathName(w.first_path)}`.toLowerCase();
        return hay.includes(q);
      })
      .slice(0, 40);

    const kanjiHits = (si.kanji || [])
      .filter((k) => {
        if (jlptFilter !== "all" && k.jlpt !== jlptFilter) return false;
        const hay = `${k.kanji} ${k.first_lesson || ""} ${pathName(k.first_path)}`.toLowerCase();
        return hay.includes(q) || k.kanji === query.trim();
      })
      .slice(0, 40);

    const rows = [
      ...vocabHits.map(
        (w) => `<tr>
          <td>Vocab</td>
          <td>${escapeHtml(w.jp)}</td>
          <td>${escapeHtml(w.reading || "")}</td>
          <td>${escapeHtml(w.first_lesson || "")}</td>
          <td>${escapeHtml(w.latest_lesson || "")}</td>
          <td>${w.encounters}</td>
          <td>${escapeHtml(w.stage || "")}</td>
        </tr>`
      ),
      ...kanjiHits.map(
        (k) => `<tr>
          <td>Kanji</td>
          <td>${escapeHtml(k.kanji)}</td>
          <td>${k.joyo ? "joyo" : ""} ${k.jlpt || ""}</td>
          <td>${escapeHtml(k.first_lesson || "")}</td>
          <td>${escapeHtml(k.latest_lesson || "")}</td>
          <td>${k.encounters}</td>
          <td>${escapeHtml(k.stage || "")}</td>
        </tr>`
      ),
    ];

    box.innerHTML =
      rows.join("") || `<tr><td colspan="7">No matches for “${escapeHtml(query)}”.</td></tr>`;
  }

  // --------------------------------------------------------------------------
  // Filters
  // --------------------------------------------------------------------------

  function populateFilters() {
    const pathSelect = $("#filterPlaylist");
    const paths = independentPaths();
    pathSelect.innerHTML =
      `<option value="all">All playlists</option>` +
      paths
        .map((p) => `<option value="${p.path_id}">${escapeHtml(pathName(p.path_id))}</option>`)
        .join("");
  }

  function bindFilters() {
    $("#filterPlaylist").addEventListener("change", (e) => {
      filters.playlist = e.target.value;
      renderFiltered();
    });
    $("#filterJlpt").addEventListener("change", (e) => {
      filters.jlpt = e.target.value;
      renderSearch($("#searchInput").value);
    });
    $("#filterKind").addEventListener("change", (e) => {
      filters.kind = e.target.value;
      renderFiltered();
    });
    $("#filterRole").addEventListener("change", (e) => {
      filters.role = e.target.value;
      renderFiltered();
    });
    $("#filterLesson").addEventListener("input", (e) => {
      filters.lesson = e.target.value;
      renderFiltered();
    });
    let searchTimer;
    $("#searchInput").addEventListener("input", (e) => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => renderSearch(e.target.value), 150);
    });
  }

  function renderFiltered() {
    chartDefaults();
    renderGrowthCharts();
    renderLearningValue();
    renderPlaylists();
  }

  // --------------------------------------------------------------------------
  // Export
  // --------------------------------------------------------------------------

  function bindExport() {
    const root = $("#exportMenu");
    $("#exportToggle").addEventListener("click", (e) => {
      e.stopPropagation();
      root.classList.toggle("open");
    });
    document.addEventListener("click", () => root.classList.remove("open"));

    $("#exportJson").addEventListener("click", () => {
      downloadBlob(
        JSON.stringify(DATA, null, 2),
        "kml_channel_learning.json",
        "application/json"
      );
    });
    $("#exportCsv").addEventListener("click", () => {
      const rows = [["lesson", "playlist", "kind", "new", "reinforced", "total", "stars", "role", "jlpt_gain", "spoken_top1000"]];
      for (const L of globalPath().per_lesson || []) {
        const lv = L.learning_value || {};
        rows.push([
          L.label,
          pathName(L.source_path),
          L.kind,
          lv.new_total,
          lv.reinforced_total,
          lv.total_learning_value,
          lv.stars,
          lv.educational_role?.label,
          lv.jlpt_gain?.combined,
          lv.spoken_frequency_gain?.headline_top_1000,
        ]);
      }
      const csv = rows.map((r) => r.map(csvEscape).join(",")).join("\n");
      downloadBlob(csv, "kml_learning_value.csv", "text/csv");
    });
    $("#exportMd").addEventListener("click", () => {
      downloadBlob(buildMarkdownSummary(), "kml_curriculum_summary.md", "text/markdown");
    });
    $("#exportPdf").addEventListener("click", () => window.print());
    $("#exportPng").addEventListener("click", async () => {
      // Export main growth chart as PNG via Chart.js
      const chart = charts.chartJoyoGrowth;
      if (!chart) return;
      const a = document.createElement("a");
      a.href = chart.toBase64Image("image/png", 1);
      a.download = "kml_joyo_growth.png";
      a.click();
    });
  }

  function csvEscape(v) {
    const s = String(v ?? "");
    if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
    return s;
  }

  function downloadBlob(text, filename, type) {
    const blob = new Blob([text], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  function buildMarkdownSummary() {
    const s = DATA.summary;
    const g = globalPath();
    const lines = [
      `# KML Curriculum Summary`,
      ``,
      `_Generated ${DATA.generated_at} · Dashboard v${DASHBOARD_VERSION}_`,
      ``,
      `## Overview`,
      ``,
      `| Metric | Value |`,
      `|---|---|`,
      `| Videos | ${s.global_videos} |`,
      `| Paths | ${s.independent_paths} |`,
      `| Vocabulary | ${s.global_unique_vocabulary} |`,
      `| Kanji | ${s.global_unique_kanji} |`,
      `| Joyo | ${s.global_joyo_percent}% |`,
      `| Multi-context vocab | ${s.vocab_multiple_contexts} |`,
      ``,
      `## Milestones`,
      ``,
      ...(g.milestone_statements || []).slice(0, 30).map((m) => `- ${m}`),
      ``,
      `## Exposure statements`,
      ``,
      ...((g.exposure && g.exposure.statements) || []).slice(0, 20).map((m) => `- ${m}`),
      ``,
    ];
    return lines.join("\n");
  }

  // --------------------------------------------------------------------------
  // Theme
  // --------------------------------------------------------------------------

  function bindTheme() {
    const saved = localStorage.getItem("kml-dashboard-theme");
    if (saved === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else if (saved === "light") {
      document.documentElement.removeAttribute("data-theme");
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      document.documentElement.setAttribute("data-theme", "dark");
    }
    $("#themeToggle").addEventListener("click", () => {
      const dark = document.documentElement.getAttribute("data-theme") === "dark";
      if (dark) {
        document.documentElement.removeAttribute("data-theme");
        localStorage.setItem("kml-dashboard-theme", "light");
      } else {
        document.documentElement.setAttribute("data-theme", "dark");
        localStorage.setItem("kml-dashboard-theme", "dark");
      }
      chartDefaults();
      renderFiltered();
      renderExposure();
      renderJlpt();
      renderHeatmaps();
    });
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // --------------------------------------------------------------------------
  // Render all
  // --------------------------------------------------------------------------

  function renderAll() {
    chartDefaults();
    renderHeader();
    populateFilters();
    renderGrowthCharts();
    renderLearningValue();
    renderPlaylists();
    renderExposure();
    renderJlpt();
    renderHeatmaps();
    renderMilestones();
    renderSearch($("#searchInput")?.value || "");
  }

  async function init() {
    $("#dashboardVersion").textContent = `v${DASHBOARD_VERSION}`;
    bindTheme();
    bindFilters();
    bindExport();
    $("#reloadBtn").addEventListener("click", () => loadData());
    await loadData();
    setInterval(() => loadData({ silent: true }), POLL_MS);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") loadData({ silent: true });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
