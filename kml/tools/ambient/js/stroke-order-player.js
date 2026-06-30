/**
 * Stroke Order Exhibition — KanjiVG path animation for the calligraphy studio profile.
 */
(function (global) {
  function prepareStrokes(svg, options = {}) {
    if (!svg) return null;
    const strokes = svg.querySelectorAll("path");
    if (!strokes.length) return null;

    const drawColor = options.drawColor || "rgba(232, 224, 212, 0.92)";
    strokes.forEach((stroke) => {
      const length = stroke.getTotalLength();
      stroke.style.fill = "none";
      stroke.style.stroke = drawColor;
      if (options.strokeWidth != null) {
        stroke.style.strokeWidth = String(options.strokeWidth);
      } else {
        stroke.style.removeProperty("stroke-width");
      }
      stroke.style.strokeLinecap = "butt";
      stroke.style.strokeLinejoin = "miter";
      stroke.style.removeProperty("vector-effect");
      stroke.style.strokeDasharray = String(length);
      stroke.style.strokeDashoffset = String(length);
      stroke.style.transition = "none";
      stroke.style.filter = "none";
    });

    svg.getBoundingClientRect();
    return strokes;
  }

  function animateStrokes(strokes, options = {}) {
    const drawMs = options.drawMs ?? 900;
    const gapMs = options.gapMs ?? 1100;
    const finalColor = options.finalColor || "rgba(245, 240, 232, 0.96)";
    const onsets = options.strokeOnsetsMs;

    if (!strokes || !strokes.length) {
      return Promise.resolve(0);
    }

    if (Array.isArray(onsets) && onsets.length === strokes.length) {
      return animateStrokesRhythmic(strokes, {
        strokeOnsetsMs: onsets,
        drawMs,
        finalColor,
        easing: options.easing || "ease-out",
      });
    }

    strokes.forEach((stroke) => {
      stroke.style.transition = `stroke-dashoffset ${drawMs}ms ease-out, stroke 320ms ease`;
    });

    return new Promise((resolve) => {
      strokes.forEach((stroke, index) => {
        window.setTimeout(() => {
          stroke.style.strokeDashoffset = "0";
          window.setTimeout(() => {
            stroke.style.stroke = finalColor;
          }, Math.max(0, drawMs - 140));
        }, index * gapMs);
      });

      const totalMs = (strokes.length - 1) * gapMs + drawMs;
      window.setTimeout(() => resolve(totalMs), totalMs);
    });
  }

  function animateStrokesRhythmic(strokes, options = {}) {
    const onsets = options.strokeOnsetsMs || [];
    const drawMs = options.drawMs ?? 900;
    const finalColor = options.finalColor || "rgba(245, 240, 232, 0.96)";
    const easing = options.easing || "cubic-bezier(0.33, 0.12, 0.18, 1)";

    strokes.forEach((stroke, index) => {
      const localDraw = Array.isArray(drawMs) ? drawMs[index] ?? drawMs[0] : drawMs;
      stroke.style.transition = `stroke-dashoffset ${localDraw}ms ${easing}, stroke 280ms ease`;
    });

    return new Promise((resolve) => {
      let totalMs = 0;
      strokes.forEach((stroke, index) => {
        const onset = onsets[index] ?? index * 900;
        const localDraw = Array.isArray(drawMs) ? drawMs[index] ?? drawMs[0] : drawMs;
        totalMs = Math.max(totalMs, onset + localDraw);
        window.setTimeout(() => {
          stroke.style.strokeDashoffset = "0";
          window.setTimeout(() => {
            stroke.style.stroke = finalColor;
          }, Math.max(0, localDraw - 120));
        }, onset);
      });
      window.setTimeout(() => resolve(totalMs), totalMs);
    });
  }

  function strokeAnimationDurationMs(strokeCount, options = {}) {
    if (!strokeCount) return 0;
    const onsets = options.strokeOnsetsMs;
    const drawMs = options.drawMs ?? 900;
    if (Array.isArray(onsets) && onsets.length) {
      const last = onsets[onsets.length - 1];
      const draw = Array.isArray(drawMs) ? drawMs[drawMs.length - 1] ?? drawMs[0] : drawMs;
      return last + draw;
    }
    const gapMs = options.gapMs ?? 1100;
    return (strokeCount - 1) * gapMs + drawMs;
  }

  global.KmlStrokeOrderPlayer = {
    prepareStrokes,
    animateStrokes,
    animateStrokesRhythmic,
    strokeAnimationDurationMs,
  };
})(window);
