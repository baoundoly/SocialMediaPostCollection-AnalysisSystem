from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class SyncJob(Base):
    __tablename__ = "sync_jobs"
    id = Column(Integer, primary_key=True, index=True)
    source_config_id = Column(Integer, ForeignKey("source_configs.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(20), default="running")  # running, completed, failed
    total_fetched = Column(Integer, default=0)
    total_inserted = Column(Integer, default=0)
    error_message = Column(Text)
    source_config = relationship("SourceConfig")
