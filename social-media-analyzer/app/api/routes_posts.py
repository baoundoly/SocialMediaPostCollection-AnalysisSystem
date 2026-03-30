from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.schemas.post import PostOut, PostFilter
from app.models.post import Post
from app.models.post_analysis import PostAnalysis
from app.api.deps import get_current_user
from app.models.user import User
from app.services.collector_service import CollectorService

router = APIRouter(prefix="/api", tags=["posts"])

@router.get("/posts", response_model=List[PostOut])
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Post)
    if platform_id:
        q = q.filter(Post.platform_id == platform_id)
    offset = (page - 1) * page_size
    return q.order_by(Post.collected_at.desc()).offset(offset).limit(page_size).all()

@router.get("/posts/filter", response_model=List[PostOut])
def filter_posts(
    platform_id: Optional[int] = None,
    source_config_id: Optional[int] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sentiment: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Post)
    if platform_id:
        q = q.filter(Post.platform_id == platform_id)
    if source_config_id:
        q = q.filter(Post.source_config_id == source_config_id)
    if keyword:
        q = q.filter(Post.content.ilike(f"%{keyword}%"))
    if start_date:
        q = q.filter(Post.posted_at >= start_date)
    if end_date:
        q = q.filter(Post.posted_at <= end_date)
    if sentiment:
        q = q.join(PostAnalysis, Post.id == PostAnalysis.post_id).filter(PostAnalysis.sentiment_label == sentiment)
    offset = (page - 1) * page_size
    return q.order_by(Post.collected_at.desc()).offset(offset).limit(page_size).all()

@router.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/collect/run/{source_id}")
def run_collection(source_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    service = CollectorService(db)
    result = service.run_collection(source_id)
    return result

@router.get("/collect/jobs")
def list_jobs(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.sync_job import SyncJob
    jobs = db.query(SyncJob).order_by(SyncJob.start_time.desc()).limit(50).all()
    return [
        {
            "id": j.id,
            "source_config_id": j.source_config_id,
            "start_time": j.start_time,
            "end_time": j.end_time,
            "status": j.status,
            "total_fetched": j.total_fetched,
            "total_inserted": j.total_inserted,
            "error_message": j.error_message,
        }
        for j in jobs
    ]
