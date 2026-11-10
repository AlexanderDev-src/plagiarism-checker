from io import BytesIO

import pytest

from plagiarism_checker import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("SCRAPINGBEE_API_KEY", raising=False)  # never hit the real API in tests
    return app.test_client()


def upload(client, data, name):
    return client.post("/", data={"document": (BytesIO(data), name)}, content_type="multipart/form-data")


def test_get_shows_form(client):
    assert b'name="document"' in client.get("/").data


def test_valid_txt(client):
    r = upload(client, "สวัสดี hello".encode(), "a.txt")
    assert r.status_code == 200 and b"12 characters" in r.data
    assert b"SCRAPINGBEE_API_KEY" in r.data


def test_shows_search_links(client, monkeypatch):
    monkeypatch.setattr("plagiarism_checker.google_top_urls", lambda p: ["https://example.com/x", "https://example.com/y"])
    fetched = []
    monkeypatch.setattr("plagiarism_checker.fetch_html", lambda u: fetched.append(u) or ("<p>hi</p>" if u.endswith("x") else None))
    r = upload(client, b"one two three four five six", "a.txt")
    assert b'href="https://example.com/x"' in r.data
    assert b"fetched</span>" in r.data and b"could not fetch" in r.data
    assert sorted(fetched) == ["https://example.com/x", "https://example.com/y"]  # each URL fetched once


def test_search_network_error_is_shown(client, monkeypatch):
    def boom(p):
        raise OSError("timed out")

    monkeypatch.setattr("plagiarism_checker.google_top_urls", boom)
    r = upload(client, b"one two three four five six", "a.txt")
    assert r.status_code == 200 and b"Search failed: timed out" in r.data


@pytest.mark.parametrize("data,name", [(b"x", "a.pdf"), (b"\xff\xfe", "a.txt"), (b"  \n", "a.txt")])
def test_rejects_bad_input(client, data, name):
    assert upload(client, data, name).status_code == 400


def test_missing_file(client):
    assert client.post("/", data={}).status_code == 400
