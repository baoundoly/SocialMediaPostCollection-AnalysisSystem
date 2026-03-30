from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AnalysisOut(BaseModel):
    id: int
    post_id: int
    language: Optional[str]
    sentiment_label: Optional[str]
    sentiment_score: Optional[float]
    toxicity_score: Optional[float]
    summary_text: Optional[str]
    analyzed_at: datetime

    class Config:
        from_attributes = True

class SentimentSummary(BaseModel):
    positive: int
    negative: int
    neutral: int
    total: int

class TrendPoint(BaseModel):
    date: str
    positive: int
    negative: int
    neutral: int
