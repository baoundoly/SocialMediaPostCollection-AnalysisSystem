"""
Sentiment analysis for Bangla and English social-media posts.

Strategy
--------
- **English**: NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner),
  which is specifically designed for social-media text and handles slang,
  emoticons, and punctuation emphasis.

- **Bangla**: Lexicon-based scoring using a hand-curated dictionary of common
  positive and negative Bangla words.  The final label maps the normalised
  score to ``"positive"``, ``"negative"``, or ``"neutral"``.

Both analysers return a unified result dict::

    {
        "label":    "positive" | "negative" | "neutral",
        "score":    float in [-1.0, 1.0],
        "language": "bn" | "en" | "mixed",
    }
"""

from __future__ import annotations

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# ---------------------------------------------------------------------------
# Lazy initialisation (same strategy as preprocessor – avoid calling
# nltk.download at import time to mitigate NLTK downloader path-traversal).
# ---------------------------------------------------------------------------
_VADER_READY = False
_vader: SentimentIntensityAnalyzer | None = None


def _ensure_vader() -> SentimentIntensityAnalyzer:
    global _VADER_READY, _vader
    if not _VADER_READY:
        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)
        _vader = SentimentIntensityAnalyzer()
        _VADER_READY = True
    return _vader  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Bangla lexicon
# ---------------------------------------------------------------------------
# Positive words with approximate intensity scores in (0, 1]
BANGLA_POSITIVE_WORDS: dict[str, float] = {
    "ভালো": 0.6, "ভালোবাসা": 0.9, "সুন্দর": 0.7, "অসাধারণ": 0.9,
    "দারুণ": 0.8, "চমৎকার": 0.85, "খুশি": 0.75, "আনন্দ": 0.8,
    "সফল": 0.7, "উত্তম": 0.65, "প্রিয়": 0.7, "মজা": 0.65,
    "বন্ধু": 0.5, "ধন্যবাদ": 0.6, "শান্তি": 0.7, "আশা": 0.6,
    "প্রেম": 0.85, "হাসি": 0.7, "সেরা": 0.85, "অভূতপূর্ব": 0.9,
    "অপূর্ব": 0.85, "মনোরম": 0.75, "উপকারী": 0.65, "চমকপ্রদ": 0.8,
    "স্বাস্থ্যকর": 0.6, "উৎসাহ": 0.7, "বিজয়": 0.8, "সম্মান": 0.65,
    "সঠিক": 0.55, "পছন্দ": 0.6, "অর্জন": 0.7, "সহযোগিতা": 0.6,
}

# Negative words with approximate intensity scores in (0, 1]
BANGLA_NEGATIVE_WORDS: dict[str, float] = {
    "খারাপ": 0.6, "দুঃখ": 0.7, "কষ্ট": 0.65, "বিপদ": 0.7,
    "রাগ": 0.65, "ঘৃণা": 0.85, "ভয়": 0.7, "সমস্যা": 0.55,
    "ব্যর্থ": 0.7, "ক্ষতি": 0.65, "অসুখ": 0.7, "মৃত্যু": 0.85,
    "দুর্নীতি": 0.8, "অন্যায়": 0.75, "নিষ্ঠুর": 0.85, "ভয়ংকর": 0.85,
    "দুর্বল": 0.5, "বিরক্ত": 0.6, "ক্ষোভ": 0.7, "হতাশ": 0.65,
    "নিষেধ": 0.5, "কান্না": 0.65, "অভিযোগ": 0.6, "দোষ": 0.6,
    "লজ্জা": 0.6, "অপমান": 0.75, "অবমাননা": 0.8, "বেদনা": 0.7,
    "আঘাত": 0.7, "ব্যথা": 0.65, "ক্লান্ত": 0.5, "বিপর্যয়": 0.85,
}

# Intensifiers that amplify the score of the following token
BANGLA_INTENSIFIERS: dict[str, float] = {
    "খুব": 1.4, "অনেক": 1.3, "অত্যন্ত": 1.5, "একদম": 1.4,
    "সত্যিই": 1.3, "সবচেয়ে": 1.5,
}

# Negation words that flip the polarity of the next sentiment token
BANGLA_NEGATIONS: set[str] = {"না", "নয়", "নেই", "নি", "কখনো না"}


class SentimentAnalyzer:
    """Analyse the sentiment of Bangla and English text."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, text: str, language: str) -> dict:
        """Return a sentiment result dict for *text*.

        Parameters
        ----------
        text:
            Raw or pre-cleaned post text.
        language:
            Language code returned by :class:`~nlp.language_detector.LanguageDetector`.
            Use ``"bn"`` for Bangla, ``"en"`` for English, ``"mixed"`` for
            code-switched text.

        Returns
        -------
        dict
            Keys: ``label`` (str), ``score`` (float), ``language`` (str).
        """
        if language == "en":
            return self._analyze_english(text)
        if language == "bn":
            return self._analyze_bangla(text)
        # mixed: blend both scores
        return self._analyze_mixed(text)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _analyze_english(self, text: str) -> dict:
        vader = _ensure_vader()
        scores = vader.polarity_scores(text)
        compound = scores["compound"]
        label = self._compound_to_label(compound)
        return {"label": label, "score": round(compound, 4), "language": "en"}

    def _analyze_bangla(self, text: str) -> dict:
        tokens = text.split()
        score = 0.0
        negate_next = False
        intensifier = 1.0

        for token in tokens:
            token_clean = token.strip("।,;:!?")
            if token_clean in BANGLA_NEGATIONS:
                negate_next = True
                continue
            if token_clean in BANGLA_INTENSIFIERS:
                intensifier = BANGLA_INTENSIFIERS[token_clean]
                continue

            if token_clean in BANGLA_POSITIVE_WORDS:
                val = BANGLA_POSITIVE_WORDS[token_clean] * intensifier
                score += -val if negate_next else val
            elif token_clean in BANGLA_NEGATIVE_WORDS:
                val = BANGLA_NEGATIVE_WORDS[token_clean] * intensifier
                score += val if negate_next else -val

            negate_next = False
            intensifier = 1.0

        # Normalise score to [-1, 1]
        word_count = max(len(tokens), 1)
        normalised = max(-1.0, min(1.0, score / word_count))
        label = self._compound_to_label(normalised)
        return {"label": label, "score": round(normalised, 4), "language": "bn"}

    def _analyze_mixed(self, text: str) -> dict:
        en_result = self._analyze_english(text)
        bn_result = self._analyze_bangla(text)
        blended = (en_result["score"] + bn_result["score"]) / 2
        label = self._compound_to_label(blended)
        return {"label": label, "score": round(blended, 4), "language": "mixed"}

    @staticmethod
    def _compound_to_label(compound: float) -> str:
        if compound >= 0.05:
            return "positive"
        if compound <= -0.05:
            return "negative"
        return "neutral"
