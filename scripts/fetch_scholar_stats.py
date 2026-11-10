#!/usr/bin/env python3
"""Fetch public Google Scholar profile metrics for the static homepage."""

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROFILE_URL = "https://scholar.google.com/citations?user=V_7bX4QAAAAJ&hl=en"
OUTPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "scholar.json"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    request = Request(
        PROFILE_URL,
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

    data = {
        "citations": int(values[0].replace(",", "")),
        "hIndex": int(values[2].replace(",", "")),
        "i10Index": int(values[4].replace(",", "")),
        "updatedAt": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    OUTPUT_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

