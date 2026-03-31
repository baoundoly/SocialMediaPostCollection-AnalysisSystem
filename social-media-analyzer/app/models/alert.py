from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)
    reference_id = Column(Integer)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # info, warning, critical
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
