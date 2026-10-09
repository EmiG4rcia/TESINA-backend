from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


class ScheduledOrderItemCreate(BaseModel):
    product_id: int
    planned_quantity: Decimal


class ScheduledOrderItemUpdate(BaseModel):
    planned_quantity: Decimal


class ScheduledOrderItemResponse(BaseModel):
    id: int
    product_id: int
    planned_quantity: Decimal
    product_name: Optional[str] = None
    product_unit: Optional[str] = None
    modified_by_username: Optional[str] = None
    modified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScheduledOrderCreate(BaseModel):
    destination_id: int
    scheduled_date: date
    notes: Optional[str] = None
    items: Optional[List[ScheduledOrderItemCreate]] = []


class ScheduledOrderUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class ScheduledOrderResponse(BaseModel):
    id: int
    destination_id: int
    destination_name: Optional[str] = None
    scheduled_date: date
    status: str
    notes: Optional[str]
    created_at: datetime
    items: List[ScheduledOrderItemResponse] = []

    class Config:
        from_attributes = True