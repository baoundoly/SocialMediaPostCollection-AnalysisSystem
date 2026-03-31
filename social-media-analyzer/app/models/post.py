from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    source_config_id = Column(Integer, ForeignKey("source_configs.id"))
    external_post_id = Column(String(255), index=True)
    author_name = Column(String(255))
    author_handle = Column(String(255))
    content = Column(Text)
    post_url = Column(String(512))
    media_url = Column(String(512))
    posted_at = Column(DateTime)
    likes_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    shares_count = Column(BigInteger, default=0)
    views_count = Column(BigInteger, default=0)
    raw_payload = Column(Text)
    collected_at = Column(DateTime, default=datetime.utcnow)
    platform = relationship("Platform")
    source_config = relationship("SourceConfig")
    analysis = relationship("PostAnalysis", back_populates="post", uselist=False)
    post_keywords = relationship("PostKeyword", back_populates="post")
    post_entities = relationship("PostEntity", back_populates="post")

class PostKeyword(Base):
    __tablename__ = "post_keywords"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    weight = Column(Float, default=1.0)
    post = relationship("Post", back_populates="post_keywords")
    keyword = relationship("Keyword")

class PostEntity(Base):
    __tablename__ = "post_entities"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    post = relationship("Post", back_populates="post_entities")
    entity = relationship("Entity")
