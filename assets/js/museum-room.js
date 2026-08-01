/**
 * Shared museum-room UI: copyright year + reveal-on-scroll.
 */
(function () {
  "use strict";

  var year = document.getElementById("copyrightYear");
  if (year) year.textContent = String(new Date().getFullYear());

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
