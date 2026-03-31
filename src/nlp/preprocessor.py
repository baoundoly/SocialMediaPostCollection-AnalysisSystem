"""
Text preprocessing for Bangla and English social-media posts.

Cleaning steps applied to *all* languages:
  1. Strip URLs, @mentions, and #hashtags (social-media noise).
  2. Remove HTML entities and tags.
  3. Collapse repeated whitespace.

Additional language-specific steps:
  - English: lower-case, remove punctuation, remove stop-words, tokenise.
  - Bangla : normalise Unicode (canonical NFC form), remove punctuation,
             remove Bangla stop-words, tokenise.
"""

import re
import unicodedata

import nltk
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import word_tokenize

# ---------------------------------------------------------------------------
# NLTK data – download quietly only when the corpus is missing.
# NOTE: we intentionally avoid calling nltk.download() at module import time
# to mitigate the path-traversal risk in NLTK's downloader. The helper below
# is called lazily the first time a method that needs the data is invoked.
# ---------------------------------------------------------------------------
_NLTK_READY = False


def _ensure_nltk_data() -> None:
    global _NLTK_READY
    if _NLTK_READY:
        return
    for resource, path in [
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
    ]:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(path, quiet=True)
    _NLTK_READY = True


# ---------------------------------------------------------------------------
# Bangla stop-words (hand-curated, common function words)
# ---------------------------------------------------------------------------
BANGLA_STOPWORDS: set[str] = {
    "আমি", "আমার", "আমাকে", "আমরা", "আমাদের",
    "তুমি", "তোমার", "তোমাকে", "তোমরা", "তোমাদের",
    "আপনি", "আপনার", "আপনাকে", "আপনারা", "আপনাদের",
    "সে", "তার", "তাকে", "তারা", "তাদের",
    "এ", "এই", "এটা", "এটি", "এখানে", "এখন",
    "ও", "এবং", "বা", "কিন্তু", "তবে", "যদি", "তাহলে",
    "না", "নয়", "নেই", "নি",
    "হয়", "হয়েছে", "হয়েছিল", "হবে", "হচ্ছে",
    "আছে", "আছি", "আছেন", "ছিল", "ছিলাম", "ছিলেন",
    "করা", "করে", "করেছে", "করেছিল", "করবে", "করছে",
    "যে", "যা", "যার", "যাকে", "যারা", "যাদের",
    "কি", "কী", "কেন", "কীভাবে", "কোথায়", "কখন",
    "থেকে", "দিয়ে", "জন্য", "পর্যন্ত", "সাথে", "মধ্যে",
    "একটি", "একটা", "একজন", "কোনো", "সব", "সকল",
    "তো", "ও", "আর", "হলো", "হল",
}

# Punctuation to strip from tokens (extends ASCII punctuation with common
# Unicode punctuation used in Bangla writing)
_BANGLA_PUNCT = re.compile(
    r"[।॥,;:!?\.\"\'\(\)\[\]\{\}\-–—/\\|@#$%^&*+=<>`~]"
)

# Shared patterns
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#(\w+)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HTML_ENTITY_RE = re.compile(r"&[a-zA-Z]+;|&#\d+;")
_WHITESPACE_RE = re.compile(r"\s+")


class TextPreprocessor:
    """Clean and tokenise text for NLP tasks."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def clean(self, text: str) -> str:
        """Return *text* after removing social-media noise (URLs, mentions,
        hashtag symbols, HTML) and collapsing whitespace.

        The returned string retains all script characters so it can be
        inspected by the language detector or fed to further processors.
        """
        text = _HTML_TAG_RE.sub(" ", text)
        text = _HTML_ENTITY_RE.sub(" ", text)
        text = _URL_RE.sub(" ", text)
        text = _MENTION_RE.sub(" ", text)
        # Keep the hashtag word, strip the '#' prefix
        text = _HASHTAG_RE.sub(r"\1", text)
        text = _WHITESPACE_RE.sub(" ", text)
        return text.strip()

    def tokenize_english(self, text: str) -> list[str]:
        """Return lower-cased, stop-word-free English tokens from *text*."""
        _ensure_nltk_data()
        text = self.clean(text).lower()
        tokens = word_tokenize(text)
        en_stops = set(nltk_stopwords.words("english"))
        return [
            t for t in tokens
            if t.isalpha() and t not in en_stops and len(t) > 1
        ]

    def tokenize_bangla(self, text: str) -> list[str]:
        """Return stop-word-free Bangla tokens from *text*.

        Tokenisation is whitespace-based after punctuation removal, which is
        appropriate for Bangla text that is naturally space-delimited.
        """
        text = unicodedata.normalize("NFC", self.clean(text))
        text = _BANGLA_PUNCT.sub(" ", text)
        tokens = _WHITESPACE_RE.sub(" ", text).split()
        return [
            t for t in tokens
            if t and t not in BANGLA_STOPWORDS and len(t) > 1
        ]

    def tokenize(self, text: str, language: str) -> list[str]:
        """Dispatch to the language-specific tokeniser.

        Parameters
        ----------
        text:
            Raw post text.
        language:
            ``"bn"``, ``"en"``, or ``"mixed"``.  For mixed text both
            tokenisers are applied and their results merged (deduped, order
            preserved).
        """
        if language == "bn":
            return self.tokenize_bangla(text)
        if language == "en":
            return self.tokenize_english(text)
        # mixed: apply both and return combined unique tokens
        bn_tokens = self.tokenize_bangla(text)
        en_tokens = self.tokenize_english(text)
        seen: set[str] = set()
        result: list[str] = []
        for token in bn_tokens + en_tokens:
            if token not in seen:
                seen.add(token)
                result.append(token)
        return result
