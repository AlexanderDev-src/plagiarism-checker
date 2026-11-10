import random

from plagiarism_checker.phrases import extract_phrases


def test_phrases_are_5_to_10_words_from_text_in_order():
    words = [f"w{i}" for i in range(200)]
    phrases = extract_phrases(" ".join(words), count=5, rng=random.Random(1))
    assert len(phrases) == 5
    starts = [words.index(p.split()[0]) for p in phrases]
    assert starts == sorted(starts)
    for p, s in zip(phrases, starts):
        assert 5 <= len(p.split()) <= 10 and p.split() == words[s : s + len(p.split())]


def test_short_and_empty_text():
    assert extract_phrases("one two three") == ["one two three"]
    assert extract_phrases("   ") == []


def test_never_returns_short_tail_phrase():
    text = " ".join(f"w{i}" for i in range(12))  # second slot has only 2 words
    for seed in range(20):
        assert all(len(p.split()) >= 5 for p in extract_phrases(text, rng=random.Random(seed)))
