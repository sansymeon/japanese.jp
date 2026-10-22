/**
 * Shared museum-room UI: copyright year, mobile nav, Start Here and
 * Vocabulary links, reveal-on-scroll.
 */
(function () {
  "use strict";

  var year = document.getElementById("copyrightYear");
  if (year) year.textContent = String(new Date().getFullYear());

  var START_HERE_HREF = "/start-here/rooms/";
  var VOCABULARY_HREF = "/kml/vocabulary/";

  var EN_NAV = [
    { href: "/start-here/rooms/", label: "LEARN JAPANESE", current: function (path) { return /^\/start-here(\/|$)/.test(path) || /^\/kml\/vocabulary(\/|$)/.test(path); } },
    { href: "/study-kanji/", label: "STUDY KANJI", current: function (path) { return /^\/study-kanji(\/|$)/.test(path) || /^\/kml\/contents\/books(\/|$)/.test(path); } },
    { href: "/museum/", label: "MUSEUM", current: function (path) { return /^\/museum(\/|$)/.test(path); } },
    { href: "/", label: "HOME", current: function (path) { return path === "" || path === "/index.html"; } },
  ];

  var JA_NAV = [
    { href: "/start-here/rooms/", label: "はじめに", current: function (path) { return /^\/start-here(\/|$)/.test(path); } },
    { href: "/kml/vocabulary/", label: "語彙", current: function (path) { return /^\/kml\/vocabulary(\/|$)/.test(path); } },
    { href: "/kanken/", label: "漢検への道", current: function (path) { return /^\/kanken(\/|$)/.test(path) || /^\/ja\/kanken(\/|$)/.test(path); } },
    { href: "/kml/contents/books/", label: "漢字の学び", current: function (path) { return /^\/kml\/contents\/books(\/|$)/.test(path); } },
    { href: "/ja/collections/", label: "映像コレクション", current: function (path) { return /^\/ja\/collections(\/|$)/.test(path); } },
    { href: "/ja/", label: "ホーム", current: function (path) { return path === "/ja" || path === "/ja/index.html"; } },
  ];

  function normalizeMuseumNav(list) {
    if (!list) return;
    var items = isJapanesePage() ? JA_NAV : EN_NAV;
    var path = pathWithoutSlash(window.location.pathname);
    list.textContent = "";
    items.forEach(function (item) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = item.href;
      a.textContent = item.label;
      if (item.current(path)) a.setAttribute("aria-current", "page");
      li.appendChild(a);
      list.appendChild(li);
    });
  }

  function isJapanesePage() {
    var lang = (document.documentElement.getAttribute("lang") || "").toLowerCase();
    return lang === "ja" || lang.indexOf("ja-") === 0;
  }

  function isStartHereHref(href) {
    if (!href) return false;
    var path = href.split("?")[0].split("#")[0].replace(/\/+$/, "");
    return (
      /(^|\/)start-here(\/index\.html)?$/i.test(path) ||
      /(^|\/)start-here\/rooms(\/index\.html)?$/i.test(path)
    );
  }

  function isVocabularyHref(href) {
    if (!href) return false;
    var path = href.split("?")[0].split("#")[0].replace(/\/+$/, "");
    return /(^|\/)kml\/vocabulary(\/index\.html)?$/i.test(path);
  }

  function ensureStartHereLink(list) {
    if (!list || isJapanesePage()) return;
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

  function ensureVocabularyLink(list) {
    if (!list || isJapanesePage()) return;
    var anchors = list.querySelectorAll("a");
    var i;
    var startHereItem = null;
    for (i = 0; i < anchors.length; i++) {
      if (isVocabularyHref(anchors[i].getAttribute("href"))) return;
      if ((anchors[i].textContent || "").trim() === "Vocabulary") return;
      if (
        !startHereItem &&
        (isStartHereHref(anchors[i].getAttribute("href")) ||
          (anchors[i].textContent || "").trim() === "Start Here")
      ) {
        startHereItem = anchors[i].closest("li") || anchors[i];
      }
    }
    var li = document.createElement("li");
    var a = document.createElement("a");
    a.href = VOCABULARY_HREF;
    a.textContent = "Vocabulary";
    if (/(^|\/)kml\/vocabulary(\/|$)/i.test(window.location.pathname)) {
      a.setAttribute("aria-current", "page");
    }
    li.appendChild(a);
    if (startHereItem && startHereItem.parentNode === list) {
      if (startHereItem.nextSibling) {
        list.insertBefore(li, startHereItem.nextSibling);
      } else {
        list.appendChild(li);
      }
    } else if (list.firstChild) {
      list.insertBefore(li, list.firstChild.nextSibling);
    } else {
      list.appendChild(li);
    }
  }

  function pathWithoutSlash(pathname) {
    return (pathname || "").split("?")[0].split("#")[0].replace(/\/+$/, "");
  }

  var header = document.querySelector(".museum-header, .books-header");
  var inner = header && header.querySelector(".museum-header-inner, .books-header-inner");
  var panel = header && header.querySelector("nav");
  var links =
    (panel && panel.querySelector(".museum-nav, .books-nav")) ||
    (header && header.querySelector(".museum-nav, .books-nav"));

  if (inner && links) {
    normalizeMuseumNav(links);

    if (panel && !header.querySelector(".museum-nav-toggle")) {
      if (!panel.id) panel.id = "museumNav";
      var menuJa = isJapanesePage();
      var toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "museum-nav-toggle";
      toggle.setAttribute("aria-controls", panel.id);
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", menuJa ? "メニューを開く" : "Open menu");
      toggle.textContent = menuJa ? "メニュー" : "Menu";
      inner.insertBefore(toggle, panel);

      function setOpen(open) {
        if (open) header.classList.add("is-nav-open");
        else header.classList.remove("is-nav-open");
        if (panel) {
          if (open) panel.classList.add("is-open");
          else panel.classList.remove("is-open");
        }
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        toggle.setAttribute(
          "aria-label",
          open
            ? menuJa
              ? "メニューを閉じる"
              : "Close menu"
            : menuJa
              ? "メニューを開く"
              : "Open menu"
        );
      }

      toggle.addEventListener("click", function () {
        setOpen(!header.classList.contains("is-nav-open"));
      });
      links.addEventListener("click", function (event) {
        if (event.target.closest("a")) setOpen(false);
      });
    }
  }

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
