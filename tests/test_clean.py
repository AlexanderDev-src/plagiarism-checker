from plagiarism_checker.clean import main_text

PAGE = """<html><head><title>T</title><style>p{}</style></head><body>
<header>Site name</header><nav><a>Home</a></nav>
<main><h1>Title</h1><p>First   line.</p>
<script>var x = 1;</script><p>Second <b>line</b>.</p></main>
<aside>Ads</aside><footer>© 2026</footer></body></html>"""


def test_keeps_main_content_only():
    assert main_text(PAGE) == "Title First line. Second line ."


def test_prefers_article_over_main():
    assert main_text("<main>menu<article>story</article></main>") == "story"


def test_falls_back_to_body_and_handles_fragments():
    assert main_text("<body><div>plain <i>text</i></div><footer>x</footer></body>") == "plain text"
    assert main_text("just text") == "just text"
    assert main_text("") == ""
