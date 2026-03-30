from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role_id: int = 3

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    role_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
