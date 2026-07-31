/**
 * Kanji Components player.
 * Scene types: kanji | newComponent | newFamily
 * Quiet observation + deliberate New Component / New Family pauses.
 */
(function () {
  "use strict";

  const ENTRANCE_SIDES = ["left", "right", "right", "left"];

  const DEFAULT_TIMING = {
    heroFadeInMs: 1800,
    afterHeroPauseMs: 900,
    componentArriveMs: 1400,
    componentStaggerMs: 1700,
    afterComponentsPauseMs: 1400,
    keywordFadeInMs: 1400,
    keywordHoldMs: 3200,
    keywordFadeOutMs: 1100,
    afterKeywordsPauseMs: 900,
    componentsFadeOutMs: 1600,
    heroAloneMs: 2400,
    crossfadeMs: 1600,
    blackBetweenMs: 700,
    crestBlackBeforeMs: 900,
    crestRevealMs: 2800,
    crestHoldMs: 1400,
    soundtrackFadeMs: 8000,
    crestFadeOutMs: 3500,
    crestBlackAfterMs: 800,
  };

  const DEFAULT_INTRO_TIMING = {
    headingFadeInMs: 1400,
    glyphFadeInMs: 2000,
    glyphAloneHoldMs: 2800,
    labelFadeInMs: 1600,
    completeHoldMs: 4500,
    fadeOutMs: 1800,
    blackAfterMs: 900,
  };

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function parseTimingScale() {
    const raw = new URLSearchParams(location.search).get("timingScale");
    if (raw == null || raw === "") return 1;
    const n = Number(raw);
    return Number.isFinite(n) && n > 0 ? n : 1;
  }

  function scaleTiming(timing, scale) {
    const out = {};
    for (const [k, v] of Object.entries(timing)) {
      out[k] = Math.max(40, Math.round(Number(v) * scale));
    }
    return out;
  }

  function sceneType(scene) {
    return scene?.type || "kanji";
  }

  function partGlyph(part) {
    return part.glyph || part.kanji || "";
  }

  function partLabel(part) {
    return part.label || part.keyword || "";
  }

  class KanjiComponentsPlayer {
    constructor(root) {
      this.root = root;
      this.stage = qs("[data-kc-stage]", root);
      this.hero = qs("[data-kc-hero]", root);
      this.row = qs("[data-kc-components]", root);
      this.intro = qs("[data-kc-intro]", root);
      this.introHeading = qs("[data-kc-intro-heading]", root);
      this.introGlyph = qs("[data-kc-intro-glyph]", root);
      this.introLabel = qs("[data-kc-intro-label]", root);
      this.veil = qs("[data-kc-veil]", root);
      this.crest = qs("[data-kc-crest]", root);
      this.crestImg = qs("[data-kc-crest-img]", root);
      this.chromeLabel = qs("[data-kc-chrome-label]", root);
      this.audioEl = qs("[data-kc-audio]", root);
      this.autoplayGate = qs("[data-kc-autoplay-gate]", root);
      this.scenes = [];
      this.families = {};
      this.timing = { ...DEFAULT_TIMING };
      this.introTiming = { ...DEFAULT_INTRO_TIMING };
      this.soundtrack = null;
      this.bookends = null;
      this.skipBookends = false;
      this.scale = 1;
      this.index = 0;
      this.runId = 0;
      this.destroyed = false;
      this._soundtrackStarted = false;
      this.presentationEnded = false;
    }

    localUrl(relative) {
      if (!relative) return "";
      if (/^https?:\/\//.test(relative) || relative.startsWith("/")) return relative;
      return `./${relative.replace(/^\.\//, "")}`;
    }

    initAudio() {
      if (!this.soundtrack?.main || !this.audioEl) return;
      this.audioEl.src = this.localUrl(this.soundtrack.main);
      this.audioEl.loop = this.soundtrack.loop !== false;
      this.audioEl.preload = "auto";
      try {
        this.audioEl.load();
      } catch (_) {
        /* ignore */
      }
    }

    async ensureAudioUnlocked() {
      if (!this.soundtrack?.main || !this.audioEl) return;

      try {
        await this.audioEl.play();
        this.audioEl.pause();
        this.audioEl.currentTime = 0;
        return;
      } catch (err) {
        if (err?.name !== "NotAllowedError") {
          console.warn("[Kanji Components audio] autoplay probe", err);
        }
      }

      await this.waitForAutoplayGate();
    }

    waitForAutoplayGate() {
      const gate = this.autoplayGate;
      if (!gate) return Promise.resolve();

      return new Promise((resolve) => {
        let settled = false;
        const finish = async () => {
          if (settled) return;
          settled = true;
          gate.classList.remove("is-visible");
          gate.hidden = true;
          gate.removeEventListener("keydown", onKeyDown);

          if (this.audioEl) {
            try {
              await this.audioEl.play();
              this.audioEl.pause();
              this.audioEl.currentTime = 0;
            } catch (err) {
              console.warn("[Kanji Components audio] gate unlock", err);
            }
          }
          resolve();
        };

        const onKeyDown = (e) => {
          if (e.code === "Enter" || e.code === "Space") {
            e.preventDefault();
            finish();
          }
        };

        gate.hidden = false;
        requestAnimationFrame(() => gate.classList.add("is-visible"));
        gate.addEventListener("click", finish, { once: true });
        gate.addEventListener("keydown", onKeyDown);
        gate.focus();

        if (new URLSearchParams(location.search).get("capture") === "1") {
          window.setTimeout(() => finish(), 400);
        }
      });
    }

    async startSoundtrack() {
      if (!this.soundtrack?.main || !this.audioEl || this._soundtrackStarted) return;
      try {
        this.audioEl.currentTime = 0;
        await this.audioEl.play();
        this._soundtrackStarted = true;
      } catch (err) {
        console.warn("[Kanji Components audio] play()", err);
      }
    }

    stopSoundtrack() {
      if (!this.audioEl) return;
      try {
        this.audioEl.pause();
      } catch (_) {
        /* ignore */
      }
      this._soundtrackStarted = false;
    }

    async fadeOutSoundtrack(fadeMs) {
      const audio = this.audioEl;
      if (!audio || audio.paused || audio.ended) return;
      const startVolume = audio.volume;
      const steps = Math.max(1, Math.round(fadeMs / 50));
      const stepMs = fadeMs / steps;
      for (let i = 1; i <= steps; i++) {
        if (this.destroyed) return;
        audio.volume = startVolume * (1 - i / steps);
        await this.wait(stepMs);
      }
      try {
        audio.pause();
        audio.currentTime = 0;
        audio.volume = startVolume;
      } catch (_) {
        /* ignore */
      }
      this._soundtrackStarted = false;
    }

    applyCssVars() {
      const t = this.timing;
      const it = this.introTiming;
      const root = document.documentElement;
      root.style.setProperty("--kc-hero-fade-ms", `${t.heroFadeInMs}ms`);
      root.style.setProperty("--kc-arrive-ms", `${t.componentArriveMs}ms`);
      root.style.setProperty("--kc-keyword-fade-ms", `${t.keywordFadeInMs}ms`);
      root.style.setProperty("--kc-leave-ms", `${t.componentsFadeOutMs}ms`);
      root.style.setProperty("--kc-crossfade-ms", `${t.crossfadeMs}ms`);
      root.style.setProperty("--kc-crest-fade-ms", `${t.crestRevealMs}ms`);
      root.style.setProperty("--kc-intro-heading-ms", `${it.headingFadeInMs}ms`);
      root.style.setProperty("--kc-intro-glyph-ms", `${it.glyphFadeInMs}ms`);
      root.style.setProperty("--kc-intro-label-ms", `${it.labelFadeInMs}ms`);
      root.style.setProperty("--kc-intro-out-ms", `${it.fadeOutMs}ms`);
    }

    async showCrest(fadeMs) {
      if (!this.crest || !this.crestImg) return;
      const image =
        this.bookends?.closing?.image || "assets/images/gold_closing.png";
      this.crestImg.src = this.localUrl(image);
      if (this.crestImg.decode) {
        try {
          await this.crestImg.decode();
        } catch (_) {
          /* optional */
        }
      }
      document.documentElement.style.setProperty(
        "--kc-crest-fade-ms",
        `${fadeMs}ms`
      );
      this.crest.classList.add("is-visible");
      await this.wait(fadeMs);
    }

    async hideCrest(fadeMs) {
      if (!this.crest) return;
      document.documentElement.style.setProperty(
        "--kc-crest-fade-ms",
        `${fadeMs}ms`
      );
      this.crest.classList.remove("is-visible");
      await this.wait(fadeMs);
    }

    async playClosingCrest(runId) {
      const t = this.timing;
      const still = () => this.stillRunning(runId);

      this.hideIntroImmediate();
      this.stage.classList.add("is-leaving");
      this.veil.classList.add("is-dark");
      await this.wait(t.crestBlackBeforeMs ?? t.crossfadeMs);
      if (!still()) return;

      await this.showCrest(t.crestRevealMs);
      if (!still()) return;

      await this.wait(t.crestHoldMs);
      if (!still()) return;

      await this.fadeOutSoundtrack(t.soundtrackFadeMs);
      if (!still()) return;

      await this.hideCrest(t.crestFadeOutMs);
      if (!still()) return;

      await this.wait(t.crestBlackAfterMs);
    }

    async init() {
      const params = new URLSearchParams(location.search);
      const collection = params.get("collection") || "lesson_01_components";
      this.scale = parseTimingScale();
      if (this.scale < 0.5) {
        document.documentElement.classList.add("kml-timing-fast");
      }

      const urls = window.KmlCollectionPaths
        ? window.KmlCollectionPaths.collectionUrls(collection)
        : [
            `./collections/prototypes/${collection}.json`,
            `./collections/${collection}.json`,
          ];

      let data = null;
      let lastErr = null;
      for (const url of urls) {
        try {
          const res = await fetch(url);
          if (!res.ok) throw new Error(`${res.status} ${url}`);
          data = await res.json();
          break;
        } catch (err) {
          lastErr = err;
        }
      }
      if (!data) {
        throw lastErr || new Error("Collection not found");
      }

      this.scenes = data.scenes || [];
      this.families = data.families || {};
      this.soundtrack = data.soundtrack || null;
      this.bookends = data.bookends || null;
      this.skipBookends = params.get("skipBookends") === "1";
      this.timing = scaleTiming(
        { ...DEFAULT_TIMING, ...(data.timing || {}) },
        this.scale
      );
      this.introTiming = scaleTiming(
        { ...DEFAULT_INTRO_TIMING, ...(data.introTiming || {}) },
        this.scale
      );
      this.applyCssVars();
      this.initAudio();

      if (data.display?.hideChrome) {
        this.root.classList.add("is-hide-chrome");
      }
      if (this.chromeLabel && data.title) {
        this.chromeLabel.textContent = data.title;
      }

      document.title = data.title
        ? `${data.title} — KML`
        : "Kanji Components — KML";

      const start = Math.max(0, parseInt(params.get("exhibit") || "0", 10) || 0);
      this.singleExhibit = params.get("singleExhibit") === "1";
      this.loop = data.display?.loop === true;

      this.bindKeys();
      await this.ensureAudioUnlocked();
      await this.startSoundtrack();
      await this.playFrom(start);
    }

    bindKeys() {
      window.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight" || e.key === " ") {
          e.preventDefault();
          this.skipTo(this.index + 1);
        } else if (e.key === "ArrowLeft") {
          e.preventDefault();
          this.skipTo(this.index - 1);
        } else if (e.key === "r" || e.key === "R") {
          this.skipTo(this.index);
        }
      });
    }

    skipTo(index) {
      if (!this.scenes.length) return;
      const count = this.scenes.length;
      let next = index;
      if (next < 0) next = this.loop ? count - 1 : 0;
      if (next >= count) {
        if (this.loop) next = 0;
        else return;
      }
      this.playFrom(next);
    }

    wait(ms) {
      return new Promise((resolve) => {
        const id = this.runId;
        window.setTimeout(() => {
          if (id === this.runId) resolve();
        }, ms);
      });
    }

    stillRunning(runId) {
      return !this.destroyed && this.runId === runId;
    }

    hideIntroImmediate() {
      if (!this.intro) return;
      this.intro.classList.remove("is-active", "is-visible");
      this.introHeading?.classList.remove("is-visible");
      this.introGlyph?.classList.remove("is-visible");
      this.introLabel?.classList.remove("is-visible");
    }

    clearKanjiStage() {
      this.hero.textContent = "";
      this.hero.classList.remove("is-visible");
      this.row.innerHTML = "";
      this.stage.classList.remove("is-leaving", "is-entering", "is-hidden");
    }

    clearStage() {
      this.clearKanjiStage();
      this.hideIntroImmediate();
      this.veil.classList.remove("is-dark");
    }

    buildComponent(part, index) {
      const side = ENTRANCE_SIDES[index % ENTRANCE_SIDES.length];
      const el = document.createElement("div");
      el.className = `kc-component from-${side}`;
      el.dataset.componentIndex = String(index);
      if (part.familyId) el.dataset.familyId = part.familyId;

      const glyph = document.createElement("span");
      glyph.className = "kc-component-kanji";
      glyph.lang = "ja";
      glyph.textContent = partGlyph(part);

      const label = document.createElement("span");
      label.className = "kc-component-keyword";
      label.textContent = partLabel(part);

      el.appendChild(glyph);
      el.appendChild(label);
      return el;
    }

    populateKanji(scene) {
      this.hideIntroImmediate();
      this.clearKanjiStage();
      this.stage.classList.remove("is-hidden");
      this.hero.textContent = scene.kanji || "";
      this.hero.lang = "ja";

      const parts = scene.components || [];
      for (let i = 0; i < parts.length; i++) {
        this.row.appendChild(this.buildComponent(parts[i], i));
      }
    }

    populateIntro(scene) {
      this.clearKanjiStage();
      this.stage.classList.add("is-hidden");
      if (!this.intro) return;

      const isFamily = sceneType(scene) === "newFamily";
      this.intro.dataset.introKind = isFamily ? "family" : "component";
      if (this.introHeading) {
        this.introHeading.textContent = isFamily
          ? "New Family"
          : "New Component";
      }
      if (this.introGlyph) {
        this.introGlyph.textContent = scene.glyph || "";
        this.introGlyph.lang = "ja";
      }
      if (this.introLabel) {
        this.introLabel.textContent = scene.label || "";
      }
      this.introHeading?.classList.remove("is-visible");
      this.introGlyph?.classList.remove("is-visible");
      this.introLabel?.classList.remove("is-visible");
      this.intro.classList.add("is-active");
      this.intro.classList.remove("is-leaving");
    }

    async revealFromBlack(fromBlack, runId) {
      const t = this.timing;
      if (fromBlack) {
        const panel =
          this.stage.classList.contains("is-hidden") && this.intro
            ? this.intro
            : this.stage;
        panel.style.transition = "none";
        panel.classList.add("is-entering");
        void panel.offsetWidth;
        panel.style.transition = "";
        panel.classList.remove("is-entering");
        this.veil.classList.remove("is-dark");
        await this.wait(t.crossfadeMs);
        return this.stillRunning(runId);
      }
      this.stage.classList.remove("is-entering", "is-leaving");
      this.intro?.classList.remove("is-entering", "is-leaving");
      this.veil.classList.remove("is-dark");
      return true;
    }

    async finishOrAdvance(index, scene, runId) {
      const t = this.timing;
      const count = this.scenes.length;

      if (this.singleExhibit) {
        document.dispatchEvent(
          new CustomEvent("kml-components-exhibit-end", {
            detail: { index, sceneId: scene.id, type: sceneType(scene) },
          })
        );
        return;
      }

      const next = index + 1;
      if (next >= count && !this.loop) {
        if (!this.skipBookends && this.bookends?.closing) {
          await this.playClosingCrest(runId);
        } else {
          this.veil.classList.add("is-dark");
          await this.wait(t.crossfadeMs);
          this.stopSoundtrack();
        }
        if (this.stillRunning(runId)) {
          this.presentationEnded = true;
          document.dispatchEvent(new CustomEvent("kml-components-presentation-end"));
        }
        return;
      }

      this.stage.classList.add("is-leaving");
      this.intro?.classList.add("is-leaving");
      this.veil.classList.add("is-dark");
      await this.wait(t.crossfadeMs);
      if (!this.stillRunning(runId)) return;

      await this.wait(t.blackBetweenMs);
      if (!this.stillRunning(runId)) return;

      await this.playExhibit(next % count, runId, { fromBlack: true });
    }

    async playFrom(index) {
      this.runId += 1;
      const runId = this.runId;
      this.index = index;
      this.presentationEnded = false;
      await this.playExhibit(index, runId, { fromBlack: false });
    }

    async playExhibit(index, runId, options = {}) {
      if (!this.stillRunning(runId) || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count) {
        if (this.loop) {
          await this.playExhibit(0, runId, { fromBlack: true });
        }
        return;
      }

      this.index = index;
      const scene = this.scenes[index];
      const type = sceneType(scene);

      if (type === "newComponent" || type === "newFamily") {
        await this.playIntroScene(index, scene, runId, options);
      } else {
        await this.playKanjiScene(index, scene, runId, options);
      }
    }

    async playIntroScene(index, scene, runId, options = {}) {
      const it = this.introTiming;
      const fromBlack = options.fromBlack === true;

      this.populateIntro(scene);
      if (!(await this.revealFromBlack(fromBlack, runId))) return;

      await this.wait(80);
      if (!this.stillRunning(runId)) return;

      // Heading
      this.introHeading?.classList.add("is-visible");
      await this.wait(it.headingFadeInMs);
      if (!this.stillRunning(runId)) return;

      // Glyph
      this.introGlyph?.classList.add("is-visible");
      await this.wait(it.glyphFadeInMs);
      if (!this.stillRunning(runId)) return;

      // Observe shape before naming
      await this.wait(it.glyphAloneHoldMs);
      if (!this.stillRunning(runId)) return;

      // Label
      this.introLabel?.classList.add("is-visible");
      await this.wait(it.labelFadeInMs);
      if (!this.stillRunning(runId)) return;

      // Hold complete exhibit
      await this.wait(it.completeHoldMs);
      if (!this.stillRunning(runId)) return;

      // Soft exit
      document.documentElement.style.setProperty(
        "--kc-intro-out-ms",
        `${it.fadeOutMs}ms`
      );
      this.intro?.classList.add("is-leaving");
      this.introHeading?.classList.remove("is-visible");
      this.introGlyph?.classList.remove("is-visible");
      this.introLabel?.classList.remove("is-visible");
      await this.wait(it.fadeOutMs);
      if (!this.stillRunning(runId)) return;

      this.hideIntroImmediate();
      await this.wait(it.blackAfterMs);
      if (!this.stillRunning(runId)) return;

      await this.finishOrAdvance(index, scene, runId);
    }

    async playKanjiScene(index, scene, runId, options = {}) {
      const t = this.timing;
      const fromBlack = options.fromBlack === true;

      this.populateKanji(scene);
      if (!(await this.revealFromBlack(fromBlack, runId))) return;

      await this.wait(80);
      if (!this.stillRunning(runId)) return;
      this.hero.classList.add("is-visible");
      await this.wait(t.heroFadeInMs);
      if (!this.stillRunning(runId)) return;

      await this.wait(t.afterHeroPauseMs);
      if (!this.stillRunning(runId)) return;

      const cells = [...this.row.querySelectorAll(".kc-component")];
      for (let i = 0; i < cells.length; i++) {
        if (!this.stillRunning(runId)) return;
        cells[i].classList.add("is-visible");
        await this.wait(t.componentArriveMs);
        if (!this.stillRunning(runId)) return;
        if (i < cells.length - 1) {
          await this.wait(
            Math.max(0, t.componentStaggerMs - t.componentArriveMs)
          );
          if (!this.stillRunning(runId)) return;
        }
      }

      await this.wait(t.afterComponentsPauseMs);
      if (!this.stillRunning(runId)) return;

      const labels = [...this.row.querySelectorAll(".kc-component-keyword")];
      document.documentElement.style.setProperty(
        "--kc-keyword-fade-ms",
        `${t.keywordFadeInMs}ms`
      );
      for (const label of labels) label.classList.add("is-visible");
      await this.wait(t.keywordFadeInMs);
      if (!this.stillRunning(runId)) return;

      await this.wait(t.keywordHoldMs);
      if (!this.stillRunning(runId)) return;

      document.documentElement.style.setProperty(
        "--kc-keyword-fade-ms",
        `${t.keywordFadeOutMs}ms`
      );
      for (const label of labels) label.classList.remove("is-visible");
      await this.wait(t.keywordFadeOutMs);
      if (!this.stillRunning(runId)) return;

      await this.wait(t.afterKeywordsPauseMs);
      if (!this.stillRunning(runId)) return;

      for (const cell of cells) {
        cell.classList.add("is-leaving");
        cell.classList.remove("is-visible");
      }
      await this.wait(t.componentsFadeOutMs);
      if (!this.stillRunning(runId)) return;

      await this.wait(t.heroAloneMs);
      if (!this.stillRunning(runId)) return;

      await this.finishOrAdvance(index, scene, runId);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.documentElement.classList.add("kml-typography-kanji-components");
    const root = qs("[data-kc-root]");
    if (!root) return;
    const player = new KanjiComponentsPlayer(root);
    window.KmlKanjiComponentsPlayer = player;
    player.init().catch((err) => {
      console.error(err);
      const stage = qs("[data-kc-stage]");
      if (stage) {
        stage.innerHTML =
          `<p style="color:#c4a052;font-size:1.25rem;text-align:center;padding:2rem">` +
          `Could not load collection.</p>`;
      }
    });
  });
})();
