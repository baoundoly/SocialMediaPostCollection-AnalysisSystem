from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "social_media_analyzer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.scheduled_jobs"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "collect-all-sources-every-hour": {
            "task": "app.tasks.scheduled_jobs.collect_all_sources",
            "schedule": 3600.0,
        },
        "analyze-pending-posts-every-30min": {
            "task": "app.tasks.scheduled_jobs.analyze_pending_posts",
            "schedule": 1800.0,
        },
    },
)
