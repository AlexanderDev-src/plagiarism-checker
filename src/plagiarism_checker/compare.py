import string

SHINGLE = 8  # words in a row that must match to count as copied


def _norm(words: list[str]) -> list[str]:
    return [w.lower().strip(string.punctuation) for w in words]


def _runs(words: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]


def compare(text: str, pages: dict[str, str]) -> tuple[float, list[dict]]:
    """Return (% of `text` found in any page, [{url, similarity, passages}] for pages with matches).

    A word counts as copied when it sits in a run of SHINGLE words that also appears in a page.
    Similarity is measured against the document, so a long page is not penalised (containment, not Jaccard).
    """
    # shortcut: exact runs of whitespace words, so reworded text is missed; use fuzzy matching if that matters
    words = text.split()
    if not words:
        return 0.0, []
    n = min(SHINGLE, len(words))
    mine = _runs(_norm(words), n)

    covered, matches = set(), []
    for url, page in pages.items():
        theirs = set(_runs(_norm(page.split()), n))
        idx = sorted({j for i, run in enumerate(mine) if run in theirs for j in range(i, i + n)})
        if not idx:
            continue
        passages, start = [], 0
        for k in range(1, len(idx) + 1):
            if k == len(idx) or idx[k] != idx[k - 1] + 1:  # a gap ends the passage
                passages.append(" ".join(words[idx[start] : idx[k - 1] + 1]))
                start = k
        covered.update(idx)
        matches.append({"url": url, "similarity": round(100 * len(idx) / len(words), 1), "passages": passages})
    return round(100 * len(covered) / len(words), 1), matches
