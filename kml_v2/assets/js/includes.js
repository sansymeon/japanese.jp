/**
 * KML V2 — HTML partial includes (supports nested includes)
 *
 * Usage:
 *   <html data-site-root="..">
 *   <div data-include="components/header/header.html"></div>
 *
 * Placeholders inside partials:
 *   {{root}}     → value of data-site-root (relative path to site root)
 *   {{path:...}} → {{root}}/... convenience
 *
 * Requires HTTP (not file://). Serve kml_v2/ with any static server.
 */

(function () {
  const root =
    document.documentElement.getAttribute("data-site-root") || ".";

  function resolveUrl(path) {
    const clean = String(path).replace(/^\//, "");
    return `${root.replace(/\/$/, "")}/${clean}`;
  }

  function rewrite(html) {
    return html
      .replaceAll("{{root}}", root.replace(/\/$/, "") || ".")
      .replace(/\{\{path:([^}]+)\}\}/g, (_, p) => resolveUrl(p.trim()));
  }

  async function inject(el) {
    const src = el.getAttribute("data-include");
    if (!src) return;

    const url = resolveUrl(src);
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) {
      throw new Error(`Include failed: ${url} (${res.status})`);
    }

    const html = rewrite(await res.text());
    const wrap = document.createElement("div");
    wrap.innerHTML = html.trim();

    const nested = [...wrap.querySelectorAll("[data-include]")];
    const parent = el.parentNode;
    const nodes = [...wrap.childNodes];
    nodes.forEach((node) => parent.insertBefore(node, el));
    el.remove();

    await Promise.all(nested.map((child) => inject(child)));
  }

  async function run() {
    const nodes = [...document.querySelectorAll("[data-include]")];
    await Promise.all(nodes.map((el) => inject(el)));
    document.dispatchEvent(new CustomEvent("kml:includes-ready"));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
