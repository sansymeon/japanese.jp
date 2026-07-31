/**
 * KML V2 — small UI helpers shared across pages
 */

(function (global) {
  const KML = (global.KML = global.KML || {});

  KML.qs = (sel, root = document) => root.querySelector(sel);
  KML.qsa = (sel, root = document) => [...root.querySelectorAll(sel)];

  KML.onReady = (fn) => {
    const run = () => fn();
    document.addEventListener("kml:includes-ready", run, { once: true });
    if (document.readyState !== "loading") {
      queueMicrotask(run);
    } else {
      document.addEventListener("DOMContentLoaded", run, { once: true });
    }
  };
})(window);
