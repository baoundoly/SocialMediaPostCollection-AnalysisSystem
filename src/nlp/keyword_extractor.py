"""
Keyword extraction for Bangla and English social-media posts.

Two complementary strategies are used:

- **Frequency-based** (default): rank tokens by term frequency after
  stop-word removal.  Works well for single posts or small collections.

- **TF-IDF-based**: rank tokens across a *corpus* of posts so that
  words appearing in many posts receive lower weight (removes corpus-level
  noise).  Requires at least two documents.

Both strategies return a list of ``(keyword, score)`` tuples, sorted
descending by score, capped to *top_n* results.
"""

from __future__ import annotations

from collections import Counter
from math import log

from .preprocessor import TextPreprocessor

_preprocessor = TextPreprocessor()


class KeywordExtractor:
    """Extract the most relevant keywords from one or more posts."""

    # ------------------------------------------------------------------
    # Single-document extraction
    # ------------------------------------------------------------------

    def extract(
        self,
        text: str,
        language: str,
        top_n: int = 10,
    ) -> list[tuple[str, float]]:
        """Return the top *top_n* keywords from a single *text*.

        Parameters
        ----------
        text:
            Raw post text.
        language:
            Language code (``"bn"``, ``"en"``, or ``"mixed"``).
        top_n:
            Maximum number of keywords to return.

        Returns
        -------
        list of (keyword, score) tuples
            Score is normalised term frequency in ``[0, 1]``.
        """
        tokens = _preprocessor.tokenize(text, language)
        if not tokens:
            return []
        counts = Counter(tokens)
        max_freq = counts.most_common(1)[0][1]
        return [
            (word, round(freq / max_freq, 4))
            for word, freq in counts.most_common(top_n)
        ]

    # ------------------------------------------------------------------
    # Corpus-level extraction (TF-IDF)
    # ------------------------------------------------------------------

    def extract_from_corpus(
        self,
        texts: list[str],
        language: str,
        top_n: int = 10,
    ) -> list[tuple[str, float]]:
        """Return the top *top_n* keywords across a *corpus* of texts using
        TF-IDF scoring.

        Parameters
        ----------
        texts:
            List of raw post texts.
        language:
            Language code shared by the texts (or ``"mixed"``).
        top_n:
            Maximum number of keywords to return.

        Returns
        -------
        list of (keyword, score) tuples
            Score is the aggregated TF-IDF weight.
        """
        if not texts:
            return []

        # Tokenise each document
        tokenised = [_preprocessor.tokenize(t, language) for t in texts]
        num_docs = len(tokenised)

        # Build document-frequency table
        df: Counter[str] = Counter()
        for doc in tokenised:
            for word in set(doc):
                df[word] += 1

        # Aggregate TF-IDF scores across the corpus
        tfidf_scores: Counter[str] = Counter()
        for doc in tokenised:
            if not doc:
                continue
            doc_len = len(doc)
            tf_counts = Counter(doc)
            for word, count in tf_counts.items():
                tf = count / doc_len
                idf = log((num_docs + 1) / (df[word] + 1)) + 1.0
                tfidf_scores[word] += tf * idf

        if not tfidf_scores:
            return []

        # Normalise by max score so values are in (0, 1]
        max_score = tfidf_scores.most_common(1)[0][1]
        return [
            (word, round(score / max_score, 4))
            for word, score in tfidf_scores.most_common(top_n)
        ]
