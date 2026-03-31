"""
Main orchestrator for the Bangla + English NLP analysis module.

``PostAnalyzer`` is the single entry point that most consumers will use.
It bundles language detection, text preprocessing, sentiment analysis, and
keyword extraction into one convenient call.

Example
-------
>>> from nlp import PostAnalyzer
>>> analyzer = PostAnalyzer()
>>> result = analyzer.analyze("This product is absolutely amazing!")
>>> result["sentiment"]["label"]
'positive'
"""

from __future__ import annotations

import re

from .keyword_extractor import KeywordExtractor
from .language_detector import LanguageDetector
from .preprocessor import TextPreprocessor
from .sentiment_analyzer import SentimentAnalyzer

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_WORD_RE = re.compile(r"#(\w+)")


class PostAnalyzer:
    """Analyse a social-media post (Bangla, English, or mixed).

    Attributes
    ----------
    detector:
        :class:`~nlp.language_detector.LanguageDetector` instance.
    preprocessor:
        :class:`~nlp.preprocessor.TextPreprocessor` instance.
    sentiment_analyzer:
        :class:`~nlp.sentiment_analyzer.SentimentAnalyzer` instance.
    keyword_extractor:
        :class:`~nlp.keyword_extractor.KeywordExtractor` instance.
    """

    def __init__(self) -> None:
        self.detector = LanguageDetector()
        self.preprocessor = TextPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.keyword_extractor = KeywordExtractor()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, text: str, top_keywords: int = 10) -> dict:
        """Perform a full NLP analysis of a single post.

        Parameters
        ----------
        text:
            Raw post text (URLs, mentions, hashtags accepted).
        top_keywords:
            How many top keywords to include in the result.

        Returns
        -------
        dict with keys:
            - ``language``   : detected language code.
            - ``cleaned``    : text after noise removal.
            - ``tokens``     : list of meaningful tokens.
            - ``sentiment``  : dict with ``label``, ``score``, ``language``.
            - ``keywords``   : list of ``(keyword, score)`` tuples.
            - ``stats``      : basic text statistics dict.
        """
        language = self.detector.detect(text)
        cleaned = self.preprocessor.clean(text)
        tokens = self.preprocessor.tokenize(cleaned, language)
        sentiment = self.sentiment_analyzer.analyze(cleaned, language)
        keywords = self.keyword_extractor.extract(cleaned, language, top_n=top_keywords)
        stats = self._compute_stats(text, cleaned, tokens)

        return {
            "language": language,
            "cleaned": cleaned,
            "tokens": tokens,
            "sentiment": sentiment,
            "keywords": keywords,
            "stats": stats,
        }

    def analyze_corpus(
        self,
        texts: list[str],
        top_keywords: int = 20,
    ) -> dict:
        """Analyse a collection of posts and return an aggregate report.

        Parameters
        ----------
        texts:
            List of raw post texts.
        top_keywords:
            How many corpus-level keywords to surface.

        Returns
        -------
        dict with keys:
            - ``total``              : total number of posts.
            - ``language_counts``    : breakdown of detected languages.
            - ``sentiment_counts``   : count of positive / negative / neutral.
            - ``avg_sentiment_score``: mean compound score across the corpus.
            - ``top_keywords``       : corpus-level TF-IDF keywords.
            - ``posts``              : list of per-post analysis dicts.
        """
        posts = [self.analyze(t) for t in texts]

        language_counts: dict[str, int] = {}
        sentiment_counts: dict[str, int] = {"positive": 0, "negative": 0, "neutral": 0}
        total_score = 0.0

        for post in posts:
            lang = post["language"]
            language_counts[lang] = language_counts.get(lang, 0) + 1
            sentiment_counts[post["sentiment"]["label"]] += 1
            total_score += post["sentiment"]["score"]

        avg_score = round(total_score / len(posts), 4) if posts else 0.0

        # Determine the dominant language for corpus-level keyword extraction
        dominant_lang = max(language_counts, key=lambda k: language_counts[k]) if language_counts else "en"
        corpus_keywords = self.keyword_extractor.extract_from_corpus(
            texts, dominant_lang, top_n=top_keywords
        )

        return {
            "total": len(posts),
            "language_counts": language_counts,
            "sentiment_counts": sentiment_counts,
            "avg_sentiment_score": avg_score,
            "top_keywords": corpus_keywords,
            "posts": posts,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_stats(raw: str, cleaned: str, tokens: list[str]) -> dict:
        """Return basic statistics about the post."""
        words = cleaned.split()
        urls = len(_URL_RE.findall(raw))
        mentions = len(_MENTION_RE.findall(raw))
        hashtags = len(_HASHTAG_WORD_RE.findall(raw))
        return {
            "char_count": len(raw),
            "word_count": len(words),
            "token_count": len(tokens),
            "url_count": urls,
            "mention_count": mentions,
            "hashtag_count": hashtags,
        }
