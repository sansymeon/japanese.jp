/**
 * KML Digital Art Exhibition – gallery presentation engine.
 * Collection-driven; scenes reuse ambient JSON scene format.
 */
(function () {
  "use strict";

  const ENGINE_VERSION = "2026-06-16-mobile-verse-v1";

  const DEFAULTS = {
    artworkArrivalMs: 8000,
    artworkAloneMs: 6000,
    kanjiRevealMs: 5500,
    keywordDelayMs: 4500,
    keywordFadeMs: 4500,
    titleHoldMs: 8000,
    titleFadeMs: 5500,
    verseJpRevealMs: 6500,
    verseEnDelayMs: 9000,
    verseEnFadeMs: 5500,
    reflectionHoldMs: 12000,
    versesFadeMs: 5500,
    verseJpHoldMs: null,
    verseJpFadeMs: null,
    verseEnRevealMs: null,
    verseEnHoldMs: null,
    verseEnFadeMs: null,
    essenceKanjiRevealMs: 2500,
    essenceHoldMs: 0,
    imageExhaleFadeMs: 16000,
    kanjiAloneHoldMs: 9000,
    kanjiExhaleFadeMs: 20000,
    blackHoldMs: 3500,
    exhibitBlackHoldMs: 500,
    kenBurnsDurationMs: 300000,
    openingBlackBeforeMs: 2000,
    openingFluteMs: 16000,
    openingRevealMs: 6000,
    openingHoldMs: 4000,
    openingExhaleMs: 6000,
    openingBlackAfterMs: 0,
    closingRevealMs: 8000,
    closingHoldMs: 14000,
    closingExhaleMs: 22000,
    closingBlackBeforeMs: 3500,
    closingPostSoundtrackHoldMs: 0,
    closingSilenceHoldMs: 5000,
    closingFadeToBlackMs: 12000,
    closingBlackAfterMs: 5000,
  };

  class ExhibitionPlayer {
    constructor(root, collection) {
      this.root = root;
      this.collection = collection;
      this.scenes = collection.scenes || [];
      this.timing = { ...DEFAULTS, ...(collection.exhibition || {}) };
      this.display = { loop: true, showKeyword: true, ...(collection.display || {}) };
      this.bookends = collection.bookends || null;
      this.soundtrack = collection.soundtrack || null;
      this.assetsBase = (collection.assetsBase || "../../assets").replace(/\/$/, "");

      const params = new URLSearchParams(window.location.search);
      this.timingScale = Math.max(0.05, parseFloat(params.get("timingScale") || "1") || 1);
      this.startExhibit = Math.max(0, parseInt(params.get("exhibit") || "0", 10) || 0);
      this.singleExhibit =
        params.get("singleExhibit") === "1" || params.get("exhibitLimit") === "1";
      this.skipBookends = params.get("skipBookends") === "1";
      const startPhase = (params.get("startPhase") || params.get("skipTo") || "")
        .trim()
        .toLowerCase();
      this.startPhase = startPhase;
      this.verseMode =
        params.get("verseMode") || this.display.verseMode || "simultaneous";
      this._cameraParam = params.get("camera");
      this.cameraHistory = [];

      this.sceneIndex = 0;
      this.paused = false;
      this.destroyed = false;
      this.runId = 0;
      this.wakeResolvers = [];
      this.bookendAudio = null;
      this.mainAudio = null;
      this.audioUnlocked = false;
      this.introPlayingFromGate = false;
      this.presentationEnded = false;

      this.presentationEnded = false;
      this.activeArtworkKey = "a";
      this._imageVerseCrossfadedTo = -1;

      this.artworkLayers = {
        a: {
          wrap: root.querySelector('[data-exhibition-artwork="a"]'),
          img: root.querySelector('[data-exhibition-artwork-img="a"]'),
        },
        b: {
          wrap: root.querySelector('[data-exhibition-artwork="b"]'),
          img: root.querySelector('[data-exhibition-artwork-img="b"]'),
        },
      };

      this.els = {
        loading: root.querySelector("[data-exhibition-loading]"),
        error: root.querySelector("[data-exhibition-error]"),
        autoplayGate: root.querySelector("[data-exhibition-autoplay-gate]"),
        veil: root.querySelector("[data-exhibition-veil]"),
        artwork: this.artworkLayers.a.wrap,
        artworkImg: this.artworkLayers.a.img,
        bookend: root.querySelector("[data-exhibition-bookend]"),
        bookendComposition: root.querySelector("[data-exhibition-bookend-composition]"),
        bookendImg: root.querySelector("[data-exhibition-bookend-img]"),
        bookendStamp: root.querySelector("[data-exhibition-bookend-stamp]"),
        bookendTitle: root.querySelector("[data-exhibition-bookend-title]"),
        kanji: root.querySelector("[data-exhibition-kanji]"),
        keyword: root.querySelector("[data-exhibition-keyword]"),
        verseJp: root.querySelector("[data-exhibition-verse-jp]"),
        verseEn: root.querySelector("[data-exhibition-verse-en]"),
      };

      this.applyPresentationMode();
      this.applyTheme();
      this.bindKeys();
      if (this.hasExhibitionAudio()) {
        this.initAudio();
      }
    }

    applyPresentationMode() {
      const params = new URLSearchParams(window.location.search);
      const typo = params.get("typography") || this.display.typography || "";
      const verseMode = params.get("verseMode") || this.display.verseMode || "simultaneous";
      const root = document.documentElement;

      root.classList.toggle("kml-typography-legacy", typo === "legacy");
      root.classList.toggle("kml-typography-mobile", typo === "mobile");
      root.classList.toggle("kml-typography-mobile-refine", typo === "mobile-refine");
      root.classList.toggle("kml-typography-placard", typo === "placard");
      root.classList.toggle("kml-verse-sequential", verseMode === "sequential");
      root.classList.toggle("kml-verse-staggered", verseMode === "staggered");
      root.classList.toggle("kml-verse-authored", this.useAuthoredVerseLayout(typo));

      const family = this.display.family || "";
      const profile = this.display.exhibitProfile || "";
      this.root.classList.toggle("is-japanese-reflections", family === "japaneseReflections");
      this.root.classList.toggle("is-image-verse", profile === "imageVerse");
      this.root.classList.toggle(
        "is-gallery-crest-bookends",
        this.display.bookendStyle === "galleryCrest"
      );
    }

    useAuthoredVerseLayout(typo) {
      const layout = this.display.verseLayout;
      if (layout === "authored") return true;
      if (layout === "legacy") return false;
      const profile = typo ?? new URLSearchParams(window.location.search).get("typography");
      return profile === "mobile-refine";
    }

    formatVerseHtml(html) {
      if (!html) return "";
      if (this.useAuthoredVerseLayout() && window.KmlVerseDisplay) {
        return window.KmlVerseDisplay.formatAuthoredVerseHtml(html);
      }
      if (window.KmlVerseDisplay) {
        return window.KmlVerseDisplay.legacyFormatter(html);
      }
      return html;
    }

    get fixedKanji() {
      return Boolean(this.display.fixedKanji);
    }

    get showKeyword() {
      return this.display.showKeyword !== false;
    }

    get isSequentialVerses() {
      return this.verseMode === "sequential";
    }

    get isStaggeredVerses() {
      return this.verseMode === "staggered";
    }

    get isImageVerseProfile() {
      return this.display.exhibitProfile === "imageVerse";
    }

    syncLegacyArtworkRefs() {
      const layer = this.artworkLayers[this.activeArtworkKey];
      if (!layer) return;
      this.els.artwork = layer.wrap;
      this.els.artworkImg = layer.img;
    }

    imageVerseExhibitDurationMs(t = this.timing) {
      const s = this.sequentialVerseTiming(t);
      return (
        t.artworkAloneMs +
        t.kanjiRevealMs +
        (t.imageVerseKanjiHoldMs ?? 2000) +
        (t.imageVerseKanjiFadeMs ?? t.titleFadeMs ?? 1600) +
        s.verseJpRevealMs +
        s.verseJpHoldMs +
        s.verseJpFadeMs +
        s.verseEnRevealMs +
        s.verseEnHoldMs +
        s.verseEnFadeMs +
        (t.exhibitTransitionMs ?? 4000)
      );
    }

    skipsToReflection(index = this.sceneIndex) {
      if (index !== this.startExhibit) return false;
      return this.startPhase === "reflection" || this.startPhase === "verses";
    }

    preambleUntilVersesMs(t = this.timing) {
      let ms = t.artworkArrivalMs + t.artworkAloneMs + t.kanjiRevealMs;
      if (this.showKeyword) {
        ms += t.keywordDelayMs + t.keywordFadeMs;
      }
      ms += t.titleHoldMs + t.titleFadeMs;
      return ms;
    }

    sequentialVerseTiming(t = this.timing) {
      const holdPool = t.verseEnDelayMs + t.reflectionHoldMs;
      return {
        verseJpRevealMs: t.verseJpRevealMs,
        verseJpHoldMs: t.verseJpHoldMs ?? Math.round(holdPool * 0.42),
        verseJpFadeMs: t.verseJpFadeMs ?? t.titleFadeMs,
        verseEnRevealMs: t.verseEnRevealMs ?? t.verseEnFadeMs,
        verseEnHoldMs: t.verseEnHoldMs ?? holdPool - Math.round(holdPool * 0.42),
        verseEnFadeMs: t.verseEnFadeMs ?? t.versesFadeMs,
      };
    }

    get useGalleryGuardian() {
      if (this._cameraParam === "legacy") return false;
      if (this._cameraParam === "guardian") return true;
      const id = this.collection.id || "";
      const theme = this.collection.meta?.theme;
      return id.startsWith("heart_") || theme === "heart";
    }

    get debug() {
      if (this.display.debug) return true;
      return new URLSearchParams(window.location.search).get("debug") === "1";
    }

    debugLog(label, detail = {}) {
      if (!this.debug) return;
      console.log(`[KML Exhibition] ${label}`, detail);
    }

    audioLog(label, detail = {}) {
      console.log(`[KML Exhibition audio] ${label}`, detail);
    }

    audioError(label, err, detail = {}) {
      console.error(`[KML Exhibition audio] ${label}`, err, detail);
    }

    debugKanjiState(label) {
      if (!this.debug) return;
      const kanji = this.els.kanji;
      const veil = this.els.veil;
      console.log(`[KML Exhibition] ${label}`, {
        engineVersion: ENGINE_VERSION,
        textContent: kanji?.textContent ?? null,
        classList: kanji ? [...kanji.classList] : null,
        opacity: kanji ? getComputedStyle(kanji).opacity : null,
        zIndex: kanji ? getComputedStyle(kanji).zIndex : null,
        veilClear: veil?.classList.contains("is-clear") ?? null,
        veilOpacity: veil ? getComputedStyle(veil).opacity : null,
        veilZIndex: veil ? getComputedStyle(veil).zIndex : null,
      });
    }

    applyTheme() {
      const t = this.timing;
      const root = document.documentElement;
      root.style.setProperty("--ex-fade", `${t.kanjiRevealMs}ms`);
      root.style.setProperty("--ex-keyword-fade", `${t.keywordFadeMs}ms`);
      root.style.setProperty("--ex-exhale", `${t.imageExhaleFadeMs}ms`);
      root.style.setProperty("--ex-kanji-exhale", `${t.kanjiExhaleFadeMs}ms`);
      root.style.setProperty("--ken-burns-duration", `${t.kenBurnsDurationMs}ms`);
      root.style.setProperty("--ex-bookend-fade", `${t.openingRevealMs}ms`);
      root.style.setProperty("--ex-bookend-exhale", `${t.openingExhaleMs}ms`);
      const verseFade = t.titleFadeMs;
      root.style.setProperty("--ex-verse-fade", `${verseFade}ms`);
      if (this.isImageVerseProfile) {
        root.style.setProperty("--ex-transition", `${t.exhibitTransitionMs ?? 4000}ms`);
        root.style.setProperty("--ex-kanji-fade", `${t.imageVerseKanjiFadeMs ?? t.titleFadeMs ?? 1600}ms`);
        root.style.setProperty("--ken-burns-duration", `${t.kenBurnsDurationMs ?? 30000}ms`);
      }
      this.root.classList.toggle("is-fixed-kanji", this.fixedKanji);
      this.root.classList.toggle("is-sequential-verses", this.isSequentialVerses);
      this.root.classList.toggle("is-staggered-verses", this.isStaggeredVerses);
      if (this.els.artworkImg) {
        this.els.artworkImg.style.transition = `opacity ${t.imageExhaleFadeMs}ms ease-in`;
      }
    }

    setKanjiCentered(on) {
      if (this.fixedKanji) {
        this.setClass(this.els.kanji, "is-on-black", on);
        this.setClass(this.els.kanji, "is-floating", false);
      } else {
        this.setClass(this.els.kanji, "is-floating", on);
        this.setClass(this.els.kanji, "is-on-black", false);
      }
    }

    bindKeys() {
      document.addEventListener("keydown", this.onKeyDown = (e) => {
        if (e.code === "Space") {
          e.preventDefault();
          this.togglePause();
        } else if (e.code === "ArrowRight") {
          this.interruptAndNext();
        } else if (e.code === "ArrowLeft") {
          this.interruptAndPrev();
        }
      });
    }

    assetUrl(relative, rev) {
      if (!relative) return "";
      if (/^https?:\/\//.test(relative) || relative.startsWith("/")) return relative;
      const base = `${this.assetsBase}/${relative.replace(/^\//, "")}`;
      return rev != null && rev !== "" ? `${base}?v=${rev}` : base;
    }

    localUrl(relative) {
      if (!relative) return "";
      if (/^https?:\/\//.test(relative) || relative.startsWith("/")) return relative;
      const clean = relative.replace(/^\.\//, "");
      return `./${clean}`;
    }

    bookendImageUrl(relative) {
      if (!relative) return "";
      if (relative.startsWith("bookends/") || relative.startsWith("./bookends/")) {
        return this.localUrl(relative);
      }
      return this.assetUrl(relative);
    }

    clearBookendText() {
      if (this.els.kanji) this.els.kanji.textContent = "";
      if (this.els.keyword) this.els.keyword.textContent = "";
      this.setClass(this.els.kanji, "is-visible", false);
      this.setClass(this.els.kanji, "is-exhaling", false);
      this.setKanjiCentered(false);
      this.setClass(this.els.keyword, "is-visible", false);
    }

    resetBookendLayer() {
      this.setClass(this.els.bookend, "is-visible", false);
      this.setClass(this.els.bookend, "is-exhaling", false);
      this.setClass(this.els.bookend, "is-crest-exhaling", false);
      this.setClass(this.els.bookend, "is-title-visible", false);
      this.setClass(this.els.bookend, "is-title-exhaling", false);
      this.setClass(this.els.bookend, "is-opening-bookend", false);
      this.setClass(this.els.bookend, "is-closing-bookend", false);
      this.setClass(this.els.bookend, "is-bookend-large", false);
      this.setClass(this.els.bookend, "is-bookend-small", false);
      if (this.els.bookendImg) {
        this.els.bookendImg.removeAttribute("src");
        this.els.bookendImg.alt = "";
      }
      this.hideBookendStamp();
      this.hideBookendTitle(false);
    }

    hideBookendTitle(animate = true) {
      const title = this.els.bookendTitle;
      if (!title) return;
      title.innerHTML = "";
      title.classList.add("exhibition-hidden");
      this.setClass(this.els.bookend, "is-title-visible", false);
      this.setClass(this.els.bookend, "is-crest-exhaling", false);
      if (!animate) return;
    }

    async hideBookendCrest(fadeMs) {
      if (!this.els.bookend) return;
      document.documentElement.style.setProperty("--ex-bookend-exhale", `${fadeMs}ms`);
      this.setClass(this.els.bookend, "is-crest-exhaling", true);
      await this.wait(fadeMs);
      if (this.els.bookendImg) {
        this.els.bookendImg.removeAttribute("src");
        this.els.bookendImg.alt = "";
      }
      this.setClass(this.els.bookend, "is-crest-exhaling", false);
      this.hideBookendStamp();
    }

    async showBookendTitle(html, fadeMs) {
      const title = this.els.bookendTitle;
      if (!title || !html) return;
      this.hideBookendStamp();
      title.innerHTML = html;
      title.classList.remove("exhibition-hidden");
      document.documentElement.style.setProperty("--ex-bookend-title-fade", `${fadeMs}ms`);
      this.setClass(this.els.bookend, "is-visible", true);
      this.setClass(this.els.bookend, "is-exhaling", false);
      this.setClass(this.els.bookend, "is-title-visible", true);
      await this.wait(fadeMs);
    }

    async hideBookendTitleFade(fadeMs) {
      if (!this.els.bookend) return;
      document.documentElement.style.setProperty("--ex-bookend-title-fade", `${fadeMs}ms`);
      this.setClass(this.els.bookend, "is-title-exhaling", true);
      await this.wait(fadeMs);
      this.hideBookendTitle(false);
      this.resetBookendLayer();
    }

    hideBookendStamp() {
      const stamp = this.els.bookendStamp;
      if (!stamp) return;
      stamp.removeAttribute("src");
      stamp.alt = "";
      stamp.classList.add("exhibition-hidden");
    }

    applyBookendStamp(bookendConfig, phase) {
      const stamp = this.els.bookendStamp;
      if (!stamp || !bookendConfig?.stamp) {
        this.hideBookendStamp();
        return;
      }
      const showStamp = phase === "opening" || bookendConfig.bookendSize === "large";
      if (!showStamp) {
        this.hideBookendStamp();
        return;
      }
      stamp.src = this.bookendImageUrl(bookendConfig.stamp);
      stamp.alt = "";
      stamp.classList.remove("exhibition-hidden");
    }

    applyBookendPresentation(bookendConfig, phase) {
      if (!this.els.bookend) return;
      const size = bookendConfig?.bookendSize || (phase === "opening" ? "large" : "small");
      this.setClass(this.els.bookend, "is-opening-bookend", phase === "opening");
      this.setClass(this.els.bookend, "is-closing-bookend", phase === "closing");
      this.setClass(this.els.bookend, "is-bookend-large", size === "large");
      this.setClass(this.els.bookend, "is-bookend-small", size === "small");
    }

    async showBookendImage(imagePath, fadeMs, bookendConfig = null, phase = "") {
      if (!this.els.bookend || !this.els.bookendImg || !imagePath) return;
      if (phase) this.applyBookendPresentation(bookendConfig, phase);
      this.applyBookendStamp(bookendConfig, phase);
      const url = this.bookendImageUrl(imagePath);
      document.documentElement.style.setProperty("--ex-bookend-fade", `${fadeMs}ms`);
      this.els.bookendImg.src = url;
      this.els.bookendImg.alt = "";
      await this.wait(50);
      this.setClass(this.els.bookend, "is-exhaling", false);
      this.setClass(this.els.bookend, "is-visible", true);
      await this.wait(fadeMs);
    }

    async hideBookendImage(fadeMs) {
      if (!this.els.bookend) return;
      document.documentElement.style.setProperty("--ex-bookend-exhale", `${fadeMs}ms`);
      this.setClass(this.els.bookend, "is-exhaling", true);
      await this.wait(fadeMs);
      this.resetBookendLayer();
    }

    initAudio() {
      const introPath = this.bookends?.opening?.audio || null;
      const ambientPath = this.soundtrack?.main || null;

      this.bookendAudio = this.mountAudioElement({
        kind: "intro",
        selector: "[data-exhibition-intro-audio]",
        ref: "bookendAudio",
        src: introPath,
      });
      this.mainAudio = this.mountAudioElement({
        kind: "ambient",
        selector: "[data-exhibition-ambient-audio]",
        ref: "mainAudio",
        src: ambientPath,
      });
    }

    mountAudioElement({ kind, selector, src }) {
      let audio = this.root.querySelector(selector);
      if (!audio) {
        audio = document.createElement("audio");
        audio.preload = "auto";
        if (selector.startsWith("[") && selector.endsWith("]")) {
          audio.setAttribute(selector.slice(1, -1), "");
        }
        const host = this.root.querySelector(".exhibition-audio") || this.root;
        host.appendChild(audio);
      }

      audio.dataset.exhibitionAudio = kind;
      if (src) {
        audio.src = this.localUrl(src);
      }

      audio.addEventListener("error", () => {
        this.audioError(`${kind} load error`, audio.error, {
          src: audio.currentSrc || audio.src,
          networkState: audio.networkState,
          readyState: audio.readyState,
        });
      });

      const createdLabel = kind === "intro" ? "intro audio created" : "ambient audio created";
      this.audioLog(createdLabel, {
        element: audio,
        src: audio.currentSrc || audio.src || null,
        inDom: document.contains(audio),
      });

      return audio;
    }

    audioEl(kind = "bookend") {
      if (kind === "main") {
        if (!this.mainAudio) this.initAudio();
        return this.mainAudio;
      }
      if (!this.bookendAudio) this.initAudio();
      return this.bookendAudio;
    }

    hasExhibitionAudio() {
      return Boolean(this.bookends?.opening?.audio || this.soundtrack?.main);
    }

    async ensureAudioUnlocked() {
      if (this.audioUnlocked || !this.hasExhibitionAudio()) return;
      if (!this.bookendAudio && !this.mainAudio) this.initAudio();

      const audio = this.bookendAudio || this.mainAudio;
      if (!audio) return;

      try {
        await audio.play();
        audio.pause();
        audio.currentTime = 0;
        this.audioUnlocked = true;
        this.audioLog("autoplay unlocked", { src: audio.currentSrc || audio.src });
        return;
      } catch (err) {
        if (err.name !== "NotAllowedError") {
          this.audioError("autoplay probe error", err, { src: audio.currentSrc || audio.src });
          return;
        }
      }

      this.audioLog("autoplay blocked, showing gate", {});
      await this.waitForAutoplayGate();
    }

    waitForAutoplayGate() {
      const gate = this.els.autoplayGate;
      if (!gate) {
        this.audioUnlocked = true;
        return Promise.resolve();
      }

      return new Promise((resolve) => {
        let settled = false;
        const finish = async () => {
          if (settled) return;
          settled = true;

          gate.classList.remove("is-visible");
          gate.classList.add("exhibition-hidden");
          gate.removeEventListener("keydown", onKeyDown);

          if (!this.bookendAudio && !this.mainAudio) this.initAudio();
          const audio = this.bookendAudio || this.mainAudio;
          if (audio) {
            try {
              await audio.play();
              audio.pause();
              audio.currentTime = 0;
              this.audioLog("autoplay unlocked", { via: "autoplay gate" });
            } catch (err) {
              this.audioError("autoplay unlock error", err, { via: "autoplay gate" });
            }
          }

          this.audioUnlocked = true;
          resolve();
        };

        const onKeyDown = (e) => {
          if (e.code === "Enter" || e.code === "Space") {
            e.preventDefault();
            finish();
          }
        };

        gate.classList.remove("exhibition-hidden");
        requestAnimationFrame(() => gate.classList.add("is-visible"));
        gate.addEventListener("click", finish, { once: true });
        gate.addEventListener("keydown", onKeyDown);
        gate.focus();
      });
    }

    async waitForAudioEnd(audio, runId = this.runId) {
      if (!audio || audio.ended) return;
      await new Promise((resolve) => {
        let settled = false;
        const done = () => {
          if (settled || runId !== this.runId) return;
          settled = true;
          audio.removeEventListener("ended", done);
          if (audio === this.bookendAudio) {
            this.audioLog("intro ended", { src: audio.currentSrc || audio.src });
          }
          resolve();
        };
        audio.addEventListener("ended", done);
        this.wakeResolvers.push(() => {
          audio.pause();
          done();
        });
      });
    }

    async playAudioUntilEnd(audioPath, { kind = "bookend", maxMs = 0 } = {}) {
      if (!audioPath) return;

      const url = this.localUrl(audioPath);
      const audio = this.audioEl(kind);
      const runId = this.runId;
      const isIntro = kind === "bookend";
      audio.src = url;
      audio.currentTime = 0;
      audio.loop = false;

      try {
        await audio.play();
        if (isIntro) {
          this.audioLog("intro started", { url, maxMs });
        }
        this.debugLog("audio playing", { url, kind, maxMs });
        await new Promise((resolve) => {
          let settled = false;
          const done = (reason) => {
            if (settled || runId !== this.runId) return;
            settled = true;
            audio.removeEventListener("ended", onEnded);
            if (isIntro && reason === "ended") {
              this.audioLog("intro ended", { url });
            }
            resolve();
          };
          const onEnded = () => done("ended");
          audio.addEventListener("ended", onEnded);
          if (maxMs > 0) window.setTimeout(() => done("maxMs"), maxMs);
          this.wakeResolvers.push(() => {
            audio.pause();
            done("interrupted");
          });
        });
      } catch (err) {
        const label = isIntro ? "intro play() error" : "ambient play() error";
        this.audioError(label, err, { url, kind, maxMs });
        if (maxMs > 0) await this.wait(maxMs);
      }
    }

    async playBookendAudio(audioPath, fallbackMs) {
      await this.playAudioUntilEnd(audioPath, { kind: "bookend", maxMs: fallbackMs });
    }

    async startSoundtrack() {
      const path = this.soundtrack?.main;
      if (!path) return;

      const audio = this.audioEl("main");
      if (!audio.paused && audio.src && !audio.ended) return;

      audio.src = this.localUrl(path);
      audio.currentTime = 0;
      audio.loop = false;

      try {
        await audio.play();
        this.debugLog("soundtrack started", { path });
      } catch (err) {
        this.debugLog("soundtrack unavailable", { path, error: err.message });
      }
    }

    async waitForSoundtrackEnd() {
      const audio = this.mainAudio;
      if (!audio || audio.paused || audio.ended) return;
      this.debugLog("waiting for soundtrack end");
      await this.waitForAudioEnd(audio);
    }

    stopBookendAudio() {
      if (this.bookendAudio) {
        this.bookendAudio.pause();
        this.bookendAudio.currentTime = 0;
      }
    }

    stopSoundtrack() {
      if (this.mainAudio) {
        this.mainAudio.pause();
        this.mainAudio.currentTime = 0;
      }
    }

    stopAllAudio() {
      this.stopBookendAudio();
      this.stopSoundtrack();
    }

    setAudioPaused(paused) {
      [this.bookendAudio, this.mainAudio].forEach((audio) => {
        if (!audio || audio.ended) return;
        if (paused) audio.pause();
        else {
          audio.play().catch((err) => {
            this.audioError("resume play() error", err, {
              src: audio.currentSrc || audio.src,
              kind: audio.dataset.exhibitionAudio,
            });
          });
        }
      });
    }

    setClass(el, className, on) {
      if (!el) return;
      el.classList.toggle(className, on);
    }

    resetImageVerseForeground() {
      const { kanji, keyword, verseJp, verseEn } = this.els;
      this.setClass(kanji, "is-visible", false);
      this.setClass(kanji, "is-exhaling", false);
      this.setClass(kanji, "is-floating", false);
      this.setClass(keyword, "is-visible", false);
      this.setClass(verseJp, "is-visible", false);
      this.setClass(verseEn, "is-visible", false);
    }

    populateVerseContent(scene) {
      if (this.els.kanji) this.els.kanji.textContent = scene.kanji || "";
      if (this.els.keyword) this.els.keyword.textContent = scene.keyword || "";
      if (this.els.verseJp) {
        const raw = scene.verse?.jpHtml || scene.verse?.jp || "";
        this.els.verseJp.lang = "ja";
        this.els.verseJp.innerHTML = this.formatVerseHtml(raw);
        const authored =
          this.useAuthoredVerseLayout() &&
          window.KmlVerseDisplay?.usesAuthoredLines(raw);
        this.els.verseJp.classList.toggle("has-authored-lines", Boolean(authored));
      }
      if (this.els.verseEn) {
        this.els.verseEn.textContent = scene.verse?.en || "";
      }
    }

    populateArtworkLayer(key, scene) {
      const layer = this.artworkLayers[key];
      if (!layer?.img || !scene) return;
      const src = this.assetUrl(scene.image, scene.imageRev);
      layer.img.classList.remove("ken-burns", "gallery-guardian");
      layer.img.removeAttribute("data-gallery-shot");
      layer.img.src = src;
      layer.img.alt = scene.kanji || "";
      this.applyImageFraming(layer.img, scene);
    }

    async crossfadeArtworkLayers(nextScene, fadeMs) {
      const inactiveKey = this.activeArtworkKey === "a" ? "b" : "a";
      const activeKey = this.activeArtworkKey;
      const inactive = this.artworkLayers[inactiveKey];
      const active = this.artworkLayers[activeKey];
      if (!inactive?.wrap || !active?.wrap) return;

      this.populateArtworkLayer(inactiveKey, nextScene);
      await this.applySceneCameraToImage(inactive.img, nextScene);

      document.documentElement.style.setProperty("--ex-transition", `${fadeMs}ms`);
      this.setClass(inactive.wrap, "is-exhaling", false);
      this.setClass(inactive.wrap, "is-on-top", true);
      this.setClass(inactive.wrap, "is-visible", true);
      this.setClass(active.wrap, "is-exhaling", true);

      await this.wait(fadeMs);

      this.setClass(active.wrap, "is-visible", false);
      this.setClass(active.wrap, "is-exhaling", false);
      this.setClass(inactive.wrap, "is-on-top", false);
      this.activeArtworkKey = inactiveKey;
      this.syncLegacyArtworkRefs();
    }

    resetLayers() {
      const { veil, artwork, kanji, keyword, verseJp, verseEn } = this.els;
      this.setClass(veil, "is-clear", false);
      this.setClass(artwork, "is-visible", false);
      this.setClass(artwork, "is-exhaling", false);
      this.setClass(kanji, "is-visible", false);
      this.setClass(kanji, "is-exhaling", false);
      this.setClass(kanji, "is-floating", false);
      this.setClass(kanji, "is-on-black", false);
      this.setClass(keyword, "is-visible", false);
      this.setClass(verseJp, "is-visible", false);
      this.setClass(verseEn, "is-visible", false);
      this.resetBookendLayer();
    }

    applyImageFraming(img, scene) {
      if (scene.imageFocus) {
        img.style.objectPosition = scene.imageFocus;
        img.style.setProperty("--image-transform-origin", scene.imageFocus);
      } else {
        img.style.removeProperty("object-position");
        img.style.setProperty("--image-transform-origin", "center center");
      }
      if (this.useGalleryGuardian) {
        img.style.setProperty("--image-scale", "1");
      } else if (scene.imageScale) {
        img.style.setProperty("--image-scale", String(scene.imageScale));
      } else {
        img.style.setProperty("--image-scale", "1");
      }
    }

    exhibitDurationMs(t = this.timing) {
      let ms =
        t.artworkArrivalMs +
        t.artworkAloneMs +
        t.kanjiRevealMs +
        t.keywordDelayMs +
        t.titleHoldMs +
        t.titleFadeMs +
        t.essenceKanjiRevealMs +
        (t.essenceHoldMs || 0) +
        t.imageExhaleFadeMs +
        t.kanjiAloneHoldMs +
        t.kanjiExhaleFadeMs;
      if (this.showKeyword) {
        ms += t.keywordFadeMs;
      }
      if (this.isSequentialVerses) {
        const s = this.sequentialVerseTiming(t);
        ms +=
          s.verseJpRevealMs +
          s.verseJpHoldMs +
          s.verseJpFadeMs +
          s.verseEnRevealMs +
          s.verseEnHoldMs +
          s.verseEnFadeMs;
      } else {
        ms +=
          t.verseJpRevealMs +
          t.verseEnDelayMs +
          t.verseEnFadeMs +
          t.reflectionHoldMs +
          t.versesFadeMs;
      }
      return ms;
    }

    async waitForArtworkImage(img) {
      if (!img) return;
      if (img.complete && img.naturalWidth > 0) return;
      await new Promise((resolve) => {
        img.addEventListener("load", resolve, { once: true });
        img.addEventListener("error", resolve, { once: true });
      });
    }

    async applySceneCameraToImage(img, scene) {
      if (!img?.src) return;

      img.classList.remove("ken-burns", "gallery-guardian");
      await this.waitForArtworkImage(img);

      if (this.useGalleryGuardian && window.GalleryGuardian) {
        const aspectRatio =
          img.naturalWidth > 0 ? img.naturalWidth / img.naturalHeight : 0.75;
        const coverBoost = window.GalleryGuardian.measureCoverBoost(img);
        const durationMs = Math.round(
          (this.isImageVerseProfile
            ? this.imageVerseExhibitDurationMs()
            : this.exhibitDurationMs()) * this.timingScale
        );
        const plan = window.GalleryGuardian.plan(scene, {
          sceneIndex: this.sceneIndex,
          history: this.cameraHistory,
          aspectRatio,
          framingScale: 1,
          durationMs,
          coverBoost,
        });
        this.cameraHistory.push(plan);
        if (this.cameraHistory.length > 6) {
          this.cameraHistory.shift();
        }
        window.GalleryGuardian.applyToImage(img, plan);
        this.debugLog("gallery guardian", {
          scene: scene.id,
          kanji: scene.kanji,
          shot: plan.shot,
          coverBoost: plan.coverBoost,
          scaleFrom: plan.scaleFrom,
          scaleTo: plan.scaleTo,
          durationMs: plan.durationMs,
        });
        return;
      }

      img.classList.add("ken-burns");
    }

    async applySceneCamera(scene) {
      return this.applySceneCameraToImage(this.els.artworkImg, scene);
    }

    populateScene(scene) {
      this.populateArtworkLayer(this.activeArtworkKey, scene);
      this.syncLegacyArtworkRefs();
      this.populateVerseContent(scene);
    }

    async playImageVerseExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const s = this.sequentialVerseTiming();
      const kanjiHoldMs = t.imageVerseKanjiHoldMs ?? 2000;
      const kanjiFadeMs = t.imageVerseKanjiFadeMs ?? t.titleFadeMs ?? 1600;
      const transitionMs = t.exhibitTransitionMs ?? 4000;
      const skippedCrossfade = this._imageVerseCrossfadedTo === index;
      this._imageVerseCrossfadedTo = -1;

      this.resetImageVerseForeground();
      this.populateVerseContent(scene);

      if (!skippedCrossfade) {
        const layer = this.artworkLayers[this.activeArtworkKey];
        this.populateArtworkLayer(this.activeArtworkKey, scene);
        this.syncLegacyArtworkRefs();
        await this.applySceneCameraToImage(layer.img, scene);
        if (!stillRunning()) return;

        this.setClass(this.els.veil, "is-clear", true);
        this.setClass(layer.wrap, "is-exhaling", false);
        this.setClass(layer.wrap, "is-on-top", true);
        this.setClass(layer.wrap, "is-visible", true);
        await this.wait(t.artworkArrivalMs + t.artworkAloneMs);
        if (!stillRunning()) return;
      } else {
        await this.wait(t.artworkAloneMs);
        if (!stillRunning()) return;
      }

      this.setClass(this.els.kanji, "is-visible", true);
      await this.wait(t.kanjiRevealMs);
      if (!stillRunning()) return;
      await this.wait(kanjiHoldMs);
      if (!stillRunning()) return;
      this.setClass(this.els.kanji, "is-visible", false);
      await this.wait(kanjiFadeMs);
      if (!stillRunning()) return;

      this.setClass(this.els.verseJp, "is-visible", true);
      await this.wait(s.verseJpRevealMs);
      if (!stillRunning()) return;
      await this.wait(s.verseJpHoldMs);
      if (!stillRunning()) return;
      this.setClass(this.els.verseJp, "is-visible", false);
      await this.wait(s.verseJpFadeMs);
      if (!stillRunning()) return;

      this.setClass(this.els.verseEn, "is-visible", true);
      await this.wait(s.verseEnRevealMs);
      if (!stillRunning()) return;
      await this.wait(s.verseEnHoldMs);
      if (!stillRunning()) return;
      this.setClass(this.els.verseEn, "is-visible", false);
      await this.wait(s.verseEnFadeMs);
      if (!stillRunning()) return;

      if (this.singleExhibit) {
        document.dispatchEvent(
          new CustomEvent("kml-exhibition-exhibit-end", {
            detail: { index: this.sceneIndex, sceneId: scene.id },
          })
        );
        return;
      }

      const next = this.sceneIndex + 1;
      if (next >= count) {
        if (this.display.loop) {
          if (this.bookends?.opening) {
            await this.playOpeningBookend();
            if (!stillRunning()) return;
          }
          this._imageVerseCrossfadedTo = -1;
          this.activeArtworkKey = "a";
          this.syncLegacyArtworkRefs();
          await this.playImageVerseExhibit(0);
        } else if (this.bookends?.closing) {
          await this.playClosingBookend();
        }
        return;
      }

      const nextScene = this.scenes[next];
      await this.crossfadeArtworkLayers(nextScene, transitionMs);
      if (!stillRunning()) return;
      this._imageVerseCrossfadedTo = next;
      await this.playImageVerseExhibit(next);
    }

    wait(ms) {
      const runId = this.runId;
      const delay = Math.max(0, Math.round(ms * this.timingScale));
      return new Promise((resolve) => {
        const id = window.setTimeout(() => {
          if (!this.destroyed && runId === this.runId) resolve();
        }, delay);
        this.wakeResolvers.push(() => clearTimeout(id));
      });
    }

    clearRun() {
      this.runId += 1;
      this.wakeResolvers.forEach((fn) => fn());
      this.wakeResolvers = [];
    }

    togglePause() {
      this.paused = !this.paused;
      this.root.classList.toggle("is-paused", this.paused);
      this.setAudioPaused(this.paused);
    }

    interruptAndNext() {
      this.clearRun();
      this.playExhibit(this.sceneIndex + 1);
    }

    interruptAndPrev() {
      this.clearRun();
      this.playExhibit(this.sceneIndex - 1);
    }

    async playOpeningBookend() {
      const opening = this.bookends?.opening;
      if (!opening) return;

      if (this.display.bookendStyle === "galleryCrest" && opening.image) {
        await this.playGalleryCrestOpeningBookend(opening);
        return;
      }

      if (opening.image) {
        await this.playOpeningImageBookend(opening);
        return;
      }

      await this.playOpeningKanjiBookend(opening);
    }

    async playGalleryCrestOpeningBookend(opening) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;
      const holdUntilAudioEnds = Boolean(opening.audio && opening.holdUntilAudioEnds);

      this.debugLog("enter playGalleryCrestOpeningBookend", {
        image: opening.image,
        audio: opening.audio,
      });
      this.resetLayers();
      this.clearBookendText();
      this.hideBookendTitle(false);

      await this.wait(t.openingBlackBeforeMs);
      if (!stillRunning()) return;

      let introAudio = null;
      if (opening.audio && holdUntilAudioEnds) {
        if (this.introPlayingFromGate) {
          this.introPlayingFromGate = false;
          introAudio = this.waitForAudioEnd(this.bookendAudio, runId);
        } else {
          introAudio = this.playAudioUntilEnd(opening.audio, { kind: "bookend" });
        }
      } else if (opening.audio) {
        this.playAudioUntilEnd(opening.audio, {
          kind: "bookend",
          maxMs: t.openingFluteMs,
        });
      }

      await this.showBookendImage(opening.image, t.openingRevealMs, opening, "opening");
      if (!stillRunning()) return;

      if (introAudio) {
        await introAudio;
        if (!stillRunning()) return;
      } else {
        await this.wait(t.openingHoldMs);
        if (!stillRunning()) return;
        this.stopBookendAudio();
      }

      await this.hideBookendImage(t.openingExhaleMs);
      if (!stillRunning()) return;

      this.setClass(this.els.veil, "is-corridor", true);
      this.setClass(this.els.veil, "is-clear", false);
      const blackMs = t.openingBlackAfterMs ?? 1200;
      if (blackMs > 0) {
        await this.wait(blackMs);
        if (!stillRunning()) return;
      }

      await this.startSoundtrack();
      this.debugLog("exit playGalleryCrestOpeningBookend");
    }

    async playClosingBookend() {
      const closing = this.bookends?.closing;
      if (!closing) return;

      if (this.display.bookendStyle === "galleryCrest" && closing.image) {
        await this.playGalleryCrestClosingBookend(closing);
        return;
      }

      if (closing.image) {
        await this.playClosingImageBookend(closing);
        return;
      }

      await this.playClosingKanjiBookend(closing);
    }

    async playGalleryCrestClosingBookend(closing) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;
      const holdUntilSoundtrackEnds = Boolean(
        this.soundtrack?.main && closing.holdUntilSoundtrackEnds !== false
      );
      const crestFadeMs = t.closingExhaleMs ?? t.closingFadeToBlackMs ?? 3000;
      const titleRevealMs = t.closingTitleRevealMs ?? 2500;
      const titleFadeMs = t.closingTitleFadeMs ?? t.closingFadeToBlackMs ?? 3000;

      this.debugLog("enter playGalleryCrestClosingBookend", {
        image: closing.image,
        holdUntilSoundtrackEnds,
        titleHtml: closing.titleHtml,
      });
      this.resetLayers();
      this.clearBookendText();
      this.hideBookendTitle(false);

      await this.wait(t.closingBlackBeforeMs ?? t.blackHoldMs);
      if (!stillRunning()) return;

      await this.showBookendImage(closing.image, t.closingRevealMs, closing, "closing");
      if (!stillRunning()) return;

      if (holdUntilSoundtrackEnds) {
        await this.waitForSoundtrackEnd();
        if (!stillRunning()) return;
      } else {
        await this.wait(t.closingHoldMs);
        if (!stillRunning()) return;
      }

      await this.hideBookendCrest(crestFadeMs);
      if (!stillRunning()) return;

      let outroAudio = null;
      if (closing.audio) {
        outroAudio = this.playAudioUntilEnd(closing.audio, { kind: "bookend" });
      }

      if (closing.titleHtml) {
        await this.showBookendTitle(closing.titleHtml, titleRevealMs);
        if (!stillRunning()) return;
      }

      if (outroAudio) {
        await outroAudio;
        if (!stillRunning()) return;
      } else if (closing.titleHtml) {
        await this.wait(t.closingSilenceHoldMs ?? 2000);
        if (!stillRunning()) return;
      }

      await this.hideBookendTitleFade(titleFadeMs);
      if (!stillRunning()) return;

      await this.wait(t.closingBlackAfterMs ?? 0);
      this.stopAllAudio();
      this.finishPresentation();
      this.debugLog("exit playGalleryCrestClosingBookend");
    }

    async playOpeningImageBookend(opening) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;
      const holdUntilAudioEnds = Boolean(opening.audio && opening.holdUntilAudioEnds);

      this.debugLog("enter playOpeningImageBookend", {
        image: opening.image,
        audio: opening.audio,
        holdUntilAudioEnds,
      });
      this.resetLayers();
      this.clearBookendText();

      await this.wait(t.openingBlackBeforeMs);
      if (!stillRunning()) return;

      if (holdUntilAudioEnds) {
        let introAudio;
        if (this.introPlayingFromGate) {
          this.introPlayingFromGate = false;
          introAudio = this.waitForAudioEnd(this.bookendAudio, runId);
        } else {
          introAudio = this.playAudioUntilEnd(opening.audio, { kind: "bookend" });
        }
        await this.showBookendImage(opening.image, t.openingRevealMs, opening, "opening");
        if (!stillRunning()) return;
        await introAudio;
        if (!stillRunning()) return;
      } else {
        const fluteMs = t.openingFluteMs;
        if (opening.audio) {
          this.playAudioUntilEnd(opening.audio, { kind: "bookend", maxMs: fluteMs });
          this.debugLog("opening flute started with artwork fade-in", { fluteMs });
        }
        await this.showBookendImage(opening.image, t.openingRevealMs, opening, "opening");
        if (!stillRunning()) return;
        await this.wait(t.openingHoldMs);
        if (!stillRunning()) return;
        this.stopBookendAudio();
      }

      await this.hideBookendImage(t.openingExhaleMs);
      if (!stillRunning()) return;

      const afterMs = t.openingBlackAfterMs ?? 0;
      if (afterMs > 0) await this.wait(afterMs);
      if (!stillRunning()) return;

      await this.startSoundtrack();
      this.debugLog("exit playOpeningImageBookend");
    }

    async playOpeningKanjiBookend(opening) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;
      const kanji = opening.kanji || "心";

      this.debugLog("enter playOpeningKanjiBookend", { kanji });
      this.resetLayers();
      if (this.els.kanji) this.els.kanji.textContent = kanji;
      if (this.els.keyword) this.els.keyword.textContent = "";

      await this.wait(t.openingBlackBeforeMs);
      if (!stillRunning()) return;

      this.setKanjiCentered(true);
      this.setClass(this.els.kanji, "is-visible", true);
      await this.wait(t.openingRevealMs + t.openingHoldMs);
      if (!stillRunning()) return;

      this.setClass(this.els.kanji, "is-exhaling", true);
      await this.wait(t.openingExhaleMs);
      if (!stillRunning()) return;

      this.setClass(this.els.kanji, "is-visible", false);
      this.setClass(this.els.kanji, "is-exhaling", false);
      this.setKanjiCentered(false);
      await this.wait(t.blackHoldMs);
    }

    async playClosingImageBookend(closing) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;
      const holdUntilSoundtrackEnds = Boolean(
        this.soundtrack?.main && closing.holdUntilSoundtrackEnds !== false
      );

      this.debugLog("enter playClosingImageBookend", {
        image: closing.image,
        holdUntilSoundtrackEnds,
      });
      this.resetLayers();
      this.clearBookendText();

      await this.wait(t.closingBlackBeforeMs ?? t.blackHoldMs);
      if (!stillRunning()) return;

      await this.showBookendImage(closing.image, t.closingRevealMs, closing, "closing");
      if (!stillRunning()) return;

      if (holdUntilSoundtrackEnds) {
        await this.waitForSoundtrackEnd();
        if (!stillRunning()) return;
      } else {
        await this.wait(t.closingHoldMs);
        if (!stillRunning()) return;
      }

      if (closing.audio) {
        await this.playAudioUntilEnd(closing.audio, { kind: "bookend" });
        if (!stillRunning()) return;
      } else {
        const postSoundtrackMs = t.closingPostSoundtrackHoldMs ?? 0;
        if (postSoundtrackMs > 0) {
          await this.wait(postSoundtrackMs);
          if (!stillRunning()) return;
        }
      }

      const silenceMs = t.closingSilenceHoldMs ?? 5000;
      await this.wait(silenceMs);
      if (!stillRunning()) return;

      const fadeMs = t.closingFadeToBlackMs ?? t.closingExhaleMs;
      await this.hideBookendImage(fadeMs);
      if (!stillRunning()) return;
      await this.wait(t.closingBlackAfterMs);
      this.stopAllAudio();
      this.finishPresentation();
      this.debugLog("exit playClosingImageBookend");
    }

    finishPresentation() {
      if (this.presentationEnded) return;
      this.presentationEnded = true;
      this.paused = true;
      this.clearRun();
      document.dispatchEvent(
        new CustomEvent("kml-exhibition-presentation-end", {
          detail: { collection: this.collection.id },
        })
      );
    }

    async playClosingKanjiBookend(closing) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;
      const kanji = closing.kanji || "心";

      this.resetLayers();
      if (this.els.kanji) this.els.kanji.textContent = kanji;
      if (this.els.keyword) this.els.keyword.textContent = "";

      await this.wait(t.blackHoldMs);
      if (!stillRunning()) return;

      this.setKanjiCentered(true);
      this.setClass(this.els.kanji, "is-visible", true);
      await this.wait(t.closingRevealMs + t.closingHoldMs);
      if (!stillRunning()) return;

      this.setClass(this.els.kanji, "is-exhaling", true);
      await this.wait(t.closingExhaleMs);
      if (!stillRunning()) return;

      this.setClass(this.els.kanji, "is-visible", false);
      this.setClass(this.els.kanji, "is-exhaling", false);
      this.setKanjiCentered(false);
      await this.wait(t.closingBlackAfterMs);
      this.stopAllAudio();
      this.finishPresentation();
    }

    async playSequentialVerses(stillRunning) {
      const s = this.sequentialVerseTiming();

      this.setClass(this.els.verseJp, "is-visible", true);
      await this.wait(s.verseJpRevealMs);
      if (!stillRunning()) return;
      await this.wait(s.verseJpHoldMs);
      if (!stillRunning()) return;
      this.setClass(this.els.verseJp, "is-visible", false);
      await this.wait(s.verseJpFadeMs);
      if (!stillRunning()) return;

      this.setClass(this.els.verseEn, "is-visible", true);
      await this.wait(s.verseEnRevealMs);
      if (!stillRunning()) return;
      await this.wait(s.verseEnHoldMs);
      if (!stillRunning()) return;
      this.setClass(this.els.verseEn, "is-visible", false);
      await this.wait(s.verseEnFadeMs);
      if (!stillRunning()) return;
    }

    async playStaggeredVerses(stillRunning) {
      const t = this.timing;
      this.debugLog("reflection: staggered verses", {
        verseJpRevealMs: t.verseJpRevealMs,
        verseEnDelayMs: t.verseEnDelayMs,
      });
      this.setClass(this.els.verseJp, "is-visible", true);
      await this.wait(t.verseJpRevealMs + t.verseEnDelayMs);
      if (!stillRunning()) return;
      this.setClass(this.els.verseEn, "is-visible", true);
      await this.wait(t.verseEnFadeMs + t.reflectionHoldMs);
      if (!stillRunning()) return;
      this.setClass(this.els.verseJp, "is-visible", false);
      this.setClass(this.els.verseEn, "is-visible", false);
      await this.wait(t.versesFadeMs);
      if (!stillRunning()) return;
    }

    async playReflectionPhase(stillRunning) {
      if (this.isSequentialVerses) {
        await this.playSequentialVerses(stillRunning);
        return;
      }
      await this.playStaggeredVerses(stillRunning);
    }

    async playExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;
      if (this.isImageVerseProfile) {
        return this.playImageVerseExhibit(index);
      }

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;

      this.resetLayers();
      this.populateScene(scene);
      await this.applySceneCamera(scene);
      if (!stillRunning()) return;

      const jumpToReflection = this.skipsToReflection(this.sceneIndex);

      if (jumpToReflection) {
        this.debugLog("startPhase skip → reflection", {
          startPhase: this.startPhase,
          sceneId: scene.id,
          verseMode: this.verseMode,
        });
        this.setClass(this.els.veil, "is-clear", true);
        this.setClass(this.els.artwork, "is-visible", true);
      } else {
        // ── 1. Artwork arrival from black ──
        this.setClass(this.els.veil, "is-corridor", false);
        this.setClass(this.els.veil, "is-clear", true);
        await this.wait(80);
        if (!stillRunning()) return;
        this.setClass(this.els.artwork, "is-visible", true);
        await this.wait(t.artworkArrivalMs + t.artworkAloneMs);
        if (!stillRunning()) return;

        // ── 2. Kanji reveal, then keyword (exhibit title) ──
        this.setClass(this.els.kanji, "is-visible", true);
        await this.wait(t.kanjiRevealMs);
        if (!stillRunning()) return;

        if (this.showKeyword && scene.keyword) {
          await this.wait(t.keywordDelayMs);
          if (!stillRunning()) return;
          this.setClass(this.els.keyword, "is-visible", true);
          await this.wait(t.keywordFadeMs + t.titleHoldMs);
          if (!stillRunning()) return;
        } else {
          await this.wait(t.keywordDelayMs + t.titleHoldMs);
          if (!stillRunning()) return;
        }

        // ── 3. Reflection — title fades, curator's notes ──
        this.setClass(this.els.kanji, "is-visible", false);
        this.setClass(this.els.keyword, "is-visible", false);
        await this.wait(t.titleFadeMs);
        if (!stillRunning()) return;
      }

      await this.playReflectionPhase(stillRunning);

      // ── 4. Return to essence — kanji alone ──
      this.setClass(this.els.verseJp, "is-visible", false);
      this.setClass(this.els.verseEn, "is-visible", false);
      this.setClass(this.els.kanji, "is-visible", true);
      await this.wait(t.essenceKanjiRevealMs);
      if (!stillRunning()) return;
      if (t.essenceHoldMs > 0) {
        await this.wait(t.essenceHoldMs);
        if (!stillRunning()) return;
      }

      // ── 5. Long exhale — artwork fades, kanji on black, then kanji fades ──
      this.setKanjiCentered(true);
      this.setClass(this.els.artwork, "is-exhaling", true);
      await this.wait(t.imageExhaleFadeMs + t.kanjiAloneHoldMs);
      if (!stillRunning()) return;
      this.setClass(this.els.kanji, "is-exhaling", true);
      await this.wait(t.kanjiExhaleFadeMs);
      if (!stillRunning()) return;

      // Black corridor between exhibits (post-kanji; kanji-on-black beat is kanjiAloneHoldMs above)
      this.setClass(this.els.veil, "is-corridor", true);
      this.setClass(this.els.veil, "is-clear", false);
      this.setClass(this.els.artwork, "is-visible", false);
      this.setClass(this.els.artwork, "is-exhaling", false);
      this.setClass(this.els.kanji, "is-visible", false);
      this.setClass(this.els.kanji, "is-exhaling", false);
      this.setKanjiCentered(false);
      await this.wait(t.exhibitBlackHoldMs ?? t.blackHoldMs);
      if (!stillRunning()) return;

      if (this.singleExhibit) {
        document.dispatchEvent(
          new CustomEvent("kml-exhibition-exhibit-end", {
            detail: { index: this.sceneIndex, sceneId: scene.id },
          })
        );
        return;
      }

      // ── 6. Next exhibit, loop, or closing bookend ──
      const next = this.sceneIndex + 1;

      if (next >= count) {
        if (this.display.loop) {
          if (this.bookends?.opening) {
            await this.playOpeningBookend();
            if (!stillRunning()) return;
          }
          this.playExhibit(0);
        } else if (this.bookends?.closing) {
          await this.playClosingBookend();
        }
        return;
      }

      this.playExhibit(next);
    }

    async start() {
      if (!this.scenes.length) throw new Error("Collection has no scenes.");
      const preambleMs = Math.round(this.preambleUntilVersesMs() * this.timingScale);
      this.debugLog("start", {
        engineVersion: ENGINE_VERSION,
        collection: this.collection.id,
        hasOpeningBookend: Boolean(this.bookends?.opening),
        firstScene: this.scenes[0]?.kanji,
        startExhibit: this.startExhibit,
        singleExhibit: this.singleExhibit,
        startPhase: this.startPhase || "full",
        verseMode: this.verseMode,
        timingScale: this.timingScale,
        msUntilVerses: this.skipsToReflection(this.startExhibit) ? 0 : preambleMs,
      });
      this.els.loading?.classList.add("exhibition-hidden");
      this.els.error?.classList.add("exhibition-hidden");
      if (!this.skipBookends) {
        await this.ensureAudioUnlocked();
      }
      if (this.destroyed) return;
      if (!this.skipBookends && this.bookends?.opening) {
        await this.playOpeningBookend();
        if (this.destroyed) return;
        this.debugLog("opening bookend complete, starting playExhibit(0)");
      }
      const startAt = Math.min(
        Math.max(0, this.startExhibit),
        Math.max(0, this.scenes.length - 1)
      );
      await this.playExhibit(startAt);
    }

    destroy() {
      this.destroyed = true;
      this.clearRun();
      this.stopAllAudio();
      document.removeEventListener("keydown", this.onKeyDown);
    }
  }

  async function loadCollection(name) {
    const url = `./collections/${name}.json`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Could not load collection "${name}" (${res.status}).`);
    return res.json();
  }

  function collectionFromQuery() {
    const params = new URLSearchParams(window.location.search);
    return params.get("collection") || "heart_v5";
  }

  async function boot() {
    const root = document.querySelector("[data-exhibition-root]");
    if (!root) return;

    const loading = root.querySelector("[data-exhibition-loading]");
    const errorEl = root.querySelector("[data-exhibition-error]");
    const name = collectionFromQuery();

    try {
      const collection = await loadCollection(name);
      if (new URLSearchParams(window.location.search).get("debug") === "1") {
        console.log("[KML Exhibition] boot", { engineVersion: ENGINE_VERSION, collection: name });
      }
      const player = new ExhibitionPlayer(root, collection);
      window.kmlExhibition = player;
      await player.start();
    } catch (err) {
      loading?.classList.add("exhibition-hidden");
      if (errorEl) {
        errorEl.textContent = err.message || String(err);
        errorEl.classList.remove("exhibition-hidden");
      } else {
        console.error(err);
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
