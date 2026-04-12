// ==============================
// Active Kanji Highlight
// ==============================

const sections = document.querySelectorAll(".kanji-entry");
const navLinks = document.querySelectorAll(".anchor-list a");

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