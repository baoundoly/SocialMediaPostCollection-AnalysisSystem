from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role_id: Optional[int] = 3  # default viewer

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInfo(BaseModel):
    id: int
    full_name: str
    email: str
    role_id: int
    status: str

    class Config:
        from_attributes = True
