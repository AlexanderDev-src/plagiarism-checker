import json

from plagiarism_checker import app
from plagiarism_checker.report import build_report

RESULT = {
    "filename": "a.txt",
    "chars": 42,
    "similarity": 75.0,
    "search_error": None,
    "matches": [
        {
            "url": "https://example.com/x",
            "similarity": 75.0,
            "passages": ["สวัสดี hello world one two three"],
        }
    ],
}


def test_build_report_is_a_pdf_with_thai_text():
    pdf = build_report(RESULT)
    assert pdf.startswith(b"%PDF") and len(pdf) > 1000


def test_no_matches_still_builds():
    pdf = build_report({**RESULT, "matches": [], "similarity": 0.0})
    assert pdf.startswith(b"%PDF")


def test_route_returns_pdf_download():
    r = app.test_client().post("/api/report", data=json.dumps(RESULT), content_type="application/json")
    assert r.status_code == 200
    assert r.mimetype == "application/pdf"
    assert "report.pdf" in r.headers["Content-Disposition"]
    assert r.data.startswith(b"%PDF")


def test_route_rejects_unknown_shape():
    r = app.test_client().post("/api/report", data=json.dumps({"x": 1}), content_type="application/json")
    assert r.status_code == 400 and r.json["error"]
    r = app.test_client().post("/api/report", data="not json", content_type="application/json")
    assert r.status_code == 400
