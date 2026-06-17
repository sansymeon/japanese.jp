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
      this.singleExhibit = params.get("singleExhibit") === "1";
      this.skipBookends = params.get("skipBookends") === "1";
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

      this.els = {
        loading: root.querySelector("[data-exhibition-loading]"),
        error: root.querySelector("[data-exhibition-error]"),
        autoplayGate: root.querySelector("[data-exhibition-autoplay-gate]"),
        veil: root.querySelector("[data-exhibition-veil]"),
        artwork: root.querySelector("[data-exhibition-artwork]"),
        artworkImg: root.querySelector("[data-exhibition-artwork-img]"),
        bookend: root.querySelector("[data-exhibition-bookend]"),
        bookendImg: root.querySelector("[data-exhibition-bookend-img]"),
        kanji: root.querySelector("[data-exhibition-kanji]"),
        keyword: root.querySelector("[data-exhibition-keyword]"),
        verseJp: root.querySelector("[data-exhibition-verse-jp]"),
        verseEn: root.querySelector("[data-exhibition-verse-en]"),
      };

      this.applyPresentationMode();
      this.applyTheme();
      this.bindKeys();
    }

    applyPresentationMode() {
      const params = new URLSearchParams(window.location.search);
      const typo = params.get("typography") || this.display.typography || "";
      const verseMode = params.get("verseMode") || this.display.verseMode || "simultaneous";
      const root = document.documentElement;

      root.classList.toggle("kml-typography-legacy", typo === "legacy");
      root.classList.toggle("kml-typography-mobile", typo === "mobile");
      root.classList.toggle("kml-typography-mobile-refine", typo === "mobile-refine");
      root.classList.toggle("kml-verse-sequential", verseMode === "sequential");
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
      this.root.classList.toggle("is-fixed-kanji", this.fixedKanji);
      this.root.classList.toggle("is-sequential-verses", this.isSequentialVerses);
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

    assetUrl(relative) {
      if (!relative) return "";
      if (/^https?:\/\//.test(relative) || relative.startsWith("/")) return relative;
      return `${this.assetsBase}/${relative.replace(/^\//, "")}`;
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
      if (this.els.bookendImg) {
        this.els.bookendImg.removeAttribute("src");
        this.els.bookendImg.alt = "";
      }
    }

    async showBookendImage(imagePath, fadeMs) {
      if (!this.els.bookend || !this.els.bookendImg || !imagePath) return;
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

          const introPath = this.bookends?.opening?.audio;
          const audio = this.bookendAudio;
          if (introPath && audio) {
            const url = this.localUrl(introPath);
            audio.src = url;
            audio.currentTime = 0;
            audio.loop = false;
            try {
              await audio.play();
              this.introPlayingFromGate = true;
              this.audioLog("intro started", { url, via: "autoplay gate" });
            } catch (err) {
              this.audioError("intro play() error", err, { url, via: "autoplay gate" });
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

    async applySceneCamera(scene) {
      const img = this.els.artworkImg;
      if (!img?.src) return;

      img.classList.remove("ken-burns", "gallery-guardian");
      await this.waitForArtworkImage(img);

      if (this.useGalleryGuardian && window.GalleryGuardian) {
        const aspectRatio =
          img.naturalWidth > 0 ? img.naturalWidth / img.naturalHeight : 0.75;
        const coverBoost = window.GalleryGuardian.measureCoverBoost(img);
        const durationMs = Math.round(this.exhibitDurationMs() * this.timingScale);
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

    populateScene(scene) {
      const src = this.assetUrl(scene.image);
      if (this.els.artworkImg && src) {
        this.els.artworkImg.classList.remove("ken-burns", "gallery-guardian");
        this.els.artworkImg.removeAttribute("data-gallery-shot");
        this.els.artworkImg.src = src;
        this.els.artworkImg.alt = scene.kanji || "";
        this.applyImageFraming(this.els.artworkImg, scene);
      }
      if (this.els.kanji) this.els.kanji.textContent = scene.kanji || "";
      if (this.els.keyword) this.els.keyword.textContent = scene.keyword || "";
      if (this.els.verseJp) {
        this.els.verseJp.innerHTML = scene.verse?.jpHtml || scene.verse?.jp || "";
      }
      if (this.els.verseEn) {
        this.els.verseEn.textContent = scene.verse?.en || "";
      }
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

      if (opening.image) {
        await this.playOpeningImageBookend(opening);
        return;
      }

      await this.playOpeningKanjiBookend(opening);
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
        await this.showBookendImage(opening.image, t.openingRevealMs);
        if (!stillRunning()) return;
        await introAudio;
        if (!stillRunning()) return;
      } else {
        const fluteMs = t.openingFluteMs;
        if (opening.audio) {
          this.playAudioUntilEnd(opening.audio, { kind: "bookend", maxMs: fluteMs });
          this.debugLog("opening flute started with artwork fade-in", { fluteMs });
        }
        await this.showBookendImage(opening.image, t.openingRevealMs);
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

    async playClosingBookend() {
      const closing = this.bookends?.closing;
      if (!closing) return;

      if (closing.image) {
        await this.playClosingImageBookend(closing);
        return;
      }

      await this.playClosingKanjiBookend(closing);
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

      await this.wait(t.blackHoldMs);
      if (!stillRunning()) return;

      await this.showBookendImage(closing.image, t.closingRevealMs);
      if (!stillRunning()) return;

      if (holdUntilSoundtrackEnds) {
        await this.waitForSoundtrackEnd();
        if (!stillRunning()) return;
      } else {
        await this.wait(t.closingHoldMs);
        if (!stillRunning()) return;
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

    async playExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

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

      // ── 1. Artwork arrival from black ──
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

      if (this.isSequentialVerses) {
        await this.playSequentialVerses(stillRunning);
      } else {
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
      if (!this.fixedKanji) {
        this.setKanjiCentered(true);
      }
      this.setClass(this.els.artwork, "is-exhaling", true);
      await this.wait(t.imageExhaleFadeMs + t.kanjiAloneHoldMs);
      if (!stillRunning()) return;
      this.setClass(this.els.kanji, "is-exhaling", true);
      await this.wait(t.kanjiExhaleFadeMs);
      if (!stillRunning()) return;

      // Black corridor between exhibits
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
      this.debugLog("start", {
        engineVersion: ENGINE_VERSION,
        collection: this.collection.id,
        hasOpeningBookend: Boolean(this.bookends?.opening),
        firstScene: this.scenes[0]?.kanji,
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
