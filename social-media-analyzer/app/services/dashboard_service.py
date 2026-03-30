from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.post import Post, PostKeyword
from app.models.post_analysis import PostAnalysis
from app.models.keyword import Keyword
from app.models.platform import Platform
from app.models.sync_job import SyncJob
from app.models.alert import Alert

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self):
        total_posts = self.db.query(func.count(Post.id)).scalar() or 0
        analyzed_posts = self.db.query(func.count(PostAnalysis.id)).scalar() or 0
        sync_jobs = self.db.query(func.count(SyncJob.id)).scalar() or 0
        unread_alerts = self.db.query(func.count(Alert.id)).filter(Alert.is_read == False).scalar() or 0
        platforms = self.db.query(Platform).all()
        platform_breakdown = {p.name: (self.db.query(func.count(Post.id)).filter(Post.platform_id == p.id).scalar() or 0) for p in platforms}
        return {"total_posts": total_posts, "analyzed_posts": analyzed_posts, "sync_jobs": sync_jobs,
                "unread_alerts": unread_alerts, "platform_breakdown": platform_breakdown}

    def get_sentiment_chart(self, days=7):
        start_date = datetime.utcnow() - timedelta(days=days)
        results = self.db.query(PostAnalysis, Post).join(Post, PostAnalysis.post_id == Post.id).filter(Post.posted_at >= start_date).all()
        trend_map = {}
        for analysis, post in results:
            if not post.posted_at: continue
            day_key = post.posted_at.strftime("%Y-%m-%d")
            if day_key not in trend_map:
                trend_map[day_key] = {"date": day_key, "positive": 0, "negative": 0, "neutral": 0}
            label = analysis.sentiment_label or "neutral"
            if label in trend_map[day_key]: trend_map[day_key][label] += 1
        return sorted(trend_map.values(), key=lambda x: x["date"])

    def get_top_keywords(self, top_n=20):
        results = (self.db.query(Keyword.keyword_text, func.sum(PostKeyword.weight).label("total_weight"))
            .join(PostKeyword, Keyword.id == PostKeyword.keyword_id).group_by(Keyword.keyword_text)
            .order_by(func.sum(PostKeyword.weight).desc()).limit(top_n).all())
        return [{"keyword": r.keyword_text, "weight": float(r.total_weight)} for r in results]

    def get_top_posts(self, limit=10):
        posts = self.db.query(Post).order_by((Post.likes_count + Post.comments_count + Post.shares_count).desc()).limit(limit).all()
        return [{"id": p.id, "author_name": p.author_name, "content": (p.content or "")[:150],
                 "likes_count": p.likes_count, "comments_count": p.comments_count,
                 "shares_count": p.shares_count, "posted_at": str(p.posted_at)} for p in posts]
