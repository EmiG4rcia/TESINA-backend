from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    unit: str
    stock_quantity: Optional[Decimal] = Decimal("0")
    stock_min_alert: Optional[Decimal] = Decimal("0")
    alert_enabled: Optional[bool] = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    stock_quantity: Optional[Decimal] = None
    stock_min_alert: Optional[Decimal] = None
    alert_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
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


class RecipeItemCreate(BaseModel):
    raw_material_id: int
    estimated_quantity: Decimal
    unit: str
    yield_quantity: Optional[Decimal] = Decimal("1")
    yield_unit: Optional[str] = "unidad"

class RecipeItemResponse(BaseModel):
    id: int
    raw_material_id: int
    estimated_quantity: Decimal
    unit: str
    raw_material_name: Optional[str] = None
    yield_unit: str = "unidad"
    yield_quantity: Decimal = Decimal("1")
    class Config:
        from_attributes = True