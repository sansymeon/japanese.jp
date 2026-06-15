const params = new URLSearchParams(window.location.search);
const REVIEW_SET = params.get("set") === "v2" ? "v2" : "v1";
const DATA_URL = REVIEW_SET === "v2" ? "data/lesson_01_kml_v2.json" : "data/lesson_01_kml_v1.json";
const IMAGE_DIR = REVIEW_SET === "v2" ? "images_v2" : "images";

let allItems = [];
let activeFilter = "all";

/** Resolve thumbnail URL relative to this page (works with serve.sh from review dir). */
function imageUrl(slug) {
  return `${IMAGE_DIR}/${slug}.png`;
}

async function init() {
  const res = await fetch(DATA_URL);
  const data = await res.json();
  allItems = data.items.sort((a, b) => a.order - b.order);
  document.getElementById("page-title").textContent = data.title;
  document.getElementById("page-source").textContent = data.source;
  document.querySelector("footer p").textContent =
    REVIEW_SET === "v2"
      ? "KML Visual Layout v2 test · Sorted by lesson order"
      : "KML Visual Styles v1 evaluation run · Sorted by lesson order";
  if (REVIEW_SET === "v2") {
    document.querySelectorAll('[data-filter="WASH"],[data-filter="GLOW"],[data-filter="CINE"]').forEach((el) => {
      el.style.display = "none";
    });
  }
  bindFilters();
  bindLightbox();
  render();
}

function bindFilters() {
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeFilter = btn.dataset.filter;
      render();
    });
  });
}

function matchesFilter(item) {
  switch (activeFilter) {
    case "all":
      return true;
    case "strongest":
      return item.tier === "strongest" || item.tier === "hero" || item.styleShort === "HERO";
    case "weakest":
      return item.tier === "weakest" || item.flagged;
    case "WASH":
      return item.styleShort === "WASH";
    case "GLOW":
      return item.styleShort === "GLOW";
    case "CINE":
      return item.styleShort === "CINE";
    case "HERO":
      return item.galleryPriority === "hero" || item.styleShort === "HERO";
    case "FEAT":
      return item.galleryPriority === "feature" || item.styleShort === "FEAT";
    default:
      return true;
  }
}

function render() {
  const grid = document.getElementById("grid");
  const visible = allItems.filter(matchesFilter);
  document.getElementById("count-label").textContent =
    `Showing ${visible.length} of ${allItems.length}`;

  grid.innerHTML = "";

  if (!visible.length) {
    grid.innerHTML = `<div class="empty-state">No images match this filter.</div>`;
    return;
  }

  for (const item of visible) {
    grid.appendChild(buildCard(item));
  }
}

function buildCard(item) {
  const card = document.createElement("article");
  card.className = "card";
  card.dataset.slug = item.slug;

  const tierBadge =
    item.tier === "strongest"
      ? `<span class="tier-badge strongest">Strong</span>`
      : item.tier === "weakest"
        ? `<span class="tier-badge weakest">Weak</span>`
        : "";

  const accentTag = item.is_accent
    ? `<span class="accent-tag">accent</span>`
    : "";

  const src = imageUrl(item.slug);

  card.innerHTML = `
    <div class="thumb-wrap" data-full="${src}" tabindex="0" role="button" aria-label="View full image for ${item.keyword}">
      <img src="${src}" alt="${item.keyword} (${item.kanji}) — ${item.style}" loading="lazy" />
      ${tierBadge}
    </div>
    <div class="card-body">
      <div class="card-head">
        <span class="kanji">${item.kanji}</span>
        <div class="keyword-block">
          <div class="keyword">${item.keyword}</div>
          <div class="slug">${item.slug} · #${item.order}</div>
        </div>
      </div>
      <div class="style-row">
        <span class="style-badge ${item.styleShort}">${item.galleryPriority || item.styleShort}</span>
        ${accentTag}
        <span class="distance">${item.image_distance || ""}</span>
      </div>
      <div class="toggles">
        <button type="button" class="toggle-btn prompt-toggle" aria-expanded="false">Prompt</button>
        <button type="button" class="toggle-btn notes-toggle" aria-expanded="false">Notes</button>
      </div>
    </div>
    <div class="panel prompt" hidden></div>
    <div class="panel notes" hidden></div>
  `;

  const promptPanel = card.querySelector(".panel.prompt");
  const notesPanel = card.querySelector(".panel.notes");
  promptPanel.textContent = item.prompt;
  notesPanel.textContent = item.notes;

  const promptBtn = card.querySelector(".prompt-toggle");
  const notesBtn = card.querySelector(".notes-toggle");

  promptBtn.addEventListener("click", () => {
    togglePanel(promptBtn, promptPanel, notesPanel, notesBtn);
  });
  notesBtn.addEventListener("click", () => {
    togglePanel(notesBtn, notesPanel, promptPanel, promptBtn);
  });

  const thumb = card.querySelector(".thumb-wrap");
  thumb.addEventListener("click", () => openLightbox(src, item.keyword));
  thumb.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      openLightbox(src, item.keyword);
    }
  });

  return card;
}

function togglePanel(btn, panel, otherPanel, otherBtn) {
  const open = btn.getAttribute("aria-expanded") === "true";
  btn.setAttribute("aria-expanded", String(!open));
  panel.classList.toggle("open", !open);
  panel.hidden = open;

  if (!open && otherPanel.classList.contains("open")) {
    otherBtn.setAttribute("aria-expanded", "false");
    otherPanel.classList.remove("open");
    otherPanel.hidden = true;
  }
}

function bindLightbox() {
  const lb = document.getElementById("lightbox");
  lb.addEventListener("click", closeLightbox);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeLightbox();
  });
}

function openLightbox(src, alt) {
  const lb = document.getElementById("lightbox");
  const img = lb.querySelector("img");
  img.src = src;
  img.alt = alt;
  lb.classList.add("open");
  lb.setAttribute("aria-hidden", "false");
}

function closeLightbox() {
  const lb = document.getElementById("lightbox");
  lb.classList.remove("open");
  lb.setAttribute("aria-hidden", "true");
  lb.querySelector("img").src = "";
}

init().catch((err) => {
  console.error(err);
  document.getElementById("grid").innerHTML =
    `<div class="empty-state">Failed to load review data. Serve this folder over HTTP.<br><code>${err.message}</code></div>`;
});
