from io import BytesIO

from plagiarism_checker import app
from plagiarism_checker.compare import compare

DOC = "one two three four five six seven eight nine ten eleven twelve"


def test_copied_part_is_found_and_counted():
    page = "intro words. Four, FIVE six seven eight nine ten eleven twelve and more " + "filler " * 500
    pct, matches = compare(DOC, {"https://a.com": page, "https://b.com": "nothing alike here at all"})
    assert matches == [
        {"url": "https://a.com", "similarity": 75.0, "passages": ["four five six seven eight nine ten eleven twelve"]}
    ]
    assert pct == 75.0  # 9 of 12 words, and a long page does not lower it


def test_identical_unrelated_and_empty():
    assert compare(DOC, {"u": DOC})[0] == 100.0
    assert compare(DOC, {"u": "completely different"}) == (0.0, [])
    assert compare("", {"u": DOC}) == (0.0, [])
    assert compare(DOC, {"u": ""}) == (0.0, [])


def test_short_document_uses_whole_text():
    assert compare("hello world", {"u": "say hello world now"})[0] == 100.0


def test_overall_is_the_union_of_pages():
    first, last = " ".join(DOC.split()[:8]), " ".join(DOC.split()[4:])
    pct, matches = compare(DOC, {"a": first, "b": last})
    assert [m["similarity"] for m in matches] == [66.7, 66.7] and pct == 100.0  # 8/12 each; overlap counted once
    assert compare(DOC, {"a": DOC, "b": DOC})[0] == 100.0


def test_two_separate_passages_from_one_page():
    text = "a1 a2 a3 a4 a5 a6 a7 a8 zzz b1 b2 b3 b4 b5 b6 b7 b8"
    _, matches = compare(text, {"u": "a1 a2 a3 a4 a5 a6 a7 a8 other b1 b2 b3 b4 b5 b6 b7 b8"})
    assert [len(p.split()) for p in matches[0]["passages"]] == [8, 8]


def test_route_returns_similarity(monkeypatch):
    monkeypatch.setattr("plagiarism_checker.google_top_urls", lambda p: ["https://a.com"])
    monkeypatch.setattr("plagiarism_checker.fetch_html", lambda u: f"<main>{DOC}</main>")
    r = app.test_client().post(
        "/api/check", data={"document": (BytesIO(DOC.encode()), "a.txt")}, content_type="multipart/form-data"
    )
    assert r.json["similarity"] == 100.0
    assert r.json["matches"] == [{"url": "https://a.com", "similarity": 100.0, "passages": [DOC]}]
