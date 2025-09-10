"""Heuristic keyword extractor for noun-like tokens.

This module defines a simple approach for extracting the top three
candidate keywords from unstructured text without relying on heavy
external NLP libraries. The algorithm tokenizes on alphabetic words
only, removes a small stopword list and a curated list of common
verbs, then scores tokens based on frequency, capitalization, and
length. Results are deterministic and suitable for small articles
where approximate noun extraction suffices.
"""

import re
from collections import Counter
from typing import List


_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when",
    "while", "for", "on", "in", "to", "of", "by", "with", "as", "at",
    "from", "that", "this", "these", "those", "it", "its", "be", "is",
    "are", "was", "were", "been", "being", "am", "i", "you", "he",
    "she", "they", "them", "we", "us", "our", "your", "his", "her",
    "their", "my", "mine", "yours", "ours", "theirs", "do", "does",
    "did", "done", "have", "has", "had", "having", "will", "would",
    "can", "could", "should", "shall", "may", "might", "must", "not",
    "no", "yes", "so", "than", "too", "very", "there", "here", "what",
    "which", "who", "whom", "whose", "how", "why", "where", "into",
    "over", "under", "again", "further", "once", "about", "both",
    "between", "out", "up", "down", "off", "above", "below", "because",
    "until", "after", "before", "during", "each", "few", "more", "most",
    "other", "some", "such", "only", "own", "same", "s", "t", "d",
    "ll", "m", "o", "re", "ve", "y", "don", "shouldn", "now",
}


_COMMON_VERBS = {
    "use", "build", "create", "make", "run", "scale", "deploy",
    "call", "send", "fetch", "return", "process", "analyze",
    "extract", "store", "search", "handle", "test", "containerize",
    "support", "add", "include", "design", "choose", "implement",
    "prefer", "focus", "integrate", "accept", "provide", "generate",
    "score", "classify", "view",
}


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']+")


def extract_top3_nouns_like(text: str) -> List[str]:
    """Extract up to three frequent noun-like tokens from the text.

    The function tokenizes the input, strips possessive markers,
    removes stopwords and common verbs, and computes a frequency-based
    ranking. It adds small bonuses for tokens that appear capitalized in
    the original text (likely proper nouns) and for longer tokens. The
    top three unique tokens are returned.

    Parameters
    ----------
    text : str
        The input string from which to extract keywords.

    Returns
    -------
    List[str]
        A list containing at most three keyword candidates. The list
        may be empty if no suitable tokens are found.
    """
    if not text or not text.strip():
        return []

    tokens = _WORD_RE.findall(text)
    if not tokens:
        return []

    cleaned: list[str] = []
    for tok in tokens:
        base = tok.lower().rstrip("'").rstrip("’")
        if base.endswith("'s") or base.endswith("’s"):
            base = base[:-2]
        if base in _STOPWORDS or base in _COMMON_VERBS or len(base) < 3:
            continue
        cleaned.append(base)

    if not cleaned:
        return []

    caps = {tok.lower() for tok in tokens if tok[:1].isupper() and tok[1:].islower()}
    counts = Counter(cleaned)
    scored: list[tuple[str, float, int]] = []
    for word, freq in counts.items():
        bonus = 0.25 if word in caps else 0.0
        length_bonus = 0.10 if len(word) >= 7 else 0.0
        score = freq + bonus + length_bonus
        scored.append((word, score, freq))

    scored.sort(key=lambda x: (-x[1], -x[2], x[0]))
    top: list[str] = []
    for w, _, _ in scored:
        if w not in top:
            top.append(w)
        if len(top) == 3:
            break
    return top