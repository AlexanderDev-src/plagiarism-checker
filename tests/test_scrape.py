import io
from email.message import Message
from urllib.error import URLError

import pytest

from plagiarism_checker import scrape


class FakeResp(io.BytesIO):
    def __init__(self, body: bytes, content_type: str):
        super().__init__(body)
        self.headers = Message()
        self.headers["Content-Type"] = content_type


def use(monkeypatch, resp=None, error=None):
    def fake_urlopen(req, timeout):
        if error:
            raise error
        return resp

    monkeypatch.setattr(scrape, "urlopen", fake_urlopen)


def test_returns_decoded_html(monkeypatch):
    use(monkeypatch, FakeResp("<p>ไทย</p>".encode("tis-620"), "text/html; charset=tis-620"))
    assert scrape.fetch_html("https://a.com") == "<p>ไทย</p>"


def test_non_html_is_skipped(monkeypatch):
    use(monkeypatch, FakeResp(b"%PDF", "application/pdf"))
    assert scrape.fetch_html("https://a.com/x.pdf") is None


@pytest.mark.parametrize("err", [URLError("down"), ValueError("bad url")])
def test_errors_return_none(monkeypatch, err):
    use(monkeypatch, error=err)
    assert scrape.fetch_html("https://a.com") is None


def test_rejects_non_http_scheme(monkeypatch):
    use(monkeypatch, error=AssertionError("must not fetch"))
    assert scrape.fetch_html("file:///etc/passwd") is None
