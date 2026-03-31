"""
Tests for the Bangla + English NLP analysis module.

Run with:
    pytest tests/
"""

import sys
import os

# Allow importing from src/ without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from nlp.language_detector import LanguageDetector
from nlp.preprocessor import TextPreprocessor
from nlp.sentiment_analyzer import SentimentAnalyzer
from nlp.keyword_extractor import KeywordExtractor
from nlp.analyzer import PostAnalyzer


# ---------------------------------------------------------------------------
# LanguageDetector
# ---------------------------------------------------------------------------

class TestLanguageDetector:
    def setup_method(self):
        self.detector = LanguageDetector()

    def test_detects_english(self):
        assert self.detector.detect("Hello world this is a simple English sentence") == "en"

    def test_detects_bangla(self):
        assert self.detector.detect("এটি একটি বাংলা বাক্য") == "bn"

    def test_detects_mixed(self):
        # Contains both Bangla and enough Latin characters
        assert self.detector.detect("আমি Python programming শিখছি") == "mixed"

    def test_empty_text_returns_unknown(self):
        assert self.detector.detect("") == "unknown"
        assert self.detector.detect("   ") == "unknown"

    def test_numbers_only_returns_unknown(self):
        assert self.detector.detect("12345 6789") == "unknown"

    def test_is_bangla_helper(self):
        assert self.detector.is_bangla("বাংলা ভাষা সুন্দর")
        assert not self.detector.is_bangla("Hello world")

    def test_is_english_helper(self):
        assert self.detector.is_english("This is English text")
        assert not self.detector.is_english("বাংলা বাক্য")

    def test_is_mixed_helper(self):
        assert self.detector.is_mixed("বাংলা text mixed")


# ---------------------------------------------------------------------------
# TextPreprocessor
# ---------------------------------------------------------------------------

class TestTextPreprocessor:
    def setup_method(self):
        self.preprocessor = TextPreprocessor()

    def test_clean_removes_url(self):
        result = self.preprocessor.clean("Check this out https://example.com today")
        assert "https://" not in result
        assert "example.com" not in result

    def test_clean_removes_mention(self):
        result = self.preprocessor.clean("Hey @username how are you?")
        assert "@username" not in result

    def test_clean_keeps_hashtag_word(self):
        result = self.preprocessor.clean("Love #Python programming")
        assert "Python" in result
        assert "#" not in result

    def test_clean_removes_html(self):
        result = self.preprocessor.clean("<b>Bold</b> text &amp; more")
        assert "<b>" not in result
        assert "&amp;" not in result
        assert "Bold" in result

    def test_tokenize_english_removes_stopwords(self):
        tokens = self.preprocessor.tokenize_english("This is a very good product")
        assert "this" not in tokens
        assert "is" not in tokens
        assert "good" in tokens
        assert "product" in tokens

    def test_tokenize_english_returns_lowercase(self):
        tokens = self.preprocessor.tokenize_english("Hello World")
        assert all(t == t.lower() for t in tokens)

    def test_tokenize_bangla_removes_stopwords(self):
        tokens = self.preprocessor.tokenize_bangla("এটি একটি সুন্দর দিন")
        # "এটি" and "একটি" are stop-words
        assert "এটি" not in tokens
        assert "একটি" not in tokens
        assert "সুন্দর" in tokens

    def test_tokenize_mixed_returns_both_scripts(self):
        tokens = self.preprocessor.tokenize("আমি Python শিখছি", "mixed")
        has_bangla = any("\u0980" <= c <= "\u09FF" for t in tokens for c in t)
        has_latin = any(c.isascii() and c.isalpha() for t in tokens for c in t)
        assert has_bangla
        assert has_latin

    def test_tokenize_dispatch_en(self):
        tokens = self.preprocessor.tokenize("hello world", "en")
        assert isinstance(tokens, list)

    def test_tokenize_dispatch_bn(self):
        tokens = self.preprocessor.tokenize("সুন্দর দিন", "bn")
        assert isinstance(tokens, list)


# ---------------------------------------------------------------------------
# SentimentAnalyzer
# ---------------------------------------------------------------------------

class TestSentimentAnalyzer:
    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    # English
    def test_english_positive(self):
        result = self.analyzer.analyze("I love this! It is absolutely amazing.", "en")
        assert result["label"] == "positive"
        assert result["score"] > 0
        assert result["language"] == "en"

    def test_english_negative(self):
        result = self.analyzer.analyze("This is terrible and awful.", "en")
        assert result["label"] == "negative"
        assert result["score"] < 0
        assert result["language"] == "en"

    def test_english_neutral(self):
        result = self.analyzer.analyze("The product arrived on Tuesday.", "en")
        assert result["label"] == "neutral"
        assert result["language"] == "en"

    # Bangla
    def test_bangla_positive(self):
        result = self.analyzer.analyze("এটি খুব সুন্দর এবং অসাধারণ", "bn")
        assert result["label"] == "positive"
        assert result["score"] > 0
        assert result["language"] == "bn"

    def test_bangla_negative(self):
        result = self.analyzer.analyze("এটি খুব খারাপ এবং দুঃখজনক", "bn")
        assert result["label"] == "negative"
        assert result["score"] < 0
        assert result["language"] == "bn"

    def test_bangla_negation_flips_positive(self):
        # "না সুন্দর" should be negative
        result = self.analyzer.analyze("না সুন্দর", "bn")
        assert result["label"] in ("negative", "neutral")

    # Mixed
    def test_mixed_returns_mixed_language(self):
        result = self.analyzer.analyze("ভালো product আমি love করি", "mixed")
        assert result["language"] == "mixed"
        assert "label" in result
        assert "score" in result

    def test_result_score_in_range(self):
        for lang, text in [
            ("en", "Absolutely fantastic!!!"),
            ("bn", "অসাধারণ সুন্দর ভালোবাসা"),
        ]:
            result = self.analyzer.analyze(text, lang)
            assert -1.0 <= result["score"] <= 1.0


# ---------------------------------------------------------------------------
# KeywordExtractor
# ---------------------------------------------------------------------------

class TestKeywordExtractor:
    def setup_method(self):
        self.extractor = KeywordExtractor()

    def test_extract_english_returns_keywords(self):
        text = "machine learning is transforming the world machine learning algorithms"
        keywords = self.extractor.extract(text, "en")
        assert len(keywords) > 0
        words = [kw for kw, _ in keywords]
        assert "machine" in words or "learning" in words

    def test_extract_bangla_returns_keywords(self):
        text = "বাংলা ভাষা বাংলাদেশের জাতীয় ভাষা"
        keywords = self.extractor.extract(text, "bn")
        assert len(keywords) > 0

    def test_extract_top_n_respected(self):
        text = "one two three four five six seven eight nine ten"
        keywords = self.extractor.extract(text, "en", top_n=3)
        assert len(keywords) <= 3

    def test_extract_scores_in_range(self):
        text = "good good good bad"
        keywords = self.extractor.extract(text, "en")
        for _, score in keywords:
            assert 0.0 < score <= 1.0

    def test_extract_empty_text_returns_empty(self):
        assert self.extractor.extract("", "en") == []

    def test_extract_from_corpus(self):
        corpus = [
            "machine learning is amazing",
            "deep learning neural networks",
            "machine learning neural networks are powerful",
        ]
        keywords = self.extractor.extract_from_corpus(corpus, "en", top_n=5)
        assert len(keywords) > 0
        words = [kw for kw, _ in keywords]
        assert "machine" in words or "learning" in words or "neural" in words

    def test_extract_from_empty_corpus(self):
        assert self.extractor.extract_from_corpus([], "en") == []

    def test_corpus_scores_in_range(self):
        corpus = ["great product", "amazing product", "wonderful product"]
        keywords = self.extractor.extract_from_corpus(corpus, "en")
        for _, score in keywords:
            assert 0.0 < score <= 1.0


# ---------------------------------------------------------------------------
# PostAnalyzer (integration)
# ---------------------------------------------------------------------------

class TestPostAnalyzer:
    def setup_method(self):
        self.analyzer = PostAnalyzer()

    def test_analyze_english_post(self):
        result = self.analyzer.analyze("I love this amazing product! #great @user https://example.com")
        assert result["language"] == "en"
        assert result["sentiment"]["label"] == "positive"
        assert "https://" not in result["cleaned"]
        assert isinstance(result["keywords"], list)
        assert result["stats"]["url_count"] == 1
        assert result["stats"]["mention_count"] == 1
        assert result["stats"]["hashtag_count"] == 1

    def test_analyze_bangla_post(self):
        result = self.analyzer.analyze("এটি অসাধারণ একটি দিন আজকে")
        assert result["language"] == "bn"
        assert isinstance(result["tokens"], list)
        assert isinstance(result["keywords"], list)

    def test_analyze_returns_required_keys(self):
        result = self.analyzer.analyze("test post")
        for key in ("language", "cleaned", "tokens", "sentiment", "keywords", "stats"):
            assert key in result

    def test_stats_structure(self):
        result = self.analyzer.analyze("Hello @user check https://example.com #cool")
        stats = result["stats"]
        for key in ("char_count", "word_count", "token_count", "url_count", "mention_count", "hashtag_count"):
            assert key in stats
        assert stats["url_count"] == 1
        assert stats["mention_count"] == 1
        assert stats["hashtag_count"] == 1

    def test_analyze_corpus(self):
        posts = [
            "This is a great product!",
            "আমি এই পণ্যটি পছন্দ করি",
            "The service was terrible and disappointing",
        ]
        report = self.analyzer.analyze_corpus(posts)
        assert report["total"] == 3
        assert "language_counts" in report
        assert "sentiment_counts" in report
        assert "avg_sentiment_score" in report
        assert "top_keywords" in report
        assert len(report["posts"]) == 3

    def test_corpus_sentiment_counts_sum_to_total(self):
        posts = ["great", "awful", "okay it was fine enough words here"]
        report = self.analyzer.analyze_corpus(posts)
        total_labels = sum(report["sentiment_counts"].values())
        assert total_labels == report["total"]

    def test_empty_corpus(self):
        report = self.analyzer.analyze_corpus([])
        assert report["total"] == 0
        assert report["posts"] == []
