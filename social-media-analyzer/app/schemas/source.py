from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SourceConfigCreate(BaseModel):
    platform_id: int
    source_type: Optional[str] = None
    keyword: Optional[str] = None
    account_name: Optional[str] = None
    page_name: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None

class SourceConfigUpdate(BaseModel):
    source_type: Optional[str] = None
    keyword: Optional[str] = None
    account_name: Optional[str] = None
    page_name: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    status: Optional[str] = None

class SourceConfigOut(BaseModel):
    id: int
    platform_id: int
    source_type: Optional[str]
    keyword: Optional[str]
    account_name: Optional[str]
    page_name: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
