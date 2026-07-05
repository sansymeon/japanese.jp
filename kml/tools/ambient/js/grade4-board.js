/**
 * Grade 4 display board — gojūon frames and camera states.
 */
(function () {
  "use strict";

  const HIRAGANA =
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん";

  function gridIndex(kana) {
    const i = HIRAGANA.indexOf(kana);
    return i >= 0 ? i : 49;
  }

  function approachTransform(kana) {
    const idx = gridIndex(kana);
    const col = idx % 10;
    const row = Math.floor(idx / 10);
    return {
      scale: 2.35,
      tx: 36.5 - col * 8.2,
      ty: 14 + row * 13.5,
    };
  }

  function buildFrame(kana, count) {
    const frame = document.createElement("div");
    frame.className = "g4-frame";
    frame.dataset.kana = kana;
    frame.style.setProperty("--g4-accent", `var(--kml-g4-${kana}, #6b6358)`);
    const label = document.createElement("span");
    label.className = "g4-frame-label";
    label.textContent = kana;
    frame.appendChild(label);
    if (count > 0) {
      const sub = document.createElement("span");
      sub.className = "g4-frame-count";
      sub.textContent = `${count}`;
      frame.appendChild(sub);
    }
    return frame;
  }

  const KmlGrade4Board = {
    HIRAGANA,

    renderBoard(container, { sectionCounts = {}, highlight = "", visited = [] } = {}) {
      if (!container) return;
      container.innerHTML = "";
      const cells = HIRAGANA.split("");
      while (cells.length < 50) cells.push("");
      cells.slice(0, 50).forEach((kana) => {
        if (!kana) {
          const pad = document.createElement("div");
          pad.className = "g4-frame";
          pad.style.visibility = "hidden";
          container.appendChild(pad);
          return;
        }
        const count = sectionCounts[kana] || 0;
        const frame = buildFrame(kana, count);
        if (kana === highlight) frame.classList.add("is-active");
        if (visited.includes(kana)) frame.classList.add("is-visited");
        container.appendChild(frame);
      });
    },

    setCamera(camera, mode, kana) {
      if (!camera) return;
      camera.className = "g4-board-camera";
      if (mode === "overview") {
        camera.classList.add("is-overview");
        return;
      }
      if (mode === "pan") {
        camera.classList.add("is-panning");
        return;
      }
      if (mode === "approach" && kana) {
        const { scale, tx, ty } = approachTransform(kana);
        camera.classList.add("is-approach");
        camera.style.setProperty("--g4-approach-scale", String(scale));
        camera.style.setProperty("--g4-approach-tx", `${tx}%`);
        camera.style.setProperty("--g4-approach-ty", `${ty}%`);
      }
    },

    markVisited(container, kana) {
      const frame = container?.querySelector(`[data-kana="${kana}"]`);
      frame?.classList.remove("is-active");
      frame?.classList.add("is-visited");
    },

    setHighlight(container, kana) {
      container?.querySelectorAll(".g4-frame").forEach((f) => {
        f.classList.toggle("is-active", f.dataset.kana === kana);
      });
    },
  };

  window.KmlGrade4Board = KmlGrade4Board;
})();
