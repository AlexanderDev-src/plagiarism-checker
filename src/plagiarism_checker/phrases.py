import random


def extract_phrases(text: str, count: int = 5, rng=random) -> list[str]:
    """Pick up to `count` non-overlapping random phrases of 5-10 words, in document order."""
    # shortcut: splits on whitespace, so Thai/CJK text without spaces counts as few "words"; add a tokenizer if that matters
    words = text.split()
    if len(words) < 5:
        return [" ".join(words)] if words else []
    starts = range(0, len(words), 10)  # 10-word slots keep phrases from overlapping
    phrases = []
    for s in sorted(rng.sample(starts, min(count, len(starts)))):
        chunk = words[s : s + rng.randint(5, 10)]
        if len(chunk) >= 5:  # the last slot can be too short
            phrases.append(" ".join(chunk))
    return phrases
