/**
 * Shared museum-room UI: copyright year, mobile nav, Start Here link, reveal-on-scroll.
 */
(function () {
  "use strict";

  var year = document.getElementById("copyrightYear");
  if (year) year.textContent = String(new Date().getFullYear());

  var START_HERE_HREF = "/start-here/";

  function isStartHereHref(href) {
    if (!href) return false;
    var path = href.split("?")[0].split("#")[0].replace(/\/+$/, "");
    return /(^|\/)start-here(\/index\.html)?$/i.test(path);
  }

  function ensureStartHereLink(list) {
    if (!list) return;
    var anchors = list.querySelectorAll("a");
    var i;
    for (i = 0; i < anchors.length; i++) {
      if (isStartHereHref(anchors[i].getAttribute("href"))) return;
      if ((anchors[i].textContent || "").trim() === "Start Here") return;
    }
    var li = document.createElement("li");
    var a = document.createElement("a");
    a.href = START_HERE_HREF;
    a.textContent = "Start Here";
    if (/(^|\/)start-here(\/|$)/i.test(window.location.pathname)) {
      a.setAttribute("aria-current", "page");
    }
    li.appendChild(a);
    list.insertBefore(li, list.firstChild);
  }

  function pathWithoutSlash(pathname) {
    return (pathname || "").split("?")[0].split("#")[0].replace(/\/+$/, "");
  }

  function isStartHereLandingPath(pathname) {
    var path = pathWithoutSlash(pathname);
    return /(^|\/)start-here$/i.test(path) || /(^|\/)start-here\/index\.html$/i.test(path);
  }

  function isStartHereRoomsIndexPath(pathname) {
    var path = pathWithoutSlash(pathname);
    return /(^|\/)start-here\/rooms(\/index\.html)?$/i.test(path);
  }

  function ensureStartHereFooter(nav) {
    if (!nav || nav.hasAttribute("data-no-start-here")) return;
    if (isStartHereLandingPath(window.location.pathname)) return;
    if (isStartHereRoomsIndexPath(window.location.pathname)) return;
    var anchors = nav.querySelectorAll("a");
    var i;
    for (i = 0; i < anchors.length; i++) {
      if (isStartHereHref(anchors[i].getAttribute("href"))) return;
      if ((anchors[i].textContent || "").trim() === "Start Here") return;
    }
    var a = document.createElement("a");
    a.href = START_HERE_HREF;
    a.textContent = "Start Here";
    nav.insertBefore(a, nav.firstChild);
  }

  var header = document.querySelector(".museum-header, .books-header");
  var inner = header && header.querySelector(".museum-header-inner, .books-header-inner");
  var panel = header && header.querySelector("nav");
  var links =
    (panel && panel.querySelector(".museum-nav, .books-nav")) ||
    (header && header.querySelector(".museum-nav, .books-nav"));

  if (inner && links) {
    ensureStartHereLink(links);

    if (panel && !header.querySelector(".museum-nav-toggle")) {
      if (!panel.id) panel.id = "museumNav";
      var toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "museum-nav-toggle";
      toggle.setAttribute("aria-controls", panel.id);
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open menu");
      toggle.textContent = "Menu";
      inner.insertBefore(toggle, panel);

      function setOpen(open) {
        if (open) header.classList.add("is-nav-open");
        else header.classList.remove("is-nav-open");
        if (panel) {
          if (open) panel.classList.add("is-open");
          else panel.classList.remove("is-open");
        }
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      }

      toggle.addEventListener("click", function () {
        setOpen(!header.classList.contains("is-nav-open"));
      });
      links.addEventListener("click", function (event) {
        if (event.target.closest("a")) setOpen(false);
      });
    }
  }

  document.querySelectorAll(".museum-footer nav").forEach(ensureStartHereFooter);

  var nodes = document.querySelectorAll(".reveal");
  if (!nodes.length) return;

  if (!("IntersectionObserver" in window)) {
    nodes.forEach(function (el) {
      el.classList.add("is-visible");
    });
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: "0px 0px -8% 0px" }
  );

  nodes.forEach(function (el) {
    observer.observe(el);
  });
})();
