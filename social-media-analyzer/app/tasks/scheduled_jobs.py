from app.core.scheduler import celery_app

@celery_app.task(name="app.tasks.scheduled_jobs.collect_all_sources")
def collect_all_sources():
    from app.core.database import SessionLocal
    from app.models.source_config import SourceConfig
    from app.services.collector_service import CollectorService
    db = SessionLocal()
    try:
        sources = db.query(SourceConfig).filter(SourceConfig.status == "active").all()
        service = CollectorService(db)
        return [{"source_id": s.id, "result": service.run_collection(s.id)} for s in sources]
    finally:
        db.close()

@celery_app.task(name="app.tasks.scheduled_jobs.analyze_pending_posts")
def analyze_pending_posts():
    from app.core.database import SessionLocal
    from app.models.post import Post
    from app.models.post_analysis import PostAnalysis
    from app.services.analysis_service import AnalysisService
    db = SessionLocal()
    try:
        analyzed_ids = {r[0] for r in db.query(PostAnalysis.post_id).all()}
        pending = db.query(Post).filter(~Post.id.in_(analyzed_ids)).limit(100).all()
        service = AnalysisService(db)
        for post in pending:
            service.analyze_post(post.id)
        return {"analyzed": len(pending)}
    finally:
        db.close()
