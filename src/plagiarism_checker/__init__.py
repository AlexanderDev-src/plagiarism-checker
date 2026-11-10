from concurrent.futures import ThreadPoolExecutor

from flask import Flask, render_template, request

from .phrases import extract_phrases
from .scrape import fetch_html
from .search import google_top_urls

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB; Flask returns 413 above this


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    file = request.files.get("document")
    # shortcut: .txt only, add .docx/.pdf when the text-reading step lands
    if not file or not file.filename.lower().endswith(".txt"):
        return render_template("index.html", error="Please upload a .txt file."), 400
    try:
        text = file.read().decode("utf-8")
    except UnicodeDecodeError:
        return render_template("index.html", error="File must be UTF-8 text."), 400
    if not text.strip():
        return render_template("index.html", error="The file is empty."), 400

    phrases = extract_phrases(text)
    results, search_error = [(p, []) for p in phrases], None
    try:
        with ThreadPoolExecutor() as pool:  # searches are I/O-bound; run them at once
            results = list(zip(phrases, pool.map(google_top_urls, phrases)))
    except KeyError:
        search_error = "Search is off: set SCRAPINGBEE_API_KEY."
    except OSError as e:
        search_error = f"Search failed: {e}"

    urls = list(dict.fromkeys(u for _, found in results for u in found))  # phrases can share a URL
    with ThreadPoolExecutor() as pool:
        pages = dict(zip(urls, pool.map(fetch_html, urls)))

    return render_template(
        "index.html",
        filename=file.filename,
        chars=len(text),
        results=results,
        search_error=search_error,
        pages=pages,
    )


def main() -> None:
    app.run(debug=True)
