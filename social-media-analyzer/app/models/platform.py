from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Platform(Base):
    __tablename__ = "platforms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    base_api_url = Column(String(255))
    status = Column(String(20), default="active")
