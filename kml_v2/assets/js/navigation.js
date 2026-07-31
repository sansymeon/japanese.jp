/**
 * KML V2 — site navigation helpers (mobile toggle, current page mark)
 */

(function () {
  function bindToggle() {
    const toggle = document.getElementById("navToggle");
    const nav = document.getElementById("siteNav");
    if (!toggle || !nav) return;

    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  function markCurrent() {
    const here = location.pathname.replace(/\/$/, "") || "/";
    document.querySelectorAll(".site-nav a[href]").forEach((a) => {
      try {
        const path = new URL(a.href, location.href).pathname.replace(/\/$/, "");
        if (path && (here === path || here.endsWith(path))) {
          a.setAttribute("aria-current", "page");
        }
      } catch {
        /* ignore bad hrefs */
      }
    });
  }

  function init() {
    bindToggle();
    markCurrent();
  }

  document.addEventListener("kml:includes-ready", init);
  if (document.readyState !== "loading") {
    // Fallback if includes finished before this script loaded
    queueMicrotask(() => {
      if (document.getElementById("siteNav")) init();
    });
  }
})();
