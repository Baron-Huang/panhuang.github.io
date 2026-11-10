#!/usr/bin/env python3
"""Refresh public Google Scholar data through the SerpApi Author API."""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

AUTHOR_ID = "V_7bX4QAAAAJ"
ROOT = Path(__file__).resolve().parents[1]
STATS_FILE = ROOT / "data" / "scholar.json"
PUBLICATIONS_FILE = ROOT / "data" / "publications.json"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def metric(table: list[dict], field: str) -> int:
    for row in table:
        value = row.get(field, {}).get("all")
        if isinstance(value, int):
            return value
    fail(f"SerpApi response did not include {field}.")


def main() -> None:
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        fail("SERPAPI_KEY is not configured in GitHub Actions secrets.")

    query = urlencode({
        "engine": "google_scholar_author",
        "author_id": AUTHOR_ID,
        "hl": "en",
        "num": 100,
        "sort": "pubdate",
        "api_key": api_key,
    })
    try:
        with urlopen(f"https://serpapi.com/search.json?{query}", timeout=60) as response:
            payload = json.load(response)
    except (HTTPError, URLError) as error:
        fail(f"SerpApi request failed: {error}")

    if payload.get("error"):
        fail(f"SerpApi error: {payload['error']}")

    papers = [
        {
            "id": paper.get("citation_id") or paper["title"].casefold(),
            "title": paper["title"],
            "authors": paper.get("authors", ""),
            "venue": paper.get("publication", ""),
            "year": paper.get("year", ""),
        }
        for paper in payload.get("articles", [])
        if paper.get("title")
    ]
    if not papers:
        fail("SerpApi response did not include any Scholar articles.")

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    table = payload.get("cited_by", {}).get("table", [])
    stats = {
        "citations": metric(table, "citations"),
        "hIndex": metric(table, "h_index"),
        "i10Index": metric(table, "i10_index"),
        "publicationCount": len(papers),
        "updatedAt": now,
    }
    STATS_FILE.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    previous = {"papers": [], "news": []}
    if PUBLICATIONS_FILE.exists():
        previous = json.loads(PUBLICATIONS_FILE.read_text(encoding="utf-8"))
    previous_ids = {paper.get("id") for paper in previous.get("papers", [])}
    new_papers = [] if not previous_ids else [paper for paper in papers if paper["id"] not in previous_ids]
    news = [dict(paper, detectedAt=now) for paper in new_papers] + previous.get("news", [])
    PUBLICATIONS_FILE.write_text(
        json.dumps({"updatedAt": now, "papers": papers, "news": news[:20]}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
