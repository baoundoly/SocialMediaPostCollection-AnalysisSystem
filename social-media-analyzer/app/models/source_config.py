from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class SourceConfig(Base):
    __tablename__ = "source_configs"
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    source_type = Column(String(50))
    keyword = Column(String(255))
    account_name = Column(String(255))
    page_name = Column(String(255))
    api_key_encrypted = Column(String(512))
    access_token_encrypted = Column(String(512))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    platform = relationship("Platform")
