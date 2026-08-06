const BLOCKS = {
  "21-25": {
    dataUrl: "data/lessons_21_25_draft.json",
    storageKey: "quietCinematicReview:21-25:v3",
  },
  "26-30": {
    dataUrl: "data/lessons_26_30_draft.json",
    storageKey: "quietCinematicReview:26-30:v1",
  },
};

const params = new URLSearchParams(window.location.search);
const BLOCK = BLOCKS[params.get("block")] ? params.get("block") : "21-25";
const CONFIG = BLOCKS[BLOCK];

/** @type {{ id: string, title: string, notes?: string, targetFinalCount?: number, assetsBase: string, items: any[] }} */
let draft = null;
/** @type {any[]} */
let items = [];
let dragId = null;

function imageUrl(item) {
  const base = (draft.assetsBase || "../../../assets").replace(/\/$/, "");
  return `${base}/${item.image}`;
}

function loadStoredOrder() {
  try {
    const raw = localStorage.getItem(CONFIG.storageKey);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function persist() {
  const payload = {
    savedAt: new Date().toISOString(),
    block: BLOCK,
    order: items.map((it) => it.slug),
    removed: (draft.items || [])
      .map((it) => it.slug)
      .filter((slug) => !items.some((it) => it.slug === slug)),
  };
  localStorage.setItem(CONFIG.storageKey, JSON.stringify(payload));
}

function applyStoredState(stored) {
  if (!stored || !Array.isArray(stored.order)) return;
  const bySlug = new Map(draft.items.map((it) => [it.slug, it]));
  const removed = new Set(stored.removed || []);
  const next = [];
  for (const slug of stored.order) {
    if (removed.has(slug)) continue;
    const it = bySlug.get(slug);
    if (it) next.push({ ...it });
  }
  // Keep any newly added draft items that weren't in the saved order.
  for (const it of draft.items) {
    if (removed.has(it.slug)) continue;
    if (!next.some((x) => x.slug === it.slug)) next.push({ ...it });
  }
  items = next;
}

async function init() {
  document.querySelectorAll(".block-link").forEach((link) => {
    link.classList.toggle("active", link.dataset.block === BLOCK);
  });

  const res = await fetch(CONFIG.dataUrl);
  if (!res.ok) throw new Error(`Failed to load ${CONFIG.dataUrl}`);
  draft = await res.json();
  items = draft.items.map((it) => ({ ...it }));

  const stored = loadStoredOrder();
  if (stored) applyStoredState(stored);

  document.getElementById("page-title").textContent = draft.title.replace(
    /\s*\(Draft Review\)\s*$/,
    ""
  );
  document.getElementById("page-subtitle").textContent =
    "Draft review pool · Quiet Cinematic Japan";
  document.getElementById("page-notes").textContent = draft.notes || "";

  bindToolbar();
  bindLightbox();
  render();
}

function bindToolbar() {
  document.getElementById("btn-export").addEventListener("click", exportOrder);
  document.getElementById("btn-download").addEventListener("click", downloadJson);
  document.getElementById("btn-reset").addEventListener("click", resetDraft);
}

function resetDraft() {
  if (!confirm("Restore the original draft order and bring back removed images?")) {
    return;
  }
  localStorage.removeItem(CONFIG.storageKey);
  items = draft.items.map((it) => ({ ...it }));
  render();
}

function currentExportPayload() {
  return {
    id: draft.id,
    title: draft.title,
    theme: draft.theme,
    status: "review-edited",
    block: BLOCK,
    targetFinalCount: draft.targetFinalCount,
    candidateCount: items.length,
    exportedAt: new Date().toISOString(),
    assetsBase: draft.assetsBase,
    items: items.map((it, index) => ({
      ...it,
      order: index + 1,
    })),
  };
}

async function exportOrder() {
  const payload = currentExportPayload();
  const text = JSON.stringify(payload, null, 2);
  try {
    await navigator.clipboard.writeText(text);
    flashButton(document.getElementById("btn-export"), "Copied");
  } catch {
    prompt("Copy this JSON:", text);
  }
}

function downloadJson() {
  const payload = currentExportPayload();
  const blob = new Blob([JSON.stringify(payload, null, 2) + "\n"], {
    type: "application/json",
  });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${draft.id}_edited.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  flashButton(document.getElementById("btn-download"), "Saved");
}

function flashButton(btn, label) {
  const original = btn.textContent;
  btn.textContent = label;
  setTimeout(() => {
    btn.textContent = original;
  }, 1200);
}

function removeItem(slug) {
  items = items.filter((it) => it.slug !== slug);
  persist();
  render();
}

function moveItem(fromSlug, toSlug) {
  if (fromSlug === toSlug) return;
  const fromIndex = items.findIndex((it) => it.slug === fromSlug);
  const toIndex = items.findIndex((it) => it.slug === toSlug);
  if (fromIndex < 0 || toIndex < 0) return;
  const [moved] = items.splice(fromIndex, 1);
  items.splice(toIndex, 0, moved);
  persist();
  render();
}

function render() {
  const grid = document.getElementById("grid");
  const target = draft.targetFinalCount || 30;
  document.getElementById("count-label").textContent =
    `${items.length} candidates`;
  document.getElementById("target-label").textContent =
    `target ~${target} final · started at ${draft.candidateCount}`;

  grid.innerHTML = "";
  if (!items.length) {
    grid.innerHTML =
      `<div class="empty-state">All images removed. Reset draft to restore the pool.</div>`;
    return;
  }

  items.forEach((item, index) => {
    grid.appendChild(buildCard(item, index + 1));
  });
}

function buildCard(item, order) {
  const card = document.createElement("article");
  card.className = "card";
  card.draggable = true;
  card.dataset.slug = item.slug;

  card.innerHTML = `
    <div class="card-thumb">
      <span class="card-order">${order}</span>
      <button type="button" class="card-remove" aria-label="Remove ${item.slug}">×</button>
      <img src="${imageUrl(item)}" alt="${item.title}" loading="lazy" draggable="false" />
    </div>
    <div class="card-body">
      <h2 class="card-title"><span class="card-kanji">${item.kanji || ""}</span>${item.title}</h2>
      <p class="card-meta">${item.filename}</p>
      <p class="card-meta">id: ${item.id}</p>
      <span class="card-lesson">Lesson ${item.lesson}</span>
    </div>
  `;

  card.querySelector(".card-remove").addEventListener("click", (e) => {
    e.stopPropagation();
    removeItem(item.slug);
  });

  card.querySelector("img").addEventListener("click", (e) => {
    e.stopPropagation();
    openLightbox(item);
  });

  card.addEventListener("dragstart", (e) => {
    dragId = item.slug;
    card.classList.add("dragging");
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", item.slug);
  });

  card.addEventListener("dragend", () => {
    dragId = null;
    card.classList.remove("dragging");
    document.querySelectorAll(".card.drag-over").forEach((el) => {
      el.classList.remove("drag-over");
    });
  });

  card.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    card.classList.add("drag-over");
  });

  card.addEventListener("dragleave", () => {
    card.classList.remove("drag-over");
  });

  card.addEventListener("drop", (e) => {
    e.preventDefault();
    card.classList.remove("drag-over");
    const from = e.dataTransfer.getData("text/plain") || dragId;
    if (from) moveItem(from, item.slug);
  });

  return card;
}

function openLightbox(item) {
  const box = document.getElementById("lightbox");
  const img = box.querySelector("img");
  img.src = imageUrl(item);
  img.alt = item.title;
  document.getElementById("lightbox-caption").textContent =
    `L${item.lesson} · ${item.kanji} ${item.title} · ${item.filename}`;
  box.classList.add("open");
  box.setAttribute("aria-hidden", "false");
}

function closeLightbox() {
  const box = document.getElementById("lightbox");
  box.classList.remove("open");
  box.setAttribute("aria-hidden", "true");
  box.querySelector("img").src = "";
}

function bindLightbox() {
  const box = document.getElementById("lightbox");
  document.getElementById("lightbox-close").addEventListener("click", (e) => {
    e.stopPropagation();
    closeLightbox();
  });
  box.addEventListener("click", closeLightbox);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeLightbox();
  });
}

init().catch((err) => {
  document.getElementById("count-label").textContent = "Failed to load draft";
  document.getElementById("grid").innerHTML =
    `<div class="empty-state">${err.message}</div>`;
  console.error(err);
});
