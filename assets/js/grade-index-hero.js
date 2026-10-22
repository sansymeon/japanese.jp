/* Grade-index heroes. Filenames live in /kanken/grade-index-heroes.json.
   This does not read lesson heroes or study-image crops. */
(function () {
  var section = document.querySelector(".room-hero[data-grade-index]");
  if (!section) return;
  var key = section.getAttribute("data-grade-index");
  if (!key) return;

  fetch("/kanken/grade-index-heroes.json", { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error(String(res.status));
      return res.json();
    })
    .then(function (data) {
      var item = data && data.levels && data.levels[key];
      if (!item || !item.src) return;
      var img = section.querySelector(".room-hero-media img");
      if (!img) return;
      if (img.getAttribute("src") !== item.src) img.setAttribute("src", item.src);
      section.classList.toggle("room-hero--gold", item.artwork === "gold");
    })
    .catch(function () {});
})();
