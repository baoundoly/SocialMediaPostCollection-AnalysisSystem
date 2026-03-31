# SocialMediaPostCollection-AnalysisSystem

Social Media Post Collection and Analysis System with Bangla + English NLP support.

## NLP Analysis Module

The `src/nlp` package provides end-to-end natural-language processing for social-media
posts written in **Bangla (Bengali)**, **English**, or a **mix of both**.

### Features

| Feature | English | Bangla | Mixed |
|---------|---------|--------|-------|
| Language detection | ✅ | ✅ | ✅ |
| Text cleaning (URLs, mentions, hashtags, HTML) | ✅ | ✅ | ✅ |
| Tokenisation & stop-word removal | ✅ | ✅ | ✅ |
| Sentiment analysis | ✅ VADER | ✅ Lexicon | ✅ Blended |
| Keyword extraction (frequency) | ✅ | ✅ | ✅ |
| Corpus-level TF-IDF keywords | ✅ | ✅ | ✅ |
| Post statistics | ✅ | ✅ | ✅ |

### Module structure

```
src/nlp/
├── __init__.py          # Public re-exports
├── analyzer.py          # PostAnalyzer – main orchestrator
├── language_detector.py # Script-based Bangla / English / mixed detection
├── preprocessor.py      # Cleaning, tokenisation, stop-word removal
├── sentiment_analyzer.py# VADER (English) + lexicon-based (Bangla)
└── keyword_extractor.py # Frequency & TF-IDF keyword extraction
```

### Quick start

```python
from nlp import PostAnalyzer

analyzer = PostAnalyzer()

# Single post
result = analyzer.analyze("This product is absolutely amazing! #great @user")
print(result["language"])          # "en"
print(result["sentiment"]["label"])# "positive"
print(result["keywords"][:3])      # [('amazing', 1.0), ('product', 0.5), ...]
print(result["stats"])
# {'char_count': 47, 'word_count': 7, 'token_count': 3,
#  'url_count': 0, 'mention_count': 1, 'hashtag_count': 1}

# Bangla post
result = analyzer.analyze("এটি অসাধারণ একটি দিন")
print(result["language"])          # "bn"
print(result["sentiment"]["label"])# "positive"

# Corpus analysis
posts = [
    "This is a great product!",
    "আমি এই পণ্যটি পছন্দ করি",
    "The service was disappointing",
]
report = analyzer.analyze_corpus(posts)
print(report["sentiment_counts"])  # {'positive': 2, 'negative': 1, 'neutral': 0}
print(report["avg_sentiment_score"])
print(report["top_keywords"])
```

### Installation

```bash
pip install -r requirements.txt
```

### Running tests

```bash
pytest tests/
```
