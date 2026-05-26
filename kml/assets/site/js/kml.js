// ==============================
// Active Kanji Highlight
// ==============================

(function(){

const sections = document.querySelectorAll(".kanji-entry");
const navLinks = document.querySelectorAll(".anchor-list a");

if (sections.length && navLinks.length) {

  const observer = new IntersectionObserver(entries => {

    entries.forEach(entry => {

      if (entry.isIntersecting) {

        navLinks.forEach(link => link.classList.remove("active"));

        const id = entry.target.getAttribute("id");
        const activeLink = document.querySelector(`.anchor-list a[href="#${id}"]`);

        if (activeLink) activeLink.classList.add("active");

      }

    });

  },{
    rootMargin: "-40% 0px -55% 0px",
    threshold: 0
  });

  sections.forEach(section => observer.observe(section));

}

})();
// ==============================
// KML Reflection + Verse Timing
// ==============================

(function(){

const entries = document.querySelectorAll(".kanji-entry");

if (!entries.length) return;

const observer = new IntersectionObserver((entriesList) => {

  entriesList.forEach(entry => {

    if (!entry.isIntersecting) return;

    const card = entry.target;

    const reflection = card.querySelector(".kml-reflection");
    const verses = card.querySelector(".kml-verses");

    if (!reflection) return;

    // Prevent retrigger
    if (card.dataset.animated) return;
    card.dataset.animated = "true";

    // Step 1: reflection
    setTimeout(() => {
      reflection.classList.add("visible");
    }, 400);

    // Step 2: verses
    if (verses) {
      setTimeout(() => {
        verses.classList.add("visible");
      }, 1200);
    }

  });

},{
  threshold: 0.35
});

entries.forEach(entry => observer.observe(entry));

})();

// ==============================
// KML Primitive Labels
// ==============================

(function(){

const COMPONENT_LABELS = {
  "一": "line",
  "丶": "drop",
  "口": "mouth",
  "日": "sun",
  "月": "moon",
  "田": "field",
  "目": "eye",
  "儿": "two legs",
  "八": "split",
  "十": "ten",
  "卜": "divination",
  "⺈": "hooked cover",
  "貝": "shellfish"
};

const seen = new Set();

document.querySelectorAll("[data-primitive]").forEach(el => {

  const key = el.dataset.primitive;
  const label = COMPONENT_LABELS[key];

  if (!label) return;

  el.title = label;

  if (!seen.has(key)) {
    el.textContent = `${key} (${label})`;
    seen.add(key);
  }

});

})();

// ==============================
// Click-to-reveal verse furigana
// ==============================

(function () {
  document.querySelectorAll(".toggle-reading").forEach((el) => {
    el.addEventListener("click", () => {
      el.classList.toggle("show-reading");
    });
  });
})();