/**
 * Shougaku Kanji Exhibition — colorful kanji groups fading in and out.
 */
(function () {
  "use strict";

  const DEFAULT_TIMING = {
    titleFadeInMs: 1200,
    titleHoldMs: 3500,
    titleFadeOutMs: 1000,
    groupFadeInMs: 2800,
    groupHoldMs: 9000,
    groupFadeOutMs: 2200,
    staggerMs: 70,
    groupGapMs: 600,
    endFadeMs: 3000,
  };

  function shuffle(array) {
    const copy = array.slice();
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  class ShougakuPlayer {
    constructor(root, collection) {
      this.root = root;
      this.collection = collection;
      this.timing = { ...DEFAULT_TIMING, ...(collection.timing || {}) };
      this.display = {
        loop: true,
        randomizeGroups: true,
        randomizeWithinGroup: true,
        showTitle: true,
        ...(collection.display || {}),
      };
      this.palette = collection.palette || [
        "#e85d4c",
        "#f4a261",
        "#e9c46a",
        "#2a9d8f",
        "#4895ef",
        "#7b61ff",
        "#f72585",
      ];
      this.groups = (collection.groups || []).map((group) => group.kanji.slice());
      this.params = new URLSearchParams(window.location.search);
      this.captureMode = this.params.get("capture") === "1";
      if (this.captureMode) {
        this.display.loop = false;
        this.root.classList.add("shougaku-capture");
      }

      this.els = {
        loading: root.querySelector("[data-shougaku-loading]"),
        error: root.querySelector("[data-shougaku-error]"),
        autoplayGate: root.querySelector("[data-shougaku-autoplay-gate]"),
        titleScreen: root.querySelector("[data-shougaku-title-screen]"),
        titleMain: root.querySelector("[data-shougaku-title-main]"),
        titleSub: root.querySelector("[data-shougaku-title-sub]"),
        gridWrap: root.querySelector("[data-shougaku-grid-wrap]"),
        grid: root.querySelector("[data-shougaku-grid]"),
        status: root.querySelector("[data-shougaku-status]"),
        btnToggle: root.querySelector("[data-shougaku-toggle]"),
      };

      this.mainAudio = null;
      this.paused = false;
      this.destroyed = false;
      this.playing = false;
      this.groupQueue = [];
      this.lastGroupIndex = -1;
    }

    assetUrl(path) {
      if (!path) return "";
      if (/^https?:\/\//.test(path)) return path;
      return path.replace(/^\.\//, "");
    }

    setStatus(text) {
      if (this.els.status) this.els.status.textContent = text;
    }

    pickNextGroupIndex() {
      if (!this.groups.length) return -1;
      if (this.groups.length === 1) return 0;

      if (!this.display.randomizeGroups) {
        this.lastGroupIndex = (this.lastGroupIndex + 1) % this.groups.length;
        return this.lastGroupIndex;
      }

      let next = this.lastGroupIndex;
      while (next === this.lastGroupIndex) {
        next = Math.floor(Math.random() * this.groups.length);
      }
      this.lastGroupIndex = next;
      return next;
    }

    buildGroupQueue() {
      if (this.display.randomizeGroups) {
        this.groupQueue = shuffle(
          Array.from({ length: this.groups.length }, (_, index) => index)
        );
        this.lastGroupIndex = this.groupQueue[this.groupQueue.length - 1];
        return;
      }
      this.groupQueue = Array.from({ length: this.groups.length }, (_, index) => index);
      this.lastGroupIndex = -1;
    }

    nextQueuedGroupIndex() {
      if (!this.groupQueue.length) {
        if (!this.display.loop) {
          return -1;
        }
        this.buildGroupQueue();
      }
      if (!this.groupQueue.length) {
        return -1;
      }
      const index = this.groupQueue.shift();
      this.lastGroupIndex = index;
      return index;
    }

    randomColor() {
      return this.palette[Math.floor(Math.random() * this.palette.length)];
    }

    clearGrid() {
      if (!this.els.grid) return;
      this.els.grid.innerHTML = "";
    }

    renderGroup(kanjiList) {
      const grid = this.els.grid;
      const wrap = this.els.gridWrap;
      if (!grid || !wrap) return [];

      const cols = this.collection.grid?.cols || 4;
      const rows = this.collection.grid?.rows || 10;
      grid.style.setProperty("--shougaku-cols", String(cols));
      grid.style.setProperty("--shougaku-rows", String(rows));
      grid.style.setProperty("--shougaku-fade", `${this.timing.groupFadeInMs}ms`);
      this.clearGrid();

      const cells = kanjiList.map((kanji) => {
        const cell = document.createElement("div");
        cell.className = "shougaku-cell";
        const glyph = document.createElement("span");
        glyph.className = "shougaku-kanji";
        glyph.textContent = kanji;
        glyph.style.color = this.randomColor();
        cell.appendChild(glyph);
        grid.appendChild(cell);
        return cell;
      });

      wrap.classList.remove("shougaku-hidden");
      return cells;
    }

    async fadeCells(cells, visible) {
      const stagger = this.timing.staggerMs;
      const order = shuffle(cells.slice());
      for (let i = 0; i < order.length; i += 1) {
        if (this.destroyed) return;
        await this.waitWhilePaused();
        order[i].classList.toggle("is-visible", visible);
        if (i < order.length - 1) {
          await wait(stagger);
        }
      }
    }

    async waitWhilePaused() {
      while (this.paused && !this.destroyed) {
        await wait(100);
      }
    }

    async showTitle() {
      if (!this.display.showTitle || !this.els.titleScreen) return;

      this.els.titleMain.textContent = this.collection.title || "";
      this.els.titleSub.textContent = this.collection.titleEn || "";
      this.els.titleScreen.classList.add("is-visible");
      await wait(this.timing.titleFadeInMs + this.timing.titleHoldMs);
      this.els.titleScreen.classList.remove("is-visible");
      await wait(this.timing.titleFadeOutMs);
    }

    async playGroup(groupIndex) {
      const source = this.groups[groupIndex] || [];
      const kanjiList = this.display.randomizeWithinGroup
        ? shuffle(source)
        : source.slice();
      const cells = this.renderGroup(kanjiList);
      if (!cells.length) return;

      this.setStatus(
        `Group ${groupIndex + 1} / ${this.groups.length} · ${kanjiList.length} kanji`
      );

      await this.fadeCells(cells, true);
      await wait(this.timing.groupHoldMs);
      await this.fadeCells(cells, false);
      await wait(this.timing.groupFadeOutMs + this.timing.groupGapMs);
    }

    async startSoundtrack() {
      const track = this.collection.soundtrack?.main;
      if (!track) return;

      this.mainAudio = new Audio(this.assetUrl(track));
      this.mainAudio.loop = !!this.display.loop;
      try {
        await this.mainAudio.play();
      } catch (error) {
        console.warn("Soundtrack autoplay blocked:", error);
      }
    }

    bindControls() {
      const gateBtn = this.root.querySelector("[data-shougaku-start]");
      if (gateBtn) {
        gateBtn.addEventListener("click", () => this.begin());
      }
      if (this.els.btnToggle) {
        this.els.btnToggle.addEventListener("click", () => this.togglePause());
      }
    }

    togglePause() {
      this.paused = !this.paused;
      if (this.mainAudio) {
        if (this.paused) this.mainAudio.pause();
        else this.mainAudio.play().catch(() => {});
      }
      if (this.els.btnToggle) {
        this.els.btnToggle.textContent = this.paused ? "Play" : "Pause";
      }
    }

    hideLoading() {
      this.els.loading?.classList.add("shougaku-hidden");
    }

    showError(message) {
      if (!this.els.error) return;
      this.els.error.textContent = message;
      this.els.error.classList.remove("shougaku-hidden");
      this.hideLoading();
    }

    async begin() {
      if (this.playing) return;
      this.playing = true;
      this.els.autoplayGate?.classList.add("shougaku-hidden");
      this.hideLoading();
      await this.startSoundtrack();
      await this.run();
    }

    async run() {
      await this.showTitle();
      this.buildGroupQueue();

      while (!this.destroyed) {
        const groupIndex = this.nextQueuedGroupIndex();
        if (groupIndex < 0) break;

        await this.waitWhilePaused();
        await this.playGroup(groupIndex);
      }

      if (this.mainAudio) {
        await wait(this.timing.endFadeMs);
        this.mainAudio.pause();
      }
    }

    init() {
      if (!this.groups.length) {
        this.showError("Collection has no kanji groups.");
        return;
      }

      document.title = this.collection.title || "Shougaku Kanji Exhibition";
      this.bindControls();
      this.hideLoading();

      if (this.captureMode) {
        this.begin();
        return;
      }

      this.els.autoplayGate?.classList.remove("shougaku-hidden");
    }
  }

  async function loadCollection(id) {
    const response = await fetch(`./collections/${id}.json`);
    if (!response.ok) {
      throw new Error(`Failed to load collection "${id}" (${response.status})`);
    }
    return response.json();
  }

  async function boot() {
    const root = document.querySelector("[data-shougaku-root]");
    if (!root) return;

    const params = new URLSearchParams(window.location.search);
    const collectionId = params.get("collection") || "grade_2";

    try {
      const collection = await loadCollection(collectionId);
      const player = new ShougakuPlayer(root, collection);
      player.init();
      window.shougakuPlayer = player;
    } catch (error) {
      const errorEl = root.querySelector("[data-shougaku-error]");
      if (errorEl) {
        errorEl.textContent = error.message || String(error);
        errorEl.classList.remove("shougaku-hidden");
      }
      root.querySelector("[data-shougaku-loading]")?.classList.add("shougaku-hidden");
      console.error(error);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
