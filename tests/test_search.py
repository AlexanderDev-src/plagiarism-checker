import io
import json
from urllib.parse import parse_qs, urlparse

import pytest

from plagiarism_checker import search


def test_returns_top_urls_and_quotes_phrase(monkeypatch):
    seen = {}

    def fake_urlopen(url, timeout):
        seen["q"] = parse_qs(urlparse(url).query)
        body = {"organic_results": [{"url": f"https://s{i}.com"} for i in range(8)]}
        return io.BytesIO(json.dumps(body).encode())

    monkeypatch.setenv("SCRAPINGBEE_API_KEY", "test-key")
    monkeypatch.setattr(search, "urlopen", fake_urlopen)
    assert search.google_top_urls("hello world") == [f"https://s{i}.com" for i in range(5)]
    assert seen["q"]["search"] == ['"hello world"'] and seen["q"]["api_key"] == ["test-key"]


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("SCRAPINGBEE_API_KEY", raising=False)
    with pytest.raises(KeyError):
        search.google_top_urls("x")
