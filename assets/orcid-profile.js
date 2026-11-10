(() => {
  const orcid = "0000-0001-8158-2628";
  const endpoint = `https://pub.orcid.org/v3.0/${orcid}/record`;
  const valueOf = (field) => field?.value?.trim() || "";
  const localizedValue = (field) =>
    field?.content || field?.value || field?.["translated-title"]?.value || "";

  fetch(endpoint, { headers: { Accept: "application/vnd.orcid+json" } })
    .then((response) => {
      if (!response.ok) throw new Error("ORCID profile is unavailable");
      return response.json();
    })
    .then((record) => {
      const person = record.person || {};
      const biography = localizedValue(person.biography);
      const name = [
        valueOf(person.name?.["given-names"]),
        valueOf(person.name?.["family-name"]),
      ].filter(Boolean).join(" ");
      const keywords = (person.keywords?.keyword || [])
        .map((keyword) => localizedValue(keyword))
        .filter(Boolean);
      const card = document.querySelector("[data-orcid-profile]");
      if (!card) return;

      const nameElement = card.querySelector("[data-orcid-name]");
      const bioElement = card.querySelector("[data-orcid-bio]");
      const keywordElement = card.querySelector("[data-orcid-keywords]");
      if (name) nameElement.textContent = name;
      bioElement.textContent = biography || "Public profile information from ORCID.";
      if (keywords.length) {
        keywordElement.textContent = keywords.join(" · ");
        keywordElement.hidden = false;
      }
      card.hidden = false;
    })
    .catch(() => {
      // Keep the section hidden when the public ORCID record cannot be reached.
    });

  fetch(`https://pub.orcid.org/v3.0/${orcid}/peer-reviews`, {
    headers: { Accept: "application/vnd.orcid+json" },
  })
    .then((response) => response.ok ? response.json() : Promise.reject())
    .then((data) => {
      const countReviewSummaries = (node) => {
        if (Array.isArray(node)) return node.reduce((total, item) => total + countReviewSummaries(item), 0);
        if (!node || typeof node !== "object") return 0;
        return Object.entries(node).reduce((total, [key, value]) => {
          if (key === "peer-review-summary" && Array.isArray(value)) return total + value.length;
          return total + countReviewSummaries(value);
        }, 0);
      };
      return countReviewSummaries(data);
    })
    .then((count) => {
      document.querySelectorAll("[data-orcid-metric='peerReviews']").forEach((element) => {
        element.textContent = new Intl.NumberFormat("en-US").format(count);
      });
    })
    .catch(() => {});
})();
