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
      const news = Array.isArray(data.news) ? data.news.slice(0, 6) : [];
      if (!news.length) {
        newsList.innerHTML = '<p class="news-empty">New publications indexed by Google Scholar will appear here automatically.</p>';
        return;
      }
      newsList.innerHTML = news.map((item) => `
        <article class="news-item">
          <time class="news-date" datetime="${escapeHtml(item.detectedAt)}">New paper</time>
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
