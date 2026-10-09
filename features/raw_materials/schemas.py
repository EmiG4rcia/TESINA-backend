from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class RawMaterialCreate(BaseModel):
    name: str
    unit: str
    stock_quantity: Optional[Decimal] = Decimal("0")
    stock_min_alert: Optional[Decimal] = Decimal("0")
    alert_enabled: Optional[bool] = True


class RawMaterialUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    stock_quantity: Optional[Decimal] = None
    stock_min_alert: Optional[Decimal] = None
    alert_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class RawMaterialResponse(BaseModel):
    id: int
    name: str
    unit: str
    stock_quantity: Decimal
    stock_min_alert: Decimal
    alert_enabled: bool
    is_active: bool
    is_low_stock: bool = False
    created_at: datetime

    class Config:
        from_attributes = True