from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.models.post import Post, PostKeyword, PostEntity
from app.models.post_analysis import PostAnalysis
from app.models.keyword import Keyword
from app.models.entity import Entity
from app.utils.sentiment import analyze_sentiment
from app.utils.keyword_extractor import extract_keywords
from app.utils.entity_extractor import extract_entities
from app.utils.text_cleaner import clean_text
try:
    from langdetect import detect as langdetect_detect
    from langdetect.lang_detect_exception import LangDetectException
except ImportError:
    langdetect_detect = None

class AnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def analyze_post(self, post_id: int) -> Optional[PostAnalysis]:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return None

        content = post.content or ""
        cleaned = clean_text(content)

        # Language detection
        language = "en"
        if langdetect_detect and cleaned:
            try:
                language = langdetect_detect(cleaned)
            except Exception:
                language = "en"

        # Sentiment
        sentiment_label, sentiment_score = analyze_sentiment(cleaned)

        # Toxicity
        toxicity_score = self._compute_toxicity(cleaned)

        # Summary (first 200 chars)
        summary_text = cleaned[:200] if cleaned else ""

        # Upsert analysis
        analysis = self.db.query(PostAnalysis).filter(PostAnalysis.post_id == post_id).first()
        if analysis:
            analysis.language = language
            analysis.sentiment_label = sentiment_label
            analysis.sentiment_score = sentiment_score
            analysis.toxicity_score = toxicity_score
            analysis.summary_text = summary_text
            analysis.analyzed_at = datetime.utcnow()
        else:
            analysis = PostAnalysis(
                post_id=post_id,
                language=language,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score,
                toxicity_score=toxicity_score,
                summary_text=summary_text,
            )
            self.db.add(analysis)

        # Keywords
        keywords = extract_keywords(cleaned)
        self.db.query(PostKeyword).filter(PostKeyword.post_id == post_id).delete()
        for kw_text, weight in keywords:
            kw = self.db.query(Keyword).filter(Keyword.keyword_text == kw_text).first()
            if not kw:
                kw = Keyword(keyword_text=kw_text)
                self.db.add(kw)
                self.db.flush()
            pk = PostKeyword(post_id=post_id, keyword_id=kw.id, weight=weight)
            self.db.add(pk)

        # Entities
        entities = extract_entities(cleaned)
        self.db.query(PostEntity).filter(PostEntity.post_id == post_id).delete()
        for ent_name, ent_type in entities:
            ent = self.db.query(Entity).filter(Entity.entity_name == ent_name, Entity.entity_type == ent_type).first()
            if not ent:
                ent = Entity(entity_name=ent_name, entity_type=ent_type)
                self.db.add(ent)
                self.db.flush()
            pe = PostEntity(post_id=post_id, entity_id=ent.id)
            self.db.add(pe)

        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def _compute_toxicity(self, text: str) -> float:
        toxic_words = ["hate", "kill", "stupid", "idiot", "moron", "loser", "trash", "disgusting", "awful", "terrible"]
        text_lower = text.lower()
        count = sum(1 for w in toxic_words if w in text_lower)
        return min(1.0, count / max(len(text.split()), 1) * 5)

    def get_sentiment_summary(self, platform_id: Optional[int] = None) -> dict:
        q = self.db.query(PostAnalysis).join(Post, PostAnalysis.post_id == Post.id)
        if platform_id:
            q = q.filter(Post.platform_id == platform_id)
        results = q.all()
        positive = sum(1 for r in results if r.sentiment_label == "positive")
        negative = sum(1 for r in results if r.sentiment_label == "negative")
        neutral = sum(1 for r in results if r.sentiment_label == "neutral")
        return {"positive": positive, "negative": negative, "neutral": neutral, "total": len(results)}

    def get_sentiment_trends(self, days: int = 7, platform_id: Optional[int] = None) -> list:
        from datetime import date
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        q = self.db.query(PostAnalysis, Post).join(Post, PostAnalysis.post_id == Post.id).filter(
            Post.posted_at >= start_date, Post.posted_at <= end_date
        )
        if platform_id:
            q = q.filter(Post.platform_id == platform_id)
        results = q.all()
        trend_map = {}
        for analysis, post in results:
            if not post.posted_at:
                continue
            day_key = post.posted_at.strftime("%Y-%m-%d")
            if day_key not in trend_map:
                trend_map[day_key] = {"positive": 0, "negative": 0, "neutral": 0}
            label = analysis.sentiment_label or "neutral"
            trend_map[day_key][label] = trend_map[day_key].get(label, 0) + 1
        return [
            {"date": k, **v}
            for k, v in sorted(trend_map.items())
        ]
