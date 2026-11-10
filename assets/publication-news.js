(() => {
  const newsList = document.querySelector("[data-publication-news]");
  if (!newsList) return;

  const escapeHtml = (value) => value.replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  })[character]);

  fetch("data/publications.json", { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error("Publication news is unavailable");
      return response.json();
    })
    .then((data) => {
      const publicationYear = (item) => {
        const match = String(item.year || item.venue || "").match(/20\d{2}/);
        return match ? Number(match[0]) : 0;
      };
      const latest = (Array.isArray(data.papers) ? data.papers : [])
        .slice()
        .sort((left, right) => publicationYear(right) - publicationYear(left))
        .slice(0, 3);
      if (!latest.length) {
        newsList.innerHTML = '<p class="news-empty">Recent publications will appear after the next Scholar update.</p>';
        return;
      }
      newsList.innerHTML = latest.map((item) => `
        <article class="news-item">
          <time class="news-date">${escapeHtml(String(publicationYear(item) || "Latest"))}</time>
          <div>
            <h3>${escapeHtml(item.title)}</h3>
            <p>${escapeHtml([item.authors, item.venue].filter(Boolean).join(" · "))}</p>
          </div>
        </article>
      `).join("");
    })
    .catch(() => {
      newsList.innerHTML = '<p class="news-empty">Publication news will be available after the next Scholar update.</p>';
    });
})();
