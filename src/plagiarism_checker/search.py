import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen

API = "https://app.scrapingbee.com/api/v1/store/google"


def google_top_urls(phrase: str, n: int = 5) -> list[str]:
    """Top `n` Google result URLs for the exact phrase. Raises KeyError if SCRAPINGBEE_API_KEY is unset, OSError on network/HTTP errors."""
    key = os.environ["SCRAPINGBEE_API_KEY"]
    query = urlencode({"api_key": key, "search": f'"{phrase}"', "nb_results": n})
    with urlopen(f"{API}?{query}", timeout=30) as resp:
        data = json.load(resp)
    return [r["url"] for r in data.get("organic_results", [])[:n]]
