/**
 * Gallery Guardian – lightweight exhibition camera planner (Heart collections).
 * Shot grammar + Director sequencing; no CV/ML.
 */
(function () {
  "use strict";

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

  const IMMERSIVE_SCALE_MIN = 1.0;
  const COVER_BOOST_MAX = 1.28;

  const VERSE_HINTS = [
    { re: /mist|fog|dissolv|hidden|beyond|haze|霞|霧/i, boost: ["reveal", "drift", "reflect"] },
    { re: /path|foot|continu|flow|river|journey|bridge|道|流|歩|旅/i, boost: ["follow", "establish"] },
    { re: /stood|still|quiet|silence|unmoving|静|黙/i, boost: ["contemplate", "withdraw"] },
    { re: /moon|water|reflect|surface|light|月|水|光|映/i, boost: ["reflect", "reveal"] },
    { re: /mountain|valley|land|山|谷|野/i, boost: ["establish", "withdraw"] },
  ];

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

  function verseText(scene) {
    const jp = scene.verse?.jp || "";
    const en = scene.verse?.en || "";
    const html = scene.verse?.jpHtml || "";
    return `${jp} ${en} ${html}`.replace(/<[^>]+>/g, " ");
  }

  function shotWeights(scene, aspectRatio, framingScale) {
    const weights = {};
    Object.keys(SHOTS).forEach((key) => {
      weights[key] = SHOTS[key].weight;
    });

    if (aspectRatio < 0.88) {
      weights.reflect += 8;
      weights.drift += 6;
      weights.establish -= 4;
    } else if (aspectRatio > 1.12) {
      weights.establish += 10;
      weights.follow += 8;
      weights.reflect -= 4;
    }

    if (framingScale < 0.92) {
      weights.approach = 0;
      weights.reveal = Math.max(4, weights.reveal - 4);
      weights.contemplate += 6;
      weights.drift += 4;
    }

    const text = verseText(scene);
    VERSE_HINTS.forEach((hint) => {
      if (!hint.re.test(text)) return;
      hint.boost.forEach((name) => {
        if (weights[name] != null) weights[name] += 12;
      });
    });

    if (scene.id === "L40_love" || scene.kanji === "愛") {
      weights.approach += 6;
      weights.reveal += 4;
    }
    if (scene.id === "L32_heart" || scene.kanji === "心") {
      weights.contemplate += 14;
      weights.withdraw += 6;
      weights.approach = 0;
    }

    return weights;
  }

  function pickShot(scene, sceneIndex, history, aspectRatio, framingScale) {
    const seed = hashSeed(`${scene.id}:${sceneIndex}`);
    const weights = shotWeights(scene, aspectRatio, framingScale);
    const last = history[history.length - 1];
    const prev = history[history.length - 2];

    const entries = Object.entries(weights).filter(([, w]) => w > 0);
    const filtered = entries.filter(([name]) => {
      if (name === last) return false;
      if (name === prev && entries.length > 3) return false;
      return true;
    });
    const pool = filtered.length ? filtered : entries;

    let total = 0;
    pool.forEach(([, w]) => {
      total += w;
    });

    let pick = seededUnit(seed) * total;
    let chosen = pool[0][0];
    for (const [name, w] of pool) {
      pick -= w;
      if (pick <= 0) {
        chosen = name;
        break;
      }
    }

    return chosen;
  }

  function directionFlip(seed, history) {
    const last = history[history.length - 1];
    if (last && last.flipX) return { flipX: !last.flipX, flipY: last.flipY };
    return {
      flipX: seededUnit(seed + 1) > 0.5,
      flipY: seededUnit(seed + 2) > 0.35,
    };
  }

  function immersiveScale(value, coverBoost) {
    return Math.max(IMMERSIVE_SCALE_MIN, value * coverBoost);
  }

  /**
   * Detect baked-in black margins in source art; return a cover boost >= 1.
   * Lightweight edge sampling only — no ML.
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
      history = [],
      aspectRatio = 0.75,
      framingScale = 1,
      durationMs = 125000,
      coverBoost = 1,
    } = options;

    const seed = hashSeed(`${scene.id}:${sceneIndex}`);
    const shotName = pickShot(scene, sceneIndex, history, aspectRatio, framingScale);
    const shot = SHOTS[shotName];
    const dir = directionFlip(seed, history);

    const mul = (v, flip) => (flip ? -v : v);
    const jitter = (base, spread) => base + (seededUnit(seed + spread) - 0.5) * 0.8;

    const plan = {
      shot: shotName,
      durationMs,
      coverBoost,
      scaleFrom: immersiveScale(jitter(shot.s0, 10), coverBoost),
      scaleTo: immersiveScale(jitter(shot.s1, 11), coverBoost),
      xFrom: mul(jitter(shot.x0, 12), dir.flipX),
      yFrom: mul(jitter(shot.y0, 13), dir.flipY),
      xTo: mul(jitter(shot.x1, 14), dir.flipX),
      yTo: mul(jitter(shot.y1, 15), dir.flipY),
      flipX: dir.flipX,
      flipY: dir.flipY,
    };

    return plan;
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

    img.classList.add("gallery-guardian");
    img.dataset.galleryShot = cameraPlan.shot;
  }

  window.GalleryGuardian = {
    plan,
    applyToImage,
    measureCoverBoost,
    SHOTS,
    IMMERSIVE_SCALE_MIN,
  };
})();
