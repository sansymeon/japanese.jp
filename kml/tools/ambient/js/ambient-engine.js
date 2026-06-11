/**
 * KML Ambient Player – collection-driven rendering engine.
 * Swap collections via JSON; no code changes required.
 */
(function () {
  "use strict";

  const DEFAULTS = {
    timing: {
      fadeMs: 4000,
      kanjiLeadMs: 2000,
      imageLeadMs: 6000,
      verseLeadMs: 12000,
      holdMs: 35000,
      crossfadeMs: 5000,
      kenBurnsDurationMs: 180000,
    },
    background: {
      mode: "auto", // "video" | "image" | "auto"
      kenBurns: true,
      overlayOpacity: 0.52,
      blurPx: 0,
    },
    display: {
      showKeyword: true,
      showFurigana: false,
      loop: true,
      autoAdvance: true,
      hideChrome: false,
    },
  };

  class AmbientPlayer {
    constructor(root, collection) {
      this.root = root;
      this.collection = collection;
      this.scenes = collection.scenes || [];
      this.timing = { ...DEFAULTS.timing, ...(collection.timing || {}) };
      this.background = { ...DEFAULTS.background, ...(collection.background || {}) };
      this.display = { ...DEFAULTS.display, ...(collection.display || {}) };
      const params = new URLSearchParams(window.location.search);
      if (params.get("capture") === "1") {
        this.display.hideChrome = true;
      }
      this.assetsBase = (collection.assetsBase || "../../assets").replace(/\/$/, "");
      this.soundtrack = collection.soundtrack || null;

      this.sceneIndex = 0;
      this.paused = false;
      this.destroyed = false;
      this.timers = [];
      this.activeBgSlot = 0;
      this.introAudio = null;
      this.mainAudio = null;
      this.audioUnlocked = false;
      this._studyForegroundHidden = false;
      this._studyLoopFinishing = false;

      this.els = {
        loading: root.querySelector("[data-ambient-loading]"),
        error: root.querySelector("[data-ambient-error]"),
        autoplayGate: root.querySelector("[data-ambient-autoplay-gate]"),
        title: root.querySelector("[data-ambient-title]"),
        status: root.querySelector("[data-ambient-status]"),
        progress: root.querySelector("[data-ambient-progress]"),
        kanjiBlock: root.querySelector("[data-ambient-kanji-block]"),
        kanji: root.querySelector("[data-ambient-kanji]"),
        keyword: root.querySelector("[data-ambient-keyword]"),
        imageWrap: root.querySelector("[data-ambient-image-wrap]"),
        image: root.querySelector("[data-ambient-image]"),
        verses: root.querySelector("[data-ambient-verses]"),
        verseJp: root.querySelector("[data-ambient-verse-jp]"),
        verseEn: root.querySelector("[data-ambient-verse-en]"),
        bgA: root.querySelector('[data-ambient-bg="0"]'),
        bgB: root.querySelector('[data-ambient-bg="1"]'),
        overlay: root.querySelector("[data-ambient-overlay]"),
        btnToggle: root.querySelector("[data-ambient-toggle]"),
        btnPrev: root.querySelector("[data-ambient-prev]"),
        btnNext: root.querySelector("[data-ambient-next]"),
        btnFurigana: root.querySelector("[data-ambient-furigana]"),
      };

      this.applyTheme();
      this.bindControls();
      if (this.isStudy && this.hasStudyAudio()) {
        this.initAudio();
      }
    }

    hasStudyAudio() {
      return Boolean(this.soundtrack?.main);
    }

    localUrl(relative) {
      if (!relative) return "";
      if (/^https?:\/\//.test(relative) || relative.startsWith("/")) return relative;
      return `./${relative.replace(/^\.\//, "")}`;
    }

    audioLog(label, detail = {}) {
      console.log(`[KML Study audio] ${label}`, detail);
    }

    audioError(label, err, detail = {}) {
      console.error(`[KML Study audio] ${label}`, err, detail);
    }

    initAudio() {
      const mainPath = this.soundtrack?.main || null;

      this.mainAudio = this.mountAudioElement({
        kind: "ambient",
        selector: "[data-ambient-lesson-audio]",
        src: mainPath,
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
        const host = this.root.querySelector(".ambient-audio") || this.root;
        host.appendChild(audio);
      }

      audio.dataset.ambientAudio = kind;
      if (src) audio.src = this.localUrl(src);

      audio.addEventListener("error", () => {
        this.audioError(`${kind} load error`, audio.error, {
          src: audio.currentSrc || audio.src,
        });
      });

      const label = kind === "intro" ? "intro audio created" : "ambient audio created";
      this.audioLog(label, { src: audio.currentSrc || audio.src || null });

      return audio;
    }

    async ensureAudioUnlocked() {
      if (this.audioUnlocked || !this.hasStudyAudio()) return;

      const audio = this.mainAudio;
      if (!audio) return;

      try {
        await audio.play();
        audio.pause();
        audio.currentTime = 0;
        this.audioUnlocked = true;
        this.audioLog("autoplay unlocked", {});
        return;
      } catch (err) {
        if (err.name !== "NotAllowedError") {
          this.audioError("autoplay probe error", err, {});
          return;
        }
      }

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
          gate.classList.add("ambient-hidden");
          gate.removeEventListener("keydown", onKeyDown);

          const probe = this.mainAudio;
          if (probe) {
            try {
              await probe.play();
              probe.pause();
              probe.currentTime = 0;
              this.audioLog("autoplay unlocked", { via: "gate" });
            } catch (err) {
              this.audioError("gate unlock play() error", err, {});
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

        gate.classList.remove("ambient-hidden");
        requestAnimationFrame(() => gate.classList.add("is-visible"));
        gate.addEventListener("click", finish, { once: true });
        gate.addEventListener("keydown", onKeyDown);
        gate.focus();
      });
    }

    async playAudioUntilEnd(audioPath, { element, label = "intro" } = {}) {
      if (!audioPath || !element) return;

      const url = this.localUrl(audioPath);
      element.src = url;
      element.currentTime = 0;
      element.loop = false;

      try {
        await element.play();
        this.audioLog(`${label} started`, { url });
        await new Promise((resolve) => {
          let settled = false;
          const done = () => {
            if (settled || this.destroyed) return;
            settled = true;
            element.removeEventListener("ended", onEnded);
            this.audioLog(`${label} ended`, { url });
            resolve();
          };
          const onEnded = () => done();
          element.addEventListener("ended", onEnded);
        });
      } catch (err) {
        this.audioError(`${label} play() error`, err, { url });
      }
    }

    async waitForSoundtrackEnd() {
      const audio = this.mainAudio;
      if (!audio || audio.ended) return;
      this.audioLog("waiting for soundtrack end", {});
      await new Promise((resolve) => {
        let settled = false;
        const done = () => {
          if (settled || this.destroyed) return;
          settled = true;
          audio.removeEventListener("ended", done);
          this.audioLog("ambient audio ended", {});
          resolve();
        };
        audio.addEventListener("ended", done);
      });
    }

    async fadeOutStudyForegroundOnly(t) {
      if (this._studyForegroundHidden) return;
      this._studyForegroundHidden = true;
      this.root.classList.add("is-foreground-exiting");
      this.setForegroundVisible({});
      const fadeMs = t.studyLoopConcertFadeMs ?? t.studyExitFadeMs ?? 1800;
      document.documentElement.style.setProperty(
        "--ambient-study-exit-fade",
        `${fadeMs}ms`
      );
      await this.wait(fadeMs);
      this.root.classList.remove("is-foreground-exiting");
    }

    async fadeStudyBackgroundToBlack(t) {
      const fadeMs = t.studyLoopFadeMs ?? t.crossfadeMs ?? 2500;
      const currentEl = this.bgSlotEl(this.activeBgSlot);
      currentEl.classList.remove("is-active");
      await this.wait(fadeMs);
      this.clearBgSlot(currentEl);
    }

    async beginStudyConcert(t, count) {
      if (this._studyLoopFinishing) return;
      this._studyLoopFinishing = true;

      try {
        await this.fadeOutStudyForegroundOnly(t);
        if (this.destroyed || this.paused) return;

        await this.waitForSoundtrackEnd();
        if (this.destroyed || this.paused) return;

        await this.fadeStudyBackgroundToBlack(t);
        if (this.destroyed || this.paused) return;

        await this.playScene(0, { syncSoundtrack: true, loopRestart: true });
      } finally {
        this._studyLoopFinishing = false;
      }
    }

    async startSoundtrack(forceRestart = false) {
      const path = this.soundtrack?.main;
      if (!path || !this.mainAudio) return;

      const audio = this.mainAudio;
      if (!forceRestart && !audio.paused && audio.src && !audio.ended) return;

      audio.src = this.localUrl(path);
      audio.currentTime = 0;
      audio.loop = false;

      try {
        await audio.play();
        this.audioLog("ambient audio started", { url: audio.src, forceRestart });
      } catch (err) {
        this.audioError("ambient play() error", err, { url: audio.src });
      }
    }

    stopAllAudio() {
      if (this.mainAudio) {
        this.mainAudio.pause();
        this.mainAudio.currentTime = 0;
      }
    }

    setAudioPaused(paused) {
      if (!this.mainAudio || this.mainAudio.ended) return;
      if (paused) this.mainAudio.pause();
      else {
        this.mainAudio.play().catch((err) => this.audioError("resume play() error", err, {}));
      }
    }

    get isStudy() {
      return this.collection.presentation === "study";
    }

    applyTheme() {
      const root = document.documentElement;
      root.style.setProperty("--ambient-fade", `${this.timing.fadeMs}ms`);
      root.style.setProperty(
        "--ambient-study-exit-fade",
        `${this.timing.studyExitFadeMs ?? 800}ms`
      );
      root.style.setProperty("--ambient-overlay", String(this.background.overlayOpacity));
      root.style.setProperty("--ken-burns-duration", `${this.timing.kenBurnsDurationMs}ms`);
      this.root.classList.toggle("is-study", this.isStudy);

      if (this.els.overlay) {
        this.els.overlay.style.opacity = String(this.background.overlayOpacity);
      }
      if (this.els.title) {
        this.els.title.textContent = this.collection.title || this.collection.id || "KML Ambient";
      }
      if (this.els.keyword) {
        this.els.keyword.hidden = !this.display.showKeyword;
      }
      if (this.els.verseJp) {
        this.els.verseJp.classList.toggle("show-furigana", this.display.showFurigana);
      }
      if (this.els.btnFurigana) {
        this.els.btnFurigana.hidden = !this.els.verseJp;
      }
      this.root.classList.toggle("is-manual", !this.display.autoAdvance);
      this.root.classList.toggle("is-capture", this.display.hideChrome);
      if (this.els.progress && !this.display.autoAdvance) {
        this.els.progress.style.width = "0%";
      }
    }

    bindControls() {
      this.els.btnToggle?.addEventListener("click", () => this.togglePause());
      this.els.btnPrev?.addEventListener("click", () => this.prevScene());
      this.els.btnNext?.addEventListener("click", () => this.nextScene());
      this.els.btnFurigana?.addEventListener("click", () => {
        this.display.showFurigana = !this.display.showFurigana;
        this.els.verseJp?.classList.toggle("show-furigana", this.display.showFurigana);
      });
      document.addEventListener("keydown", this.onKeyDown = (e) => {
        if (e.code === "Space") {
          e.preventDefault();
          this.togglePause();
        } else if (e.code === "ArrowRight") {
          this.nextScene();
        } else if (e.code === "ArrowLeft") {
          this.prevScene();
        }
      });
    }

    assetUrl(relative) {
      if (!relative) return "";
      if (/^https?:\/\//.test(relative) || relative.startsWith("/")) return relative;
      return `${this.assetsBase}/${relative.replace(/^\//, "")}`;
    }

    resolveBackgroundMode(scene) {
      const mode = this.background.mode;
      if (mode === "video") return scene.video ? "video" : "image";
      if (mode === "image") return "image";
      return scene.video ? "video" : "image";
    }

    bgSlotEl(slot) {
      return slot === 0 ? this.els.bgA : this.els.bgB;
    }

    clearBgSlot(slotEl) {
      if (!slotEl) return;
      slotEl.innerHTML = "";
      slotEl.classList.remove("is-active");
    }

    async mountBackground(slotEl, scene) {
      const mode = this.resolveBackgroundMode(scene);
      slotEl.innerHTML = "";

      if (mode === "video") {
        const video = document.createElement("video");
        video.src = this.assetUrl(scene.video);
        video.muted = true;
        video.playsInline = true;
        video.loop = true;

        const loaded = await new Promise((resolve) => {
          video.addEventListener("loadeddata", () => resolve(true), { once: true });
          video.addEventListener("error", () => resolve(false), { once: true });
          video.load();
        });

        if (loaded) {
          slotEl.appendChild(video);
          await video.play().catch(() => {});
          return;
        }
      }

      this.mountImageBackground(slotEl, scene);
    }

    mountImageBackground(slotEl, scene) {
      const src = this.assetUrl(scene.image || scene.videoPoster);
      if (!src) return;

      const img = document.createElement("img");
      img.src = src;
      img.alt = scene.kanji || "";
      if (this.background.kenBurns) {
        img.classList.add("ken-burns");
      }
      slotEl.appendChild(img);
    }

    async crossfadeBackground(scene) {
      const nextSlot = this.activeBgSlot === 0 ? 1 : 0;
      const nextEl = this.bgSlotEl(nextSlot);
      const currentEl = this.bgSlotEl(this.activeBgSlot);

      await this.mountBackground(nextEl, scene);

      nextEl.classList.add("is-active");
      currentEl.classList.remove("is-active");

      this.schedule(() => {
        this.clearBgSlot(currentEl);
      }, this.timing.crossfadeMs + 100);

      this.activeBgSlot = nextSlot;
    }

    setForegroundVisible({ kanji = false, keyword = false, image = false, verses = false, verseJp = false, verseEn = false }) {
      if (this.isStudy) {
        this.els.kanjiBlock?.classList.toggle("is-visible", kanji);
        if (this.display.showKeyword) {
          this.els.keyword?.classList.toggle("is-visible", keyword);
        }
        this.els.verseJp?.classList.toggle("is-visible", verseJp);
        this.els.verseEn?.classList.remove("is-visible");
        return;
      }
      this.els.kanjiBlock?.classList.toggle("is-visible", kanji);
      this.els.imageWrap?.classList.toggle("is-visible", image);
      this.els.verses?.classList.toggle("is-visible", verses);
    }

    populateForeground(scene) {
      if (this.els.kanji) this.els.kanji.textContent = scene.kanji || "";
      if (this.els.keyword) {
        this.els.keyword.textContent = scene.keyword || "";
        this.els.keyword.hidden = !this.display.showKeyword || !scene.keyword;
      }
      if (this.els.image) {
        const src = this.assetUrl(scene.image);
        this.els.image.src = src;
        this.els.image.alt = `Study image for ${scene.kanji || scene.id}`;
        this.els.imageWrap.hidden = !src;
      }
      if (this.els.verseJp) {
        this.els.verseJp.innerHTML = scene.verse?.jpHtml || scene.verse?.jp || "";
        this.els.verseJp.classList.toggle("show-furigana", this.display.showFurigana);
      }
      if (this.els.verseEn) {
        this.els.verseEn.textContent = scene.verse?.en || "";
      }
      if (this.els.status) {
        const parts = [
          `${this.sceneIndex + 1} / ${this.scenes.length}`,
          scene.kanji || scene.id,
        ];
        if (scene.lesson) parts.push(`L${scene.lesson}`);
        if (scene.heartPart) parts.push(scene.heartPart);
        this.els.status.textContent = parts.join(" · ");
      }
    }

    sceneTiming(scene) {
      return { ...this.timing, ...(scene.timing || {}) };
    }

    schedule(fn, delay) {
      const id = window.setTimeout(() => {
        this.timers = this.timers.filter((t) => t !== id);
        if (!this.destroyed && !this.paused) fn();
      }, delay);
      this.timers.push(id);
      return id;
    }

    clearTimers() {
      this.timers.forEach(clearTimeout);
      this.timers = [];
    }

    totalSceneDuration(t) {
      if (this.isStudy) {
        return t.sceneDurationMs || 20000;
      }
      return t.crossfadeMs + t.kanjiLeadMs + t.imageLeadMs + t.verseLeadMs + (t.holdMs || 0);
    }

    runSceneProgress(t, startedAt) {
      if (this.destroyed || this.paused) return;
      const total = this.totalSceneDuration(t);
      const elapsed = Date.now() - startedAt;
      const pct = Math.min(100, (elapsed / total) * 100);
      if (this.els.progress) this.els.progress.style.width = `${pct}%`;
      if (elapsed < total) {
        requestAnimationFrame(() => this.runSceneProgress(t, startedAt));
      }
    }

    revealScene(t) {
      if (this.isStudy) {
        this.revealStudyScene(t);
        return;
      }
      this.schedule(() => this.setForegroundVisible({ kanji: true }), t.kanjiLeadMs);
      this.schedule(() => this.setForegroundVisible({ kanji: true, image: true }), t.imageLeadMs);
      this.schedule(
        () => this.setForegroundVisible({ kanji: true, image: true, verses: true }),
        t.verseLeadMs
      );
    }

    revealStudyScene(t) {
      this.setForegroundVisible({});
      this.schedule(() => this.setForegroundVisible({ kanji: true }), t.kanjiLeadMs);
      if (this.display.showKeyword) {
        this.schedule(
          () => this.setForegroundVisible({ kanji: true, keyword: true }),
          t.keywordLeadMs
        );
      }
      this.schedule(
        () => this.setForegroundVisible({ kanji: true, keyword: false, verseJp: true }),
        t.verseJpLeadMs
      );
    }

    async fadeOutStudyForeground(t) {
      if (this._studyForegroundHidden) return;
      this._studyForegroundHidden = true;
      this.root.classList.add("is-foreground-exiting");
      this.setForegroundVisible({});
      await this.wait(t.studyExitFadeMs ?? 800);
      this.root.classList.remove("is-foreground-exiting");
      await this.wait(t.studyEmptyBeatMs ?? 400);
    }

    scheduleStudyAdvance(t, count) {
      const isLastInLoop =
        this.sceneIndex === count - 1 && this.display.loop && this.soundtrack?.main;

      if (isLastInLoop) {
        const exitMs = (t.studyExitFadeMs ?? 800) + (t.studyEmptyBeatMs ?? 400);
        const fadeAt = Math.max(0, this.totalSceneDuration(t) - exitMs);

        this.schedule(() => {
          if (!this.destroyed && !this.paused) this.beginStudyConcert(t, count);
        }, fadeAt);
        return;
      }

      const exitMs = (t.studyExitFadeMs ?? 800) + (t.studyEmptyBeatMs ?? 400);
      const fadeAt = Math.max(0, this.totalSceneDuration(t) - exitMs);

      this.schedule(() => {
        if (!this.destroyed && !this.paused) this.fadeOutStudyForeground(t);
      }, fadeAt);

      this.schedule(() => {
        const next = this.sceneIndex + 1;
        if (next >= count && !this.display.loop) {
          this.paused = true;
          this.updateToggleLabel();
          return;
        }
        this.playScene(next);
      }, this.totalSceneDuration(t));
    }

    async prepareStudyScene(scene, t, hasPriorForeground) {
      if (hasPriorForeground && !this._studyForegroundHidden) {
        await this.fadeOutStudyForeground(t);
      } else {
        this.setForegroundVisible({});
      }
      this._studyForegroundHidden = false;

      await this.crossfadeBackground(scene);
      this.populateForeground(scene);
      await this.wait(t.studyKanjiGapMs ?? 350);
    }

    async prepareStudySceneWithSoundtrack(scene, t, hasPriorForeground, forceRestart = false) {
      if (hasPriorForeground && !this._studyForegroundHidden) {
        await this.fadeOutStudyForeground(t);
      } else {
        this.setForegroundVisible({});
      }
      this._studyForegroundHidden = false;

      await Promise.all([
        this.startSoundtrack(forceRestart || hasPriorForeground),
        this.crossfadeBackground(scene),
      ]);
      this.populateForeground(scene);
      await this.wait(t.studyKanjiGapMs ?? 350);
    }

    wait(ms) {
      return new Promise((resolve) => {
        const id = window.setTimeout(() => {
          this.timers = this.timers.filter((t) => t !== id);
          if (!this.destroyed) resolve();
        }, ms);
        this.timers.push(id);
      });
    }

    async playIntro(intro) {
      if (!intro?.image) return;

      const slot = this.bgSlotEl(this.activeBgSlot);
      slot.innerHTML = "";
      slot.classList.add("is-intro");

      const img = document.createElement("img");
      img.src = this.assetUrl(intro.image);
      img.alt = intro.title || this.collection.title || "";
      slot.appendChild(img);
      slot.classList.add("is-active");

      this.setForegroundVisible({});

      const holdBefore = intro.holdBeforeMs ?? 0;
      if (holdBefore > 0) await this.wait(holdBefore);

      const holdUntilAudioEnds = Boolean(intro.audio && intro.holdUntilAudioEnds);

      if (holdUntilAudioEnds && this.isStudy) {
        await this.playAudioUntilEnd(intro.audio, {
          element: this.introAudio,
          label: "intro",
        });
      } else if (intro.durationMs) {
        await this.wait(intro.durationMs);
      }

      slot.classList.remove("is-active");
      const introFade = intro.exitFadeMs ?? this.timing.introExitFadeMs ?? this.timing.fadeMs;
      await this.wait(introFade);
      slot.classList.remove("is-intro");
      this.clearBgSlot(slot);
    }

    async playScene(index, options = {}) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      const loopRestart =
        options.loopRestart || (this.isStudy && index >= count && this.display.loop);
      this.sceneIndex = ((index % count) + count) % count;

      const scene = this.scenes[this.sceneIndex];
      const t = this.sceneTiming(scene);

      this.clearTimers();
      this._studyLoopFinishing = false;

      if (this.isStudy) {
        const hasPriorForeground = this._studySceneReady;
        const syncSoundtrack =
          options.syncSoundtrack || (loopRestart && this.sceneIndex === 0);

        if (syncSoundtrack && this.soundtrack?.main) {
          await this.prepareStudySceneWithSoundtrack(scene, t, hasPriorForeground, loopRestart);
        } else {
          await this.prepareStudyScene(scene, t, hasPriorForeground);
        }
      } else {
        this.setForegroundVisible({});
        this.populateForeground(scene);
        await this.crossfadeBackground(scene);
      }

      this._studySceneReady = true;

      if (this.display.autoAdvance) {
        const startedAt = Date.now();
        this.runSceneProgress(t, startedAt);
      } else if (this.els.progress) {
        this.els.progress.style.width = "0%";
      }

      this.revealScene(t);

      if (this.display.autoAdvance) {
        if (this.isStudy) {
          this.scheduleStudyAdvance(t, count);
        } else {
          const advanceAt = this.totalSceneDuration(t);
          this.schedule(() => {
            const next = this.sceneIndex + 1;
            if (next >= count && !this.display.loop) {
              this.paused = true;
              this.updateToggleLabel();
              return;
            }
            this.playScene(next);
          }, advanceAt);
        }
      }
    }

    togglePause() {
      this.paused = !this.paused;
      this.root.classList.toggle("is-paused", this.paused);
      this.updateToggleLabel();
      this.root.querySelectorAll("video").forEach((v) => {
        if (this.paused) v.pause();
        else v.play().catch(() => {});
      });
      if (this.isStudy) this.setAudioPaused(this.paused);
      if (this.display.autoAdvance) {
        if (!this.paused) {
          this.clearTimers();
          this.playScene(this.sceneIndex);
        } else {
          this.clearTimers();
        }
      }
    }

    nextScene() {
      if (this.destroyed) return;
      this.clearTimers();
      this.playScene(this.sceneIndex + 1);
    }

    prevScene() {
      if (this.destroyed) return;
      this.clearTimers();
      this.playScene(this.sceneIndex - 1);
    }

    updateToggleLabel() {
      if (this.els.btnToggle) {
        this.els.btnToggle.textContent = this.paused ? "Resume motion" : "Pause motion";
      }
    }

    async start() {
      if (!this.scenes.length) throw new Error("Collection has no scenes.");
      this.els.loading?.classList.add("ambient-hidden");
      this.els.error?.classList.add("ambient-hidden");
      if (this.isStudy && this.hasStudyAudio()) {
        await this.ensureAudioUnlocked();
      }
      if (this.collection.intro) {
        await this.playIntro(this.collection.intro);
      }
      const syncSoundtrack = this.isStudy && Boolean(this.soundtrack?.main);
      await this.playScene(0, { syncSoundtrack });
    }

    destroy() {
      this.destroyed = true;
      this.clearTimers();
      this.stopAllAudio();
      document.removeEventListener("keydown", this.onKeyDown);
      this.root.querySelectorAll("video").forEach((v) => {
        v.pause();
        v.removeAttribute("src");
        v.load();
      });
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
    return params.get("collection") || "lesson_40_study";
  }

  async function boot() {
    const root = document.querySelector("[data-ambient-root]");
    if (!root) return;

    const loading = root.querySelector("[data-ambient-loading]");
    const errorEl = root.querySelector("[data-ambient-error]");
    const name = collectionFromQuery();

    try {
      const collection = await loadCollection(name);
      const player = new AmbientPlayer(root, collection);
      window.kmlAmbient = player;
      await player.start();
    } catch (err) {
      loading?.classList.add("ambient-hidden");
      if (errorEl) {
        errorEl.textContent = err.message || String(err);
        errorEl.classList.remove("ambient-hidden");
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
