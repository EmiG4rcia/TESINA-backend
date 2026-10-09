from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


class ProductionInputCreate(BaseModel):
    raw_material_id: int
    quantity_used: Decimal
    estimated_quantity: Optional[Decimal] = None


class ProductionInputResponse(BaseModel):
    id: int
    raw_material_id: int
    raw_material_name: Optional[str] = None
    raw_material_unit: Optional[str] = None
    quantity_used: Decimal
    estimated_quantity: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ProductionLogCreate(BaseModel):
    product_id: int
    produced_quantity: Decimal
    notes: Optional[str] = None
    inputs: List[ProductionInputCreate] = []


class ProductionLogResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_unit: Optional[str] = None
    produced_quantity: Decimal
    estimated_quantity: Optional[Decimal] = None
    notes: Optional[str] = None
    created_by_username: Optional[str] = None
    created_at: datetime
    inputs: List[ProductionInputResponse] = []
    yield_percentage: Optional[float] = None

    class Config:
        from_attributes = True