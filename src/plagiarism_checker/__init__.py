from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

from flask import Flask, Response, jsonify, request

from .clean import main_text
from .compare import compare
from .phrases import extract_phrases
from .report import build_report
from .scrape import fetch_html
from .search import google_top_urls

WEB_DIST = Path(__file__).resolve().parents[2] / "web" / "dist"  # Astro build output

app = Flask(__name__, static_folder=WEB_DIST, static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB
# Live run: every page that loaded did so in under 3.5 s; a slow-drip site took 17 s and still failed.
FETCH_DEADLINE = 6  # seconds for the whole fetch step; urlopen's timeout is per read, not total


def bad_request(message: str, status: int = 400):
    return jsonify(error=message), status


@app.errorhandler(413)
def too_large(_):
    return bad_request("File is larger than 2 MB.", 413)


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/check")
def check():
    file = request.files.get("document")
    # shortcut: .txt only, add .docx/.pdf when the text-reading step lands
    if not file or not file.filename.lower().endswith(".txt"):
        return bad_request("Please upload a .txt file.")
    try:
        text = file.read().decode("utf-8")
    except UnicodeDecodeError:
        return bad_request("File must be UTF-8 text.")
    if not text.strip():
        return bad_request("The file is empty.")

    phrases = extract_phrases(text)
    found, search_error = [[] for _ in phrases], None
    try:
        with ThreadPoolExecutor() as pool:  # searches are I/O-bound; run them at once
            found = list(pool.map(google_top_urls, phrases))
    except KeyError:
        search_error = "Search is off: set SCRAPINGBEE_API_KEY."
    except OSError as e:
        search_error = f"Search failed: {e}"

    urls = list(dict.fromkeys(u for us in found for u in us))  # phrases can share a URL
    pool = ThreadPoolExecutor()
    futures = {u: pool.submit(fetch_html, u) for u in urls}
    done, _ = wait(futures.values(), timeout=FETCH_DEADLINE)
    pool.shutdown(wait=False, cancel_futures=True)  # don't wait for stragglers; they end on their own timeout
    htmls = {u: f.result() if f in done else None for u, f in futures.items()}
    pages = {u: main_text(h) if h else "" for u, h in htmls.items()}  # url -> cleaned text, "" if unusable

    similarity, matches = compare(text, pages)

    return jsonify(
        filename=file.filename,
        chars=len(text),
        search_error=search_error,
        similarity=similarity,
        matches=matches,
        results=[
            {"phrase": p, "urls": [{"url": u, "fetched": bool(pages[u])} for u in us]}
            for p, us in zip(phrases, found)
        ],
    )


@app.post("/api/report")
def report():
    data = request.get_json(silent=True)
    if (
        not isinstance(data, dict) or "matches" not in data
    ):  # only our own /api/check result shape
        return bad_request("Send the JSON result from /api/check.")
    pdf = build_report(data)
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report.pdf"},
    )


def main() -> None:
    app.run(debug=True)
