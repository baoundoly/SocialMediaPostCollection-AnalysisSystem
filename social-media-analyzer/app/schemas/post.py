from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostOut(BaseModel):
    id: int
    platform_id: int
    source_config_id: Optional[int]
    external_post_id: Optional[str]
    author_name: Optional[str]
    author_handle: Optional[str]
    content: Optional[str]
    post_url: Optional[str]
    posted_at: Optional[datetime]
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    collected_at: datetime

    class Config:
        from_attributes = True

class PostFilter(BaseModel):
    platform_id: Optional[int] = None
    source_config_id: Optional[int] = None
    keyword: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sentiment: Optional[str] = None
    page: int = 1
    page_size: int = 20
