from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, index=True)
    keyword_text = Column(String(255), unique=True, nullable=False, index=True)
