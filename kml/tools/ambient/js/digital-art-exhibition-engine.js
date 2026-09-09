/**
 * Digital Art Exhibition engine.
 *
 * Soundtrack is the master clock. Images inhabit the room; they do not
 * chase beats. Collection JSON supplies title, opening, artworks, music.
 */
(function () {
  "use strict";

  const DEFAULTS = {
    openingBlackBeforeMs: 1000,
    openingRevealMs: 4500,
    openingHoldMs: 4500,
    openingDissolveMs: 9000,
    titleDelayMs: 1600,
    titleRevealMs: 2800,
    dissolveMs: 10000,
    endingFadeMs: 12000,
    endingBlackAfterMs: 1600,
    brandDelayMs: 900,
    brandRevealMs: 2400,
    brandHoldMs: 2800,
    brandFadeMs: 2200,
  };

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function clamp(n, lo, hi) {
    return Math.min(hi, Math.max(lo, n));
  }

  function smoothstep(u) {
    const x = clamp(u, 0, 1);
    return x * x * (3 - 2 * x);
  }

  function envelope(t, fadeInStart, fadeInEnd, fadeOutStart, fadeOutEnd) {
    if (t < fadeInStart) return 0;
    if (t < fadeInEnd) {
      const span = Math.max(1, fadeInEnd - fadeInStart);
      return smoothstep((t - fadeInStart) / span);
    }
    if (t < fadeOutStart) return 1;
    if (t < fadeOutEnd) {
      const span = Math.max(1, fadeOutEnd - fadeOutStart);
      return 1 - smoothstep((t - fadeOutStart) / span);
    }
    return 0;
  }

  function parseScale() {
    const raw = new URLSearchParams(location.search).get("timingScale");
    if (raw == null || raw === "") return 1;
    const n = Number(raw);
    return Number.isFinite(n) && n > 0 ? n : 1;
  }

  function collectionId() {
    const p = new URLSearchParams(location.search);
    return (p.get("collection") || "moon").trim() || "moon";
  }

  function collectionUrls(id) {
    return [
      `./collections/digital_art/${id}.json`,
      `./collections/${id}.json`,
    ];
  }

  class DigitalArtExhibitionPlayer {
    constructor(root) {
      this.root = root;
      this.els = {
        opening: qs("[data-dae-opening]", root),
        openingImg: qs("[data-dae-opening-img]", root),
        openingTitle: qs("[data-dae-opening-title]", root),
        layers: [
          {
            wrap: qs('[data-dae-artwork="a"]', root),
            img: qs('[data-dae-artwork-img="a"]', root),
          },
          {
            wrap: qs('[data-dae-artwork="b"]', root),
            img: qs('[data-dae-artwork-img="b"]', root),
          },
        ],
        brand: qs("[data-dae-brand]", root),
        brandMark: qs("[data-dae-brand-mark]", root),
        gate: qs("[data-dae-autoplay-gate]", root),
        error: qs("[data-dae-error]", root),
        debug: qs("[data-dae-debug]", root),
        audio: qs("[data-dae-audio]", root),
      };

      this.params = new URLSearchParams(location.search);
      this.timingScale = parseScale();
      this.debug = this.params.get("debug") === "1";
      this.recordPipeline = this.params.get("recordPipeline") === "1";
      this.paused = false;
      this.started = false;
      this.ended = false;
      this.clockMs = 0;
      this._raf = 0;
      this._lastNow = 0;
      this.collection = null;
      this.schedule = null;
      this.imageCache = new Map();
      this._layerSrc = ["", ""];
      this._audioTailStartedAt = 0;
      this._audioTailClockMs = 0;
      this.ready = false;
      this.soundtrackStartedAtEpochMs = 0;
      this.presentationEnded = false;
    }

    assetUrl(path) {
      if (!path) return "";
      if (/^https?:\/\//.test(path) || path.startsWith("/") || path.startsWith("./") || path.startsWith("../")) {
        return path;
      }
      if (path.startsWith("audio/")) return `./${path}`;
      const base = (this.collection.assetsBase || "../../assets").replace(/\/$/, "");
      return `${base}/${path.replace(/^\//, "")}`;
    }

    async load() {
      const id = collectionId();
      const urls = collectionUrls(id);
      let data = null;
      let lastError = null;
      for (const url of urls) {
        try {
          const res = await fetch(url);
          if (!res.ok) {
            lastError = new Error(`${url} (${res.status})`);
            continue;
          }
          data = await res.json();
          break;
        } catch (err) {
          lastError = err;
        }
      }
      if (!data) {
        this.showError(`Could not load exhibition “${id}”.`);
        throw lastError || new Error("collection missing");
      }
      this.collection = data;
      document.title = data.title ? `${data.title} — Digital Art Exhibition` : "Digital Art Exhibition";
      this.schedule = this.buildSchedule(data);
      await this.preload();
      this.ready = true;
      this.bind();
      this.paint(0);
      if (this.debug && this.els.debug) this.els.debug.hidden = false;
      if (this.recordPipeline) {
        this.hideGate();
        await this.begin();
      } else {
        this.showGate();
      }
      window.KmlDigitalArtExhibition = this;
    }

    showError(message) {
      if (!this.els.error) return;
      this.els.error.hidden = false;
      this.els.error.textContent = message;
    }

    showGate() {
      if (!this.els.gate) return;
      this.els.gate.hidden = false;
    }

    hideGate() {
      if (!this.els.gate) return;
      this.els.gate.hidden = true;
    }

    bind() {
      if (this.els.gate) {
        this.els.gate.addEventListener("click", () => {
          this.hideGate();
          this.begin();
        });
      }
      window.addEventListener("keydown", (ev) => {
        if (ev.code === "Space") {
          ev.preventDefault();
          this.togglePause();
        }
      });
      document.addEventListener("visibilitychange", () => {
        if (document.hidden && this.started && !this.paused) this.togglePause(true);
      });
    }

    async preload() {
      const col = this.collection;
      const paths = [];
      if (col.opening?.image) paths.push(this.assetUrl(col.opening.image));
      for (const art of col.artworks || []) {
        if (art.image) paths.push(this.assetUrl(art.image));
      }
      await Promise.all(paths.map((src) => this.loadImage(src)));

      if (col.opening?.image && this.els.openingImg) {
        this.els.openingImg.src = this.assetUrl(col.opening.image);
      }
      const title = (col.opening && col.opening.title) || "";
      const titleMode = (col.opening && col.opening.titleMode) || (title ? "label" : "none");
      if (this.els.openingTitle) {
        if (title && titleMode !== "none") {
          this.els.openingTitle.textContent = title;
          this.els.openingTitle.classList.remove("is-empty");
        } else {
          this.els.openingTitle.textContent = "";
          this.els.openingTitle.classList.add("is-empty");
        }
      }
      if (col.ending?.brand && this.els.brandMark) {
        this.els.brandMark.textContent = col.ending.brand;
      }

      const audioSrc = col.soundtrack?.src || col.soundtrack?.main;
      if (audioSrc && this.els.audio) {
        this.els.audio.src = this.assetUrl(audioSrc);
        this.els.audio.preload = "auto";
        this.els.audio.loop = false;
        try {
          this.els.audio.load();
        } catch (_) {
          /* ignore */
        }
        await this.waitForAudio();
        const actualMs = Math.round((this.els.audio.duration || 0) * 1000);
        const authored = col.soundtrack?.durationMs || 0;
        if (actualMs > 1000 && Math.abs(actualMs - authored) > 500) {
          this.schedule = this.buildSchedule(col, actualMs);
        }
      }
    }

    loadImage(src) {
      if (this.imageCache.has(src)) return this.imageCache.get(src);
      const p = new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error(`image failed: ${src}`));
        img.src = src;
      });
      this.imageCache.set(src, p);
      return p;
    }

    waitForAudio() {
      const el = this.els.audio;
      if (!el || !el.src) return Promise.resolve();
      if (el.readyState >= 2 && Number.isFinite(el.duration)) return Promise.resolve();
      return new Promise((resolve) => {
        const done = () => {
          el.removeEventListener("canplaythrough", done);
          el.removeEventListener("loadedmetadata", done);
          resolve();
        };
        el.addEventListener("canplaythrough", done, { once: true });
        el.addEventListener("loadedmetadata", done, { once: true });
        window.setTimeout(done, 4000);
      });
    }

    timingFrom(col) {
      const t = { ...DEFAULTS, ...(col.timing || {}) };
      const opening = col.opening || {};
      if (opening.blackBeforeMs != null) t.openingBlackBeforeMs = opening.blackBeforeMs;
      if (opening.revealMs != null) t.openingRevealMs = opening.revealMs;
      if (opening.holdMs != null) t.openingHoldMs = opening.holdMs;
      if (opening.dissolveMs != null) t.openingDissolveMs = opening.dissolveMs;
      if (opening.titleDelayMs != null) t.titleDelayMs = opening.titleDelayMs;
      if (opening.titleRevealMs != null) t.titleRevealMs = opening.titleRevealMs;
      const ending = col.ending || {};
      if (ending.fadeMs != null) t.endingFadeMs = ending.fadeMs;
      if (ending.blackAfterMs != null) t.endingBlackAfterMs = ending.blackAfterMs;
      if (ending.brandDelayMs != null) t.brandDelayMs = ending.brandDelayMs;
      if (ending.brandRevealMs != null) t.brandRevealMs = ending.brandRevealMs;
      if (ending.brandHoldMs != null) t.brandHoldMs = ending.brandHoldMs;
      if (ending.brandFadeMs != null) t.brandFadeMs = ending.brandFadeMs;
      return t;
    }

    buildSchedule(col, soundtrackMs) {
      const t = this.timingFrom(col);
      const artworks = col.artworks || [];
      const n = artworks.length;
      const durationMs =
        soundtrackMs ||
        col.soundtrack?.durationMs ||
        this.estimateDuration(col, t);

      const openingInStart = t.openingBlackBeforeMs;
      const openingInEnd = openingInStart + t.openingRevealMs;
      const openingOutStart = openingInEnd + t.openingHoldMs;
      const openingOutEnd = openingOutStart + t.openingDissolveMs;

      const defaultDissolve = t.dissolveMs;
      const dissolves = artworks.map((art, i) => {
        if (i === n - 1) return t.endingFadeMs;
        return art.dissolveMs != null ? art.dissolveMs : defaultDissolve;
      });

      const midDissolves = dissolves.slice(0, Math.max(0, n - 1)).reduce((s, x) => s + x, 0);
      const holdBudget = Math.max(
        n * 8000,
        durationMs -
          t.openingBlackBeforeMs -
          t.openingRevealMs -
          t.openingHoldMs -
          t.openingDissolveMs -
          midDissolves -
          t.endingFadeMs
      );

      const explicit = artworks.every((art) => art.holdMs != null);
      let holds;
      if (explicit) {
        const raw = artworks.map((art) => art.holdMs);
        const sum = raw.reduce((s, x) => s + x, 0) || 1;
        if (Math.abs(sum - holdBudget) > 80) {
          holds = raw.map((h) => Math.round((holdBudget * h) / sum));
          holds[holds.length - 1] += holdBudget - holds.reduce((s, x) => s + x, 0);
        } else {
          holds = raw;
        }
      } else {
        const weights = artworks.map((art, i) => {
          if (art.weight != null) return art.weight;
          return 0.92 + i * 0.06 + (i === n - 1 ? 0.28 : 0);
        });
        const wsum = weights.reduce((s, x) => s + x, 0) || 1;
        holds = weights.map((w) => Math.round((holdBudget * w) / wsum));
        holds[holds.length - 1] += holdBudget - holds.reduce((s, x) => s + x, 0);
      }

      let cursor = openingOutStart;
      const layers = [];
      for (let i = 0; i < n; i += 1) {
        const fadeInStart = cursor;
        const fadeInEnd = fadeInStart + (i === 0 ? t.openingDissolveMs : dissolves[i - 1]);
        const fadeOutStart = fadeInEnd + holds[i];
        const fadeOutEnd = fadeOutStart + dissolves[i];
        layers.push({
          id: artworks[i].id || `art-${i}`,
          src: this.assetUrl(artworks[i].image),
          motion: artworks[i].motion || col.room?.motion || "still",
          fadeInStart,
          fadeInEnd,
          fadeOutStart,
          fadeOutEnd,
        });
        cursor = fadeOutStart;
      }

      const lastOut = n ? layers[n - 1].fadeOutEnd : openingOutEnd;
      const brand = col.ending?.brand
        ? {
            fadeInStart: lastOut + t.brandDelayMs,
            fadeInEnd: lastOut + t.brandDelayMs + t.brandRevealMs,
            fadeOutStart: lastOut + t.brandDelayMs + t.brandRevealMs + t.brandHoldMs,
            fadeOutEnd:
              lastOut +
              t.brandDelayMs +
              t.brandRevealMs +
              t.brandHoldMs +
              t.brandFadeMs,
          }
        : null;

      const titleDelay = t.titleDelayMs;
      const titleReveal = t.titleRevealMs;

      return {
        durationMs,
        opening: {
          fadeInStart: openingInStart,
          fadeInEnd: openingInEnd,
          fadeOutStart: openingOutStart,
          fadeOutEnd: openingOutEnd,
        },
        title: {
          fadeInStart: openingInEnd + titleDelay,
          fadeInEnd: openingInEnd + titleDelay + titleReveal,
          fadeOutStart: openingOutStart,
          fadeOutEnd: openingOutEnd,
        },
        artworks: layers,
        brand,
        endMs: brand ? brand.fadeOutEnd + t.endingBlackAfterMs : lastOut + t.endingBlackAfterMs,
      };
    }

    estimateDuration(col, t) {
      const arts = col.artworks || [];
      const holds = arts.reduce((s, art) => s + (art.holdMs || 16000), 0);
      const dissolves = arts.reduce((s, art, i) => {
        if (i === arts.length - 1) return s;
        return s + (art.dissolveMs || t.dissolveMs);
      }, 0);
      return (
        t.openingBlackBeforeMs +
        t.openingRevealMs +
        t.openingHoldMs +
        t.openingDissolveMs +
        holds +
        dissolves +
        t.endingFadeMs
      );
    }

    async begin() {
      if (this.started) return;
      this.started = true;
      this._audioTailStartedAt = 0;
      this._audioTailClockMs = 0;
      const audio = this.els.audio;
      if (audio && audio.src) {
        audio.playbackRate = this.timingScale === 1 ? 1 : clamp(1 / this.timingScale, 0.25, 8);
        try {
          await audio.play();
        } catch (_) {
          this.showGate();
          this.started = false;
          return;
        }
        this.soundtrackStartedAtEpochMs = Date.now();
      }
      this._lastNow = performance.now();
      if (!this.soundtrackStartedAtEpochMs) this.soundtrackStartedAtEpochMs = Date.now();
      this.loop();
    }

    togglePause(forcePause) {
      if (!this.started || this.ended) return;
      const next = forcePause === true ? true : !this.paused;
      this.paused = next;
      const audio = this.els.audio;
      if (audio && audio.src) {
        if (next) audio.pause();
        else audio.play().catch(() => {});
      }
      if (!next) {
        this._lastNow = performance.now();
        this.loop();
      }
    }

    seekMs(ms) {
      this.clockMs = clamp(ms, 0, this.schedule.endMs);
      this._audioTailStartedAt = 0;
      this._audioTailClockMs = 0;
      const audio = this.els.audio;
      if (audio && Number.isFinite(audio.duration)) {
        audio.currentTime = clamp(this.clockMs / 1000, 0, audio.duration);
      }
      this.paint(this.clockMs);
    }

    loop() {
      if (this.paused || this.ended) return;
      const now = performance.now();
      const audio = this.els.audio;
      const durationMs = this.schedule.durationMs || 0;
      if (audio && audio.src && Number.isFinite(audio.currentTime)) {
        const audioMs = audio.currentTime * 1000;
        const audioDone = audio.ended || (durationMs > 0 && audioMs >= durationMs - 30);
        if (audioDone) {
          if (!this._audioTailStartedAt) {
            this._audioTailStartedAt = now;
            this._audioTailClockMs = Math.max(audioMs, durationMs);
          }
          this.clockMs = this._audioTailClockMs + (now - this._audioTailStartedAt);
        } else {
          this.clockMs = audioMs;
        }
      } else {
        this.clockMs += (now - this._lastNow) / this.timingScale;
      }
      this._lastNow = now;
      this.paint(this.clockMs);
      if (this.clockMs >= this.schedule.endMs) {
        this.finish();
        return;
      }
      this._raf = requestAnimationFrame(() => this.loop());
    }

    finish() {
      if (this.ended) return;
      this.ended = true;
      this.presentationEnded = true;
      this.paint(this.schedule.endMs);
      const audio = this.els.audio;
      if (audio && !audio.paused) {
        try {
          audio.pause();
        } catch (_) {
          /* ignore */
        }
      }
      document.dispatchEvent(
        new CustomEvent("kml-digital-art-exhibition-end", {
          detail: { collection: this.collection.id },
        })
      );
    }

    paint(ms) {
      const sch = this.schedule;
      const openingOp = envelope(
        ms,
        sch.opening.fadeInStart,
        sch.opening.fadeInEnd,
        sch.opening.fadeOutStart,
        sch.opening.fadeOutEnd
      );
      if (this.els.opening) this.els.opening.style.opacity = String(openingOp);

      const titleOp = envelope(
        ms,
        sch.title.fadeInStart,
        sch.title.fadeInEnd,
        sch.title.fadeOutStart,
        sch.title.fadeOutEnd
      );
      if (this.els.openingTitle) this.els.openingTitle.style.opacity = String(titleOp);

      const arts = sch.artworks;
      const vis = [];
      for (let i = 0; i < arts.length; i += 1) {
        const op = envelope(
          ms,
          arts[i].fadeInStart,
          arts[i].fadeInEnd,
          arts[i].fadeOutStart,
          arts[i].fadeOutEnd
        );
        if (op > 0.002) vis.push({ i, op, art: arts[i] });
      }
      const shown = vis.sort((a, b) => a.i - b.i).slice(-2);
      const used = new Set();
      const assignment = new Array(2).fill(null);
      for (const item of shown) {
        const sticky = this._layerSrc.findIndex((src) => src === item.art.src);
        if (sticky >= 0 && assignment[sticky] == null) {
          assignment[sticky] = item;
          used.add(sticky);
        }
      }
      for (const item of shown) {
        if (assignment.some((slot) => slot && slot.art.src === item.art.src)) continue;
        const free = assignment.findIndex((slot, idx) => slot == null && !used.has(idx));
        const slot = free >= 0 ? free : 0;
        assignment[slot] = item;
        used.add(slot);
      }
      for (let slot = 0; slot < 2; slot += 1) {
        const layer = this.els.layers[slot];
        const item = assignment[slot];
        if (!item) {
          layer.wrap.style.opacity = "0";
          this._layerSrc[slot] = "";
          continue;
        }
        if (this._layerSrc[slot] !== item.art.src) {
          this._layerSrc[slot] = item.art.src;
          layer.img.src = item.art.src;
          layer.img.alt = "";
        }
        const breath = item.art.motion === "breath";
        layer.wrap.classList.toggle("is-breath", breath);
        if (breath) {
          const span = Math.max(1, item.art.fadeOutEnd - item.art.fadeInStart);
          layer.wrap.style.setProperty("--dae-breath-ms", `${Math.round(span)}ms`);
        }
        layer.wrap.style.zIndex = String(1 + item.i);
        layer.wrap.style.opacity = String(item.op);
      }

      if (this.els.brand) {
        if (sch.brand) {
          this.els.brand.style.opacity = String(
            envelope(
              ms,
              sch.brand.fadeInStart,
              sch.brand.fadeInEnd,
              sch.brand.fadeOutStart,
              sch.brand.fadeOutEnd
            )
          );
        } else {
          this.els.brand.style.opacity = "0";
        }
      }

      if (this.debug && this.els.debug) {
        const active = vis.reduce((best, cur) => (cur.op >= best.op ? cur : best), vis[0]);
        const label = active ? active.art.id : openingOp > 0.05 ? "opening" : "black";
        this.els.debug.textContent = `${(ms / 1000).toFixed(1)}s  ${label}`;
      }
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    const root = qs("[data-dae-root]");
    if (!root) return;
    const player = new DigitalArtExhibitionPlayer(root);
    player.load().catch((err) => {
      console.error(err);
      player.showError("The exhibition could not be opened.");
    });
  });
})();
