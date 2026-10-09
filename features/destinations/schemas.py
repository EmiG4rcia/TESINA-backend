from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DestinationCreate(BaseModel):
    name: str
    address: Optional[str] = None
    contact: Optional[str] = None


class DestinationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    is_active: Optional[bool] = None


class DestinationResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    contact: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True