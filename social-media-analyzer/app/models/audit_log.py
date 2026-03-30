from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    module_name = Column(String(100))
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
