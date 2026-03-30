from typing import Tuple

def analyze_sentiment(text: str) -> Tuple[str, float]:
    if not text or not text.strip(): return "neutral", 0.0
    try:
        from textblob import TextBlob
        score = TextBlob(text).sentiment.polarity
        label = "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"
        return label, round(score, 4)
    except Exception:
        return "neutral", 0.0
