from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/overview")
def overview(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    service = DashboardService(db)
    return service.get_overview()

@router.get("/sentiment")
def sentiment(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = DashboardService(db)
    return service.get_sentiment_chart(days)

@router.get("/keywords")
def keywords(
    top_n: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = DashboardService(db)
    return service.get_top_keywords(top_n)

@router.get("/top-posts")
def top_posts(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = DashboardService(db)
    return service.get_top_posts(limit)
