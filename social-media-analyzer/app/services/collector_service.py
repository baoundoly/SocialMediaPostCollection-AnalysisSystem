from sqlalchemy.orm import Session
from datetime import datetime
from app.models.source_config import SourceConfig
from app.models.sync_job import SyncJob
from app.models.post import Post
from app.models.platform import Platform
from app.collectors.facebook_collector import FacebookCollector
from app.collectors.youtube_collector import YouTubeCollector
from app.collectors.twitter_collector import TwitterCollector
from app.collectors.reddit_collector import RedditCollector

COLLECTOR_MAP = {
    "facebook": FacebookCollector,
    "youtube": YouTubeCollector,
    "twitter": TwitterCollector,
    "reddit": RedditCollector,
}

class CollectorService:
    def __init__(self, db: Session):
        self.db = db

    def run_collection(self, source_config_id: int) -> dict:
        sc = self.db.query(SourceConfig).filter(SourceConfig.id == source_config_id).first()
        if not sc:
            return {"error": "Source config not found"}

        platform = self.db.query(Platform).filter(Platform.id == sc.platform_id).first()
        platform_name = platform.name.lower() if platform else "unknown"

        job = SyncJob(source_config_id=source_config_id, start_time=datetime.utcnow(), status="running")
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        try:
            collector_cls = COLLECTOR_MAP.get(platform_name)
            if not collector_cls:
                raise ValueError(f"No collector for platform: {platform_name}")

            collector = collector_cls(sc)
            posts_data = collector.fetch_posts()

            inserted = 0
            for post_data in posts_data:
                existing = self.db.query(Post).filter(
                    Post.external_post_id == post_data.get("external_post_id"),
                    Post.platform_id == sc.platform_id,
                ).first()
                if existing:
                    continue
                post = Post(
                    platform_id=sc.platform_id,
                    source_config_id=sc.id,
                    external_post_id=post_data.get("external_post_id"),
                    author_name=post_data.get("author_name"),
                    author_handle=post_data.get("author_handle"),
                    content=post_data.get("content"),
                    post_url=post_data.get("post_url"),
                    media_url=post_data.get("media_url"),
                    posted_at=post_data.get("posted_at"),
                    likes_count=post_data.get("likes_count", 0),
                    comments_count=post_data.get("comments_count", 0),
                    shares_count=post_data.get("shares_count", 0),
                    views_count=post_data.get("views_count", 0),
                    raw_payload=post_data.get("raw_payload"),
                )
                self.db.add(post)
                inserted += 1

            self.db.commit()
            job.status = "completed"
            job.total_fetched = len(posts_data)
            job.total_inserted = inserted
            job.end_time = datetime.utcnow()
            self.db.commit()
            return {"status": "completed", "fetched": len(posts_data), "inserted": inserted}

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.end_time = datetime.utcnow()
            self.db.commit()
            return {"status": "failed", "error": str(e)}
