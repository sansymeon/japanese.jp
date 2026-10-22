/**
 * Preserve ?lang=en across the 漢検 level directories.
 * Japanese entry (no query) is unchanged. Lesson HTML is left in Japanese.
 */
(function () {
  "use strict";

  if (new URLSearchParams(window.location.search).get("lang") !== "en") return;
  document.documentElement.setAttribute("data-kanken-lang", "en");

  function isPathway(pathname) {
    var path = pathname.replace(/\/index\.html$/, "");
    if (path.charAt(path.length - 1) !== "/") path += "/";
    if (path === "/kanken/") return true;
    if (/^\/kanken\/level-[a-z0-9]+\/$/.test(path)) return true;
    if (path === "/school-grade/grade-1/") return true;
    return false;
  }

  document.querySelectorAll("a[href]").forEach(function (anchor) {
    var raw = anchor.getAttribute("href");
    if (!raw || raw.charAt(0) === "#" || /^(mailto:|javascript:)/i.test(raw)) return;
    var url;
    try {
      url = new URL(raw, window.location.href);
    } catch (err) {
      return;
    }
    if (url.origin !== window.location.origin) return;
    if (!isPathway(url.pathname)) return;
    if (url.searchParams.get("lang") === "en") return;
    url.searchParams.set("lang", "en");
    anchor.setAttribute("href", url.pathname + url.search + url.hash);
  });
})();
