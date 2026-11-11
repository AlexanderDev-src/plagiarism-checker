from urllib.request import Request, urlopen

MAX_BYTES = 2 * 1024 * 1024
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; plagiarism-checker)"}


def fetch_html(url: str, timeout: int = 5) -> str | None:
    """HTML of `url`, or None if it is not http(s), not HTML, or fails to load."""
    # shortcut: plain HTTP fetch (no ScrapingBee credits); sites that block bots return None, route through ScrapingBee if too many fail
    if not url.startswith(("http://", "https://")):
        return None
    try:
        with urlopen(Request(url, headers=HEADERS), timeout=timeout) as resp:
            if resp.headers.get_content_type() != "text/html":
                return None
            body = resp.read(MAX_BYTES)
            return body.decode(resp.headers.get_content_charset() or "utf-8", errors="replace")
    except (OSError, ValueError, LookupError):  # network/HTTP errors, bad URL, unknown charset
        return None
