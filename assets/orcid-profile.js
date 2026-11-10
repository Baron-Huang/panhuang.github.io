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

})();
