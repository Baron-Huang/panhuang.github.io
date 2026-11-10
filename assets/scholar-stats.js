(() => {
  const dataUrl = "data/scholar.json";

  fetch(dataUrl, { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error("Scholar statistics are unavailable");
      return response.json();
    })
    .then((stats) => {
      const formatter = new Intl.NumberFormat("en-US");
      document.querySelectorAll("[data-scholar-metric]").forEach((element) => {
        const value = stats[element.dataset.scholarMetric];
        if (Number.isFinite(value)) element.textContent = formatter.format(value);
      });
    })
    .catch(() => {
      // Keep the page's last committed values visible if the data file is unavailable.
    });
})();

