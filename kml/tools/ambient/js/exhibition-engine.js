/**
 * KML Digital Art Exhibition – gallery presentation engine.
 * Collection-driven; scenes reuse ambient JSON scene format.
 */
(function () {
  "use strict";

  const ENGINE_VERSION = "2026-06-29-image-verse-crossfade";

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
      this.meta = collection.meta || {};
      this.bookends = collection.bookends || null;
      this.soundtrack = collection.soundtrack || null;
      this.assetsBase = this.normalizeAssetsBase(collection.assetsBase || "./assets");

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
      const modeParam = (params.get("confirmationMode") || "").trim().toLowerCase();
      const defaultMode = (this.display.confirmationMode || "stacked").toLowerCase();
      this.confirmationMode = ["stacked", "replace", "crossfade"].includes(modeParam)
        ? modeParam
        : defaultMode;
      this.contentType = collection.contentType || this.display.contentType || "";
      this.edition = collection.edition || this.display.edition || "";
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
      this._soundtrackStarted = false;

      this.presentationEnded = false;
      this.activeArtworkKey = "a";
      this._imageVerseCrossfadedTo = -1;
      this._galleryCrossfadedTo = -1;
      this._verseReadingCrossfadedTo = -1;
      this._assistedReadingCrossfadedTo = -1;
      this._compoundsCrossfadedTo = -1;
      this._seamlessHandoffTo = -1;

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
        vocabIntroOverlay: root.querySelector("[data-vocabulary-intro-overlay]"),
        vocabIntroJpBlock: root.querySelector("[data-vocabulary-intro-jp-block]"),
        vocabIntroJp: root.querySelector("[data-vocabulary-intro-jp]"),
        vocabIntroReading: root.querySelector("[data-vocabulary-intro-reading]"),
        vocabIntroEn: root.querySelector("[data-vocabulary-intro-en]"),
        kanji: root.querySelector("[data-exhibition-kanji]"),
        keyword: root.querySelector("[data-exhibition-keyword]"),
        verseJp: root.querySelector("[data-exhibition-verse-jp]"),
        verseEn: root.querySelector("[data-exhibition-verse-en]"),
        partyLayer: root.querySelector("[data-party-kanji-layer]"),
        partyShockKanji: root.querySelector("[data-party-shock-kanji]"),
        partyChallenge: root.querySelector("[data-party-challenge]"),
        partyPlaylist: root.querySelector("[data-party-playlist]"),
        partyComponents: root.querySelector("[data-party-components]"),
        partyEquation: root.querySelector("[data-party-equation]"),
        partyReading: root.querySelector("[data-party-reading]"),
        partyTrivia: root.querySelector("[data-party-trivia]"),
        partyStrokesFrame: root.querySelector("[data-party-strokes-frame]"),
        partyStrokeNote: root.querySelector("[data-party-stroke-note]"),
        partyComponentPulse: root.querySelector("[data-party-component-pulse]"),
        partyFinalKanji: root.querySelector("[data-party-final-kanji]"),
        partyFinalReading: root.querySelector("[data-party-final-reading]"),
        partyClosingMessage: root.querySelector("[data-party-closing-message]"),
        partyBrand: root.querySelector("[data-party-brand]"),
        partyPlaylistEnd: root.querySelector("[data-party-playlist-end]"),
        partyTagline: root.querySelector("[data-party-tagline]"),
        partyDisclaimer: root.querySelector("[data-party-disclaimer]"),
        strokeOrderLayer: root.querySelector("[data-stroke-order-layer]"),
        grade1ConfettiLayer: root.querySelector("[data-grade1-confetti-layer]"),
        g4Layer: root.querySelector("[data-g4-layer]"),
        g4Camera: root.querySelector("[data-g4-camera]"),
        g4Board: root.querySelector("[data-g4-board]"),
        g4KanjiHero: root.querySelector("[data-g4-kanji-hero]"),
        hiraganaSongLayer: root.querySelector("[data-hiragana-song-layer]"),
        hiraganaSongChart: root.querySelector("[data-hiragana-song-chart]"),
        strokeOrderKanji:
          root.querySelector('[data-stroke-order-kanji="a"]') ||
          root.querySelector("[data-stroke-order-kanji]"),
        strokeOrderSvg:
          root.querySelector('[data-stroke-order-svg="a"]') ||
          root.querySelector("[data-stroke-order-svg]"),
        anchorCompoundsLayer: root.querySelector("[data-anchor-compounds-layer]"),
        anchorCompoundsWord: root.querySelector("[data-anchor-compounds-word]"),
        anchorCompoundsReading: root.querySelector("[data-anchor-compounds-reading]"),
      };

      this.soundtrackSlots = {
        a: {
          slot: root.querySelector('[data-soundtrack-slot="a"]'),
          kanji: root.querySelector('[data-stroke-order-kanji="a"]'),
          svg: root.querySelector('[data-stroke-order-svg="a"]'),
        },
        b: {
          slot: root.querySelector('[data-soundtrack-slot="b"]'),
          kanji: root.querySelector('[data-stroke-order-kanji="b"]'),
          svg: root.querySelector('[data-stroke-order-svg="b"]'),
        },
      };
      this.activeSoundtrackSlot = "a";
      this.g4SoundtrackSlots = {
        a: {
          slot: root.querySelector('[data-g4-slot="a"]'),
          kanji: root.querySelector('[data-g4-kanji="a"]'),
        },
        b: {
          slot: root.querySelector('[data-g4-slot="b"]'),
          kanji: root.querySelector('[data-g4-kanji="b"]'),
        },
      };
      this.activeG4Slot = "a";
      this.grade4Visited = [];
      this._soundtrackCrossfadedTo = -1;

      this.partyPhases = {
        shock: root.querySelector('[data-party-phase="shock"]'),
        reveal: root.querySelector('[data-party-phase="reveal"]'),
        proof: root.querySelector('[data-party-phase="proof"]'),
        final: root.querySelector('[data-party-phase="final"]'),
        closing: root.querySelector('[data-party-phase="closing"]'),
        endcard: root.querySelector('[data-party-phase="endcard"]'),
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
      const typo = params.get("typography") || this.display.typography || "mobile-refine";
      const verseMode = params.get("verseMode") || this.display.verseMode || "simultaneous";
      const root = document.documentElement;

      root.classList.toggle("kml-typography-legacy", typo === "legacy");
      root.classList.toggle("kml-typography-mobile", typo === "mobile");
      root.classList.toggle("kml-typography-mobile-refine", typo === "mobile-refine");
      root.classList.toggle("kml-typography-placard", typo === "placard");
      root.classList.toggle("kml-typography-party-kanji", typo === "party-kanji");
      root.classList.toggle("kml-verse-sequential", verseMode === "sequential");
      root.classList.toggle("kml-verse-staggered", verseMode === "staggered");
      root.classList.toggle("kml-verse-authored", this.useAuthoredVerseLayout(typo));

      const family = this.display.family || "";
      const profile = this.display.exhibitProfile || "";
      this.root.classList.toggle("is-japanese-reflections", family === "japaneseReflections");
      this.root.classList.toggle("is-image-verse", profile === "imageVerse");
      this.root.classList.toggle("is-gallery", profile === "gallery");
      this.root.classList.toggle("is-verse-reading", profile === "verseReading");
      this.root.classList.toggle("is-assisted-reading", profile === "assistedReading");
      this.root.classList.toggle("is-vocabulary-exhibition", profile === "vocabularyExhibition");
      this.root.classList.toggle(
        "is-compounds-exhibition",
        profile === "compoundsExhibition" || profile === "japaneseVocabulary"
      );
      this.root.classList.toggle("is-japanese-vocabulary", profile === "japaneseVocabulary");
      this.root.classList.toggle(
        "is-anchor-compounds-exhibition",
        profile === "anchorCompoundsExhibition"
      );
      this.root.classList.toggle(
        "anchor-confirm-stacked",
        profile === "anchorCompoundsExhibition" && this.confirmationMode === "stacked"
      );
      this.root.classList.toggle(
        "anchor-confirm-replace",
        profile === "anchorCompoundsExhibition" && this.confirmationMode === "replace"
      );
      this.root.classList.toggle(
        "anchor-confirm-crossfade",
        profile === "anchorCompoundsExhibition" && this.confirmationMode === "crossfade"
      );
      this.root.classList.toggle(
        "is-school-compounds",
        profile === "anchorCompoundsExhibition" &&
          (this.edition === "school" || this.display.family === "schoolCompounds")
      );
      this.root.classList.toggle("is-stroke-order", profile === "strokeOrder");
      this.root.classList.toggle(
        "is-grade1-stroke-order",
        ExhibitionPlayer.isElementaryGradeStrokeOrderProfile(profile)
      );
      this.root.classList.toggle(
        "is-kanji-soundtrack",
        family === "kanjiSoundtrack" || profile === "kanjiSoundtrack"
      );
      this.root.classList.toggle("is-grade1-kanji-soundtrack", family === "grade1KanjiSoundtrack");
      this.root.classList.toggle("is-grade2-kanji-soundtrack", family === "grade2KanjiSoundtrack");
      this.root.classList.toggle("is-grade3-kanji-soundtrack", family === "grade3KanjiSoundtrack");
      this.root.classList.toggle("is-grade4-kanji-soundtrack", family === "grade4KanjiSoundtrack");
      this.root.classList.toggle("is-grade5-kanji-soundtrack", family === "grade5KanjiSoundtrack");
      this.root.classList.toggle("is-grade6-kanji-soundtrack", family === "grade6KanjiSoundtrack");
      this.root.classList.toggle("is-party-kanji", profile === "partyKanji");
      this.root.classList.toggle("is-hiragana-song", profile === "hiraganaSong");
      this.root.classList.toggle(
        "is-gallery-crest-bookends",
        this.display.bookendStyle === "galleryCrest"
      );
      const foundationsTypography =
        this.display.typographyStyle === "foundations" ||
        this.display.typographyStyle === "study" ||
        (typo === "mobile-refine" && this.meta?.theme === "heart");
      this.root.classList.toggle("is-foundations-typography", foundationsTypography);
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

    get isGalleryProfile() {
      return this.display.exhibitProfile === "gallery";
    }

    get isVerseReadingProfile() {
      return this.display.exhibitProfile === "verseReading";
    }

    get isAssistedReadingProfile() {
      return this.display.exhibitProfile === "assistedReading";
    }

    get isVocabularyExhibitionProfile() {
      return this.display.exhibitProfile === "vocabularyExhibition";
    }

    get isCompoundsExhibitionProfile() {
      return this.display.exhibitProfile === "compoundsExhibition";
    }

    get isJapaneseVocabularyProfile() {
      return this.display.exhibitProfile === "japaneseVocabulary";
    }

    get isAnchorCompoundsExhibitionProfile() {
      return this.display.exhibitProfile === "anchorCompoundsExhibition";
    }

    get isStrokeOrderProfile() {
      const profile = this.display.exhibitProfile || "";
      return (
        profile === "strokeOrder" ||
        ExhibitionPlayer.isElementaryGradeStrokeOrderProfile(profile)
      );
    }

    get isGrade1StrokeOrderProfile() {
      return this.display.exhibitProfile === "grade1StrokeOrder";
    }

    get isGrade2StrokeOrderProfile() {
      return this.display.exhibitProfile === "grade2StrokeOrder";
    }

    get isElementaryStrokeOrderProfile() {
      return ExhibitionPlayer.isElementaryGradeStrokeOrderProfile(
        this.display.exhibitProfile
      );
    }

    /** Denser forms get thinner paths so strokes stay separated. */
    get usesAdaptiveStrokeOrderWidth() {
      const profile = this.display.exhibitProfile || "";
      if (profile === "strokeOrder") return true;
      return (
        profile !== "grade1StrokeOrder" &&
        ExhibitionPlayer.isElementaryGradeStrokeOrderProfile(profile)
      );
    }

    static isElementaryGradeStrokeOrderProfile(profile) {
      return /^grade[1-6]StrokeOrder$/.test(profile || "");
    }

    strokeOrderColorsForScene(scene, timing = this.timing) {
      const kanjiColor = scene?.meta?.kanjiColor;
      if (this.isElementaryStrokeOrderProfile && kanjiColor) {
        return { drawColor: kanjiColor, finalColor: kanjiColor };
      }
      return {
        drawColor: timing.strokeOrderDrawColor,
        finalColor: timing.strokeOrderFinalColor,
      };
    }

    get isKanjiSoundtrackProfile() {
      return this.display.family === "kanjiSoundtrack";
    }

    get isGrade4KanjiSoundtrackProfile() {
      return this.display.family === "grade4KanjiSoundtrack";
    }

    get isGrade1KanjiSoundtrackProfile() {
      const family = this.display.family;
      return (
        family === "grade1KanjiSoundtrack" ||
        family === "grade2KanjiSoundtrack" ||
        family === "grade3KanjiSoundtrack" ||
        family === "grade4KanjiSoundtrack" ||
        family === "grade5KanjiSoundtrack" ||
        family === "grade6KanjiSoundtrack"
      );
    }

    get isPartyKanjiProfile() {
      return this.display.exhibitProfile === "partyKanji";
    }

    get isHiraganaSongProfile() {
      return this.display.exhibitProfile === "hiraganaSong";
    }

    get showEnglish() {
      const params = new URLSearchParams(window.location.search);
      if (params.has("showEnglish")) {
        return params.get("showEnglish") !== "0";
      }
      return this.display.showEnglish !== false;
    }

    get seamlessExhibitHandoff() {
      const t = this.timing;
      if (t.seamlessExhibitHandoff === false) return false;
      if (t.seamlessExhibitHandoff === true) return true;
      return (t.exhibitBlackHoldMs ?? t.blackHoldMs) === 0;
    }

    exhibitTransitionMs(t = this.timing) {
      return (
        t.exhibitTransitionMs ??
        t.artworkArrivalMs + (t.blackHoldMs || 0)
      );
    }

    kanjiHandoffFadeMs(t = this.timing) {
      if (t.kanjiBridgeFadeMs != null) {
        return t.kanjiBridgeFadeMs;
      }
      if (t.kanjiHandoffFadeMs != null) {
        return t.kanjiHandoffFadeMs;
      }
      return Math.min(4500, t.kanjiExhaleFadeMs);
    }

    galleryBridgeTiming(t = this.timing) {
      return {
        exhaleMs: t.imageHandoffExhaleMs ?? t.imageExhaleFadeMs,
        arrivalMs: t.imageHandoffArrivalMs ?? this.exhibitTransitionMs(t),
        kanjiBridgeMs: this.kanjiHandoffFadeMs(t),
      };
    }

    galleryBridgeHandoffMs(t = this.timing) {
      const { exhaleMs, arrivalMs } = this.galleryBridgeTiming(t);
      return exhaleMs + arrivalMs;
    }

    syncLegacyArtworkRefs() {
      const layer = this.artworkLayers[this.activeArtworkKey];
      if (!layer) return;
      this.els.artwork = layer.wrap;
      this.els.artworkImg = layer.img;
    }

    inactiveArtworkKey() {
      return this.activeArtworkKey === "a" ? "b" : "a";
    }

    artworkLayerShowsScene(key, scene) {
      const img = this.artworkLayers[key]?.img;
      if (!img || !scene) return false;
      return (
        img.dataset.kmlSceneId === (scene.id || "") &&
        img.dataset.kmlLoadedSrc === this.assetUrl(scene.image, scene.imageRev)
      );
    }

    hideArtworkLayer(key) {
      const layer = this.artworkLayers[key];
      if (!layer?.wrap) return;
      this.setClass(layer.wrap, "is-visible", false);
      this.setClass(layer.wrap, "is-exhaling", false);
      this.setClass(layer.wrap, "is-on-top", false);
    }

    showArtworkLayer(key, { onTop = true, hideOther = true } = {}) {
      if (hideOther) {
        this.hideArtworkLayer(key === "a" ? "b" : "a");
      }
      const layer = this.artworkLayers[key];
      if (!layer?.wrap) return;
      this.setClass(layer.wrap, "is-exhaling", false);
      this.setClass(layer.wrap, "is-on-top", onTop);
      this.setClass(layer.wrap, "is-visible", true);
    }

    onlyShowArtworkLayer(key, { onTop = false } = {}) {
      this.hideArtworkLayer("a");
      this.hideArtworkLayer("b");
      this.showArtworkLayer(key, { onTop, hideOther: false });
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

    galleryExhibitDurationMs(t = this.timing) {
      return this.imageVerseExhibitDurationMs(t);
    }

    timedImageExhibitDurationMs(t = this.timing) {
      if (this.isGalleryProfile) return this.galleryExhibitDurationMs(t);
      if (this.isImageVerseProfile) return this.imageVerseExhibitDurationMs(t);
      if (this.isVerseReadingProfile) return this.verseReadingExhibitDurationMs(t);
      if (this.isAssistedReadingProfile) return this.assistedReadingExhibitDurationMs(t);
      if (this.isVocabularyExhibitionProfile) return this.vocabularyExhibitionExhibitDurationMs(t);
      if (this.isCompoundsExhibitionProfile) return this.compoundsExhibitionExhibitDurationMs(t);
      if (this.isJapaneseVocabularyProfile) return this.japaneseVocabularyExhibitDurationMs(t);
      if (this.isAnchorCompoundsExhibitionProfile) {
        return this.anchorCompoundsExhibitDurationMs(t);
      }
      return this.exhibitDurationMs(t);
    }

    readingStageMs(t = this.timing, prefix = "readingStage") {
      return (
        (t[`${prefix}RevealMs`] ?? t.readingStageRevealMs ?? 1000) +
        (t[`${prefix}HoldMs`] ?? t.readingStageHoldMs ?? 7000) +
        (t[`${prefix}FadeMs`] ?? t.readingStageFadeMs ?? 1000)
      );
    }

    verseReadingExhibitDurationMs(t = this.timing) {
      let ms =
        (t.artworkAloneMs ?? 0) +
        this.readingStageMs(t, "readingHiragana") +
        this.readingStageMs(t, "readingMixed") +
        this.readingStageMs(t, "readingNatural") +
        (t.exhibitTransitionMs ?? 4000);
      if (this.showEnglish) {
        ms +=
          (t.readingEnRevealMs ?? 1000) +
          (t.readingEnHoldMs ?? 5000) +
          (t.readingEnFadeMs ?? 1000);
      }
      return ms;
    }

    assistedReadingExhibitDurationMs(t = this.timing) {
      let ms =
        (t.artworkAloneMs ?? 0) +
        (t.readingPauseBeforeMs ?? 5000) +
        (t.readingAssistedRevealMs ?? 1800) +
        (t.readingFuriganaEnterDelayMs ?? 3000) +
        (t.readingFuriganaEnterMs ?? 3000) +
        (t.readingAssistedHoldMs ?? 9000) +
        (t.readingFuriganaFadeMs ?? 2500) +
        (t.readingNativeHoldMs ?? 3500) +
        (t.readingJpFadeMs ?? 1000) +
        (t.exhibitTransitionMs ?? 4000);
      if (this.showEnglish) {
        ms +=
          (t.readingEnRevealMs ?? 1000) +
          (t.readingEnHoldMs ?? 5500) +
          (t.readingEnFadeMs ?? 1000);
      }
      return ms;
    }

    vocabularyStepMs(t = this.timing) {
      return (
        (t.vocabularyStepRevealMs ?? 1400) +
        (t.vocabularyStepHoldMs ?? 5000) +
        (t.vocabularyStepFadeMs ?? 1400)
      );
    }

    vocabularyExhibitionExhibitDurationMs(t = this.timing, stepCount = 8) {
      let ms =
        (t.artworkAloneMs ?? 0) +
        (t.vocabularyPauseBeforeMs ?? 4000) +
        stepCount * this.vocabularyStepMs(t) +
        (t.vocabularyVerseJpRevealMs ?? 1600) +
        (t.vocabularyVerseJpHoldMs ?? 7000) +
        (t.vocabularyVerseJpFadeMs ?? 1400) +
        (t.exhibitTransitionMs ?? 4000);
      if (this.showEnglish) {
        ms +=
          (t.vocabularyVerseEnRevealMs ?? 1400) +
          (t.vocabularyVerseEnHoldMs ?? 6000) +
          (t.vocabularyVerseEnFadeMs ?? 1400);
      }
      return ms;
    }

    compoundsStepMs(t = this.timing, step = {}) {
      let ms = (t.compoundsStepRevealMs ?? 1400) + (t.compoundsStepFadeMs ?? 1400);
      if (step.jpHtml) {
        ms +=
          (t.compoundsFuriganaEnterDelayMs ?? 900) +
          (t.compoundsFuriganaEnterMs ?? 2200) +
          (t.compoundsFuriganaHoldMs ?? 3000) +
          (t.compoundsFuriganaFadeMs ?? 2200) +
          (t.compoundsNativeHoldMs ?? 1600);
      }
      ms +=
        (t.compoundsReadingRevealMs ?? 1200) +
        (t.compoundsReadingHoldMs ?? 1800);
      if (step.hint) {
        ms += t.compoundsHintRevealMs ?? 1000;
      }
      ms +=
        (t.compoundsEnRevealMs ?? 1200) +
        (t.compoundsEnHoldMs ?? 3000) +
        (t.compoundsEnFadeMs ?? 1400);
      return ms;
    }

    compoundsExhibitionExhibitDurationMs(t = this.timing, stepCount = 4) {
      return (
        (t.artworkAloneMs ?? 0) +
        (t.compoundsPauseBeforeMs ?? 2400) +
        (t.compoundsKanjiRevealMs ?? 1600) +
        (t.compoundsKanjiHoldMs ?? 2800) +
        (t.compoundsKanjiFadeMs ?? 1400) +
        stepCount * this.compoundsStepMs(t) +
        (t.compoundsKanjiReturnRevealMs ?? 1400) +
        (t.compoundsKanjiReturnHoldMs ?? 2200) +
        (t.compoundsKanjiReturnFadeMs ?? 1400) +
        (t.exhibitTransitionMs ?? 3500)
      );
    }

    japaneseVocabularyStepMs(t = this.timing, step = {}) {
      let ms = (t.compoundsStepRevealMs ?? 1400) + (t.compoundsStepFadeMs ?? 1400);
      if (step.jpHtml) {
        ms +=
          (t.compoundsFuriganaEnterDelayMs ?? 900) +
          (t.compoundsFuriganaEnterMs ?? 2200) +
          (t.compoundsFuriganaHoldMs ?? 3000) +
          (t.compoundsFuriganaFadeMs ?? 2200) +
          (t.compoundsNativeHoldMs ?? 2200);
      } else {
        ms +=
          (t.compoundsReadingRevealMs ?? 1200) +
          (t.compoundsReadingHoldMs ?? 1800);
      }
      ms +=
        (t.compoundsEnRevealMs ?? 1200) +
        (t.compoundsEnHoldMs ?? 3500) +
        (t.compoundsEnFadeMs ?? 1400);
      return ms;
    }

    beautifulWordDurationMs(t = this.timing, word = {}) {
      const hasLabel = Boolean(word.labelHtml || word.label);
      let ms = 0;
      if (hasLabel) {
        ms +=
          (t.beautifulWordLabelRevealMs ?? 1600) +
          (t.beautifulWordLabelHoldMs ?? 2200);
      }
      ms +=
        (t.beautifulWordRevealMs ?? 1600) +
        (t.compoundsFuriganaEnterDelayMs ?? 900) +
        (t.compoundsFuriganaEnterMs ?? 2200) +
        (t.beautifulWordFuriganaHoldMs ?? 4500) +
        (t.compoundsFuriganaFadeMs ?? 2200) +
        (t.beautifulWordNativeHoldMs ?? 3500) +
        (t.compoundsEnRevealMs ?? 1400) +
        (t.beautifulWordEnHoldMs ?? 5000) +
        (t.compoundsEnFadeMs ?? 1600);
      // Final fade is skipped when lingering for soundtrack (standard Vocabulary ending).
      if (!this.isJapaneseVocabularyProfile) {
        ms += t.beautifulWordFadeMs ?? 1800;
      }
      if (!word.jpHtml && word.reading) {
        ms +=
          (t.compoundsReadingRevealMs ?? 1200) +
          (t.compoundsReadingHoldMs ?? 2200);
      }
      return ms;
    }

    japaneseVocabularyExhibitDurationMs(t = this.timing) {
      const scene = this.scenes[this.sceneIndex] || this.scenes[0] || {};
      const steps = scene.compounds?.steps || [];
      const word = scene.beautifulWord || this.collection.beautifulWord || {};
      let ms =
        (t.artworkAloneMs ?? 0) +
        (t.compoundsPauseBeforeMs ?? 3200) +
        (t.exhibitTransitionMs ?? 0);
      for (const step of steps) {
        ms += this.japaneseVocabularyStepMs(t, step);
      }
      if (word.jp || word.jpHtml) {
        ms += this.beautifulWordDurationMs(t, word);
      }
      return ms;
    }

    anchorCompoundsCardDurationMs(t = this.timing) {
      const fadeIn = t.anchorWordFadeInMs ?? 700;
      const hold = t.anchorWordHoldMs ?? 2500;
      const readingFadeIn = t.anchorReadingFadeInMs ?? 450;
      const transition = t.anchorTransitionMs ?? 600;
      const readingHold = t.anchorReadingHoldMs ?? 1400;
      const exit = t.anchorCardFadeOutMs ?? 500;
      const gap = t.anchorCardGapMs ?? 300;
      if (this.confirmationMode === "replace" || this.confirmationMode === "crossfade") {
        return fadeIn + hold + transition + transition + readingHold + exit + gap;
      }
      return fadeIn + hold + readingFadeIn + readingHold + exit + gap;
    }

    anchorCompoundsExhibitDurationMs(t = this.timing, cardCount = 1) {
      return cardCount * this.anchorCompoundsCardDurationMs(t);
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
      if (
        this.isGalleryProfile ||
        this.isVocabularyExhibitionProfile ||
        this.isCompoundsExhibitionProfile ||
        this.isJapaneseVocabularyProfile
      ) {
        return true;
      }
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

    audioSrcMatches(audio, relativePath) {
      if (!audio?.src || !relativePath) return false;
      try {
        const expected = new URL(this.localUrl(relativePath), window.location.href).href;
        const current = new URL(audio.src, window.location.href).href;
        return expected === current;
      } catch {
        const tail = relativePath.replace(/^\.\//, "");
        return audio.src.endsWith(tail);
      }
    }

    async waitForAudioReady(audio, timeoutMs = 8000) {
      if (!audio || audio.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) return;
      await new Promise((resolve) => {
        let settled = false;
        const finish = () => {
          if (settled) return;
          settled = true;
          audio.removeEventListener("canplay", finish);
          audio.removeEventListener("loadeddata", finish);
          resolve();
        };
        audio.addEventListener("canplay", finish);
        audio.addEventListener("loadeddata", finish);
        window.setTimeout(finish, timeoutMs);
      });
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
      if (this.isGalleryProfile) {
        root.style.setProperty("--ex-transition", `${t.exhibitTransitionMs ?? 4000}ms`);
        root.style.setProperty(
          "--ex-artwork-arrival",
          `${t.artworkArrivalFadeMs ?? 2000}ms`
        );
        root.style.setProperty("--ken-burns-duration", `${t.kenBurnsDurationMs ?? 30000}ms`);
      }
      if (this.isVerseReadingProfile) {
        const stageFade = Math.max(
          t.readingHiraganaFadeMs ?? 1000,
          t.readingMixedFadeMs ?? 1000,
          t.readingNaturalFadeMs ?? 1000,
          t.readingEnFadeMs ?? 1000
        );
        root.style.setProperty("--ex-transition", `${t.exhibitTransitionMs ?? 4000}ms`);
        root.style.setProperty("--ex-verse-fade", `${stageFade}ms`);
        root.style.setProperty("--ken-burns-duration", `${t.kenBurnsDurationMs ?? 30000}ms`);
      }
      if (this.isAssistedReadingProfile) {
        root.style.setProperty("--ex-transition", `${t.exhibitTransitionMs ?? 4000}ms`);
        root.style.setProperty(
          "--ex-artwork-arrival",
          `${t.artworkArrivalFadeMs ?? 800}ms`
        );
        root.style.setProperty("--ex-verse-fade", `${t.readingJpFadeMs ?? 1000}ms`);
        root.style.setProperty(
          "--ex-furigana-fade",
          `${t.readingFuriganaFadeMs ?? 2500}ms`
        );
        root.style.setProperty("--ken-burns-duration", `${t.kenBurnsDurationMs ?? 45000}ms`);
      }
      if (this.isVocabularyExhibitionProfile) {
        root.style.setProperty("--ex-transition", `${t.exhibitTransitionMs ?? 3500}ms`);
        root.style.setProperty(
          "--ex-artwork-arrival",
          `${t.artworkArrivalFadeMs ?? 2000}ms`
        );
        root.style.setProperty(
          "--ex-verse-fade",
          `${t.vocabularyStepFadeMs ?? 1400}ms`
        );
        root.style.setProperty(
          "--ex-furigana-fade",
          `${t.vocabularyFuriganaFadeMs ?? 2200}ms`
        );
        root.style.setProperty("--ken-burns-duration", `${t.kenBurnsDurationMs ?? 60000}ms`);
      }
      if (this.isCompoundsExhibitionProfile) {
        root.style.setProperty("--ex-transition", `${t.exhibitTransitionMs ?? 3500}ms`);
        root.style.setProperty(
          "--ex-artwork-arrival",
          `${t.artworkArrivalFadeMs ?? 2000}ms`
        );
        root.style.setProperty(
          "--ex-verse-fade",
          `${t.compoundsStepFadeMs ?? 1400}ms`
        );
        root.style.setProperty(
          "--ex-furigana-fade",
          `${t.compoundsFuriganaFadeMs ?? 2200}ms`
        );
        root.style.setProperty(
          "--ex-compounds-fade",
          `${t.compoundsKanjiRevealMs ?? 1600}ms`
        );
        root.style.setProperty("--ken-burns-duration", `${t.kenBurnsDurationMs ?? 90000}ms`);
      }
      if (this.isAnchorCompoundsExhibitionProfile) {
        this.setAnchorCompoundsFadeTiming(this.timing);
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

    normalizeAssetsBase(base) {
      const clean = String(base || "./assets").replace(/\/$/, "");
      if (clean === "../../assets" || clean === "../assets") return "./assets";
      return clean;
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

    async showBookendImage(imagePath, fadeMs, bookendConfig = null, phase = "", options = {}) {
      if (!this.els.bookend || !this.els.bookendImg || !imagePath) return;
      if (phase) this.applyBookendPresentation(bookendConfig, phase);
      this.applyBookendStamp(bookendConfig, phase);
      const url = this.bookendImageUrl(imagePath);
      document.documentElement.style.setProperty("--ex-bookend-fade", `${fadeMs}ms`);
      this.els.bookendImg.src = url;
      this.els.bookendImg.alt = "";
      await this.waitForArtworkImage(this.els.bookendImg);
      if (!this.els.bookendImg.naturalWidth) {
        this.audioError("bookend image failed to load", null, { url });
      }
      if (typeof options.onImageReady === "function") {
        options.onImageReady();
      }
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
      const mainPath = this.soundtrack?.main || null;

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
        src: mainPath,
      });

      if (mainPath && this.mainAudio) {
        this.mainAudio.load();
      }
    }

    ensureMainAudioSrc() {
      const path = this.soundtrack?.main;
      if (!path) return null;
      const audio = this.audioEl("main");
      if (!this.audioSrcMatches(audio, path)) {
        audio.src = this.localUrl(path);
        audio.loop = false;
        audio.load();
      }
      return audio;
    }

    /** Must run synchronously inside a user-gesture handler (click / key). */
    playSoundtrackFromUserGesture() {
      const path = this.soundtrack?.main;
      if (!path) return false;

      const audio = this.ensureMainAudioSrc();
      if (!audio) return false;
      if (!audio.paused && !audio.ended) {
        this._soundtrackStarted = true;
        return true;
      }

      try {
        audio.currentTime = 0;
        this._soundtrackStarted = true;
        const playPromise = audio.play();
        if (playPromise) {
          playPromise
            .then(() => {
              this.audioLog("soundtrack started", {
                path,
                via: "user gesture",
                src: audio.currentSrc || audio.src,
              });
            })
            .catch((err) => {
              this._soundtrackStarted = false;
              this.audioError("soundtrack play() error", err, { path, via: "user gesture" });
            });
        }
        return true;
      } catch (err) {
        this._soundtrackStarted = false;
        this.audioError("soundtrack play() error", err, { path, via: "user gesture" });
        return false;
      }
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

    isSilentGalleryCrestBookends() {
      if (this.bookends?.mode === "silentCrest") return true;
      if (this.display.bookendStyle !== "galleryCrest") return false;
      const opening = this.bookends?.opening;
      const closing = this.bookends?.closing;
      return Boolean(opening?.image && closing?.image && !opening?.audio && !closing?.audio);
    }

    shouldStartSoundtrackDuringOpening(opening) {
      if (!this.soundtrack?.main || !opening) return false;
      const hasVisual = Boolean(opening.image || opening.images?.length);
      if (!hasVisual) return false;
      if (opening.startSoundtrackWithImage === false) return false;
      if (opening.startSoundtrackWithImage === true) return true;
      if (opening.images?.length && this.isJapaneseVocabularyProfile) return true;
      if (this.timing.openingStartSoundtrackWithImage === true) return true;
      return (
        this.display.family === "kanjiSoundtrack" ||
        this.display.family === "grade1KanjiSoundtrack" ||
        this.display.family === "grade2KanjiSoundtrack" ||
        this.display.family === "grade3KanjiSoundtrack" ||
        this.display.family === "grade4KanjiSoundtrack" ||
        Boolean(this.display.musicalTiming)
      );
    }

    scheduleSoundtrackAfterBookendImage(stillRunning, opening) {
      const t = this.timing;
      const delayMs =
        opening.startSoundtrackAfterImageMs ?? t.openingSoundtrackDelayMs ?? 1400;
      void (async () => {
        await this.wait(delayMs);
        if (!stillRunning()) return;
        await this.startSoundtrack();
      })();
    }

    shouldStartSoundtrackWithFirstScene() {
      if (!this.soundtrack?.main) return false;
      if (
        this.isAssistedReadingProfile ||
        this.isGalleryProfile ||
        this.isVocabularyExhibitionProfile ||
        this.isCompoundsExhibitionProfile ||
        this.isJapaneseVocabularyProfile ||
        this.isAnchorCompoundsExhibitionProfile ||
        this.isStrokeOrderProfile ||
        this.isGrade1KanjiSoundtrackProfile ||
        this.isHiraganaSongProfile
      ) {
        return true;
      }
      return Boolean(this.isSilentGalleryCrestBookends() && !this.skipBookends);
    }

    get deferSoundtrackUntilFirstScene() {
      return (
        (this.timing.exhibitionBlackBeforeMs ?? 0) > 0 &&
        this.shouldStartSoundtrackWithFirstScene()
      );
    }

    shouldDeferSoundtrackForOpening() {
      if (!this.soundtrack?.main || this.skipBookends) return false;
      return this.shouldStartSoundtrackDuringOpening(this.bookends?.opening);
    }

    get shouldDeferMainSoundtrack() {
      return this.deferSoundtrackUntilFirstScene || this.shouldDeferSoundtrackForOpening();
    }

    probeUnlockAudio(audio, via = "gesture") {
      if (!audio) return;
      try {
        const playPromise = audio.play();
        if (playPromise) {
          playPromise
            .then(() => {
              audio.pause();
              audio.currentTime = 0;
              this.audioLog("autoplay unlocked", {
                via,
                src: audio.currentSrc || audio.src,
              });
            })
            .catch((err) => {
              this.audioError("autoplay unlock error", err, { via });
            });
        }
      } catch (err) {
        this.audioError("autoplay unlock error", err, { via });
      }
    }

    getSoundtrackRemainingMs() {
      const audio = this.mainAudio;
      if (!audio || audio.paused || audio.ended) return 0;
      const duration = audio.duration;
      if (!Number.isFinite(duration) || duration <= 0) return 0;
      return Math.max(0, (duration - audio.currentTime) * 1000);
    }

    ensureSoundtrackStarted() {
      const audio = this.mainAudio;
      if (audio && !audio.paused && !audio.ended) {
        this._soundtrackStarted = true;
        return;
      }
      if (this._soundtrackStarted) return;
      void this.startSoundtrack();
    }

    maybeStartSoundtrackForScene(index) {
      if (index !== 0 || !this.shouldStartSoundtrackWithFirstScene()) return;
      if (this.shouldDeferSoundtrackForOpening()) return;
      this.ensureSoundtrackStarted();
    }

    async fadeBookendWithSoundtrackEnd(fadeMs, hideFn) {
      const remaining = this.getSoundtrackRemainingMs();
      const resolvedFadeMs =
        remaining > 0 ? Math.max(500, Math.min(fadeMs, remaining)) : fadeMs;
      const audio = this.mainAudio;
      const promises = [hideFn(resolvedFadeMs)];
      if (audio && !audio.ended && !audio.paused) {
        promises.push(this.waitForAudioEnd(audio));
      }
      await Promise.all(promises);
      this.stopSoundtrack();
    }

    async fadeOutSoundtrack(fadeMs) {
      const audio = this.mainAudio;
      if (!audio || audio.paused || audio.ended) return;
      const startVolume = audio.volume;
      const steps = Math.max(1, Math.round(fadeMs / 50));
      const stepMs = fadeMs / steps;
      for (let i = 1; i <= steps; i++) {
        if (this.destroyed) return;
        audio.volume = startVolume * (1 - i / steps);
        await this.wait(stepMs);
      }
      audio.volume = startVolume;
      this.stopSoundtrack();
    }

    async fadeBookendWithSoundtrack(fadeMs, hideFn) {
      const audio = this.mainAudio;
      const promises = [hideFn(fadeMs)];
      if (audio && !audio.ended && !audio.paused) {
        promises.push(this.fadeOutSoundtrack(fadeMs));
      }
      await Promise.all(promises);
      this.stopSoundtrack();
    }

    async fadeCrestWithSoundtrackEnd(crestFadeMs) {
      await this.fadeBookendWithSoundtrackEnd(crestFadeMs, (ms) => this.hideBookendCrest(ms));
    }

    async fadeClosingImageWithSoundtrackEnd(fadeMs) {
      await this.fadeBookendWithSoundtrackEnd(fadeMs, (ms) => this.hideBookendImage(ms));
    }

    async fadeClosingImageWithSoundtrack(fadeMs) {
      await this.fadeBookendWithSoundtrack(fadeMs, (ms) => this.hideBookendImage(ms));
    }

    async ensureAudioUnlocked() {
      if (this.audioUnlocked || !this.hasExhibitionAudio()) return;
      if (!this.bookendAudio && !this.mainAudio) this.initAudio();

      const introPath = this.bookends?.opening?.audio;
      if (!introPath) {
        const audio = this.ensureMainAudioSrc();
        if (!audio) return;
        await this.waitForAudioReady(audio);
        try {
          await audio.play();
          if (!audio.paused) {
            this.audioUnlocked = true;
            if (this.shouldDeferMainSoundtrack) {
              audio.pause();
              audio.currentTime = 0;
              this.audioLog("soundtrack autoplay ok (deferred for opening schedule)", {
                src: audio.currentSrc || audio.src,
                delayMs:
                  this.bookends?.opening?.startSoundtrackAfterImageMs ??
                  this.timing.openingSoundtrackDelayMs,
              });
              return;
            }
            this._soundtrackStarted = true;
            this.audioLog("soundtrack autoplay ok", { src: audio.currentSrc || audio.src });
            return;
          }
        } catch (err) {
          if (err.name !== "NotAllowedError") {
            this.audioError("soundtrack autoplay error", err, { src: audio.currentSrc || audio.src });
          }
        }
        this.audioLog("soundtrack-only exhibition — autoplay gate", {});
        await this.waitForAutoplayGate();
        return;
      }

      const audio = this.bookendAudio;
      if (!audio) return;

      try {
        const playPromise = audio.play();
        if (playPromise) {
          await Promise.race([
            playPromise,
            new Promise((resolve) => setTimeout(resolve, 500)),
          ]);
        }
        audio.pause();
        audio.currentTime = 0;
        this.audioUnlocked = true;
        this.audioLog("autoplay unlocked", { src: audio.currentSrc || audio.src });
        return;
      } catch (err) {
        if (err.name !== "NotAllowedError") {
          this.audioError("autoplay probe error", err, { src: audio.currentSrc || audio.src });
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
        const onDocumentKeyDown = (e) => {
          if (e.code === "Enter" || e.code === "Space") {
            e.preventDefault();
            finish();
          }
        };
        const finish = () => {
          if (settled) return;
          settled = true;

          gate.classList.remove("is-visible");
          gate.classList.add("exhibition-hidden");
          gate.removeEventListener("keydown", onKeyDown);
          document.removeEventListener("keydown", onDocumentKeyDown);

          if (!this.bookendAudio && !this.mainAudio) this.initAudio();

          const introPath = this.bookends?.opening?.audio;
          if (!introPath && this.soundtrack?.main) {
            if (this.shouldDeferMainSoundtrack) {
              this.probeUnlockAudio(this.ensureMainAudioSrc(), "autoplay gate (soundtrack deferred)");
            } else {
              this.playSoundtrackFromUserGesture();
              this.audioLog("autoplay unlocked", { via: "autoplay gate (soundtrack)" });
            }
          } else {
            const audio = this.bookendAudio || this.mainAudio;
            if (audio) {
              this.probeUnlockAudio(audio, "autoplay gate");
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
        document.addEventListener("keydown", onDocumentKeyDown);
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
      if (!path) return false;

      const audio = this.ensureMainAudioSrc();
      if (!audio) return false;
      if (!audio.paused && !audio.ended) {
        this._soundtrackStarted = true;
        return true;
      }

      await this.waitForAudioReady(audio);

      try {
        await audio.play();
        this._soundtrackStarted = true;
        this.audioLog("soundtrack started", { path, src: audio.currentSrc || audio.src });
        this.debugLog("soundtrack started", { path });
        return true;
      } catch (err) {
        this._soundtrackStarted = false;
        this.audioError("soundtrack play() error", err, { path });
        this.debugLog("soundtrack unavailable", { path, error: err.message });
        return false;
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
      this.setKanjiCentered(false);
      this.setClass(kanji, "is-visible", false);
      this.setClass(kanji, "is-exhaling", false);
      this.setClass(kanji, "is-floating", false);
      kanji?.classList.remove("is-target-return");
      this.setClass(keyword, "is-visible", false);
      this.setClass(verseJp, "is-visible", false);
      this.setClass(verseEn, "is-visible", false);
      this.setClass(verseEn, "is-reading-reflection", false);
      if (verseJp) {
        verseJp.classList.remove(
          "show-furigana",
          "is-furigana-entering",
          "is-furigana-fading",
          "is-furigana-hidden",
          "is-vocab-verse-reveal",
          "has-vocab-readings"
        );
        verseJp.textContent = "";
        verseJp.innerHTML = "";
      }
      if (verseEn) {
        verseEn.textContent = "";
        verseEn.classList.remove("is-vocab-verse-reveal");
      }
    }

    setReadingStageContent(html) {
      if (!this.els.verseJp) return;
      this.els.verseJp.lang = "ja";
      this.els.verseJp.innerHTML = html || "";
      this.els.verseJp.classList.remove(
        "has-authored-lines",
        "show-furigana",
        "is-furigana-fading",
        "is-furigana-hidden"
      );
    }

    setAssistedVerseContent(jpHtml) {
      if (!this.els.verseJp) return;
      const raw = jpHtml || "";
      this.els.verseJp.lang = "ja";
      this.els.verseJp.innerHTML = this.formatVerseHtml(raw);
      const authored =
        this.useAuthoredVerseLayout() &&
        window.KmlVerseDisplay?.usesAuthoredLines(raw);
      this.els.verseJp.classList.toggle("has-authored-lines", Boolean(authored));
      this.els.verseJp.classList.add("show-furigana", "is-furigana-hidden");
      this.els.verseJp.classList.remove("is-furigana-entering", "is-furigana-fading");
    }

    vocabularyStepUsesFurigana(step) {
      return Boolean(step?.furigana || step?.jpHtml);
    }

    async playVocabularyFuriganaOut(stillRunning, fadeMs) {
      const verseJp = this.els.verseJp;
      if (!verseJp) return;
      document.documentElement.style.setProperty(
        "--ex-furigana-fade",
        `${fadeMs}ms`
      );
      verseJp.classList.add("is-furigana-fading");
      await this.wait(fadeMs);
      if (!stillRunning()) return;
      verseJp.classList.remove("is-furigana-fading");
      verseJp.classList.add("is-furigana-hidden");
    }

    setVocabularyStepContent(step) {
      if (!this.els.verseJp || !step) return;
      const jp = step.jp || "";
      const reading = step.reading || "";
      const phrase = Boolean(step.phrase);
      const commonReadings = step.commonReadings || "";
      const verseJp = this.els.verseJp;

      verseJp.lang = "ja";
      verseJp.classList.remove(
        "has-authored-lines",
        "show-furigana",
        "is-furigana-entering",
        "is-furigana-fading",
        "is-furigana-hidden",
        "is-vocab-verse-reveal",
        "has-vocab-readings"
      );
      verseJp.textContent = "";
      verseJp.innerHTML = "";

      if (commonReadings && reading) {
        verseJp.classList.add("has-vocab-readings");
        const main = document.createElement("span");
        main.className = "kml-vocab-jp-main";
        main.textContent = jp;
        verseJp.appendChild(main);

        const block = document.createElement("span");
        block.className = "kml-vocab-reading-block";

        const verseRow = document.createElement("span");
        verseRow.className = "kml-vocab-reading-row";
        const verseLabel = document.createElement("span");
        verseLabel.className = "kml-vocab-reading-label";
        verseLabel.textContent = "Verse:";
        verseRow.appendChild(verseLabel);
        verseRow.appendChild(document.createTextNode(` ${reading}`));
        block.appendChild(verseRow);

        const usualRow = document.createElement("span");
        usualRow.className = "kml-vocab-reading-row";
        const usualLabel = document.createElement("span");
        usualLabel.className = "kml-vocab-reading-label";
        usualLabel.textContent = "Usually:";
        usualRow.appendChild(usualLabel);
        usualRow.appendChild(document.createTextNode(` ${commonReadings}`));
        block.appendChild(usualRow);

        verseJp.appendChild(block);
      } else if (this.vocabularyStepUsesFurigana(step)) {
        verseJp.innerHTML = step.jpHtml || jp;
        verseJp.classList.add("show-furigana", "is-furigana-hidden");
        verseJp.classList.remove("is-furigana-entering", "is-furigana-fading");
      } else if (phrase || !reading) {
        verseJp.textContent = jp;
      } else {
        verseJp.textContent = `${jp}（${reading}）`;
      }

      if (this.els.verseEn) {
        this.els.verseEn.textContent = step.en || "";
        this.els.verseEn.classList.remove("is-reading-reflection");
      }
    }

    setVocabularyVerseReveal(jpHtml) {
      if (!this.els.verseJp) return;
      const raw = jpHtml || "";
      this.els.verseJp.lang = "ja";
      this.els.verseJp.innerHTML = this.formatVerseHtml(raw);
      const authored =
        this.useAuthoredVerseLayout() &&
        window.KmlVerseDisplay?.usesAuthoredLines(raw);
      this.els.verseJp.classList.toggle("has-authored-lines", Boolean(authored));
      this.els.verseJp.classList.add("is-vocab-verse-reveal", "show-furigana", "is-furigana-hidden");
      this.els.verseJp.classList.remove(
        "is-furigana-entering",
        "is-furigana-fading"
      );
      if (this.els.verseEn) {
        this.els.verseEn.textContent = "";
      }
    }

    async playFuriganaFadeIn(stillRunning, durationMs) {
      const verseJp = this.els.verseJp;
      if (!verseJp) return;
      verseJp.classList.add("is-furigana-entering");
      verseJp.classList.remove("is-furigana-hidden");
      void verseJp.offsetHeight;
      verseJp.classList.remove("is-furigana-entering");
      await this.wait(durationMs);
      if (!stillRunning()) return;
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
      const sceneId = scene.id || "";
      if (
        layer.img.dataset.kmlLoadedSrc === src &&
        layer.img.dataset.kmlSceneId === sceneId
      ) {
        this.applyImageFraming(layer.img, scene);
        return;
      }
      layer.img.classList.remove("ken-burns", "gallery-guardian");
      layer.img.removeAttribute("data-gallery-shot");
      layer.img.src = src;
      layer.img.dataset.kmlLoadedSrc = src;
      layer.img.dataset.kmlSceneId = sceneId;
      layer.img.alt = scene.kanji || "";
      this.applyImageFraming(layer.img, scene);
    }

    async finalExhibitConclusion(stillRunning, t = this.timing) {
      const activeWrap = this.els.artwork;
      const exhaleMs = Math.round(t.imageExhaleFadeMs * this.timingScale);
      const holdMs = Math.round(
        (t.finalKanjiAloneHoldMs ?? t.kanjiAloneHoldMs ?? 0) * this.timingScale
      );
      const kanjiFadeMs = Math.round(t.kanjiExhaleFadeMs * this.timingScale);

      document.documentElement.style.setProperty("--ex-exhale", `${exhaleMs}ms`);
      this.setClass(activeWrap, "is-exhaling", true);
      await this.wait(exhaleMs);
      if (!stillRunning()) return;

      if (holdMs > 0) {
        await this.wait(holdMs);
        if (!stillRunning()) return;
      }

      document.documentElement.style.setProperty("--ex-kanji-exhale", `${kanjiFadeMs}ms`);
      this.setClass(this.els.kanji, "is-exhaling", true);
      await this.wait(kanjiFadeMs);
      if (!stillRunning()) return;

      this.setClass(this.els.kanji, "is-visible", false);
      this.setClass(this.els.kanji, "is-exhaling", false);
    }

    /** Image A exhale → Image B arrival; kanji bridges the handoff (no black hold). */
    async galleryBridgeHandoff(nextScene, stillRunning, t = this.timing) {
      const { exhaleMs, arrivalMs, kanjiBridgeMs } = this.galleryBridgeTiming(t);
      const scaledExhale = Math.round(exhaleMs * this.timingScale);
      const scaledArrival = Math.round(arrivalMs * this.timingScale);
      const scaledKanji = Math.round(kanjiBridgeMs * this.timingScale);

      const activeKey = this.activeArtworkKey;
      const inactiveKey = activeKey === "a" ? "b" : "a";
      const active = this.artworkLayers[activeKey];
      const inactive = this.artworkLayers[inactiveKey];
      if (!active?.wrap || !inactive?.wrap) return;

      document.documentElement.style.setProperty("--ex-exhale", `${scaledExhale}ms`);
      this.setClass(active.wrap, "is-exhaling", true);
      await this.wait(scaledExhale);
      if (!stillRunning()) return;

      this.populateArtworkLayer(inactiveKey, nextScene);
      await this.applySceneCameraToImage(inactive.img, nextScene);
      if (!stillRunning()) return;

      document.documentElement.style.setProperty("--ex-transition", `${scaledArrival}ms`);
      this.setClass(inactive.wrap, "is-exhaling", false);
      this.setClass(inactive.wrap, "is-on-top", true);
      this.setClass(inactive.wrap, "is-visible", true);

      document.documentElement.style.setProperty("--ex-kanji-exhale", `${scaledKanji}ms`);
      this.setClass(this.els.kanji, "is-exhaling", true);

      await this.wait(scaledArrival);
      if (!stillRunning()) return;

      this.setClass(this.els.kanji, "is-visible", false);
      this.setClass(this.els.kanji, "is-exhaling", false);
      document.documentElement.style.setProperty(
        "--ex-kanji-exhale",
        `${t.kanjiExhaleFadeMs}ms`
      );

      this.setClass(active.wrap, "is-visible", false);
      this.setClass(active.wrap, "is-exhaling", false);
      this.setClass(inactive.wrap, "is-on-top", false);
      this.activeArtworkKey = inactiveKey;
      this.syncLegacyArtworkRefs();

      this.setClass(this.els.veil, "is-corridor", false);
      this.setClass(this.els.veil, "is-clear", true);
    }

    async crossfadeArtworkLayers(nextScene, fadeMs, options = {}) {
      const inactiveKey = this.activeArtworkKey === "a" ? "b" : "a";
      const activeKey = this.activeArtworkKey;
      const inactive = this.artworkLayers[inactiveKey];
      const active = this.artworkLayers[activeKey];
      if (!inactive?.wrap || !active?.wrap) return;

      this.populateArtworkLayer(inactiveKey, nextScene);
      if (options.still) {
        inactive.img?.classList.remove("ken-burns", "gallery-guardian");
        await this.waitForArtworkImage(inactive.img);
      } else {
        await this.applySceneCameraToImage(inactive.img, nextScene);
      }

      document.documentElement.style.setProperty("--ex-transition", `${fadeMs}ms`);
      if (this.isImageVerseProfile || this.isGalleryProfile) {
        document.documentElement.style.setProperty("--ex-exhale", `${fadeMs}ms`);
      }

      this.setClass(inactive.wrap, "is-exhaling", false);
      this.setClass(inactive.wrap, "is-on-top", true);
      this.setClass(inactive.wrap, "is-visible", true);
      this.setClass(active.wrap, "is-exhaling", true);

      await this.wait(fadeMs);

      this.onlyShowArtworkLayer(inactiveKey);
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
      this.resetVocabularyIntroOverlay();
      this.root?.classList.remove("is-opening-image-sequence");
      this.resetStrokeOrderLayer();
      this.resetAnchorCompoundsLayer();
      this.resetHiraganaSongLayer();
    }

    resetHiraganaSongLayer() {
      const layer = this.els.hiraganaSongLayer;
      if (!layer) return;
      layer.classList.add("exhibition-hidden");
      layer.classList.remove(
        "is-visible",
        "is-exhaling",
        "is-drifting",
        "is-zooming-out",
        "is-equal",
        "is-romaji-mode"
      );
      layer.setAttribute("aria-hidden", "true");
      document.documentElement.style.removeProperty("--hiragana-song-fade");
      document.documentElement.style.removeProperty("--hiragana-song-drift");
      document.documentElement.style.removeProperty("--hiragana-song-zoom");
      window.KmlHiraganaSongChart?.clearFocus(this.els.hiraganaSongChart);
    }

    resetAnchorCompoundsLayer() {
      const { anchorCompoundsLayer, anchorCompoundsWord, anchorCompoundsReading } = this.els;
      anchorCompoundsLayer?.classList.add("exhibition-hidden");
      this.clearAnchorCompoundsContent();
      anchorCompoundsWord?.classList.remove("is-visible", "is-fading-out", "is-receding", "is-softened");
      anchorCompoundsReading?.classList.remove("is-visible", "is-fading-out");
      if (anchorCompoundsWord) {
        anchorCompoundsWord.style.removeProperty("--ex-grade1-kanji-color");
        anchorCompoundsWord.style.removeProperty("color");
      }
      if (anchorCompoundsReading) {
        anchorCompoundsReading.style.removeProperty("color");
      }
      this._anchorCompoundsLayerVisible = false;
    }

    clearAnchorCompoundsContent() {
      const { anchorCompoundsWord, anchorCompoundsReading } = this.els;
      if (anchorCompoundsWord) {
        anchorCompoundsWord.textContent = "";
        anchorCompoundsWord.innerHTML = "";
        this.clearAnchorWordScale(anchorCompoundsWord);
      }
      if (anchorCompoundsReading) {
        anchorCompoundsReading.textContent = "";
      }
    }

    setAnchorCompoundsFadeTiming(t = this.timing) {
      document.documentElement.style.setProperty(
        "--ex-anchor-fade-in",
        `${t.anchorWordFadeInMs ?? 700}ms`
      );
      document.documentElement.style.setProperty(
        "--ex-anchor-reading-fade-in",
        `${t.anchorReadingFadeInMs ?? 450}ms`
      );
      document.documentElement.style.setProperty(
        "--ex-anchor-transition",
        `${t.anchorTransitionMs ?? 600}ms`
      );
      document.documentElement.style.setProperty(
        "--ex-anchor-fade-out",
        `${t.anchorCardFadeOutMs ?? 500}ms`
      );
      document.documentElement.style.setProperty(
        "--kml-anchor-crossfade-ghost",
        String(t.anchorCrossfadeGhostOpacity ?? 0.25)
      );
      document.documentElement.style.setProperty(
        "--kml-anchor-stacked-soft-opacity",
        String(t.anchorStackedWordSoftOpacity ?? 0.82)
      );
    }

    applyAnchorCompoundsColors(scene) {
      const color = scene?.meta?.kanjiColor || "#2c2824";
      const wordEl = this.els.anchorCompoundsWord;
      const readingEl = this.els.anchorCompoundsReading;
      if (wordEl) {
        wordEl.style.setProperty("--ex-grade1-kanji-color", color);
        wordEl.style.color = color;
      }
      if (readingEl) {
        readingEl.style.color = color;
      }
    }

    setAnchorCompoundsContent(scene) {
      const anchor = scene?.anchor || {};
      const word = anchor.word || "";
      const emphasize = anchor.visualWeightTarget || anchor.emphasize;
      const wordEl = this.els.anchorCompoundsWord;
      const readingEl = this.els.anchorCompoundsReading;

      if (!wordEl || !readingEl) return;

      wordEl.textContent = "";
      wordEl.innerHTML = "";

      if (emphasize && word.includes(emphasize)) {
        let index = 0;
        while (index < word.length) {
          const hit = word.indexOf(emphasize, index);
          if (hit === -1) {
            wordEl.appendChild(document.createTextNode(word.slice(index)));
            break;
          }
          if (hit > index) {
            wordEl.appendChild(document.createTextNode(word.slice(index, hit)));
          }
          const span = document.createElement("span");
          span.className = "kml-anchor-emphasis";
          span.textContent = emphasize;
          wordEl.appendChild(span);
          index = hit + emphasize.length;
        }
      } else {
        wordEl.textContent = word;
      }

      readingEl.textContent = anchor.reading || "";
      this.applyAnchorCompoundsColors(scene);
      this.applyAnchorWordScale(wordEl, word, anchor.wordScale);
    }

    applyAnchorWordScale(wordEl, word, presetScale) {
      if (!wordEl || !word) return;
      const layout = window.KmlAnchorCompoundsLayout;
      if (layout) {
        layout.applyCompoundWordScale(wordEl, word);
        if (presetScale != null) {
          wordEl.style.setProperty("--kml-compound-word-scale", String(presetScale));
        }
        return;
      }
      const n = [...word].length;
      let scale = 1;
      if (n === 3) scale = 0.74;
      else if (n === 4) scale = 0.56;
      else if (n >= 5) scale = 0.48;
      if (presetScale != null) scale = presetScale;
      wordEl.style.setProperty("--kml-compound-word-scale", String(scale));
    }

    clearAnchorWordScale(wordEl) {
      window.KmlAnchorCompoundsLayout?.clearCompoundWordScale(wordEl);
      wordEl?.style.removeProperty("--kml-compound-word-scale");
    }

    resetAnchorCompoundsCardVisuals() {
      const { anchorCompoundsWord, anchorCompoundsReading } = this.els;
      anchorCompoundsWord?.classList.remove("is-visible", "is-fading-out", "is-receding", "is-softened");
      anchorCompoundsReading?.classList.remove("is-visible", "is-fading-out");
    }

    async playAnchorCompoundsStackedCard(stillRunning, wordEl, readingEl, t) {
      const fadeIn = t.anchorWordFadeInMs ?? 700;
      const hold = t.anchorWordHoldMs ?? 2500;
      const readingFadeIn = t.anchorReadingFadeInMs ?? 450;
      const readingHold = t.anchorReadingHoldMs ?? 1400;
      const exit = t.anchorCardFadeOutMs ?? 500;

      wordEl?.classList.add("is-visible");
      await this.wait(fadeIn);
      if (!stillRunning()) return;
      await this.wait(hold);
      if (!stillRunning()) return;

      wordEl?.classList.add("is-softened");
      readingEl?.classList.add("is-visible");
      await this.wait(readingFadeIn);
      if (!stillRunning()) return;
      await this.wait(readingHold);
      if (!stillRunning()) return;

      wordEl?.classList.add("is-fading-out");
      readingEl?.classList.add("is-fading-out");
      wordEl?.classList.remove("is-visible", "is-softened");
      readingEl?.classList.remove("is-visible");
      await this.wait(exit);
    }

    async playAnchorCompoundsReplaceCard(stillRunning, wordEl, readingEl, t) {
      const fadeIn = t.anchorWordFadeInMs ?? 700;
      const hold = t.anchorWordHoldMs ?? 2200;
      const transition = t.anchorTransitionMs ?? 600;
      const readingHold = t.anchorReadingHoldMs ?? 1200;
      const exit = t.anchorCardFadeOutMs ?? 500;

      wordEl?.classList.add("is-visible");
      await this.wait(fadeIn);
      if (!stillRunning()) return;
      await this.wait(hold);
      if (!stillRunning()) return;

      wordEl?.classList.add("is-fading-out");
      wordEl?.classList.remove("is-visible");
      await this.wait(transition);
      if (!stillRunning()) return;
      wordEl?.classList.remove("is-fading-out");

      readingEl?.classList.add("is-visible");
      await this.wait(transition);
      if (!stillRunning()) return;
      await this.wait(readingHold);
      if (!stillRunning()) return;

      readingEl?.classList.add("is-fading-out");
      readingEl?.classList.remove("is-visible");
      await this.wait(exit);
    }

    async playAnchorCompoundsCrossfadeCard(stillRunning, wordEl, readingEl, t) {
      const fadeIn = t.anchorWordFadeInMs ?? 700;
      const hold = t.anchorWordHoldMs ?? 2200;
      const transition = t.anchorTransitionMs ?? 600;
      const readingHold = t.anchorReadingHoldMs ?? 1200;
      const exit = t.anchorCardFadeOutMs ?? 500;

      wordEl?.classList.add("is-visible");
      await this.wait(fadeIn);
      if (!stillRunning()) return;
      await this.wait(hold);
      if (!stillRunning()) return;

      wordEl?.classList.add("is-receding");
      await this.wait(transition);
      if (!stillRunning()) return;

      readingEl?.classList.add("is-visible");
      await this.wait(transition);
      if (!stillRunning()) return;
      await this.wait(readingHold);
      if (!stillRunning()) return;

      wordEl?.classList.add("is-fading-out");
      readingEl?.classList.add("is-fading-out");
      wordEl?.classList.remove("is-visible", "is-receding");
      readingEl?.classList.remove("is-visible");
      await this.wait(exit);
    }

    resetStrokeOrderLayer() {
      const { strokeOrderLayer } = this.els;
      strokeOrderLayer?.classList.add("exhibition-hidden");
      this.resetSoundtrackSlot("a");
      this.resetSoundtrackSlot("b");
      this.activeSoundtrackSlot = "a";
      this._soundtrackCrossfadedTo = -1;
      this.clearGrade1Confetti();
      this.clearStrokeOrderComplexity();
    }

    resetSoundtrackSlot(key) {
      const slot = this.soundtrackSlots?.[key];
      if (!slot) return;
      slot.slot?.classList.remove("is-active", "is-on-top", "is-handoff-out", "is-handoff");
      if (slot.kanji) {
        slot.kanji.textContent = "";
        slot.kanji.classList.remove("is-visible", "is-dissolving");
      }
    }

    inactiveSoundtrackSlotKey() {
      return this.activeSoundtrackSlot === "a" ? "b" : "a";
    }

    setSoundtrackSlotOnTop(key, { keepActive = null } = {}) {
      Object.entries(this.soundtrackSlots || {}).forEach(([slotKey, slot]) => {
        slot.slot?.classList.toggle("is-on-top", slotKey === key);
        if (keepActive === null) {
          slot.slot?.classList.toggle("is-active", slotKey === key);
        }
      });
      if (Array.isArray(keepActive)) {
        Object.entries(this.soundtrackSlots || {}).forEach(([slotKey, slot]) => {
          slot.slot?.classList.toggle("is-active", keepActive.includes(slotKey));
        });
      }
    }

    setSoundtrackHandoffTiming(fadeInMs, fadeOutMs) {
      document.documentElement.style.setProperty(
        "--ex-soundtrack-kanji-fade-in",
        `${fadeInMs}ms`
      );
      document.documentElement.style.setProperty(
        "--ex-soundtrack-kanji-fade-out",
        `${fadeOutMs}ms`
      );
    }

    async populateSoundtrackSlot(key, scene) {
      const slot = this.soundtrackSlots?.[key];
      if (!slot?.kanji) return;

      const kanji = scene.kanji || "";
      slot.kanji.textContent = kanji;
      slot.kanji.classList.remove("is-visible");
    }

    soundtrackMusical(scene) {
      const m = scene?.musical || {};
      return {
        kanjiFadeInMs: m.kanjiFadeInMs ?? 2600,
        kanjiHoldMs: m.kanjiHoldMs ?? 0,
        kanjiFadeOutMs: m.kanjiFadeOutMs ?? 1400,
      };
    }

    async runSoundtrackKanjiCycle(slotKey, scene, stillRunning) {
      const slot = this.soundtrackSlots[slotKey];
      if (!slot?.kanji) return;

      const m = this.soundtrackMusical(scene);
      const { kanji: kanjiEl } = slot;

      this.setSoundtrackSlotOnTop(slotKey);
      slot.slot?.classList.add("is-active");

      // Count 1 — fade in (slower than one beat, same 4s bar)
      this.setSoundtrackHandoffTiming(m.kanjiFadeInMs, m.kanjiFadeOutMs);
      kanjiEl.classList.remove("is-visible");
      void kanjiEl.offsetWidth;
      kanjiEl.classList.add("is-visible");
      await this.wait(m.kanjiFadeInMs);
      if (!stillRunning()) return;

      // Counts 2–3 — kanji held on screen
      await this.wait(m.kanjiHoldMs);
      if (!stillRunning()) return;

      // Count 4 — fade out to black
      kanjiEl.classList.remove("is-visible");
      await this.wait(m.kanjiFadeOutMs);
    }

    async playKanjiSoundtrackExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const slotKey = this.activeSoundtrackSlot;

      if (index === 0) {
        this.resetLayers();
        await this.populateSoundtrackSlot(slotKey, scene);
        if (!stillRunning()) return;
        this.els.strokeOrderLayer?.classList.remove("exhibition-hidden");
        this.setClass(this.els.veil, "is-clear", true);
        await this.waitInitialExhibitionBlack(stillRunning, 0);
        if (!stillRunning()) return;
        this.maybeStartSoundtrackForScene(0);
      } else {
        await this.populateSoundtrackSlot(slotKey, scene);
        if (!stillRunning()) return;
      }

      await this.runSoundtrackKanjiCycle(slotKey, scene, stillRunning);
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
          this.resetStrokeOrderLayer();
          this.activeSoundtrackSlot = "a";
          await this.playKanjiSoundtrackExhibit(0);
        } else if (this.bookends?.closing) {
          this.resetStrokeOrderLayer();
          await this.playClosingBookend();
        }
        return;
      }

      await this.playKanjiSoundtrackExhibit(next);
    }

    grade1Musical(scene) {
      const m = scene?.musical || {};
      return {
        kanjiFadeInMs: m.kanjiFadeInMs ?? 3000,
        kanjiHoldMs: m.kanjiHoldMs ?? 1600,
        kanjiFadeOutMs: m.kanjiFadeOutMs ?? 2200,
        crossfadeMs: m.crossfadeMs ?? 450,
      };
    }

    setGrade1HandoffTiming(fadeInMs, fadeOutMs) {
      document.documentElement.style.setProperty(
        "--ex-grade1-kanji-fade-in",
        `${fadeInMs}ms`
      );
      document.documentElement.style.setProperty(
        "--ex-grade1-kanji-fade-out",
        `${fadeOutMs}ms`
      );
    }

    applyGrade1KanjiColor(kanjiEl, scene) {
      const color = scene?.meta?.kanjiColor || "#1e88e5";
      if (kanjiEl) {
        kanjiEl.style.setProperty("--ex-grade1-kanji-color", color);
        kanjiEl.style.color = color;
      }
    }

    showGrade4Layer() {
      this.els.g4Layer?.classList.remove("exhibition-hidden");
      this.setClass(this.els.veil, "is-clear", true);
    }

    hideGrade4KanjiHero() {
      this.els.g4KanjiHero?.classList.remove("is-kanji-visible");
      this.g4SoundtrackSlots?.a?.kanji?.classList.remove("is-visible");
      this.g4SoundtrackSlots?.b?.kanji?.classList.remove("is-visible");
    }

    grade4SectionCounts() {
      const counts = {};
      for (const scene of this.scenes) {
        if (!scene.kanji) continue;
        const key = scene.meta?.gojuonSection;
        if (!key) continue;
        counts[key] = (counts[key] || 0) + 1;
      }
      return counts;
    }

    grade4SceneDuration(scene) {
      const meta = scene?.meta || {};
      const t = this.timing;
      if (meta.durationMs) return meta.durationMs;
      const type = scene?.type || "";
      if (type === "sectionBoard") {
        return meta.first ? t.sectionBoardFirstMs ?? 4500 : t.sectionBoardMs ?? 2800;
      }
      if (type === "sectionPan") return t.sectionPanMs ?? 12000;
      if (type === "sectionApproach") return t.sectionApproachMs ?? 9000;
      if (type === "sectionReturn") return t.sectionReturnMs ?? 5000;
      return 0;
    }

    inactiveG4SlotKey() {
      return this.activeG4Slot === "a" ? "b" : "a";
    }

    setG4KanjiTiming(fadeInMs, fadeOutMs) {
      const root = this.root;
      if (!root) return;
      root.style.setProperty("--kml-g4-kanji-fade-in", `${fadeInMs}ms`);
      root.style.setProperty("--kml-g4-kanji-fade-out", `${fadeOutMs}ms`);
    }

    applyGrade4KanjiColor(kanjiEl, scene) {
      const color = scene?.meta?.kanjiColor || "#c73e1d";
      if (kanjiEl) {
        kanjiEl.style.color = color;
      }
    }

    async populateGrade4Slot(key, scene) {
      const slot = this.g4SoundtrackSlots?.[key];
      if (!slot?.kanji) return;
      slot.kanji.textContent = scene.kanji || "";
      this.applyGrade4KanjiColor(slot.kanji, scene);
      slot.kanji.classList.remove("is-visible");
    }

    async grade4FadeInSlot(slotKey, scene, stillRunning) {
      const slot = this.g4SoundtrackSlots[slotKey];
      if (!slot?.kanji) return;
      const m = this.grade1Musical(scene);
      this.setG4KanjiTiming(m.kanjiFadeInMs, m.kanjiFadeOutMs);
      this.els.g4KanjiHero?.classList.add("is-kanji-visible");
      slot.slot?.classList.add("is-active", "is-on-top");
      slot.kanji.classList.remove("is-visible");
      void slot.kanji.offsetWidth;
      slot.kanji.classList.add("is-visible");
      await this.wait(m.kanjiFadeInMs);
      if (!stillRunning()) return;
      await this.wait(m.kanjiHoldMs);
    }

    async grade4CrossfadeSlots(outKey, inKey, scene, stillRunning) {
      const outSlot = this.g4SoundtrackSlots[outKey];
      const inSlot = this.g4SoundtrackSlots[inKey];
      if (!outSlot?.kanji || !inSlot?.kanji) return;
      const m = this.grade1Musical(scene);
      const overlap = Math.min(m.crossfadeMs, m.kanjiFadeInMs, m.kanjiFadeOutMs);
      const outSolo = Math.max(0, m.kanjiFadeOutMs - overlap);
      const inTail = Math.max(0, m.kanjiFadeInMs - overlap);
      this.setG4KanjiTiming(m.kanjiFadeInMs, m.kanjiFadeOutMs);
      this.els.g4KanjiHero?.classList.add("is-kanji-visible");
      inSlot.slot?.classList.add("is-active");
      outSlot.slot?.classList.add("is-active", "is-on-top");
      inSlot.kanji.classList.remove("is-visible");
      outSlot.kanji.classList.remove("is-visible");
      await this.wait(outSolo);
      if (!stillRunning()) return;
      inSlot.slot?.classList.add("is-on-top", "is-handoff");
      outSlot.slot?.classList.add("is-handoff-out");
      void inSlot.kanji.offsetWidth;
      inSlot.kanji.classList.add("is-visible");
      await this.wait(overlap);
      if (!stillRunning()) return;
      outSlot.slot?.classList.remove("is-active", "is-handoff-out", "is-on-top");
      outSlot.kanji.classList.remove("is-visible");
      outSlot.kanji.textContent = "";
      if (inTail > 0) {
        await this.wait(inTail);
        if (!stillRunning()) return;
      }
      inSlot.slot?.classList.remove("is-handoff");
      await this.wait(m.kanjiHoldMs);
    }

    async grade4FadeOutSlot(slotKey, scene, stillRunning) {
      const slot = this.g4SoundtrackSlots[slotKey];
      if (!slot?.kanji) return;
      const m = this.grade1Musical(scene);
      this.setG4KanjiTiming(m.kanjiFadeInMs, m.kanjiFadeOutMs);
      slot.kanji.classList.remove("is-visible");
      await this.wait(m.kanjiFadeOutMs);
      if (!stillRunning()) return;
      this.hideGrade4KanjiHero();
    }

    async playGrade4KanjiSoundtrackExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = index;
      const scene = this.scenes[index];
      const type = scene.type || (scene.kanji ? "kanji" : "");
      const board = window.KmlGrade4Board;
      const isLast = index >= count - 1;

      this.showGrade4Layer();

      if (index === 0) {
        this.grade4Visited = [];
        this.hideGrade4KanjiHero();
        if (!this.bookends?.opening) {
          await this.waitInitialExhibitionBlack(stillRunning, 0);
          if (!stillRunning()) return;
          this.maybeStartSoundtrackForScene(0);
        }
      }

      if (type === "sectionBoard") {
        this.hideGrade4KanjiHero();
        const meta = scene.meta || {};
        board?.renderBoard(this.els.g4Board, {
          sectionCounts: this.grade4SectionCounts(),
          highlight: meta.highlight || "",
          visited: this.grade4Visited,
        });
        board?.setCamera(this.els.g4Camera, "overview");
        await this.wait(this.grade4SceneDuration(scene));
      } else if (type === "sectionPan") {
        this.hideGrade4KanjiHero();
        board?.setCamera(this.els.g4Camera, "pan");
        await this.wait(this.grade4SceneDuration(scene));
      } else if (type === "sectionApproach") {
        this.hideGrade4KanjiHero();
        const kana = scene.meta?.section || "";
        board?.setHighlight(this.els.g4Board, kana);
        board?.setCamera(this.els.g4Camera, "approach", kana);
        await this.wait(this.grade4SceneDuration(scene));
      } else if (type === "sectionReturn") {
        this.hideGrade4KanjiHero();
        const kana = scene.meta?.section || "";
        if (kana && !this.grade4Visited.includes(kana)) {
          this.grade4Visited.push(kana);
        }
        board?.renderBoard(this.els.g4Board, {
          sectionCounts: this.grade4SectionCounts(),
          highlight: "",
          visited: this.grade4Visited,
        });
        board?.setCamera(this.els.g4Camera, "overview");
        await this.wait(this.grade4SceneDuration(scene));
      } else if (type === "kanji" || scene.kanji) {
        const prev = this.scenes[index - 1];
        const prevIsKanji = prev && (prev.type === "kanji" || prev.kanji);
        if (!prevIsKanji) {
          this.activeG4Slot = "a";
          await this.populateGrade4Slot("a", scene);
          if (!stillRunning()) return;
          await this.grade4FadeInSlot("a", scene, stillRunning);
        } else {
          const inKey = this.activeG4Slot;
          const outKey = this.inactiveG4SlotKey();
          await this.populateGrade4Slot(inKey, scene);
          if (!stillRunning()) return;
          await this.grade4CrossfadeSlots(outKey, inKey, scene, stillRunning);
        }
      }

      if (!stillRunning()) return;

      if (this.singleExhibit) {
        document.dispatchEvent(
          new CustomEvent("kml-exhibition-exhibit-end", {
            detail: { index: this.sceneIndex, sceneId: scene.id },
          })
        );
        return;
      }

      const next = index + 1;
      if (next >= count) {
        if (isLast && (scene.kanji || scene.type === "kanji")) {
          await this.grade4FadeOutSlot(this.activeG4Slot, scene, stillRunning);
        }
        if (this.soundtrack?.main) {
          await this.waitForSoundtrackEnd();
        }
        return;
      }

      if (scene.kanji || scene.type === "kanji") {
        this.activeG4Slot = this.inactiveG4SlotKey();
      }

      await this.playGrade4KanjiSoundtrackExhibit(next);
    }

    async populateGrade1Slot(key, scene) {
      const slot = this.soundtrackSlots?.[key];
      if (!slot?.kanji) return;
      slot.kanji.textContent = scene.kanji || "";
      this.applyGrade1KanjiColor(slot.kanji, scene);
      slot.kanji.classList.remove("is-visible");
    }

    clearGrade1Confetti() {
      const layer = this.els.grade1ConfettiLayer;
      if (!layer) return;
      layer.textContent = "";
      layer.classList.add("exhibition-hidden");
    }

    async playGrade1Confetti(accentColor) {
      const layer = this.els.grade1ConfettiLayer;
      if (!layer) return;
      const palette = [
        "#E53935",
        "#FB8C00",
        "#F9A825",
        "#43A047",
        "#29B6F6",
        "#1E88E5",
        "#8E24AA",
        "#EC407A",
      ];
      if (accentColor && !palette.includes(accentColor)) {
        palette.unshift(accentColor);
      }
      layer.textContent = "";
      layer.classList.remove("exhibition-hidden");
      const centerX = window.innerWidth * 0.5;
      const centerY = window.innerHeight * 0.46;
      const count = 42;
      for (let i = 0; i < count; i += 1) {
        const piece = document.createElement("span");
        piece.className = "grade1-confetti-piece";
        const color = palette[i % palette.length];
        const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.35;
        const dist = 70 + Math.random() * 130;
        const dx = Math.cos(angle) * dist;
        const dy = 40 + Math.sin(angle) * dist + Math.random() * 90;
        piece.style.left = `${centerX}px`;
        piece.style.top = `${centerY}px`;
        piece.style.background = color;
        piece.style.setProperty("--grade1-dx", `${dx.toFixed(1)}px`);
        piece.style.setProperty("--grade1-dy", `${dy.toFixed(1)}px`);
        piece.style.setProperty("--grade1-rot", `${(Math.random() * 280 - 140).toFixed(1)}deg`);
        piece.style.setProperty("--grade1-confetti-duration", `${(1.1 + Math.random() * 0.5).toFixed(2)}s`);
        layer.appendChild(piece);
      }
      await this.wait(1500);
      this.clearGrade1Confetti();
    }

    async grade1FadeInSlot(slotKey, scene, stillRunning) {
      const slot = this.soundtrackSlots[slotKey];
      if (!slot?.kanji) return;
      const m = this.grade1Musical(scene);
      this.setGrade1HandoffTiming(m.kanjiFadeInMs, m.kanjiFadeOutMs);
      slot.slot?.classList.add("is-active", "is-on-top");
      slot.kanji.classList.remove("is-visible");
      void slot.kanji.offsetWidth;
      slot.kanji.classList.add("is-visible");
      await this.wait(m.kanjiFadeInMs);
      if (!stillRunning()) return;
      await this.wait(m.kanjiHoldMs);
    }

    async grade1CrossfadeSlots(outKey, inKey, scene, stillRunning) {
      const outSlot = this.soundtrackSlots[outKey];
      const inSlot = this.soundtrackSlots[inKey];
      if (!outSlot?.kanji || !inSlot?.kanji) return;
      const m = this.grade1Musical(scene);
      const overlap = Math.min(m.crossfadeMs, m.kanjiFadeInMs, m.kanjiFadeOutMs);
      const outSolo = Math.max(0, m.kanjiFadeOutMs - overlap);
      const inTail = Math.max(0, m.kanjiFadeInMs - overlap);
      this.setGrade1HandoffTiming(m.kanjiFadeInMs, m.kanjiFadeOutMs);
      inSlot.slot?.classList.add("is-active");
      outSlot.slot?.classList.add("is-active", "is-on-top");
      inSlot.kanji.classList.remove("is-visible");

      outSlot.kanji.classList.remove("is-visible");
      await this.wait(outSolo);
      if (!stillRunning()) return;

      inSlot.slot?.classList.add("is-on-top", "is-handoff");
      outSlot.slot?.classList.add("is-handoff-out");
      void inSlot.kanji.offsetWidth;
      inSlot.kanji.classList.add("is-visible");
      await this.wait(overlap);
      if (!stillRunning()) return;

      outSlot.slot?.classList.remove("is-active", "is-handoff-out", "is-on-top");
      outSlot.kanji.classList.remove("is-visible");
      outSlot.kanji.textContent = "";
      if (inTail > 0) {
        await this.wait(inTail);
        if (!stillRunning()) return;
      }
      inSlot.slot?.classList.remove("is-handoff");
      await this.wait(m.kanjiHoldMs);
    }

    async grade1FadeOutSlot(slotKey, scene, stillRunning) {
      const slot = this.soundtrackSlots[slotKey];
      if (!slot?.kanji) return;
      const m = this.grade1Musical(scene);
      this.setGrade1HandoffTiming(m.kanjiFadeInMs, m.kanjiFadeOutMs);
      slot.kanji.classList.remove("is-visible");
      await this.wait(m.kanjiFadeOutMs);
    }

    async playGrade1KanjiSoundtrackExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const slotKey = this.activeSoundtrackSlot;
      const isLast = this.sceneIndex >= count - 1;
      const isMilestone = Boolean(scene.meta?.milestone) || isLast;

      if (index === 0) {
        this.resetLayers();
        this.clearGrade1Confetti();
        await this.populateGrade1Slot(slotKey, scene);
        if (!stillRunning()) return;
        this.els.strokeOrderLayer?.classList.remove("exhibition-hidden");
        this.setClass(this.els.veil, "is-clear", true);
        if (!this.bookends?.opening) {
          await this.waitInitialExhibitionBlack(stillRunning, 0);
          if (!stillRunning()) return;
          this.maybeStartSoundtrackForScene(0);
        }
        await this.grade1FadeInSlot(slotKey, scene, stillRunning);
      } else {
        const inKey = slotKey;
        const outKey = this.inactiveSoundtrackSlotKey();
        await this.populateGrade1Slot(inKey, scene);
        if (!stillRunning()) return;
        await this.grade1CrossfadeSlots(outKey, inKey, scene, stillRunning);
      }
      if (!stillRunning()) return;

      if (isMilestone && !this.isGrade4KanjiSoundtrackProfile && this.display.family !== "grade5KanjiSoundtrack" && this.display.family !== "grade6KanjiSoundtrack") {
        await this.playGrade1Confetti(scene.meta?.kanjiColor);
        if (!stillRunning()) return;
      }

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
        if (isLast) {
          await this.grade1FadeOutSlot(slotKey, scene, stillRunning);
        }
        this.resetStrokeOrderLayer();
        this.clearGrade1Confetti();
        if (this.bookends?.closing) {
          const outroClass =
            this.display.family === "grade4KanjiSoundtrack"
              ? "is-grade4-bookend-outro"
              : this.display.family === "grade5KanjiSoundtrack"
                ? "is-grade5-bookend-outro"
                : this.display.family === "grade6KanjiSoundtrack"
                  ? "is-grade6-bookend-outro"
                  : this.display.family === "grade2KanjiSoundtrack"
                ? "is-grade2-bookend-outro"
                : this.display.family === "grade3KanjiSoundtrack"
                  ? "is-grade3-bookend-outro"
                  : "is-grade1-bookend-outro";
          this.root.classList.add(outroClass);
          await this.playClosingBookend();
        } else if (this.soundtrack?.main) {
          await this.waitForSoundtrackEnd();
        }
        return;
      }

      this.activeSoundtrackSlot = this.inactiveSoundtrackSlotKey();
      await this.playGrade1KanjiSoundtrackExhibit(next);
    }

    async populateStrokeOrderScene(scene) {
      const strokeOrder = scene.strokeOrder || {};
      let kanji = scene.kanji || strokeOrder.kanji || "";
      let svg = strokeOrder.svg || "";

      if (!svg && strokeOrder.strokePage && window.KmlStrokePageLoader) {
        const loaded = await window.KmlStrokePageLoader.loadStrokePage(
          strokeOrder.strokePage,
          kanji
        );
        svg = loaded.svg;
        if (!kanji) kanji = loaded.kanji;
      }

      if (this.els.strokeOrderKanji) {
        this.els.strokeOrderKanji.textContent = kanji;
        this.els.strokeOrderKanji.classList.remove("is-dissolving");
        if (this.isElementaryStrokeOrderProfile) {
          this.applyGrade1KanjiColor(this.els.strokeOrderKanji, scene);
        }
      }
      if (this.els.strokeOrderSvg) {
        this.els.strokeOrderSvg.innerHTML = svg;
      }
      this.applyStrokeOrderComplexity(scene);
    }

    setStrokeOrderFadeTiming(fadeInMs, fadeOutMs) {
      document.documentElement.style.setProperty(
        "--ex-stroke-order-fade-in",
        `${fadeInMs}ms`
      );
      document.documentElement.style.setProperty(
        "--ex-stroke-order-fade-out",
        `${fadeOutMs}ms`
      );
    }

    /** KanjiVG path width — thinner as stroke count rises. */
    strokeOrderWidthForCount(strokeCount) {
      const count = Math.max(1, strokeCount || 1);
      if (count <= 5) return 8;
      if (count <= 8) return 6.5;
      if (count <= 11) return 5;
      if (count <= 14) return 4;
      return 3.5;
    }

    /** Slight size reduction so dense grade-2 forms do not crowd the frame. */
    strokeOrderScaleForCount(strokeCount) {
      const count = strokeCount || 1;
      if (count >= 16) return 0.88;
      if (count >= 11) return 0.93;
      return 1;
    }

    applyStrokeOrderComplexity(scene) {
      if (!this.usesAdaptiveStrokeOrderWidth) return null;
      const strokeCount =
        scene.strokeOrder?.strokeCount ?? scene.meta?.strokeCount ?? 1;
      const strokeWidth = this.strokeOrderWidthForCount(strokeCount);
      const scale = this.strokeOrderScaleForCount(strokeCount);
      this.root.style.setProperty(
        "--kml-stroke-order-stroke-width",
        String(strokeWidth)
      );
      if (scale < 1) {
        this.root.style.setProperty(
          "--kml-stroke-order-kanji",
          `calc(clamp(14rem, 42vmin, 30rem) * ${scale})`
        );
      } else {
        this.root.style.removeProperty("--kml-stroke-order-kanji");
      }
      return strokeWidth;
    }

    clearStrokeOrderComplexity() {
      this.root.style.removeProperty("--kml-stroke-order-stroke-width");
      this.root.style.removeProperty("--kml-stroke-order-kanji");
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
        (this.seamlessExhibitHandoff
          ? this.galleryBridgeHandoffMs(t)
          : t.imageExhaleFadeMs + t.kanjiAloneHoldMs + t.kanjiExhaleFadeMs);
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

      const expectedSrc = this.assetUrl(scene.image, scene.imageRev);
      const sceneId = scene.id || "";
      const imageReady =
        img.dataset.kmlLoadedSrc === expectedSrc &&
        img.dataset.kmlSceneId === sceneId &&
        img.complete &&
        img.naturalWidth > 0;

      if (imageReady && !this.useGalleryGuardian) {
        if (this.isImageVerseProfile) {
          img.classList.remove("ken-burns", "gallery-guardian");
          return;
        }
        if (img.classList.contains("ken-burns")) {
          return;
        }
      }

      img.classList.remove("ken-burns", "gallery-guardian");
      await this.waitForArtworkImage(img);

      if (this.useGalleryGuardian && window.GalleryGuardian) {
        const aspectRatio =
          img.naturalWidth > 0 ? img.naturalWidth / img.naturalHeight : 0.75;
        const isHeartExhibition =
          (this.collection.id || "").startsWith("heart_") ||
          this.collection.meta?.theme === "heart";
        const durationMs = Math.round(this.timedImageExhibitDurationMs() * this.timingScale);
        let coverBoost = 1;
        let framingScale = scene.imageScale ?? 1;
        let scaleMin;
        let motionScale = 1;
        let cameraDurationMs = durationMs;
        if (isHeartExhibition) {
          // Horizontal study art: hold full composition, skip letterbox auto-crop.
          coverBoost = 1;
          framingScale = scene.imageScale ?? 0.86;
          scaleMin = 0.82;
          motionScale = 1.45;
        } else if (this.isJapaneseVocabularyProfile) {
          // Slight documentary drift across the full soundtrack (including coda hold).
          coverBoost = window.GalleryGuardian.measureCoverBoost(img);
          motionScale =
            scene.galleryCamera?.motionScale ??
            this.display.cameraMotionScale ??
            1.25;
          const soundtrackMs =
            this.meta?.soundtrackDurationMs ||
            this.collection.meta?.soundtrackDurationMs ||
            0;
          if (soundtrackMs > cameraDurationMs) {
            cameraDurationMs = Math.round(soundtrackMs * this.timingScale);
          }
        } else {
          coverBoost = window.GalleryGuardian.measureCoverBoost(img);
        }
        const plan = window.GalleryGuardian.plan(scene, {
          sceneIndex: this.sceneIndex,
          history: this.cameraHistory,
          aspectRatio,
          framingScale,
          durationMs: cameraDurationMs,
          coverBoost,
          scaleMin,
          motionScale,
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

      if (!this.isImageVerseProfile) {
        img.classList.add("ken-burns");
      }
    }

    async applySceneCamera(scene) {
      return this.applySceneCameraToImage(this.els.artworkImg, scene);
    }

    populateScene(scene) {
      this.populateArtworkLayer(this.activeArtworkKey, scene);
      this.syncLegacyArtworkRefs();
      this.populateVerseContent(scene);
    }

    async playReadingStage(stillRunning, html, timing) {
      this.setReadingStageContent(html);
      this.setClass(this.els.verseJp, "is-visible", true);
      await this.wait(timing.revealMs);
      if (!stillRunning()) return;
      await this.wait(timing.holdMs);
      if (!stillRunning()) return;
      this.setClass(this.els.verseJp, "is-visible", false);
      await this.wait(timing.fadeMs);
    }

    readingStageTiming(t, prefix) {
      return {
        revealMs: t[`${prefix}RevealMs`] ?? t.readingStageRevealMs ?? 1000,
        holdMs: t[`${prefix}HoldMs`] ?? t.readingStageHoldMs ?? 7000,
        fadeMs: t[`${prefix}FadeMs`] ?? t.readingStageFadeMs ?? 1000,
      };
    }

    async waitInitialExhibitionBlack(stillRunning, index) {
      if (index !== 0) return;
      const t = this.timing;
      const blackMs = t.exhibitionBlackBeforeMs ?? t.openingBlackBeforeMs ?? 0;
      if (blackMs <= 0) return;

      this.root.classList.add("is-initial-black");
      this.setClass(this.els.veil, "is-corridor", false);
      this.setClass(this.els.veil, "is-clear", false);
      await this.wait(blackMs);
      this.root.classList.remove("is-initial-black");
      if (!stillRunning()) return;
    }

    async playAssistedReadingExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const transitionMs = t.exhibitTransitionMs ?? 4000;
      const skippedCrossfade = this._assistedReadingCrossfadedTo === index;
      this._assistedReadingCrossfadedTo = -1;
      const verse = scene.verse || {};
      const jpHtml = verse.jpHtml || verse.natural || "";

      this.resetImageVerseForeground();
      if (this.els.verseEn) {
        this.els.verseEn.textContent = "";
      }

      if (!skippedCrossfade) {
        await this.waitInitialExhibitionBlack(stillRunning, this.sceneIndex);
        if (!stillRunning()) return;

        const layer = this.artworkLayers[this.activeArtworkKey];
        if (this.sceneIndex === 0) {
          document.documentElement.style.setProperty(
            "--ex-artwork-arrival",
            `${t.artworkArrivalFadeMs ?? 800}ms`
          );
        }
        this.populateArtworkLayer(this.activeArtworkKey, scene);
        this.syncLegacyArtworkRefs();
        await this.applySceneCameraToImage(layer.img, scene);
        if (!stillRunning()) return;

        this.setClass(this.els.veil, "is-corridor", false);
        this.setClass(this.els.veil, "is-clear", true);
        this.setClass(layer.wrap, "is-exhaling", false);
        this.setClass(layer.wrap, "is-on-top", true);
        this.setClass(layer.wrap, "is-visible", true);
        if (this.sceneIndex === 0) {
          this.maybeStartSoundtrackForScene(0);
        }
        await this.wait(t.artworkArrivalMs + (t.artworkAloneMs ?? 0));
        if (!stillRunning()) return;
      } else {
        await this.wait(t.artworkAloneMs ?? 0);
        if (!stillRunning()) return;
      }

      // Quiet beat — image only
      if (!skippedCrossfade) {
        await this.wait(t.readingPauseBeforeMs ?? 5000);
        if (!stillRunning()) return;
      }

      // Natural Japanese fades in (furigana hidden initially)
      this.setAssistedVerseContent(jpHtml);
      document.documentElement.style.setProperty(
        "--ex-verse-fade",
        `${t.readingAssistedRevealMs ?? 1800}ms`
      );
      this.setClass(this.els.verseJp, "is-visible", true);
      await this.wait(t.readingAssistedRevealMs ?? 1800);
      if (!stillRunning()) return;

      // Kanji only — then furigana gently fades in
      await this.wait(t.readingFuriganaEnterDelayMs ?? 3000);
      if (!stillRunning()) return;
      await this.playFuriganaFadeIn(stillRunning, t.readingFuriganaEnterMs ?? 3000);
      if (!stillRunning()) return;

      await this.wait(t.readingAssistedHoldMs ?? 9000);
      if (!stillRunning()) return;

      // Furigana fades out (kanji unchanged)
      const verseJp = this.els.verseJp;
      if (verseJp) {
        void verseJp.offsetHeight;
        verseJp.classList.add("is-furigana-fading");
      }
      await this.wait(t.readingFuriganaFadeMs ?? 2500);
      if (!stillRunning()) return;
      if (verseJp) {
        verseJp.classList.remove("is-furigana-fading");
        verseJp.classList.add("is-furigana-hidden");
      }

      // Brief native hold after furigana disappears
      await this.wait(t.readingNativeHoldMs ?? 3500);
      if (!stillRunning()) return;

      // Fade Japanese, then English
      document.documentElement.style.setProperty(
        "--ex-verse-fade",
        `${t.readingJpFadeMs ?? 1000}ms`
      );
      this.setClass(this.els.verseJp, "is-visible", false);
      await this.wait(t.readingJpFadeMs ?? 1000);
      if (!stillRunning()) return;

      if (this.showEnglish && verse.en) {
        if (this.els.verseEn) {
          this.els.verseEn.textContent = verse.en;
        }
        this.setClass(this.els.verseEn, "is-visible", true);
        await this.wait(t.readingEnRevealMs ?? 1000);
        if (!stillRunning()) return;
        await this.wait(t.readingEnHoldMs ?? 5500);
        if (!stillRunning()) return;
        this.setClass(this.els.verseEn, "is-visible", false);
        await this.wait(t.readingEnFadeMs ?? 1000);
        if (!stillRunning()) return;
        if (this.els.verseEn) {
          this.els.verseEn.textContent = "";
        }
      }

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
            this._soundtrackStarted = false;
            this.stopSoundtrack();
            await this.playOpeningBookend();
            if (!stillRunning()) return;
          }
          this._assistedReadingCrossfadedTo = -1;
          this.activeArtworkKey = "a";
          this.syncLegacyArtworkRefs();
          await this.playAssistedReadingExhibit(0);
        } else if (this.bookends?.closing) {
          await this.playClosingBookend();
        }
        return;
      }

      const nextScene = this.scenes[next];
      await this.crossfadeArtworkLayers(nextScene, transitionMs);
      if (!stillRunning()) return;
      this._assistedReadingCrossfadedTo = next;
      await this.playAssistedReadingExhibit(next);
    }

    async playVocabularyStep(stillRunning, step, t) {
      const revealMs = t.vocabularyStepRevealMs ?? 1400;
      const holdMs = t.vocabularyStepHoldMs ?? 3500;
      const fadeMs = t.vocabularyStepFadeMs ?? 1400;
      const usesFurigana = this.vocabularyStepUsesFurigana(step);

      this.setVocabularyStepContent(step);
      document.documentElement.style.setProperty("--ex-verse-fade", `${revealMs}ms`);
      this.setClass(this.els.verseJp, "is-visible", true);
      this.setClass(this.els.verseEn, "is-visible", true);
      await this.wait(revealMs);
      if (!stillRunning()) return;

      if (usesFurigana) {
        await this.wait(t.vocabularyFuriganaEnterDelayMs ?? 700);
        if (!stillRunning()) return;
        await this.playFuriganaFadeIn(
          stillRunning,
          t.vocabularyFuriganaEnterMs ?? 2200
        );
        if (!stillRunning()) return;
        await this.wait(t.vocabularyFuriganaHoldMs ?? 3500);
        if (!stillRunning()) return;
        await this.playVocabularyFuriganaOut(
          stillRunning,
          t.vocabularyFuriganaFadeMs ?? 2200
        );
        if (!stillRunning()) return;
        await this.wait(t.vocabularyNativeHoldMs ?? 2000);
        if (!stillRunning()) return;
      } else {
        await this.wait(holdMs);
        if (!stillRunning()) return;
      }

      document.documentElement.style.setProperty("--ex-verse-fade", `${fadeMs}ms`);
      this.setClass(this.els.verseJp, "is-visible", false);
      this.setClass(this.els.verseEn, "is-visible", false);
      await this.wait(fadeMs);
      if (!stillRunning()) return;

      if (this.els.verseJp) {
        this.els.verseJp.textContent = "";
        this.els.verseJp.innerHTML = "";
      }
      if (this.els.verseEn) {
        this.els.verseEn.textContent = "";
      }
    }

    async playVocabularyExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const transitionMs = t.exhibitTransitionMs ?? 3500;
      const skippedCrossfade = this._vocabularyCrossfadedTo === index;
      this._vocabularyCrossfadedTo = -1;
      const verse = scene.verse || {};
      const steps = scene.vocabulary?.steps || [];

      this.resetImageVerseForeground();
      if (this.els.verseJp) {
        this.els.verseJp.classList.remove("is-vocab-verse-reveal");
      }

      if (!skippedCrossfade) {
        await this.waitInitialExhibitionBlack(stillRunning, this.sceneIndex);
        if (!stillRunning()) return;

        const layer = this.artworkLayers[this.activeArtworkKey];
        if (this.sceneIndex === 0) {
          document.documentElement.style.setProperty(
            "--ex-artwork-arrival",
            `${t.artworkArrivalFadeMs ?? 2000}ms`
          );
        }
        this.populateArtworkLayer(this.activeArtworkKey, scene);
        this.syncLegacyArtworkRefs();
        await this.applySceneCameraToImage(layer.img, scene);
        if (!stillRunning()) return;

        this.setClass(this.els.veil, "is-corridor", false);
        this.setClass(this.els.veil, "is-clear", true);
        this.setClass(layer.wrap, "is-exhaling", false);
        this.setClass(layer.wrap, "is-on-top", true);
        this.setClass(layer.wrap, "is-visible", true);
        const arrivalFadeMs =
          this.sceneIndex === 0 ? (t.artworkArrivalFadeMs ?? 0) : 0;
        if (arrivalFadeMs > 0) {
          await this.wait(arrivalFadeMs);
          if (!stillRunning()) return;
        }
        if (this.sceneIndex === 0) {
          this.maybeStartSoundtrackForScene(0);
        }
        await this.wait(t.artworkArrivalMs + (t.artworkAloneMs ?? 0));
        if (!stillRunning()) return;
      } else {
        await this.wait(t.artworkAloneMs ?? 0);
        if (!stillRunning()) return;
      }

      if (!skippedCrossfade) {
        await this.wait(t.vocabularyPauseBeforeMs ?? 4000);
        if (!stillRunning()) return;
      }

      for (const step of steps) {
        await this.playVocabularyStep(stillRunning, step, t);
        if (!stillRunning()) return;
      }

      const jpRevealMs = t.vocabularyVerseJpRevealMs ?? 1600;
      const jpFadeMs = t.vocabularyVerseJpFadeMs ?? 1400;

      this.setVocabularyVerseReveal(verse.jpHtml || verse.natural || "");
      document.documentElement.style.setProperty("--ex-verse-fade", `${jpRevealMs}ms`);
      this.setClass(this.els.verseJp, "is-visible", true);
      await this.wait(jpRevealMs);
      if (!stillRunning()) return;

      await this.wait(t.vocabularyVerseKanjiHoldMs ?? 3500);
      if (!stillRunning()) return;
      await this.wait(t.vocabularyVerseFuriganaEnterDelayMs ?? 900);
      if (!stillRunning()) return;
      await this.playFuriganaFadeIn(
        stillRunning,
        t.vocabularyVerseFuriganaEnterMs ?? 2500
      );
      if (!stillRunning()) return;
      await this.wait(t.vocabularyVerseFuriganaHoldMs ?? 4500);
      if (!stillRunning()) return;
      await this.playVocabularyFuriganaOut(
        stillRunning,
        t.vocabularyVerseFuriganaFadeMs ?? 2500
      );
      if (!stillRunning()) return;
      await this.wait(t.vocabularyVerseNativeHoldMs ?? 3000);
      if (!stillRunning()) return;

      document.documentElement.style.setProperty("--ex-verse-fade", `${jpFadeMs}ms`);
      this.setClass(this.els.verseJp, "is-visible", false);
      await this.wait(jpFadeMs);
      if (!stillRunning()) return;
      if (this.els.verseJp) {
        this.els.verseJp.innerHTML = "";
        this.els.verseJp.textContent = "";
        this.els.verseJp.classList.remove("is-vocab-verse-reveal", "show-furigana");
      }

      if (this.showEnglish && verse.en) {
        const enRevealMs = t.vocabularyVerseEnRevealMs ?? 1400;
        const enHoldMs = t.vocabularyVerseEnHoldMs ?? 6000;
        const enFadeMs = t.vocabularyVerseEnFadeMs ?? 1400;

        if (this.els.verseEn) {
          this.els.verseEn.textContent = verse.en;
          this.els.verseEn.classList.add("is-vocab-verse-reveal");
        }
        document.documentElement.style.setProperty("--ex-verse-fade", `${enRevealMs}ms`);
        this.setClass(this.els.verseEn, "is-visible", true);
        await this.wait(enRevealMs);
        if (!stillRunning()) return;
        await this.wait(enHoldMs);
        if (!stillRunning()) return;
        document.documentElement.style.setProperty("--ex-verse-fade", `${enFadeMs}ms`);
        this.setClass(this.els.verseEn, "is-visible", false);
        await this.wait(enFadeMs);
        if (!stillRunning()) return;
        if (this.els.verseEn) {
          this.els.verseEn.textContent = "";
          this.els.verseEn.classList.remove("is-vocab-verse-reveal");
        }
      }

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
            this._soundtrackStarted = false;
            this.stopSoundtrack();
            await this.playOpeningBookend();
            if (!stillRunning()) return;
          }
          this._vocabularyCrossfadedTo = -1;
          this.activeArtworkKey = "a";
          this.syncLegacyArtworkRefs();
          await this.playVocabularyExhibit(0);
        } else if (this.bookends?.closing) {
          await this.playClosingBookend();
        }
        return;
      }

      const nextScene = this.scenes[next];
      await this.crossfadeArtworkLayers(nextScene, transitionMs);
      if (!stillRunning()) return;
      this._vocabularyCrossfadedTo = next;
      await this.playVocabularyExhibit(next);
    }

    setCompoundsStepContent(step) {
      if (!this.els.verseJp || !step) return;
      const verseJp = this.els.verseJp;
      const verseEn = this.els.verseEn;

      verseJp.lang = "ja";
      verseJp.classList.remove(
        "has-authored-lines",
        "show-furigana",
        "is-furigana-entering",
        "is-furigana-fading",
        "is-furigana-hidden",
        "is-vocab-verse-reveal",
        "has-vocab-readings"
      );
      verseJp.textContent = "";
      verseJp.innerHTML = "";

      const main = document.createElement("span");
      main.className = "kml-compound-jp";
      main.innerHTML = step.jpHtml || step.jp || "";
      const jpText = step.jp || main.textContent || "";
      this.applyAnchorWordScale(main, jpText);
      verseJp.appendChild(main);

      const reading = document.createElement("span");
      reading.className = "kml-compound-reading";
      if (step.reading) {
        reading.textContent = `「${step.reading}」`;
      }
      verseJp.appendChild(reading);

      if (step.hint) {
        const hint = document.createElement("span");
        hint.className = "kml-compound-hint";
        hint.textContent = step.hint;
        verseJp.appendChild(hint);
      }

      if (step.jpHtml) {
        verseJp.classList.add("show-furigana", "is-furigana-hidden");
      }

      if (verseEn) {
        verseEn.textContent = step.en || "";
        verseEn.classList.remove("is-vocab-verse-reveal", "is-reading-reflection");
      }
    }

    async showCompoundsTargetKanji(stillRunning, kanji, t, { isReturn = false } = {}) {
      const revealMs = isReturn
        ? (t.compoundsKanjiReturnRevealMs ?? 1400)
        : (t.compoundsKanjiRevealMs ?? 1600);
      const holdMs = isReturn
        ? (t.compoundsKanjiReturnHoldMs ?? 2200)
        : (t.compoundsKanjiHoldMs ?? 2800);
      const fadeMs = isReturn
        ? (t.compoundsKanjiReturnFadeMs ?? 1400)
        : (t.compoundsKanjiFadeMs ?? 1400);

      this.resetImageVerseForeground();
      if (this.els.kanji) {
        this.els.kanji.textContent = kanji;
        this.els.kanji.classList.toggle("is-target-return", isReturn);
      }

      document.documentElement.style.setProperty("--ex-compounds-fade", `${revealMs}ms`);
      this.setClass(this.els.kanji, "is-visible", true);
      await this.wait(revealMs);
      if (!stillRunning()) return;
      await this.wait(holdMs);
      if (!stillRunning()) return;

      document.documentElement.style.setProperty("--ex-compounds-fade", `${fadeMs}ms`);
      this.setClass(this.els.kanji, "is-visible", false);
      await this.wait(fadeMs);
      if (!stillRunning()) return;

      if (this.els.kanji) {
        this.els.kanji.textContent = "";
        this.els.kanji.classList.remove("is-target-return");
      }
    }

    async playCompoundsStep(stillRunning, step, t) {
      const stepReveal = t.compoundsStepRevealMs ?? 1400;
      const stepFade = t.compoundsStepFadeMs ?? 1400;
      const readingReveal = t.compoundsReadingRevealMs ?? 1200;
      const readingHold = t.compoundsReadingHoldMs ?? 1800;
      const hintReveal = t.compoundsHintRevealMs ?? 1000;
      const enReveal = t.compoundsEnRevealMs ?? 1200;
      const enHold = t.compoundsEnHoldMs ?? 3000;
      const enFade = t.compoundsEnFadeMs ?? 1400;
      const usesFurigana = Boolean(step?.jpHtml);

      this.setCompoundsStepContent(step);
      const verseJp = this.els.verseJp;
      const readingEl = verseJp?.querySelector(".kml-compound-reading");
      const hintEl = verseJp?.querySelector(".kml-compound-hint");

      document.documentElement.style.setProperty("--ex-verse-fade", `${stepReveal}ms`);
      this.setClass(verseJp, "is-visible", true);
      await this.wait(stepReveal);
      if (!stillRunning()) return;

      if (usesFurigana) {
        await this.wait(t.compoundsFuriganaEnterDelayMs ?? 900);
        if (!stillRunning()) return;
        await this.playFuriganaFadeIn(
          stillRunning,
          t.compoundsFuriganaEnterMs ?? 2200
        );
        if (!stillRunning()) return;
        await this.wait(t.compoundsFuriganaHoldMs ?? 3000);
        if (!stillRunning()) return;
        await this.playVocabularyFuriganaOut(
          stillRunning,
          t.compoundsFuriganaFadeMs ?? 2200
        );
        if (!stillRunning()) return;
        await this.wait(t.compoundsNativeHoldMs ?? 1600);
        if (!stillRunning()) return;
      }

      document.documentElement.style.setProperty("--ex-verse-fade", `${readingReveal}ms`);
      readingEl?.classList.add("is-visible");
      await this.wait(readingReveal);
      if (!stillRunning()) return;
      await this.wait(readingHold);
      if (!stillRunning()) return;

      if (hintEl) {
        document.documentElement.style.setProperty("--ex-verse-fade", `${hintReveal}ms`);
        hintEl.classList.add("is-visible");
        await this.wait(hintReveal);
        if (!stillRunning()) return;
      }

      if (this.els.verseEn && step.en) {
        document.documentElement.style.setProperty("--ex-compounds-en-fade", `${enReveal}ms`);
        this.setClass(this.els.verseEn, "is-visible", true);
        await this.wait(enReveal);
        if (!stillRunning()) return;
        await this.wait(enHold);
        if (!stillRunning()) return;

        document.documentElement.style.setProperty("--ex-compounds-en-fade", `${enFade}ms`);
        this.setClass(this.els.verseEn, "is-visible", false);
        await this.wait(enFade);
        if (!stillRunning()) return;
      }

      document.documentElement.style.setProperty("--ex-verse-fade", `${stepFade}ms`);
      this.setClass(verseJp, "is-visible", false);
      readingEl?.classList.remove("is-visible");
      hintEl?.classList.remove("is-visible");
      await this.wait(stepFade);
      if (!stillRunning()) return;

      if (verseJp) {
        verseJp.textContent = "";
        verseJp.innerHTML = "";
      }
      if (this.els.verseEn) {
        this.els.verseEn.textContent = "";
      }
    }

    async playJapaneseVocabularyStep(stillRunning, step, t) {
      const stepReveal = t.compoundsStepRevealMs ?? 1400;
      const stepFade = t.compoundsStepFadeMs ?? 1400;
      const readingReveal = t.compoundsReadingRevealMs ?? 1200;
      const readingHold = t.compoundsReadingHoldMs ?? 1800;
      const enReveal = t.compoundsEnRevealMs ?? 1200;
      const enHold = t.compoundsEnHoldMs ?? 3500;
      const enFade = t.compoundsEnFadeMs ?? 1400;
      const usesFurigana = Boolean(step?.jpHtml);

      this.setCompoundsStepContent(step);
      const verseJp = this.els.verseJp;
      const readingEl = verseJp?.querySelector(".kml-compound-reading");

      document.documentElement.style.setProperty("--ex-verse-fade", `${stepReveal}ms`);
      this.setClass(verseJp, "is-visible", true);
      await this.wait(stepReveal);
      if (!stillRunning()) return;

      if (usesFurigana) {
        await this.wait(t.compoundsFuriganaEnterDelayMs ?? 900);
        if (!stillRunning()) return;
        await this.playFuriganaFadeIn(
          stillRunning,
          t.compoundsFuriganaEnterMs ?? 2200
        );
        if (!stillRunning()) return;
        await this.wait(t.compoundsFuriganaHoldMs ?? 3000);
        if (!stillRunning()) return;
        await this.playVocabularyFuriganaOut(
          stillRunning,
          t.compoundsFuriganaFadeMs ?? 2200
        );
        if (!stillRunning()) return;
        // Clean typography hold — furigana was the pronunciation confirmation.
        await this.wait(t.compoundsNativeHoldMs ?? 2200);
        if (!stillRunning()) return;
      } else {
        document.documentElement.style.setProperty("--ex-verse-fade", `${readingReveal}ms`);
        readingEl?.classList.add("is-visible");
        await this.wait(readingReveal);
        if (!stillRunning()) return;
        await this.wait(readingHold);
        if (!stillRunning()) return;
      }

      if (this.els.verseEn && step.en) {
        document.documentElement.style.setProperty("--ex-compounds-en-fade", `${enReveal}ms`);
        this.setClass(this.els.verseEn, "is-visible", true);
        await this.wait(enReveal);
        if (!stillRunning()) return;
        await this.wait(enHold);
        if (!stillRunning()) return;

        document.documentElement.style.setProperty("--ex-compounds-en-fade", `${enFade}ms`);
        this.setClass(this.els.verseEn, "is-visible", false);
        await this.wait(enFade);
        if (!stillRunning()) return;
      }

      document.documentElement.style.setProperty("--ex-verse-fade", `${stepFade}ms`);
      this.setClass(verseJp, "is-visible", false);
      readingEl?.classList.remove("is-visible");
      await this.wait(stepFade);
      if (!stillRunning()) return;

      if (verseJp) {
        verseJp.textContent = "";
        verseJp.innerHTML = "";
      }
      if (this.els.verseEn) {
        this.els.verseEn.textContent = "";
      }
    }

    async playBeautifulJapaneseWord(stillRunning, word, t, options = {}) {
      if (!word || !(word.jp || word.jpHtml)) return;

      const lingerForSoundtrack = Boolean(options.lingerForSoundtrack);
      const labelReveal = t.beautifulWordLabelRevealMs ?? 1600;
      const labelHold = t.beautifulWordLabelHoldMs ?? 2200;
      const wordReveal = t.beautifulWordRevealMs ?? 1600;
      const furiganaHold = t.beautifulWordFuriganaHoldMs ?? 4500;
      const nativeHold = t.beautifulWordNativeHoldMs ?? 3500;
      const enReveal = t.compoundsEnRevealMs ?? 1400;
      const enHold = t.beautifulWordEnHoldMs ?? 5000;
      const enFade = t.compoundsEnFadeMs ?? 1600;
      const wordFade = t.beautifulWordFadeMs ?? 1800;
      const label =
        word.labelHtml ||
        word.label ||
        "";

      this.root.classList.add("is-beautiful-word");
      if (label && this.els.keyword) {
        this.els.keyword.innerHTML = label;
        document.documentElement.style.setProperty("--ex-keyword-fade", `${labelReveal}ms`);
        this.setClass(this.els.keyword, "is-visible", true);
        await this.wait(labelReveal);
        if (!stillRunning()) return;
        await this.wait(labelHold);
        if (!stillRunning()) return;
      }

      this.setCompoundsStepContent({
        jp: word.jp,
        jpHtml: word.jpHtml,
        reading: word.reading,
        en: word.en,
      });
      const verseJp = this.els.verseJp;
      const readingEl = verseJp?.querySelector(".kml-compound-reading");
      verseJp?.classList.add("is-beautiful-word-jp");

      document.documentElement.style.setProperty("--ex-verse-fade", `${wordReveal}ms`);
      this.setClass(verseJp, "is-visible", true);
      await this.wait(wordReveal);
      if (!stillRunning()) return;

      if (word.jpHtml) {
        await this.wait(t.compoundsFuriganaEnterDelayMs ?? 900);
        if (!stillRunning()) return;
        await this.playFuriganaFadeIn(
          stillRunning,
          t.compoundsFuriganaEnterMs ?? 2200
        );
        if (!stillRunning()) return;
        await this.wait(furiganaHold);
        if (!stillRunning()) return;
        await this.playVocabularyFuriganaOut(
          stillRunning,
          t.compoundsFuriganaFadeMs ?? 2200
        );
        if (!stillRunning()) return;
        await this.wait(nativeHold);
        if (!stillRunning()) return;
      } else if (word.reading) {
        const readingReveal = t.compoundsReadingRevealMs ?? 1200;
        const readingHold = t.compoundsReadingHoldMs ?? 2200;
        document.documentElement.style.setProperty("--ex-verse-fade", `${readingReveal}ms`);
        readingEl?.classList.add("is-visible");
        await this.wait(readingReveal);
        if (!stillRunning()) return;
        await this.wait(readingHold);
        if (!stillRunning()) return;
      }

      if (this.els.verseEn && word.en) {
        document.documentElement.style.setProperty("--ex-compounds-en-fade", `${enReveal}ms`);
        this.setClass(this.els.verseEn, "is-visible", true);
        await this.wait(enReveal);
        if (!stillRunning()) return;
        await this.wait(enHold);
        if (!stillRunning()) return;

        document.documentElement.style.setProperty("--ex-compounds-en-fade", `${enFade}ms`);
        this.setClass(this.els.verseEn, "is-visible", false);
        await this.wait(enFade);
        if (!stillRunning()) return;
      }

      // Vocabulary standard ending: leave the completed final word on the scene
      // while the soundtrack continues to its natural end.
      if (lingerForSoundtrack) return;

      document.documentElement.style.setProperty("--ex-verse-fade", `${wordFade}ms`);
      document.documentElement.style.setProperty("--ex-keyword-fade", `${wordFade}ms`);
      this.setClass(verseJp, "is-visible", false);
      this.setClass(this.els.keyword, "is-visible", false);
      readingEl?.classList.remove("is-visible");
      await this.wait(wordFade);
      if (!stillRunning()) return;

      if (verseJp) {
        verseJp.classList.remove("is-beautiful-word-jp");
        verseJp.textContent = "";
        verseJp.innerHTML = "";
      }
      if (this.els.keyword) {
        this.els.keyword.textContent = "";
        this.els.keyword.innerHTML = "";
      }
      if (this.els.verseEn) {
        this.els.verseEn.textContent = "";
      }
      this.root.classList.remove("is-beautiful-word");
    }

    async clearBeautifulJapaneseWord(stillRunning, t) {
      const wordFade = t.beautifulWordFadeMs ?? 1800;
      const verseJp = this.els.verseJp;
      document.documentElement.style.setProperty("--ex-verse-fade", `${wordFade}ms`);
      document.documentElement.style.setProperty("--ex-keyword-fade", `${wordFade}ms`);
      this.setClass(verseJp, "is-visible", false);
      this.setClass(this.els.keyword, "is-visible", false);
      verseJp?.querySelector(".kml-compound-reading")?.classList.remove("is-visible");
      await this.wait(wordFade);
      if (!stillRunning()) return;

      if (verseJp) {
        verseJp.classList.remove("is-beautiful-word-jp");
        verseJp.textContent = "";
        verseJp.innerHTML = "";
      }
      if (this.els.keyword) {
        this.els.keyword.textContent = "";
        this.els.keyword.innerHTML = "";
      }
      if (this.els.verseEn) {
        this.els.verseEn.textContent = "";
      }
      this.root.classList.remove("is-beautiful-word");
    }

    /**
     * Standard KML Vocabulary ending:
     * hold final scene until soundtrack ends → fade to black → silent crest → silence.
     */
    async playJapaneseVocabularyGalleryEnding(stillRunning, layer, t) {
      // Remain in the completed scene while the ambient bed finishes naturally.
      await this.waitForSoundtrackEnd();
      if (!stillRunning()) return;

      const exhaleMs = t.vocabArtworkExhaleMs ?? 3500;
      const textFadeMs = Math.min(t.beautifulWordFadeMs ?? 1800, exhaleMs);
      document.documentElement.style.setProperty("--ex-transition", `${exhaleMs}ms`);

      const textFade = this.clearBeautifulJapaneseWord(stillRunning, {
        ...t,
        beautifulWordFadeMs: textFadeMs,
      });
      this.setClass(layer.wrap, "is-exhaling", true);
      this.setClass(layer.wrap, "is-visible", false);
      await Promise.all([textFade, this.wait(exhaleMs)]);
      if (!stillRunning()) return;

      if (this.bookends?.closing) {
        await this.playClosingBookend();
      } else {
        this.finishPresentation();
      }
    }

    async playJapaneseVocabularyExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const steps = scene.compounds?.steps || [];
      const beautifulWord = scene.beautifulWord || this.collection.beautifulWord || null;

      this.resetImageVerseForeground();
      this.root.classList.remove("is-beautiful-word");

      await this.waitInitialExhibitionBlack(stillRunning, this.sceneIndex);
      if (!stillRunning()) return;

      const layer = this.artworkLayers[this.activeArtworkKey];
      if (this.sceneIndex === 0) {
        document.documentElement.style.setProperty(
          "--ex-artwork-arrival",
          `${t.artworkArrivalFadeMs ?? 2800}ms`
        );
      }
      this.populateArtworkLayer(this.activeArtworkKey, scene);
      this.syncLegacyArtworkRefs();
      await this.applySceneCameraToImage(layer.img, scene);
      if (!stillRunning()) return;

      this.setClass(this.els.veil, "is-corridor", false);
      this.setClass(this.els.veil, "is-clear", true);
      this.setClass(layer.wrap, "is-exhaling", false);
      this.setClass(layer.wrap, "is-on-top", true);
      this.setClass(layer.wrap, "is-visible", true);
      const arrivalFadeMs =
        this.sceneIndex === 0 ? (t.artworkArrivalFadeMs ?? 2800) : 0;
      if (arrivalFadeMs > 0) {
        await this.wait(arrivalFadeMs);
        if (!stillRunning()) return;
      }
      if (this.sceneIndex === 0) {
        this.maybeStartSoundtrackForScene(0);
      }
      await this.wait(t.artworkArrivalMs + (t.artworkAloneMs ?? 0));
      if (!stillRunning()) return;

      await this.wait(t.compoundsPauseBeforeMs ?? 3200);
      if (!stillRunning()) return;

      for (const step of steps) {
        await this.playJapaneseVocabularyStep(stillRunning, step, t);
        if (!stillRunning()) return;
      }

      if (beautifulWord) {
        await this.playBeautifulJapaneseWord(stillRunning, beautifulWord, t, {
          lingerForSoundtrack: !this.singleExhibit && !this.display.loop,
        });
        if (!stillRunning()) return;
      }

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
            this._soundtrackStarted = false;
            this.stopSoundtrack();
            await this.playOpeningBookend();
            if (!stillRunning()) return;
          }
          this.activeArtworkKey = "a";
          this.syncLegacyArtworkRefs();
          await this.playJapaneseVocabularyExhibit(0);
          return;
        }

        await this.playJapaneseVocabularyGalleryEnding(stillRunning, layer, t);
        return;
      }

      const nextScene = this.scenes[next];
      const transitionMs = t.exhibitTransitionMs ?? 3500;
      await this.crossfadeArtworkLayers(nextScene, transitionMs);
      if (!stillRunning()) return;
      await this.playJapaneseVocabularyExhibit(next);
    }

    async playAnchorCompoundsCard(stillRunning, scene, t) {
      const cardGap = t.anchorCardGapMs ?? 300;
      const wordEl = this.els.anchorCompoundsWord;
      const readingEl = this.els.anchorCompoundsReading;

      this.setAnchorCompoundsContent(scene);
      this.resetAnchorCompoundsCardVisuals();
      this.setAnchorCompoundsFadeTiming(t);

      await this.waitForPaintFrame();
      if (!stillRunning()) return;

      if (this.confirmationMode === "replace") {
        await this.playAnchorCompoundsReplaceCard(stillRunning, wordEl, readingEl, t);
      } else if (this.confirmationMode === "crossfade") {
        await this.playAnchorCompoundsCrossfadeCard(stillRunning, wordEl, readingEl, t);
      } else {
        await this.playAnchorCompoundsStackedCard(stillRunning, wordEl, readingEl, t);
      }
      if (!stillRunning()) return;

      this.clearAnchorCompoundsContent();
      this.resetAnchorCompoundsCardVisuals();
      await this.wait(cardGap);
    }

    async playAnchorCompoundsExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;

      if (index === 0 || !this._anchorCompoundsLayerVisible) {
        this.resetLayers();
        if (this.els.anchorCompoundsLayer) {
          this.els.anchorCompoundsLayer.classList.remove("exhibition-hidden");
        }
        this._anchorCompoundsLayerVisible = true;
        this.setClass(this.els.veil, "is-clear", true);

        if (this.sceneIndex === 0) {
          await this.waitInitialExhibitionBlack(stillRunning, 0);
          if (!stillRunning()) return;
        }
      }

      await this.playAnchorCompoundsCard(stillRunning, scene, t);
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
          this._anchorCompoundsLayerVisible = false;
          await this.playAnchorCompoundsExhibit(0);
        } else if (this.bookends?.closing) {
          this.resetAnchorCompoundsLayer();
          await this.playClosingBookend();
        }
        return;
      }

      await this.playAnchorCompoundsExhibit(next);
    }

    async playCompoundsExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const transitionMs = t.exhibitTransitionMs ?? 3500;
      const skippedCrossfade = this._compoundsCrossfadedTo === index;
      this._compoundsCrossfadedTo = -1;
      const steps = scene.compounds?.steps || [];

      this.resetImageVerseForeground();

      if (!skippedCrossfade) {
        await this.waitInitialExhibitionBlack(stillRunning, this.sceneIndex);
        if (!stillRunning()) return;

        const layer = this.artworkLayers[this.activeArtworkKey];
        if (this.sceneIndex === 0) {
          document.documentElement.style.setProperty(
            "--ex-artwork-arrival",
            `${t.artworkArrivalFadeMs ?? 2000}ms`
          );
        }
        this.populateArtworkLayer(this.activeArtworkKey, scene);
        this.syncLegacyArtworkRefs();
        await this.applySceneCameraToImage(layer.img, scene);
        if (!stillRunning()) return;

        this.setClass(this.els.veil, "is-corridor", false);
        this.setClass(this.els.veil, "is-clear", true);
        this.setClass(layer.wrap, "is-exhaling", false);
        this.setClass(layer.wrap, "is-on-top", true);
        this.setClass(layer.wrap, "is-visible", true);
        const arrivalFadeMs =
          this.sceneIndex === 0 ? (t.artworkArrivalFadeMs ?? 0) : 0;
        if (arrivalFadeMs > 0) {
          await this.wait(arrivalFadeMs);
          if (!stillRunning()) return;
        }
        if (this.sceneIndex === 0) {
          this.maybeStartSoundtrackForScene(0);
        }
        await this.wait(t.artworkArrivalMs + (t.artworkAloneMs ?? 0));
        if (!stillRunning()) return;
      } else {
        await this.wait(t.artworkAloneMs ?? 0);
        if (!stillRunning()) return;
      }

      if (!skippedCrossfade) {
        await this.wait(t.compoundsPauseBeforeMs ?? 2400);
        if (!stillRunning()) return;
      }

      await this.showCompoundsTargetKanji(stillRunning, scene.kanji, t);
      if (!stillRunning()) return;

      for (const step of steps) {
        await this.playCompoundsStep(stillRunning, step, t);
        if (!stillRunning()) return;
      }

      await this.showCompoundsTargetKanji(stillRunning, scene.kanji, t, { isReturn: true });
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
            this._soundtrackStarted = false;
            this.stopSoundtrack();
            await this.playOpeningBookend();
            if (!stillRunning()) return;
          }
          this._compoundsCrossfadedTo = -1;
          this.activeArtworkKey = "a";
          this.syncLegacyArtworkRefs();
          await this.playCompoundsExhibit(0);
        } else if (this.bookends?.closing) {
          await this.playClosingBookend();
        }
        return;
      }

      const nextScene = this.scenes[next];
      await this.crossfadeArtworkLayers(nextScene, transitionMs);
      if (!stillRunning()) return;
      this._compoundsCrossfadedTo = next;
      await this.playCompoundsExhibit(next);
    }

    async playStrokeOrderExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const player = window.KmlStrokeOrderPlayer;

      this.resetLayers();
      await this.populateStrokeOrderScene(scene);
      if (!stillRunning()) return;

      if (this.els.strokeOrderLayer) {
        this.els.strokeOrderLayer.classList.remove("exhibition-hidden");
      }
      this.setClass(this.els.veil, "is-clear", true);

      if (this.sceneIndex === 0) {
        await this.waitInitialExhibitionBlack(stillRunning, 0);
        if (!stillRunning()) return;
        this.maybeStartSoundtrackForScene(0);
      }

      const recognitionReveal = t.strokeOrderRecognitionRevealMs ?? 2200;
      const recognitionHold = t.strokeOrderRecognitionHoldMs ?? 2800;
      const kanjiFadeOut = t.strokeOrderKanjiFadeOutMs ?? 3200;
      const strokeFade = t.strokeOrderStrokeFadeMs ?? 1600;
      const preDraw = t.strokeOrderPreDrawPauseMs ?? 500;
      const drawMs = t.strokeOrderDrawMs ?? 1200;
      const gapMs = t.strokeOrderStrokeGapMs ?? 1500;
      const postDraw = t.strokeOrderPostDrawPauseMs ?? 1600;
      const completionReveal = t.strokeOrderCompletionRevealMs ?? 1400;
      const completionHold = t.strokeOrderCompletionHoldMs ?? 3000;
      const exhibitFade = t.strokeOrderExhibitFadeMs ?? kanjiFadeOut;
      const pageTurnTransition = t.exhibitTransitionMs ?? 0;
      const pageTurnBlackHold = t.exhibitBlackHoldMs ?? 0;

      const kanjiEl = this.els.strokeOrderKanji;
      const svgWrap = this.els.strokeOrderSvg;
      const { drawColor: strokeColor, finalColor } = this.strokeOrderColorsForScene(
        scene,
        t
      );

      this.setStrokeOrderFadeTiming(recognitionReveal, kanjiFadeOut);
      kanjiEl?.classList.remove("is-dissolving");
      // Mount first, let layout settle, then fade in to avoid a first-frame jump.
      kanjiEl?.classList.remove("is-visible");
      if (kanjiEl) {
        void kanjiEl.offsetWidth;
      }
      await this.waitForPaintFrame();
      if (!stillRunning()) return;
      kanjiEl?.classList.add("is-visible");
      await this.wait(recognitionReveal);
      if (!stillRunning()) return;
      await this.wait(recognitionHold);
      if (!stillRunning()) return;

      this.setStrokeOrderFadeTiming(strokeFade, kanjiFadeOut);
      kanjiEl?.classList.remove("is-visible");
      await this.wait(kanjiFadeOut);
      if (!stillRunning()) return;

      this.setStrokeOrderFadeTiming(strokeFade, strokeFade);
      svgWrap?.classList.add("is-visible");
      const svgEl = svgWrap?.querySelector("svg");
      const strokeCount =
        scene.strokeOrder?.strokeCount ?? scene.meta?.strokeCount ?? 1;
      const strokeWidth = this.usesAdaptiveStrokeOrderWidth
        ? this.strokeOrderWidthForCount(strokeCount)
        : null;
      const strokes = player?.prepareStrokes(svgEl, {
        drawColor: strokeColor,
        finalColor,
        ...(strokeWidth != null ? { strokeWidth } : {}),
      });

      await this.wait(preDraw);
      if (!stillRunning()) return;

      if (strokes && player) {
        await player.animateStrokes(strokes, {
          drawMs,
          gapMs,
          finalColor,
        });
      } else {
        const fallbackMs =
          player?.strokeAnimationDurationMs(scene.strokeOrder?.strokeCount, {
            drawMs,
            gapMs,
          }) ?? 2000;
        await this.wait(fallbackMs);
      }
      if (!stillRunning()) return;

      await this.wait(postDraw);
      if (!stillRunning()) return;

      this.setStrokeOrderFadeTiming(completionReveal, strokeFade);
      svgWrap?.classList.remove("is-visible");
      await this.wait(strokeFade);
      if (!stillRunning()) return;

      this.setStrokeOrderFadeTiming(completionReveal, kanjiFadeOut);
      kanjiEl?.classList.add("is-visible");
      await this.wait(completionReveal);
      if (!stillRunning()) return;
      await this.wait(completionHold);
      if (!stillRunning()) return;

      // Elementary stroke-order cards use a gentle dissolve before the page-turn beat.
      if (this.isElementaryStrokeOrderProfile) {
        kanjiEl?.classList.add("is-dissolving");
      }
      this.setStrokeOrderFadeTiming(exhibitFade, exhibitFade);
      kanjiEl?.classList.remove("is-visible");
      await this.wait(exhibitFade);
      if (!stillRunning()) return;
      kanjiEl?.classList.remove("is-dissolving");

      if (pageTurnTransition > 0) {
        await this.wait(pageTurnTransition);
        if (!stillRunning()) return;
      }
      if (pageTurnBlackHold > 0) {
        await this.wait(pageTurnBlackHold);
        if (!stillRunning()) return;
      }

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
          await this.playStrokeOrderExhibit(0);
        } else if (this.bookends?.closing) {
          this.resetStrokeOrderLayer();
          await this.playClosingBookend();
        } else if (this.soundtrack?.main) {
          await this.waitForSoundtrackEnd();
          this.finishPresentation();
        } else {
          this.finishPresentation();
        }
        return;
      }

      await this.playStrokeOrderExhibit(next);
    }

    async playVerseReadingExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const transitionMs = t.exhibitTransitionMs ?? 4000;
      const skippedCrossfade = this._verseReadingCrossfadedTo === index;
      this._verseReadingCrossfadedTo = -1;
      const verse = scene.verse || {};

      this.resetImageVerseForeground();
      if (this.els.verseEn) {
        this.els.verseEn.textContent = verse.en || "";
      }

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
        await this.wait(t.artworkArrivalMs + (t.artworkAloneMs ?? 0));
        if (!stillRunning()) return;
      } else {
        await this.wait(t.artworkAloneMs ?? 0);
        if (!stillRunning()) return;
      }

      await this.playReadingStage(
        stillRunning,
        verse.hiragana,
        this.readingStageTiming(t, "readingHiragana")
      );
      if (!stillRunning()) return;
      await this.playReadingStage(
        stillRunning,
        verse.mixed,
        this.readingStageTiming(t, "readingMixed")
      );
      if (!stillRunning()) return;
      await this.playReadingStage(
        stillRunning,
        verse.natural,
        this.readingStageTiming(t, "readingNatural")
      );
      if (!stillRunning()) return;

      if (this.showEnglish && verse.en) {
        this.setClass(this.els.verseEn, "is-reading-reflection", true);
        this.setClass(this.els.verseEn, "is-visible", true);
        await this.wait(t.readingEnRevealMs ?? 1000);
        if (!stillRunning()) return;
        await this.wait(t.readingEnHoldMs ?? 5000);
        if (!stillRunning()) return;
        this.setClass(this.els.verseEn, "is-visible", false);
        await this.wait(t.readingEnFadeMs ?? 1000);
        if (!stillRunning()) return;
        this.setClass(this.els.verseEn, "is-reading-reflection", false);
      }

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
          this._verseReadingCrossfadedTo = -1;
          this.activeArtworkKey = "a";
          this.syncLegacyArtworkRefs();
          await this.playVerseReadingExhibit(0);
        } else if (this.bookends?.closing) {
          await this.playClosingBookend();
        }
        return;
      }

      const nextScene = this.scenes[next];
      await this.crossfadeArtworkLayers(nextScene, transitionMs);
      if (!stillRunning()) return;
      this._verseReadingCrossfadedTo = next;
      await this.playVerseReadingExhibit(next);
    }

    hideAllPartyPhases() {
      Object.values(this.partyPhases).forEach((phase) => {
        if (!phase) return;
        phase.classList.remove("is-visible", "is-fading");
      });
    }

    resetPartyKanjiLayers() {
      this.hideAllPartyPhases();
      if (this.els.partyLayer) {
        this.els.partyLayer.classList.add("exhibition-hidden");
      }
      if (this.els.partyStrokesFrame) {
        this.els.partyStrokesFrame.removeAttribute("src");
      }
      if (this.els.partyComponentPulse) {
        this.els.partyComponentPulse.classList.remove("is-visible", "is-pulsing");
      }
    }

    partyVisualConfig(scene) {
      const base = this.meta.partyVisual || {};
      const override = scene?.party?.visual || {};
      return { ...base, ...override };
    }

    buildPartyComponentCellsHtml(party, { pulse = false } = {}) {
      const parts = party.components || [];
      const layout = party.componentLayout || "vertical";
      const pulseClass = pulse ? " party-component-cell--pulse" : "";
      return parts
        .map(
          (c, i) =>
            `<div class="party-component-cell${pulseClass}" data-component-index="${i}">` +
            `<span class="party-component-kanji">${c.kanji}</span>` +
            (c.label && !pulse ? `<span class="party-component-label">${c.label}</span>` : "") +
            `</div>`
        )
        .join("");
    }

    buildPartyEquationHtml(party, kanji) {
      const parts = party.components || [];
      const op = party.operator || "+";
      const spans = parts.map((c) => `<span>${c.kanji}</span>`);
      if (!spans.length) return `<span class="party-result">${kanji}</span>`;
      return `${spans.join(` ${op} `)} = <span class="party-result">${kanji}</span>`;
    }

    populatePartyKanjiScene(scene) {
      const party = scene.party || {};
      const visual = this.partyVisualConfig(scene);
      const kanji = scene.kanji || "";
      const playlist = party.playlist || party.collection || "";

      if (this.els.partyShockKanji) this.els.partyShockKanji.textContent = kanji;
      if (this.els.partyFinalKanji) this.els.partyFinalKanji.textContent = kanji;
      if (this.els.partyChallenge) {
        this.els.partyChallenge.textContent = party.challenge || "";
        this.els.partyChallenge.classList.add("party-kanji-challenge--hidden");
        this.els.partyChallenge.classList.remove("is-visible");
      }
      if (this.els.partyPlaylist) {
        this.els.partyPlaylist.textContent =
          visual.showPlaylistSubtitle !== false && playlist ? playlist : "";
        this.els.partyPlaylist.style.display =
          visual.showPlaylistSubtitle !== false && playlist ? "" : "none";
      }
      if (this.els.partyPlaylistEnd) {
        this.els.partyPlaylistEnd.textContent = playlist || "";
        this.els.partyPlaylistEnd.style.display = playlist ? "" : "none";
      }
      if (this.els.partyComponents) {
        const layout = party.componentLayout || "vertical";
        const revealMode = visual.componentReveal === "slide" ? "slide" : "burst";
        this.els.partyComponents.className = "party-kanji-components";
        this.els.partyComponents.classList.add(`party-kanji-components--${revealMode}`);
        this.els.partyComponents.classList.add(
          layout === "vertical" ? "is-vertical" : "is-horizontal"
        );
        this.els.partyComponents.innerHTML = this.buildPartyComponentCellsHtml(party);
      }
      if (this.els.partyComponentPulse) {
        const layout = party.componentLayout || "vertical";
        this.els.partyComponentPulse.className =
          "party-kanji-component-pulse" +
          (layout === "vertical" ? " is-vertical" : " is-horizontal");
        this.els.partyComponentPulse.style.setProperty(
          "--pk-pulse-opacity",
          String(visual.componentPulseOpacity ?? 0.18)
        );
        this.els.partyComponentPulse.innerHTML = this.buildPartyComponentCellsHtml(party, {
          pulse: true,
        });
      }
      if (this.els.partyEquation) {
        this.els.partyEquation.innerHTML = this.buildPartyEquationHtml(party, kanji);
        this.els.partyEquation.classList.add("party-kanji-equation--hidden");
        this.els.partyEquation.classList.remove("is-visible");
      }
      if (this.els.partyReading) {
        this.els.partyReading.textContent = party.reading || "";
        const show = visual.showReadingInReveal === true && party.reading;
        this.els.partyReading.style.display = show ? "" : "none";
      }
      if (this.els.partyTrivia) {
        this.els.partyTrivia.textContent = party.trivia || "";
        const show = visual.showTrivia === true && party.trivia;
        this.els.partyTrivia.style.display = show ? "" : "none";
      }
      if (this.els.partyFinalReading) {
        this.els.partyFinalReading.textContent = party.reading || "";
        this.els.partyFinalReading.style.display = party.reading ? "" : "none";
      }
      if (this.els.partyStrokeNote) {
        this.els.partyStrokeNote.textContent = party.strokeNote || "";
        this.els.partyStrokeNote.style.display = party.strokeNote ? "" : "none";
      }
      if (this.els.partyClosingMessage) {
        this.els.partyClosingMessage.textContent =
          party.closingMessage || this.meta.closingMessage || "";
      }
      if (this.els.partyBrand) {
        this.els.partyBrand.textContent = this.meta.series || "PARTY KANJI";
      }
      if (this.els.partyTagline) {
        this.els.partyTagline.textContent =
          this.meta.tagline || "Learn this before your next party.";
      }
      if (this.els.partyDisclaimer) {
        this.els.partyDisclaimer.textContent =
          party.disclaimer || this.meta.disclaimers?.[0] || "";
      }
    }

    async playPartyKanjiPhase(stillRunning, phaseKey, fadeInMs, holdMs, fadeOutMs) {
      const phase = this.partyPhases[phaseKey];
      if (!phase) return;

      this.hideAllPartyPhases();
      phase.classList.remove("is-fading");
      phase.classList.add("is-visible");
      await this.wait(fadeInMs);
      if (!stillRunning()) return;
      await this.wait(holdMs);
      if (!stillRunning()) return;
      if (fadeOutMs > 0) {
        phase.classList.add("is-fading");
        await this.wait(fadeOutMs);
        if (!stillRunning()) return;
        phase.classList.remove("is-visible", "is-fading");
      }
    }

    async playPartyKanjiShock(stillRunning, t) {
      const phase = this.partyPhases.shock;
      if (!phase) return;

      this.hideAllPartyPhases();
      phase.classList.add("is-visible");
      await this.wait(t.partyShockKanjiRevealMs ?? 250);
      if (!stillRunning()) return;

      await this.wait(t.partyShockChallengeDelayMs ?? 3000);
      if (!stillRunning()) return;
      this.els.partyChallenge?.classList.remove("party-kanji-challenge--hidden");
      this.els.partyChallenge?.classList.add("is-visible");
      await this.wait(t.partyShockChallengeRevealMs ?? 350);
      if (!stillRunning()) return;

      await this.wait(t.partyShockHoldAfterChallengeMs ?? 1650);
      if (!stillRunning()) return;

      phase.classList.add("is-fading");
      await this.wait(t.partyShockFadeMs ?? 400);
      phase.classList.remove("is-visible", "is-fading");
      this.els.partyChallenge?.classList.add("party-kanji-challenge--hidden");
      this.els.partyChallenge?.classList.remove("is-visible");
    }

    async playPartyKanjiRevealStaged(stillRunning, t, party, visual) {
      const phase = this.partyPhases.reveal;
      if (!phase) return;

      this.hideAllPartyPhases();
      phase.classList.add("is-visible");
      await this.wait(t.partyRevealFadeInMs ?? 350);
      if (!stillRunning()) return;

      const container = this.els.partyComponents;
      container?.classList.add("is-bursting");
      await this.wait(t.partyRevealBurstMs ?? 400);
      if (!stillRunning()) return;
      container?.classList.remove("is-bursting");

      const cells = container ? [...container.querySelectorAll(".party-component-cell")] : [];
      const stagger = t.partyComponentStaggerMs ?? 2000;
      const arriveMs = t.partyComponentArriveMs ?? 450;

      for (let i = 0; i < cells.length; i++) {
        if (i > 0) await this.wait(stagger);
        if (!stillRunning()) return;
        cells[i].classList.add("is-arrived");
        if (visual.componentGlow !== false) {
          cells[i].classList.add("is-glowing");
          await this.wait(arriveMs);
          if (!stillRunning()) return;
          cells[i].classList.remove("is-glowing");
        } else {
          await this.wait(arriveMs);
        }
      }

      await this.wait(t.partyEquationDelayMs ?? 3000);
      if (!stillRunning()) return;
      this.els.partyEquation?.classList.remove("party-kanji-equation--hidden");
      this.els.partyEquation?.classList.add("is-visible");
      await this.wait(t.partyEquationRevealMs ?? 400);
      if (!stillRunning()) return;

      await this.wait(t.partyEquationHoldMs ?? 5000);
      if (!stillRunning()) return;

      phase.classList.add("is-fading");
      await this.wait(t.partyRevealFadeMs ?? 400);
      phase.classList.remove("is-visible", "is-fading");
    }

    async playPartyKanjiFinalWithPulse(stillRunning, t, visual) {
      const phase = this.partyPhases.final;
      if (!phase) return;

      this.hideAllPartyPhases();
      phase.classList.add("is-visible");
      if (visual.finalGlow !== false) {
        this.els.partyFinalKanji?.classList.add("is-reward-glow");
      }
      await this.wait(t.partyFinalFadeInMs ?? 1200);
      if (!stillRunning()) return;

      await this.wait(t.partyFinalHoldMs ?? 2000);
      if (!stillRunning()) return;

      const pulse = this.els.partyComponentPulse;
      if (pulse) {
        pulse.classList.add("is-visible");
        await this.wait(t.partyComponentPulseFadeInMs ?? 600);
        if (!stillRunning()) return;
        pulse.classList.add("is-pulsing");
        await this.wait(t.partyComponentPulseHoldMs ?? 2500);
        if (!stillRunning()) return;
        pulse.classList.remove("is-pulsing", "is-visible");
      }

      phase.classList.add("is-fading");
      await this.wait(t.partyFinalFadeOutMs ?? 700);
      phase.classList.remove("is-visible", "is-fading");
      this.els.partyFinalKanji?.classList.remove("is-reward-glow");
    }

    async playPartyKanjiExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const party = scene.party || {};
      const visual = this.partyVisualConfig(scene);

      this.resetLayers();
      this.resetPartyKanjiLayers();
      this.populatePartyKanjiScene(scene);

      if (this.els.partyLayer) {
        this.els.partyLayer.classList.remove("exhibition-hidden");
      }
      this.setClass(this.els.veil, "is-clear", true);

      await this.playPartyKanjiShock(stillRunning, t);
      if (!stillRunning()) return;

      await this.playPartyKanjiRevealStaged(stillRunning, t, party, visual);
      if (!stillRunning()) return;

      if (this.els.partyStrokesFrame && party.strokePage) {
        this.els.partyStrokesFrame.src = party.strokePage;
      }
      await this.playPartyKanjiPhase(
        stillRunning,
        "proof",
        t.partyProofFadeInMs ?? 400,
        t.partyProofHoldMs ?? 8000,
        t.partyProofFadeMs ?? 400
      );
      if (!stillRunning()) return;

      await this.playPartyKanjiFinalWithPulse(stillRunning, t, visual);
      if (!stillRunning()) return;

      await this.playPartyKanjiPhase(
        stillRunning,
        "closing",
        t.partyClosingFadeInMs ?? 400,
        t.partyClosingHoldMs ?? 3000,
        t.partyClosingFadeMs ?? 400
      );
      if (!stillRunning()) return;

      await this.playPartyKanjiPhase(
        stillRunning,
        "endcard",
        t.partyEndCardFadeInMs ?? 400,
        t.partyEndCardHoldMs ?? 2000,
        t.partyEndCardFadeMs ?? 400
      );
      if (!stillRunning()) return;

      this.resetPartyKanjiLayers();

      if (this.singleExhibit) {
        document.dispatchEvent(
          new CustomEvent("kml-exhibition-exhibit-end", {
            detail: { index: this.sceneIndex, sceneId: scene.id },
          })
        );
        this.finishPresentation();
        return;
      }

      const next = this.sceneIndex + 1;
      if (next >= count) {
        if (this.display.loop) {
          await this.playPartyKanjiExhibit(0);
        } else if (this.bookends?.closing) {
          await this.playClosingBookend();
        }
        return;
      }

      this.setClass(this.els.veil, "is-corridor", true);
      this.setClass(this.els.veil, "is-clear", false);
      await this.wait(t.exhibitBlackHoldMs ?? t.blackHoldMs ?? 500);
      if (!stillRunning()) return;

      await this.playPartyKanjiExhibit(next);
    }

    async playImageVerseExhibit(index, options = {}) {
      if (this.destroyed || !this.scenes.length) return;

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      const fromCrossfade = Boolean(options.fromCrossfade);
      const sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[sceneIndex];

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = sceneIndex;
      const t = this.timing;
      const s = this.sequentialVerseTiming();
      const kanjiHoldMs = t.imageVerseKanjiHoldMs ?? 2000;
      const kanjiFadeMs = t.imageVerseKanjiFadeMs ?? t.titleFadeMs ?? 1600;
      const transitionMs = t.exhibitTransitionMs ?? 4000;
      const skippedCrossfade =
        fromCrossfade ||
        this._imageVerseCrossfadedTo === index ||
        this.artworkLayerShowsScene(this.activeArtworkKey, scene);
      this._imageVerseCrossfadedTo = -1;

      this.resetImageVerseForeground();
      this.populateVerseContent(scene);

      const inactiveKey = this.inactiveArtworkKey();
      const activeKey = this.activeArtworkKey;
      const activeLayer = this.artworkLayers[activeKey];

      if (!skippedCrossfade) {
        this.onlyShowArtworkLayer(activeKey);
        this.populateArtworkLayer(activeKey, scene);
        this.syncLegacyArtworkRefs();
        await this.applySceneCameraToImage(activeLayer.img, scene);
        if (!stillRunning()) return;

        this.setClass(this.els.veil, "is-clear", true);
        this.showArtworkLayer(activeKey, { hideOther: false });
        await this.wait(t.artworkArrivalMs + t.artworkAloneMs);
        if (!stillRunning()) return;
      } else {
        if (!this.artworkLayerShowsScene(activeKey, scene)) {
          this.onlyShowArtworkLayer(activeKey);
          this.populateArtworkLayer(activeKey, scene);
          this.syncLegacyArtworkRefs();
          await this.applySceneCameraToImage(activeLayer.img, scene);
          if (!stillRunning()) return;
        } else {
          this.onlyShowArtworkLayer(activeKey);
        }
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
      await this.playImageVerseExhibit(next, { fromCrossfade: true });
    }

    async playGalleryExhibit(index, options = {}) {
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
      const skippedCrossfade = this._galleryCrossfadedTo === index;
      this._galleryCrossfadedTo = -1;

      this.resetImageVerseForeground();
      this.populateVerseContent(scene);

      if (!skippedCrossfade) {
        await this.waitInitialExhibitionBlack(stillRunning, this.sceneIndex);
        if (!stillRunning()) return;

        const layer = this.artworkLayers[this.activeArtworkKey];
        if (this.sceneIndex === 0) {
          document.documentElement.style.setProperty(
            "--ex-artwork-arrival",
            `${t.artworkArrivalFadeMs ?? 2000}ms`
          );
        }
        this.populateArtworkLayer(this.activeArtworkKey, scene);
        this.syncLegacyArtworkRefs();
        await this.applySceneCameraToImage(layer.img, scene);
        if (!stillRunning()) return;

        this.setClass(this.els.veil, "is-clear", true);
        this.setClass(layer.wrap, "is-exhaling", false);
        this.setClass(layer.wrap, "is-on-top", true);
        this.setClass(layer.wrap, "is-visible", true);
        const arrivalFadeMs =
          this.sceneIndex === 0 ? (t.artworkArrivalFadeMs ?? 0) : 0;
        if (arrivalFadeMs > 0) {
          await this.wait(arrivalFadeMs);
          if (!stillRunning()) return;
        }
        if (this.sceneIndex === 0) {
          this.maybeStartSoundtrackForScene(0);
        }
        await this.wait(t.artworkArrivalMs + t.artworkAloneMs);
        if (!stillRunning()) return;
      } else {
        await this.wait(t.artworkAloneMs);
        if (!stillRunning()) return;
      }

      // Same phase lengths as imageVerse — artwork only, no text.
      await this.wait(t.kanjiRevealMs);
      if (!stillRunning()) return;
      await this.wait(kanjiHoldMs);
      if (!stillRunning()) return;
      await this.wait(kanjiFadeMs);
      if (!stillRunning()) return;

      await this.wait(s.verseJpRevealMs);
      if (!stillRunning()) return;
      await this.wait(s.verseJpHoldMs);
      if (!stillRunning()) return;
      await this.wait(s.verseJpFadeMs);
      if (!stillRunning()) return;

      await this.wait(s.verseEnRevealMs);
      if (!stillRunning()) return;
      await this.wait(s.verseEnHoldMs);
      if (!stillRunning()) return;
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
          this._galleryCrossfadedTo = -1;
          this.activeArtworkKey = "a";
          this.syncLegacyArtworkRefs();
          await this.playGalleryExhibit(0);
        } else if (this.bookends?.closing) {
          await this.playClosingBookend();
        }
        return;
      }

      const nextScene = this.scenes[next];
      await this.crossfadeArtworkLayers(nextScene, transitionMs);
      if (!stillRunning()) return;
      this._galleryCrossfadedTo = next;
      await this.playGalleryExhibit(next);
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

    /**
     * Wait until ambient soundtrack currentTime reaches targetMs (wall-clock sync).
     * Falls back to relative waits when audio is unavailable.
     */
    async waitUntilSoundtrackMs(targetMs, stillRunning) {
      const audio = this.mainAudio;
      if (!audio || !this._soundtrackStarted) {
        await this.wait(Math.max(0, targetMs));
        return;
      }

      const absoluteMs = Math.max(0, targetMs);
      while (stillRunning()) {
        if (audio.ended) return;
        const nowMs = Math.max(0, (audio.currentTime || 0) * 1000);
        if (nowMs >= absoluteMs) return;
        const remaining = absoluteMs - nowMs;
        // Compensate timingScale inside wait() so poll interval stays near real-time.
        const pollMs = Math.min(Math.max(remaining, 16), 250);
        await this.wait(this.timingScale ? pollMs / this.timingScale : pollMs);
      }
    }

    waitForPaintFrame() {
      const runId = this.runId;
      return new Promise((resolve) => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            if (!this.destroyed && runId === this.runId) resolve();
          });
        });
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

      if (opening.jp || opening.en || opening.images?.length) {
        await this.playOpeningImageSequence(opening);
        return;
      }

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

    resetVocabularyIntroOverlay() {
      const overlay = this.els.vocabIntroOverlay;
      const jp = this.els.vocabIntroJp;
      const reading = this.els.vocabIntroReading;
      const en = this.els.vocabIntroEn;
      const block = this.els.vocabIntroJpBlock;
      if (jp) {
        jp.textContent = "";
        jp.innerHTML = "";
        jp.classList.remove("is-visible");
      }
      if (reading) {
        reading.textContent = "";
        reading.innerHTML = "";
        reading.classList.remove("is-visible");
      }
      if (block) {
        block.classList.remove("is-visible", "has-reading");
      }
      if (en) {
        en.textContent = "";
        en.innerHTML = "";
        en.classList.remove("is-visible");
      }
      if (overlay) {
        overlay.classList.add("exhibition-hidden");
        overlay.setAttribute("aria-hidden", "true");
      }
    }

    showVocabularyIntroOverlay() {
      const overlay = this.els.vocabIntroOverlay;
      if (!overlay) return;
      overlay.classList.remove("exhibition-hidden");
      overlay.setAttribute("aria-hidden", "false");
    }

    setVocabularyIntroJapanese(opening) {
      const jpEl = this.els.vocabIntroJp;
      if (!jpEl) return;
      const columns = opening.jpColumns?.length
        ? opening.jpColumns
        : opening.jp
          ? [opening.jp]
          : [];
      jpEl.innerHTML = columns
        .map((col) => `<span class="vocabulary-intro-jp-col">${col}</span>`)
        .join("");
    }

    setVocabularyIntroReading(opening) {
      const readingEl = this.els.vocabIntroReading;
      if (!readingEl) return;
      const lines = opening.readingLines?.length
        ? opening.readingLines
        : opening.reading
          ? String(opening.reading).split(/\n/)
          : [];
      readingEl.innerHTML = lines
        .map((line) => `<span class="vocabulary-intro-reading-line">${line}</span>`)
        .join("");
    }

    async fadeVocabularyIntroEl(el, visible, durationMs, stillRunning) {
      if (!el) return;
      document.documentElement.style.setProperty("--ex-vocab-intro-fade", `${durationMs}ms`);
      await this.waitForPaintFrame();
      if (!stillRunning()) return;
      el.classList.toggle("is-visible", visible);
      await this.wait(durationMs);
    }

    /**
     * Tea-ceremony entrance for Japanese Vocabulary:
     * atmosphere → vertical calligraphy → reading guide → English quotation.
     */
    async playOpeningImageSequence(opening) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;

      if (opening.images?.length && !(opening.jp || opening.en || opening.jpColumns)) {
        await this.playOpeningBakedImageSequence(opening);
        return;
      }

      const imagePath = opening.image || opening.images?.[0]?.image;
      if (!imagePath) return;

      this.debugLog("enter playOpeningAtmosphereText", {
        image: imagePath,
        jp: opening.jp,
        en: opening.en,
      });
      this.resetLayers();
      this.clearBookendText();
      this.hideBookendTitle(false);
      this.resetVocabularyIntroOverlay();
      this.root.classList.add("is-opening-image-sequence");

      const blackBefore = opening.blackBeforeMs ?? t.openingBlackBeforeMs ?? 800;
      if (blackBefore > 0) {
        await this.wait(blackBefore);
        if (!stillRunning()) return;
      }

      const revealMs = opening.revealMs ?? t.openingRevealMs ?? 2000;
      const atmosphereHoldMs = opening.atmosphereHoldMs ?? 5000;
      const layer = this.artworkLayers[this.activeArtworkKey];
      const scene = { id: "opening_atmosphere", image: imagePath };

      document.documentElement.style.setProperty("--ex-artwork-arrival", `${revealMs}ms`);
      this.populateArtworkLayer(this.activeArtworkKey, scene);
      await this.waitForArtworkImage(layer.img);
      layer.img.classList.remove("ken-burns", "gallery-guardian");
      this.setClass(this.els.veil, "is-corridor", false);
      this.setClass(this.els.veil, "is-clear", true);
      this.setClass(layer.wrap, "is-exhaling", false);
      this.setClass(layer.wrap, "is-on-top", true);
      this.setClass(layer.wrap, "is-visible", true);

      if (this.shouldStartSoundtrackDuringOpening(opening)) {
        this.scheduleSoundtrackAfterBookendImage(stillRunning, opening);
      }

      await this.wait(revealMs);
      if (!stillRunning()) return;
      await this.wait(atmosphereHoldMs);
      if (!stillRunning()) return;

      this.showVocabularyIntroOverlay();

      const hasJp = Boolean(opening.jp || opening.jpColumns?.length);
      if (hasJp && this.els.vocabIntroJp) {
        const jpReveal = opening.jpRevealMs ?? 2600;
        const jpHold = opening.jpHoldMs ?? 5500;
        const jpFade = opening.jpFadeMs ?? 2200;
        this.setVocabularyIntroJapanese(opening);
        this.els.vocabIntroJp.classList.remove("is-visible");
        this.els.vocabIntroJpBlock?.classList.remove("has-reading");
        await this.fadeVocabularyIntroEl(
          this.els.vocabIntroJp,
          true,
          jpReveal,
          stillRunning
        );
        if (!stillRunning()) return;
        await this.wait(jpHold);
        if (!stillRunning()) return;
        await this.fadeVocabularyIntroEl(
          this.els.vocabIntroJp,
          false,
          jpFade,
          stillRunning
        );
        if (!stillRunning()) return;
      }

      if (opening.en && this.els.vocabIntroEn) {
        const enReveal = opening.enRevealMs ?? 2600;
        const enHold = opening.enHoldMs ?? 6000;
        const enFade = opening.enFadeMs ?? 2200;
        const enText = String(opening.en);
        this.els.vocabIntroEn.innerHTML = enText
          .split(/\n/)
          .map((line) => `<span class="vocabulary-intro-en-line">${line}</span>`)
          .join("");
        this.els.vocabIntroEn.classList.remove("is-visible");
        await this.fadeVocabularyIntroEl(
          this.els.vocabIntroEn,
          true,
          enReveal,
          stillRunning
        );
        if (!stillRunning()) return;
        await this.wait(enHold);
        if (!stillRunning()) return;
        await this.fadeVocabularyIntroEl(
          this.els.vocabIntroEn,
          false,
          enFade,
          stillRunning
        );
        if (!stillRunning()) return;
      }

      const exhaleMs = opening.exhaleMs ?? t.openingExhaleMs ?? 2200;
      document.documentElement.style.setProperty("--ex-transition", `${exhaleMs}ms`);
      this.setClass(layer.wrap, "is-exhaling", true);
      this.setClass(layer.wrap, "is-visible", false);
      await this.wait(exhaleMs);
      if (!stillRunning()) return;

      this.resetVocabularyIntroOverlay();
      this.root.classList.remove("is-opening-image-sequence");
      this.activeArtworkKey = "a";
      this.syncLegacyArtworkRefs();
      this.resetLayers();
      this.setClass(this.els.veil, "is-corridor", false);
      this.setClass(this.els.veil, "is-clear", false);

      const blackAfter = opening.blackAfterMs ?? t.openingBlackAfterMs ?? 600;
      if (blackAfter > 0) {
        await this.wait(blackAfter);
        if (!stillRunning()) return;
      }

      if (this.scenes[0]) {
        await this.preloadSceneArtwork(this.scenes[0]);
      }
      this.debugLog("exit playOpeningAtmosphereText");
    }

    async playOpeningBakedImageSequence(opening) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;
      const frames = opening.images || [];
      if (!frames.length) return;

      this.resetLayers();
      this.clearBookendText();
      this.hideBookendTitle(false);
      this.root.classList.add("is-opening-image-sequence");

      const blackBefore = opening.blackBeforeMs ?? t.openingBlackBeforeMs ?? 1200;
      if (blackBefore > 0) {
        await this.wait(blackBefore);
        if (!stillRunning()) return;
      }

      const startMusic = this.shouldStartSoundtrackDuringOpening(opening);

      for (let i = 0; i < frames.length; i += 1) {
        const frame = frames[i];
        const scene = { id: `opening_sequence_${i}`, image: frame.image };
        const fadeMs =
          frame.fadeMs ??
          frame.revealMs ??
          opening.fadeMs ??
          (i === 0 ? t.openingRevealMs ?? 2400 : 2000);
        const holdMs = frame.holdMs ?? opening.holdMs ?? 3000;

        if (i === 0) {
          const layer = this.artworkLayers[this.activeArtworkKey];
          document.documentElement.style.setProperty("--ex-artwork-arrival", `${fadeMs}ms`);
          this.populateArtworkLayer(this.activeArtworkKey, scene);
          await this.waitForArtworkImage(layer.img);
          layer.img.classList.remove("ken-burns", "gallery-guardian");
          this.setClass(this.els.veil, "is-corridor", false);
          this.setClass(this.els.veil, "is-clear", true);
          this.setClass(layer.wrap, "is-exhaling", false);
          this.setClass(layer.wrap, "is-on-top", true);
          this.setClass(layer.wrap, "is-visible", true);
          if (startMusic) {
            this.scheduleSoundtrackAfterBookendImage(stillRunning, opening);
          }
          await this.wait(fadeMs);
        } else {
          await this.crossfadeArtworkLayers(scene, fadeMs, { still: true });
        }
        if (!stillRunning()) return;
        await this.wait(holdMs);
        if (!stillRunning()) return;
      }

      const exhaleMs = opening.exhaleMs ?? t.openingExhaleMs ?? 2800;
      const active = this.artworkLayers[this.activeArtworkKey];
      document.documentElement.style.setProperty("--ex-transition", `${exhaleMs}ms`);
      this.setClass(active?.wrap, "is-exhaling", true);
      this.setClass(active?.wrap, "is-visible", false);
      await this.wait(exhaleMs);
      if (!stillRunning()) return;

      this.root.classList.remove("is-opening-image-sequence");
      this.activeArtworkKey = "a";
      this.syncLegacyArtworkRefs();
      this.resetLayers();
      this.setClass(this.els.veil, "is-corridor", false);
      this.setClass(this.els.veil, "is-clear", false);

      const blackAfter = opening.blackAfterMs ?? t.openingBlackAfterMs ?? 800;
      if (blackAfter > 0) {
        await this.wait(blackAfter);
        if (!stillRunning()) return;
      }

      if (this.scenes[0]) {
        await this.preloadSceneArtwork(this.scenes[0]);
      }
    }

    async preloadSceneArtwork(scene) {
      if (!scene) return;
      const key = this.activeArtworkKey;
      this.populateArtworkLayer(key, scene);
      const img = this.artworkLayers[key]?.img;
      if (img) await this.waitForArtworkImage(img);
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

      if (this.isSilentGalleryCrestBookends()) {
        this.setClass(this.els.veil, "is-corridor", false);
        this.setClass(this.els.veil, "is-clear", true);
        if (this.scenes[0]) {
          await this.preloadSceneArtwork(this.scenes[0]);
          if (!stillRunning()) return;
        }
        this.debugLog("exit playGalleryCrestOpeningBookend (silent crest → first scene)");
        return;
      }

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

      if (
        closing.image &&
        (this.display.bookendStyle === "galleryCrest" || this.isSilentGalleryCrestBookends())
      ) {
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
      const isSilent = this.isSilentGalleryCrestBookends();
      const holdUntilSoundtrackEnds = Boolean(
        this.soundtrack?.main && closing.holdUntilSoundtrackEnds !== false
      );
      const crestFadeMs = t.closingExhaleMs ?? t.closingFadeToBlackMs ?? 3000;
      const titleRevealMs = t.closingTitleRevealMs ?? 2500;
      const titleFadeMs = t.closingTitleFadeMs ?? t.closingFadeToBlackMs ?? 3000;

      this.debugLog("enter playGalleryCrestClosingBookend", {
        image: closing.image,
        isSilent,
        holdUntilSoundtrackEnds,
        titleHtml: closing.titleHtml,
      });

      if (isSilent) {
        await this.playSilentGalleryCrestClosingBookend(closing);
        return;
      }
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

    async playSilentGalleryCrestClosingBookend(closing) {
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      const t = this.timing;
      const crestFadeMs = t.closingExhaleMs ?? t.closingFadeToBlackMs ?? 3500;
      const soundtrackAlreadyEnded = this.getSoundtrackRemainingMs() <= 0;
      // Vocabulary standard: music ended on the final scene; crest is pure silence.
      const vocabularySilentCrest =
        this.isJapaneseVocabularyProfile || closing.silentAfterSoundtrack === true;
      // Lesson vocabulary (and similar): honor explicit short close — do not pad to bed end.
      const holdUntilSoundtrackEnds = Boolean(
        this.soundtrack?.main && closing.holdUntilSoundtrackEnds !== false
      );

      this.resetLayers();
      this.clearBookendText();
      this.hideBookendTitle(false);

      await this.wait(t.closingBlackBeforeMs ?? t.blackHoldMs);
      if (!stillRunning()) return;

      await this.showBookendImage(closing.image, t.closingRevealMs, closing, "closing");
      if (!stillRunning()) return;

      const holdMs =
        t.closingHoldMs ??
        (soundtrackAlreadyEnded || vocabularySilentCrest || !holdUntilSoundtrackEnds
          ? 2800
          : 0);
      if (holdMs > 0) {
        await this.wait(holdMs);
        if (!stillRunning()) return;
      }

      if (!vocabularySilentCrest && holdUntilSoundtrackEnds) {
        while (stillRunning()) {
          const remaining = this.getSoundtrackRemainingMs();
          if (remaining <= 0 || remaining <= crestFadeMs) break;
          await this.wait(Math.min(remaining - crestFadeMs, 250));
        }
        if (!stillRunning()) return;
        await this.fadeCrestWithSoundtrackEnd(crestFadeMs);
      } else if (!vocabularySilentCrest && closing.fadeWithSoundtrackEnd) {
        await this.fadeBookendWithSoundtrack(crestFadeMs, (ms) =>
          this.hideBookendCrest(ms)
        );
      } else {
        await this.hideBookendCrest(crestFadeMs);
      }
      if (!stillRunning()) return;

      const silenceMs = t.closingSilenceHoldMs ?? 0;
      if (silenceMs > 0) {
        await this.wait(silenceMs);
        if (!stillRunning()) return;
      }

      await this.wait(t.closingBlackAfterMs ?? 0);
      this.stopAllAudio();
      this.finishPresentation();
      this.debugLog("exit playSilentGalleryCrestClosingBookend");
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

      const soundtrackWithImage = this.shouldStartSoundtrackDuringOpening(opening);
      const bookendImageOptions = soundtrackWithImage
        ? {
            onImageReady: () =>
              this.scheduleSoundtrackAfterBookendImage(stillRunning, opening),
          }
        : {};

      if (holdUntilAudioEnds) {
        let introAudio;
        if (this.introPlayingFromGate) {
          this.introPlayingFromGate = false;
          introAudio = this.waitForAudioEnd(this.bookendAudio, runId);
        } else {
          introAudio = this.playAudioUntilEnd(opening.audio, { kind: "bookend" });
        }
        await this.showBookendImage(
          opening.image,
          t.openingRevealMs,
          opening,
          "opening",
          bookendImageOptions
        );
        if (!stillRunning()) return;
        if (opening.titleHtml) {
          const titleReveal = t.openingTitleRevealMs ?? t.openingRevealMs;
          await this.showBookendTitle(opening.titleHtml, titleReveal);
          if (!stillRunning()) return;
        }
        await introAudio;
        if (!stillRunning()) return;
        if (opening.titleHtml) {
          await this.wait(t.openingHoldMs);
          if (!stillRunning()) return;
          const titleFade = t.openingTitleFadeMs ?? t.openingExhaleMs;
          await this.hideBookendTitleFade(titleFade);
          if (!stillRunning()) return;
        }
      } else {
        const fluteMs = t.openingFluteMs;
        if (opening.audio) {
          this.playAudioUntilEnd(opening.audio, { kind: "bookend", maxMs: fluteMs });
          this.debugLog("opening flute started with artwork fade-in", { fluteMs });
        }
        await this.showBookendImage(
          opening.image,
          t.openingRevealMs,
          opening,
          "opening",
          bookendImageOptions
        );
        if (!stillRunning()) return;
        if (opening.titleHtml) {
          const titleReveal = t.openingTitleRevealMs ?? t.openingRevealMs;
          await this.showBookendTitle(opening.titleHtml, titleReveal);
          if (!stillRunning()) return;
        }
        await this.wait(t.openingHoldMs);
        if (!stillRunning()) return;
        if (opening.titleHtml) {
          const titleFade = t.openingTitleFadeMs ?? t.openingExhaleMs;
          await this.hideBookendTitleFade(titleFade);
          if (!stillRunning()) return;
        }
        this.stopBookendAudio();
      }

      await this.hideBookendImage(t.openingExhaleMs);
      if (!stillRunning()) return;

      const afterMs = t.openingBlackAfterMs ?? 0;
      if (afterMs > 0) await this.wait(afterMs);
      if (!stillRunning()) return;

      if (!this._soundtrackStarted && !this.shouldStartSoundtrackDuringOpening(opening)) {
        await this.startSoundtrack();
      }
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

      const fadeMs = t.closingFadeToBlackMs ?? t.closingExhaleMs;

      if (holdUntilSoundtrackEnds) {
        const titleRevealMs = t.closingTitleRevealMs ?? 2500;
        const titleHoldMs = t.closingSilenceHoldMs ?? 2000;
        const titleLeadMs = closing.titleHtml ? titleRevealMs + titleHoldMs : 0;

        while (stillRunning()) {
          const remaining = this.getSoundtrackRemainingMs();
          if (remaining <= 0 || remaining <= titleLeadMs + fadeMs) break;
          await this.wait(Math.min(Math.max(remaining - titleLeadMs - fadeMs, 0), 250));
        }
        if (!stillRunning()) return;

        if (closing.titleHtml) {
          await this.showBookendTitle(closing.titleHtml, titleRevealMs);
          if (!stillRunning()) return;
          await this.wait(titleHoldMs);
          if (!stillRunning()) return;
        }

        while (stillRunning()) {
          const remaining = this.getSoundtrackRemainingMs();
          if (remaining <= 0 || remaining <= fadeMs) break;
          await this.wait(Math.min(remaining - fadeMs, 250));
        }
        if (!stillRunning()) return;

        if (closing.titleHtml) {
          const titleFadeMs = t.closingTitleFadeMs ?? fadeMs;
          await this.hideBookendTitleFade(titleFadeMs);
          if (!stillRunning()) return;
        }

        await this.fadeClosingImageWithSoundtrackEnd(fadeMs);
        if (!stillRunning()) return;

        await this.wait(t.closingBlackAfterMs ?? 0);
        this.stopAllAudio();
        this.finishPresentation();
        this.debugLog("exit playClosingImageBookend (soundtrack-synced fade)");
        return;
      }

      await this.wait(t.closingHoldMs ?? 0);
      if (!stillRunning()) return;

      if (closing.fadeWithSoundtrackEnd && this.soundtrack?.main) {
        await this.fadeClosingImageWithSoundtrack(fadeMs);
        if (!stillRunning()) return;
        await this.wait(t.closingBlackAfterMs ?? 0);
        this.stopAllAudio();
        this.finishPresentation();
        this.debugLog("exit playClosingImageBookend (timed fade with soundtrack)");
        return;
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

    showHiraganaSongLayer() {
      const layer = this.els.hiraganaSongLayer;
      if (!layer) return;
      layer.classList.remove("exhibition-hidden", "is-exhaling");
      layer.setAttribute("aria-hidden", "false");
      this.setClass(this.els.veil, "is-clear", true);
    }

    async playHiraganaSongExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = Math.min(Math.max(0, index), this.scenes.length - 1);
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const chartApi = window.KmlHiraganaSongChart;
      const layer = this.els.hiraganaSongLayer;
      const chartEl = this.els.hiraganaSongChart;
      if (!layer || !chartEl || !chartApi) {
        this.debugLog("hiragana song layer unavailable");
        return;
      }

      const rowIds = Array.isArray(scene.rowIds)
        ? scene.rowIds
        : chartApi.ROWS.map((row) => row.id);
      const rowOffsetsMs = Array.isArray(scene.rowOffsetsMs)
        ? scene.rowOffsetsMs
        : (scene.rows || []).map((row) => row.atMs ?? 0);
      const verses =
        Array.isArray(scene.verses) && scene.verses.length
          ? scene.verses
          : [{ id: "kana_1", mode: "kana", startMs: 0, rows: scene.rows || [] }];
      const fujiAtMs = scene.fujiAtMs ?? 291000;
      const fujiImage = scene.fujiImage || "images/mt_fuji.png";
      const introEndMs =
        scene.introEndMs ??
        this.meta?.introMs ??
        verses[0]?.startMs ??
        20000;
      const revealMs = t.chartRevealMs ?? 2800;
      const fadeOutMs = t.chartFadeOutMs ?? 3500;
      const rowFadeMs = t.rowFadeMs ?? 900;
      const fujiFadeMs = t.fujiFadeMs ?? 4500;
      const fujiExhaleMs = t.fujiExhaleMs ?? fadeOutMs;
      const soundtrackMs = this.meta?.soundtrackDurationMs ?? 329300;
      const fujiKenBurnsMs = Math.max(60000, soundtrackMs);

      const fadeRowOut = async () => {
        chartApi.setRowVisible(chartEl, false);
        await this.wait(rowFadeMs);
      };

      const fadeRowIn = async () => {
        await this.waitForPaintFrame();
        chartApi.setRowVisible(chartEl, true);
        await this.wait(rowFadeMs);
      };

      const showFocusRow = async (rowId) => {
        const hadRow = Boolean(chartEl.dataset.activeRowId);
        if (hadRow) {
          await fadeRowOut();
          if (!stillRunning()) return;
        }
        chartApi.setFocusRow(chartEl, rowId);
        await fadeRowIn();
      };

      const prepareFujiArtwork = async () => {
        const fujiScene = { id: "mt_fuji", image: fujiImage };
        this.populateArtworkLayer(this.activeArtworkKey, fujiScene);
        const artLayer = this.artworkLayers[this.activeArtworkKey];
        this.syncLegacyArtworkRefs();
        if (artLayer?.img) {
          await this.waitForArtworkImage(artLayer.img);
          if (!artLayer.img.naturalWidth) {
            this.audioError("mt_fuji image failed to load", null, {
              src: artLayer.img.currentSrc || artLayer.img.src,
            });
          }
          artLayer.img.classList.remove("gallery-guardian");
          artLayer.img.classList.add("ken-burns");
        }
        return artLayer;
      };

      const showFuji = (artLayer, fadeMs) => {
        document.documentElement.style.setProperty("--ex-fade", `${fadeMs}ms`);
        if (!artLayer?.wrap) return;
        this.setClass(artLayer.wrap, "is-exhaling", false);
        this.setClass(artLayer.wrap, "is-visible", true);
      };

      const hidePaperLayer = async (fadeMs) => {
        document.documentElement.style.setProperty("--hiragana-song-fade", `${fadeMs}ms`);
        layer.classList.add("is-exhaling");
        layer.classList.remove("is-visible", "is-drifting");
        await this.wait(fadeMs);
        this.resetHiraganaSongLayer();
      };

      this.resetLayers();
      chartApi.renderFocus(chartEl, "kana");
      // Prepare the song layer (hidden) — Fuji intro plays first without paper.
      layer.classList.remove("exhibition-hidden");
      layer.setAttribute("aria-hidden", "false");
      this.setClass(this.els.veil, "is-clear", true);

      document.documentElement.style.setProperty("--hiragana-song-fade", `${revealMs}ms`);
      document.documentElement.style.setProperty("--hiragana-song-row-fade", `${rowFadeMs}ms`);
      document.documentElement.style.setProperty("--ken-burns-duration", `${fujiKenBurnsMs}ms`);

      await this.waitInitialExhibitionBlack(stillRunning, 0);
      if (!stillRunning()) return;

      this.maybeStartSoundtrackForScene(0);
      if (!this._soundtrackStarted) {
        await this.startSoundtrack();
      }
      if (!stillRunning()) return;

      const artLayer = await prepareFujiArtwork();
      if (!stillRunning()) return;

      // ── Intro: Mt. Fuji alone ──
      showFuji(artLayer, fujiFadeMs);
      await this.wait(fujiFadeMs);
      if (!stillRunning()) return;

      await this.waitUntilSoundtrackMs(introEndMs, stillRunning);
      if (!stillRunning()) return;

      // ── Verses: paper/rows fade in over Fuji ──
      document.documentElement.style.setProperty("--hiragana-song-fade", `${revealMs}ms`);
      layer.classList.remove("is-exhaling");
      layer.classList.add("is-visible", "is-drifting");
      await this.wait(revealMs);
      if (!stillRunning()) return;

      for (const verse of verses) {
        if (!stillRunning()) return;
        const startMs = verse.startMs ?? 0;
        await this.waitUntilSoundtrackMs(startMs, stillRunning);
        if (!stillRunning()) return;

        const nextMode = verse.mode === "romaji" ? "romaji" : "kana";
        const modeChanged = chartApi.getDisplayMode(chartEl) !== nextMode;
        if (modeChanged || chartEl.dataset.activeRowId) {
          await fadeRowOut();
          if (!stillRunning()) return;
          chartApi.clearFocus(chartEl);
          chartApi.renderFocus(chartEl, nextMode);
        }
        layer.classList.toggle("is-romaji-mode", nextMode === "romaji");

        const verseRows = Array.isArray(verse.rows)
          ? verse.rows
          : rowIds.map((id, i) => ({
              id,
              atMs: startMs + (rowOffsetsMs[i] ?? 0),
            }));

        for (const row of verseRows) {
          if (!stillRunning()) return;
          const atMs = Math.max(0, (row.atMs ?? 0) - Math.round(rowFadeMs * 0.35));
          await this.waitUntilSoundtrackMs(atMs, stillRunning);
          if (!stillRunning()) return;
          await showFocusRow(row.id);
          if (!stillRunning()) return;
        }
      }

      // ── Closing: paper fades away; Fuji remains through bed end ──
      await this.waitUntilSoundtrackMs(fujiAtMs, stillRunning);
      if (!stillRunning()) return;

      showFuji(artLayer, fujiFadeMs);
      await hidePaperLayer(fujiFadeMs);
      if (!stillRunning()) return;

      await this.waitForSoundtrackEnd();
      if (!stillRunning()) return;

      document.documentElement.style.setProperty("--ex-exhale", `${fujiExhaleMs}ms`);
      if (artLayer?.wrap) {
        this.setClass(artLayer.wrap, "is-exhaling", true);
      }
      await this.wait(fujiExhaleMs);
      if (!stillRunning()) return;
      if (artLayer?.wrap) {
        this.setClass(artLayer.wrap, "is-visible", false);
        this.setClass(artLayer.wrap, "is-exhaling", false);
      }
      if (artLayer?.img) {
        artLayer.img.classList.remove("ken-burns");
      }

      if (this.singleExhibit) {
        document.dispatchEvent(
          new CustomEvent("kml-exhibition-exhibit-end", {
            detail: { index: this.sceneIndex, sceneId: scene.id },
          })
        );
        return;
      }

      if (this.bookends?.closing) {
        await this.playClosingBookend();
        return;
      }

      this.finishPresentation();
    }

    async playExhibit(index) {
      if (this.destroyed || !this.scenes.length) return;

      if (this.isGalleryProfile) {
        return this.playGalleryExhibit(index);
      }
      if (this.isImageVerseProfile) {
        return this.playImageVerseExhibit(index);
      }
      if (this.isVerseReadingProfile) {
        return this.playVerseReadingExhibit(index);
      }
      if (this.isAssistedReadingProfile) {
        return this.playAssistedReadingExhibit(index);
      }
      if (this.isVocabularyExhibitionProfile) {
        return this.playVocabularyExhibit(index);
      }
      if (this.isCompoundsExhibitionProfile) {
        return this.playCompoundsExhibit(index);
      }
      if (this.isJapaneseVocabularyProfile) {
        return this.playJapaneseVocabularyExhibit(index);
      }
      if (this.isAnchorCompoundsExhibitionProfile) {
        return this.playAnchorCompoundsExhibit(index);
      }
      if (this.isGrade1KanjiSoundtrackProfile) {
        return this.playGrade1KanjiSoundtrackExhibit(index);
      }
      if (this.isKanjiSoundtrackProfile) {
        return this.playKanjiSoundtrackExhibit(index);
      }
      if (this.isStrokeOrderProfile) {
        return this.playStrokeOrderExhibit(index);
      }
      if (this.isPartyKanjiProfile) {
        return this.playPartyKanjiExhibit(index);
      }
      if (this.isHiraganaSongProfile) {
        return this.playHiraganaSongExhibit(index);
      }

      const count = this.scenes.length;
      if (index >= count && !this.display.loop) return;

      this.clearRun();
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;

      this.sceneIndex = ((index % count) + count) % count;
      const scene = this.scenes[this.sceneIndex];
      const t = this.timing;
      const seamlessHandoff = this._seamlessHandoffTo === index;
      this._seamlessHandoffTo = -1;

      if (seamlessHandoff) {
        this.resetImageVerseForeground();
        this.populateVerseContent(scene);
      } else {
        this.resetLayers();
        this.populateScene(scene);
        await this.applySceneCamera(scene);
      }
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
      } else if (seamlessHandoff) {
        // Artwork already crossfaded in; hold on image before kanji reveal.
        this.setClass(this.els.veil, "is-corridor", false);
        this.setClass(this.els.veil, "is-clear", true);
        await this.wait(t.artworkAloneMs);
        if (!stillRunning()) return;
      } else {
        // ── 1. Artwork arrival from black ──
        this.setClass(this.els.veil, "is-corridor", false);
        this.setClass(this.els.veil, "is-clear", true);
        await this.wait(80);
        if (!stillRunning()) return;
        this.setClass(this.els.artwork, "is-visible", true);
        await this.wait(t.artworkArrivalMs + t.artworkAloneMs);
        if (!stillRunning()) return;
      }

      if (!jumpToReflection) {
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

      // ── 4. Return to essence — kanji alone (centered before fade-in; avoids title→center jump)
      this.setClass(this.els.verseJp, "is-visible", false);
      this.setClass(this.els.verseEn, "is-visible", false);
      this.setKanjiCentered(true);
      this.setClass(this.els.kanji, "is-visible", true);
      await this.wait(t.essenceKanjiRevealMs);
      if (!stillRunning()) return;
      if (t.essenceHoldMs > 0) {
        await this.wait(t.essenceHoldMs);
        if (!stillRunning()) return;
      }

      // ── 5. Handoff — gallery bridge or final conclusion ──
      this.setKanjiCentered(true);

      if (this.singleExhibit) {
        this.setClass(this.els.artwork, "is-exhaling", true);
        await this.wait(t.imageExhaleFadeMs + (t.kanjiAloneHoldMs ?? 0));
        if (!stillRunning()) return;
        this.setClass(this.els.kanji, "is-exhaling", true);
        await this.wait(t.kanjiExhaleFadeMs);
        if (!stillRunning()) return;
        this.setClass(this.els.kanji, "is-visible", false);
        this.setClass(this.els.kanji, "is-exhaling", false);
        this.setKanjiCentered(false);
        document.dispatchEvent(
          new CustomEvent("kml-exhibition-exhibit-end", {
            detail: { index: this.sceneIndex, sceneId: scene.id },
          })
        );
        return;
      }

      const next = this.sceneIndex + 1;

      if (next >= count) {
        await this.finalExhibitConclusion(stillRunning, t);
        if (!stillRunning()) return;
        this.setKanjiCentered(false);
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

      if (this.seamlessExhibitHandoff) {
        await this.galleryBridgeHandoff(this.scenes[next], stillRunning, t);
        if (!stillRunning()) return;
        this.setKanjiCentered(false);
        this._seamlessHandoffTo = next;
        await this.playExhibit(next);
        return;
      }

      // Black corridor between exhibits (legacy)
      this.setClass(this.els.artwork, "is-exhaling", true);
      await this.wait(t.imageExhaleFadeMs + (t.kanjiAloneHoldMs ?? 0));
      if (!stillRunning()) return;
      this.setClass(this.els.kanji, "is-exhaling", true);
      await this.wait(t.kanjiExhaleFadeMs);
      if (!stillRunning()) return;
      this.setClass(this.els.kanji, "is-visible", false);
      this.setClass(this.els.kanji, "is-exhaling", false);
      this.setKanjiCentered(false);
      this.setClass(this.els.veil, "is-corridor", true);
      this.setClass(this.els.veil, "is-clear", false);
      this.setClass(this.els.artwork, "is-visible", false);
      this.setClass(this.els.artwork, "is-exhaling", false);
      await this.wait(t.exhibitBlackHoldMs ?? t.blackHoldMs);
      if (!stillRunning()) return;

      await this.playExhibit(next);
    }

    async waitRecordingLead(stillRunning) {
      const leadMs = this.timing.recordingLeadMs ?? 0;
      if (leadMs <= 0) return;

      this.root.classList.add("is-initial-black");
      this.setClass(this.els.veil, "is-corridor", false);
      this.setClass(this.els.veil, "is-clear", false);
      await this.wait(leadMs);
      this.root.classList.remove("is-initial-black");
      if (!stillRunning()) return;
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
      if (this.hasExhibitionAudio()) {
        await this.ensureAudioUnlocked();
      }
      if (this.destroyed) return;
      const runId = this.runId;
      const stillRunning = () => !this.destroyed && runId === this.runId;
      await this.waitRecordingLead(stillRunning);
      if (this.destroyed) return;
      if (!this.skipBookends && this.bookends?.opening) {
        await this.playOpeningBookend();
        if (this.destroyed) return;
        this.debugLog("opening bookend complete, starting playExhibit(0)");
      } else if (!this.skipBookends) {
        this.setClass(this.els.veil, "is-corridor", false);
        this.setClass(this.els.veil, "is-clear", true);
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
    const candidates = window.KmlCollectionPaths
      ? window.KmlCollectionPaths.collectionUrls(name)
      : [`./collections/${name}.json`];

    let lastStatus = 0;
    for (const url of candidates) {
      const res = await fetch(url);
      if (res.ok) return res.json();
      lastStatus = res.status;
    }
    throw new Error(`Could not load collection "${name}" (${lastStatus}).`);
  }

  async function ensureExhibitionFontsReady(display) {
    if (!document.fonts?.load) return;

    const family = display?.family || "";
    const profile = display?.exhibitProfile || "";
    const typo = display?.typography || "";
    const needsHandwritten =
      family === "kanjiSoundtrack" ||
      profile === "kanjiSoundtrack" ||
      /KanjiSoundtrack$/.test(family) ||
      profile === "strokeOrder" ||
      profile === "japaneseVocabulary" ||
      ExhibitionPlayer.isElementaryGradeStrokeOrderProfile(profile);
    const needsSerifVerses =
      typo === "mobile-refine" &&
      (profile === "assistedReading" ||
        profile === "verseReading" ||
        profile === "vocabularyExhibition" ||
        profile === "compoundsExhibition" ||
        profile === "japaneseVocabulary" ||
        profile === "anchorCompoundsExhibition" ||
        profile === "imageVerse" ||
        profile === "gallery");
    const needsHiraganaSong =
      profile === "hiraganaSong" || family === "hiraganaSong";

    const loads = [];

    if (needsHiraganaSong) {
      loads.push(document.fonts.load("500 48px \"Noto Serif JP\""));
      loads.push(document.fonts.load("500 36px \"Cormorant Garamond\""));
    }
    if (needsHandwritten) {
      const strokeOrderProfile =
        profile === "strokeOrder" ||
        ExhibitionPlayer.isElementaryGradeStrokeOrderProfile(profile);
      const yujiSize = strokeOrderProfile ? "320px" : "48px";
      loads.push(
        document.fonts.load(`400 ${yujiSize} "Yuji Syuku"`),
        document.fonts.load('400 48px "Hachi Maru Pop"')
      );
      if (strokeOrderProfile) {
        loads.push(document.fonts.load(`400 ${yujiSize} "Noto Serif JP"`));
      }
    }

    if (needsSerifVerses) {
      loads.push(
        document.fonts.load('600 5rem "Noto Serif JP"'),
        document.fonts.load('500 3rem "Cormorant Garamond"'),
        document.fonts.load('italic 500 3rem "Cormorant Garamond"')
      );
    }

    if (!loads.length) return;
    await Promise.all(loads.map((p) => p.catch(() => {})));
    if (document.fonts.ready) await document.fonts.ready;
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
      await ensureExhibitionFontsReady(collection.display);
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
