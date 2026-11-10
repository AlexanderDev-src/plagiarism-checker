from flask import Flask, render_template, request

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

    return render_template("index.html", filename=file.filename, chars=len(text))


def main() -> None:
    app.run(debug=True)
