from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.analysis import AnalysisOut, SentimentSummary
from app.services.analysis_service import AnalysisService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/run/{post_id}", response_model=AnalysisOut)
def run_analysis(post_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    service = AnalysisService(db)
    result = service.analyze_post(post_id)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return result

@router.get("/summary", response_model=SentimentSummary)
def get_summary(
    platform_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = AnalysisService(db)
    return service.get_sentiment_summary(platform_id)

@router.get("/trends")
def get_trends(
    days: int = Query(7, ge=1, le=90),
    platform_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = AnalysisService(db)
    return service.get_sentiment_trends(days, platform_id)
