from bs4 import BeautifulSoup

NOISE = ["script", "style", "noscript", "template", "svg", "iframe", "header", "footer", "nav", "aside", "form"]


def main_text(html: str) -> str:
    """Readable main text of a page: drops scripts, menus, headers and footers; prefers <article>/<main>."""
    # shortcut: tag-based heuristics, no readability scoring; switch to trafilatura if results are noisy
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(NOISE):
        tag.decompose()
    root = soup.find("article") or soup.find("main") or soup.body or soup
    return " ".join(root.get_text(" ").split())
