/**
 * Gallery Guardian – exhibition camera planner.
 *
 * Shared philosophy (both families): widest 100% cover, centered start,
 * composition before detail, gentle push-in. Trust the artwork.
 */
(function () {
  "use strict";

  const IMMERSIVE_SCALE_MIN = 1.0;
  const COVER_BOOST_MAX = 1.28;

  const EASE = {
    comprehension:
      "cubic-bezier(0.15, 0.0, 0.25, 1.0)",
    reflection:
      "cubic-bezier(0.1, 0.0, 0.2, 1.0)",
  };

  /** @type {Record<string, { fromMul: number, toDelta: number, toJitter: number, panMax: number }>} */
  const MOTION_PROFILES = {
    comprehension: {
      fromMul: 1.0,
      toDelta: 0.085,
      toJitter: 0.018,
      panMax: 1.35,
    },
    reflection: {
      fromMul: 1.0,
      toDelta: 0.145,
      toJitter: 0.025,
      panMax: 0.85,
    },
  };

  // Legacy shot table retained for diagnostics and sample renders.
  const SHOTS = {
    contemplate: { s0: 1.02, s1: 1.08, x0: 0, y0: 0, x1: 0.6, y1: 0.4, weight: 30 },
    drift: { s0: 1.04, s1: 1.11, x0: -3.2, y0: 0.2, x1: 3.2, y1: -0.4, weight: 25 },
    reveal: { s0: 1.05, s1: 1.16, x0: 2.2, y0: -2.5, x1: -3.8, y1: 3.2, weight: 15 },
    withdraw: { s0: 1.14, s1: 1.06, x0: -2.5, y0: -1.2, x1: 3.0, y1: 1.8, weight: 15 },
    follow: { s0: 1.05, s1: 1.12, x0: 4.2, y0: 0.4, x1: -5.0, y1: -0.5, weight: 8 },
    establish: { s0: 1.08, s1: 1.02, x0: 0.5, y0: 0.5, x1: -2.0, y1: -1.2, weight: 5 },
    approach: { s0: 1.06, s1: 1.18, x0: 1.5, y0: 1.2, x1: -2.8, y1: -2.0, weight: 2 },
    reflect: { s0: 1.04, s1: 1.12, x0: -1.2, y0: 2.8, x1: 1.4, y1: -3.5, weight: 10 },
  };

  function hashSeed(str) {
    let h = 0;
    const s = String(str || "");
    for (let i = 0; i < s.length; i += 1) {
      h = ((h << 5) - h + s.charCodeAt(i)) | 0;
    }
    return Math.abs(h);
  }

  function seededUnit(seed) {
    const x = Math.sin(seed * 12.9898 + seed * 0.1234) * 43758.5453;
    return x - Math.floor(x);
  }

  function minimumCoverScale() {
    return IMMERSIVE_SCALE_MIN;
  }

  function immersiveScale(value, coverBoost) {
    return Math.max(IMMERSIVE_SCALE_MIN, value * coverBoost);
  }

  function resolveProfile(name) {
    if (name === "reflection") return MOTION_PROFILES.reflection;
    return MOTION_PROFILES.comprehension;
  }

  /**
   * Detect baked-in black margins in source art; return a cover boost >= 1.
   */
  function measureCoverBoost(img) {
    if (!img?.naturalWidth || !img?.naturalHeight) return 1;

    const sampleW = 48;
    const sampleH = 32;
    const canvas = document.createElement("canvas");
    canvas.width = sampleW;
    canvas.height = sampleH;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) return 1;

    let data;
    try {
      ctx.drawImage(img, 0, 0, sampleW, sampleH);
      data = ctx.getImageData(0, 0, sampleW, sampleH).data;
    } catch (_) {
      return 1;
    }

    const lumAt = (x, y) => {
      const i = (y * sampleW + x) * 4;
      return 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
    };

    const stripAvg = (x0, x1, y0, y1) => {
      let sum = 0;
      let count = 0;
      for (let y = y0; y < y1; y += 1) {
        for (let x = x0; x < x1; x += 1) {
          sum += lumAt(x, y);
          count += 1;
        }
      }
      return count ? sum / count : 255;
    };

    const marginX = Math.max(1, Math.round(sampleW * 0.06));
    const marginY = Math.max(1, Math.round(sampleH * 0.06));
    const center = stripAvg(
      Math.round(sampleW * 0.3),
      Math.round(sampleW * 0.7),
      Math.round(sampleH * 0.3),
      Math.round(sampleH * 0.7)
    );
    const left = stripAvg(0, marginX, 0, sampleH);
    const right = stripAvg(sampleW - marginX, sampleW, 0, sampleH);
    const top = stripAvg(0, sampleW, 0, marginY);
    const bottom = stripAvg(0, sampleW, sampleH - marginY, sampleH);

    const sideGap = center - Math.min(left, right);
    const vertGap = center - Math.min(top, bottom);
    let boost = 1;

    if (sideGap > 28) {
      boost = Math.max(boost, 1 + Math.min(0.16, (sideGap - 28) * 0.0018));
    }
    if (vertGap > 28) {
      boost = Math.max(boost, 1 + Math.min(0.14, (vertGap - 28) * 0.0016));
    }

    return Math.min(COVER_BOOST_MAX, Math.round(boost * 1000) / 1000);
  }

  function plan(scene, options = {}) {
    const {
      sceneIndex = 0,
      durationMs = 125000,
      coverBoost = 1,
      motionProfile = "comprehension",
    } = options;

    const profile = resolveProfile(motionProfile);
    const seed = hashSeed(`${scene.id}:${sceneIndex}:${motionProfile}`);
    const jitter = (spread) => (seededUnit(seed + spread) - 0.5);

    // Widest composition at 100% cover: object-fit:cover baseline (scale 1.0), centered.
    const scaleFrom = minimumCoverScale();
    const pushDelta = profile.toDelta + jitter(10) * profile.toJitter;
    const scaleTo = scaleFrom + Math.max(profile.toDelta * 0.55, pushDelta);

    const panEnd = profile.panMax * 0.25;
    const xFrom = 0;
    const yFrom = 0;
    const xTo = jitter(14) * panEnd;
    const yTo = jitter(15) * panEnd;

    return {
      shot: motionProfile,
      motionProfile,
      durationMs,
      coverBoost,
      scaleFrom,
      scaleTo,
      xFrom,
      yFrom,
      xTo,
      yTo,
      ease: EASE[motionProfile] || EASE.comprehension,
    };
  }

  function applyToImage(img, cameraPlan) {
    if (!img || !cameraPlan) return;

    img.classList.remove("ken-burns", "gallery-guardian");
    void img.offsetWidth;

    img.style.setProperty("--image-scale", "1");
    img.style.setProperty("--gg-scale-from", String(cameraPlan.scaleFrom));
    img.style.setProperty("--gg-scale-to", String(cameraPlan.scaleTo));
    img.style.setProperty("--gg-x-from", `${cameraPlan.xFrom}%`);
    img.style.setProperty("--gg-y-from", `${cameraPlan.yFrom}%`);
    img.style.setProperty("--gg-x-to", `${cameraPlan.xTo}%`);
    img.style.setProperty("--gg-y-to", `${cameraPlan.yTo}%`);
    img.style.setProperty("--gallery-guardian-duration", `${cameraPlan.durationMs}ms`);
    img.style.setProperty(
      "--gallery-guardian-ease",
      cameraPlan.ease || EASE.comprehension
    );

    img.classList.add("gallery-guardian");
    img.dataset.galleryShot = cameraPlan.shot;
  }

  window.GalleryGuardian = {
    plan,
    applyToImage,
    measureCoverBoost,
    minimumCoverScale,
    SHOTS,
    MOTION_PROFILES,
    EASE,
    IMMERSIVE_SCALE_MIN,
  };
})();
