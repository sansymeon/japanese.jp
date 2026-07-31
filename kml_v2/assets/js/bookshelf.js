/**
 * KML V2 — bookshelf renderer (metadata → book cards)
 */

(function (global) {
  const KML = (global.KML = global.KML || {});

  function bookCardHtml(book, root) {
    const href = `${root}/books/${book.id}/index.html`;
    const lessons =
      book.lesson_range_label ||
      (book.lesson_start && book.lesson_end
        ? `Lessons ${String(book.lesson_start).padStart(2, "0")}–${String(
            book.lesson_end
          ).padStart(2, "0")}`
        : "");
    return `<li>
      <a class="book-card" href="${href}">
        <span class="book-card-num">Book ${book.number}</span>
        <h3 class="book-card-title">${book.title}</h3>
        <p class="book-card-meta">${lessons || book.status || ""}</p>
      </a>
    </li>`;
  }

  async function render(selector = "[data-bookshelf]") {
    const host = document.querySelector(selector);
    if (!host || !KML.data) return;

    const index = await KML.data.booksIndex();
    const root =
      document.documentElement.getAttribute("data-site-root") || ".";
    const books = index.books || [];
    host.innerHTML = books.map((b) => bookCardHtml(b, root.replace(/\/$/, "") || ".")).join("");
  }

  KML.bookshelf = { render };

  document.addEventListener("kml:includes-ready", () => {
    if (document.querySelector("[data-bookshelf]")) {
      render().catch((err) => console.error(err));
    }
  });
})(window);
