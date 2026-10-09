from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "employee"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True