from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class PostAnalysis(Base):
    __tablename__ = "post_analysis"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, unique=True)
    language = Column(String(10))
    sentiment_label = Column(String(20))
    sentiment_score = Column(Float)
    toxicity_score = Column(Float)
    summary_text = Column(Text)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    post = relationship("Post", back_populates="analysis")
