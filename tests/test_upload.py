from io import BytesIO

import pytest

from plagiarism_checker import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv(
        "SCRAPINGBEE_API_KEY", raising=False
    )  # never hit the real API in tests
    return app.test_client()


def upload(client, data, name):
    return client.post(
        "/api/check",
        data={"document": (BytesIO(data), name)},
        content_type="multipart/form-data",
    )


def test_valid_txt(client):
    r = upload(client, "สวัสดี hello".encode(), "a.txt")
    assert r.status_code == 200 and r.json["chars"] == 12
    assert "SCRAPINGBEE_API_KEY" in r.json["search_error"]


@pytest.mark.parametrize(
    "data,name", [(b"x", "a.pdf"), (b"\xff\xfe", "a.txt"), (b"  \n", "a.txt")]
)
def test_rejects_bad_input(client, data, name):
    r = upload(client, data, name)
    assert r.status_code == 400 and r.json["error"]


def test_missing_file(client):
    assert client.post("/api/check", data={}).status_code == 400


def test_too_large_is_json(client):
    r = upload(client, b"a " * (1024 * 1024 + 1), "a.txt")
    assert r.status_code == 413 and "2 MB" in r.json["error"]


def test_search_results_and_fetch_status(client, monkeypatch):
    monkeypatch.setattr(
        "plagiarism_checker.google_top_urls",
        lambda p: ["https://example.com/x", "https://example.com/y"],
    )
    fetched = []
    monkeypatch.setattr(
        "plagiarism_checker.fetch_html",
        lambda u: fetched.append(u) or ("<p>hi</p>" if u.endswith("x") else None),
    )
    r = upload(client, b"one two three four five six", "a.txt")
    assert r.json["search_error"] is None
    assert r.json["results"][0]["urls"] == [
        {"url": "https://example.com/x", "fetched": True},
        {"url": "https://example.com/y", "fetched": False},
    ]
    assert sorted(fetched) == [
        "https://example.com/x",
        "https://example.com/y",
    ]  # each URL fetched once


def test_search_network_error_is_shown(client, monkeypatch):
    def boom(p):
        raise OSError("timed out")

    monkeypatch.setattr("plagiarism_checker.google_top_urls", boom)
    r = upload(client, b"one two three four five six", "a.txt")
    assert r.status_code == 200 and r.json["search_error"] == "Search failed: timed out"
    assert r.json["results"][0]["urls"] == []


def test_slow_page_is_cut_off_at_the_deadline(client, monkeypatch):
    import time

    monkeypatch.setattr("plagiarism_checker.FETCH_DEADLINE", 0.3)
    monkeypatch.setattr("plagiarism_checker.google_top_urls", lambda p: ["https://fast.com", "https://slow.com"])
    monkeypatch.setattr(
        "plagiarism_checker.fetch_html",
        lambda u: time.sleep(2) or "<p>late</p>" if "slow" in u else "<p>hi</p>",
    )
    t = time.time()
    r = upload(client, b"one two three four five six", "a.txt")
    assert time.time() - t < 1.5  # did not wait the full 2 s
    assert r.json["results"][0]["urls"] == [
        {"url": "https://fast.com", "fetched": True},
        {"url": "https://slow.com", "fetched": False},
    ]
