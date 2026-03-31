"""
Language detection for Bangla and English text.

Supports three outcomes:
  - "bn"    : Bangla (Bengali)
  - "en"    : English
  - "mixed" : Text containing both Bangla and English characters
"""

import re

# Unicode block for Bangla script: U+0980 – U+09FF
_BANGLA_PATTERN = re.compile(r"[\u0980-\u09FF]")
# Basic Latin letters used for English / romanised text
_LATIN_PATTERN = re.compile(r"[A-Za-z]")

# Minimum fraction of script-specific characters required to classify a
# document as belonging to that language.
_SCRIPT_THRESHOLD = 0.15


class LanguageDetector:
    """Detect whether a social-media post is written in Bangla, English, or
    a mixture of both.

    Detection is script-based (no external model required) so it works
    entirely offline and is not affected by short, informal text that
    confuses statistical language models.
    """

    def detect(self, text: str) -> str:
        """Return the dominant language label for *text*.

        Parameters
        ----------
        text:
            Raw post text.

        Returns
        -------
        str
            ``"bn"`` for Bangla, ``"en"`` for English, ``"mixed"`` when
            both scripts are present above the threshold, or ``"unknown"``
            when the text contains neither.
        """
        if not text or not text.strip():
            return "unknown"

        # Count only alphabetic / script characters so that numbers,
        # punctuation and whitespace do not skew the ratio.
        bangla_chars = len(_BANGLA_PATTERN.findall(text))
        latin_chars = len(_LATIN_PATTERN.findall(text))
        total = bangla_chars + latin_chars

        if total == 0:
            return "unknown"

        bangla_ratio = bangla_chars / total
        latin_ratio = latin_chars / total

        has_bangla = bangla_ratio >= _SCRIPT_THRESHOLD
        has_latin = latin_ratio >= _SCRIPT_THRESHOLD

        if has_bangla and has_latin:
            return "mixed"
        if has_bangla:
            return "bn"
        if has_latin:
            return "en"
        return "unknown"

    def is_bangla(self, text: str) -> bool:
        """Return ``True`` when *text* is classified as Bangla-only."""
        return self.detect(text) == "bn"

    def is_english(self, text: str) -> bool:
        """Return ``True`` when *text* is classified as English-only."""
        return self.detect(text) == "en"

    def is_mixed(self, text: str) -> bool:
        """Return ``True`` when *text* contains both Bangla and English."""
        return self.detect(text) == "mixed"
