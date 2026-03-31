from typing import List, Tuple
import re

STOPWORDS = {"the","a","an","and","or","but","in","on","at","to","for","of","with","by","from","is","are","was","were","be","been","being","have","has","had","do","does","did","will","would","could","should","may","might","must","shall","can","need","this","that","these","those","it","its","i","me","my","we","our","you","your","he","she","they","their","them","us","not","no","so","if","as","up","out","about","into"}

def extract_keywords(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    if not text or not text.strip(): return []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(max_features=top_n*2, stop_words="english", ngram_range=(1,2), min_df=1)
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        kw_scores = sorted([(feature_names[i], scores[i]) for i in range(len(feature_names)) if scores[i] > 0], key=lambda x: x[1], reverse=True)
        return kw_scores[:top_n]
    except Exception:
        return _fallback_keywords(text, top_n)

def _fallback_keywords(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    freq = {}
    for word in words:
        if word not in STOPWORDS: freq[word] = freq.get(word, 0) + 1
    total = max(sum(freq.values()), 1)
    return [(kw, round(count/total, 4)) for kw, count in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]]
