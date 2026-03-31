from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    external_comment_id = Column(String(255))
    commenter_name = Column(String(255))
    content = Column(Text)
    commented_at = Column(DateTime)
    likes_count = Column(BigInteger, default=0)
    raw_payload = Column(Text)
    post = relationship("Post")
