from app.utils.sentiment import analyze_sentiment
from app.utils.keyword_extractor import extract_keywords
from app.utils.entity_extractor import extract_entities
from app.utils.text_cleaner import clean_text
from app.models.post import Post
from datetime import datetime

def test_clean_text():
    text = "Check this out! https://example.com #hashtag @mention <b>bold</b>"
    cleaned = clean_text(text)
    assert "http" not in cleaned
    assert "<b>" not in cleaned

def test_sentiment_positive():
    label, score = analyze_sentiment("This is absolutely wonderful and amazing!")
    assert label == "positive"
    assert score > 0

def test_sentiment_negative():
    label, score = analyze_sentiment("This is terrible and awful. I hate it.")
    assert label in ("negative", "neutral") and score <= 0

def test_sentiment_neutral():
    label, score = analyze_sentiment("The meeting is at 3pm today.")
    assert label == "neutral"

def test_sentiment_empty():
    label, score = analyze_sentiment("")
    assert label == "neutral" and score == 0.0

def test_keyword_extraction():
    keywords = extract_keywords("Machine learning and artificial intelligence are transforming technology industry")
    assert len(keywords) > 0
    assert all(isinstance(k, tuple) and len(k) == 2 for k in keywords)

def test_entity_extraction():
    entities = extract_entities("Mr. John Smith from Google visited New York for the conference.")
    types = [e[1] for e in entities]
    assert "PERSON" in types or "ORG" in types or "LOCATION" in types

def test_run_analysis_endpoint(client, auth_headers, db):
    post = Post(platform_id=1, external_post_id="analysis-test-001",
                content="This is a wonderful and positive test message about technology and innovation!",
                posted_at=datetime.utcnow(), likes_count=0)
    db.add(post); db.commit(); db.refresh(post)
    response = client.post(f"/api/analysis/run/{post.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == post.id
    assert data["sentiment_label"] in ("positive", "negative", "neutral")

def test_analysis_summary(client, auth_headers):
    response = client.get("/api/analysis/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(k in data for k in ("positive", "negative", "neutral", "total"))
