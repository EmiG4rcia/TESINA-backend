from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class StockMovementResponse(BaseModel):
    id: int
    item_type: str
    item_id: int
    movement_type: str
    quantity: Decimal
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    item_name: Optional[str] = None
    created_by_username: Optional[str] = None

    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    item_type: str
    item_id: int
    quantity: Decimal
    notes: Optional[str] = None


class StockPurchase(BaseModel):
    item_type: str
    item_id: int
    quantity: Decimal
    notes: Optional[str] = None