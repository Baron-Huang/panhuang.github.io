#!/usr/bin/env python3
"""Fetch public Google Scholar data for the static homepage."""

import json
import re
import sys
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROFILE_URL = "https://scholar.google.com/citations?user=V_7bX4QAAAAJ&hl=en"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data" / "scholar.json"
PUBLICATIONS_FILE = ROOT / "data" / "publications.json"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def clean_html(value: str) -> str:
    return unescape(re.sub(r"<.*?>", "", value)).strip()


def main() -> None:
    request = Request(
        PROFILE_URL + "&cstart=0&pagesize=100",
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; PanHuangAcademicHomepage/1.0)",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError) as error:
        fail(f"Google Scholar request failed: {error}")

    values = re.findall(r'class="gsc_rsb_std">([0-9,]+)<', html)
    if len(values) < 5:
        fail("Could not parse the public Google Scholar metrics.")

    papers = []
    rows = re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', html, flags=re.DOTALL)
    for row in rows:
        title_match = re.search(r'class="gsc_a_at"[^>]*>(.*?)</a>', row, flags=re.DOTALL)
        metadata = re.findall(r'<div class="gs_gray">(.*?)</div>', row, flags=re.DOTALL)
        if not title_match:
            continue
        title = clean_html(title_match.group(1))
        authors = clean_html(metadata[0]) if metadata else ""
        venue = clean_html(metadata[1]) if len(metadata) > 1 else ""
        papers.append({"id": title.casefold(), "title": title, "authors": authors, "venue": venue})

    if not papers:
        fail("Could not parse publications from the public Google Scholar profile.")

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    stats = {
        "citations": int(values[0].replace(",", "")),
        "hIndex": int(values[2].replace(",", "")),
        "i10Index": int(values[4].replace(",", "")),
        "publicationCount": len(papers),
        "updatedAt": now,
    }
    OUTPUT_FILE.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    previous = {"papers": [], "news": []}
    if PUBLICATIONS_FILE.exists():
        previous = json.loads(PUBLICATIONS_FILE.read_text(encoding="utf-8"))
    previous_ids = {paper.get("id") for paper in previous.get("papers", [])}

    # The first run establishes the baseline; subsequent runs announce only new entries.
    new_papers = [] if not previous_ids else [paper for paper in papers if paper["id"] not in previous_ids]
    old_news = previous.get("news", [])
    news = [dict(paper, detectedAt=now) for paper in new_papers] + old_news
    PUBLICATIONS_FILE.write_text(
        json.dumps({"updatedAt": now, "papers": papers, "news": news[:20]}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
