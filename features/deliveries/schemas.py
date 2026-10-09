from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


class DeliveryProductCreate(BaseModel):
    product_id: int
    planned_quantity: Optional[Decimal] = None
    actual_quantity: Optional[Decimal] = None


class DeliveryProductUpdate(BaseModel):
    actual_quantity: Decimal


class DeliveryProductResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_unit: Optional[str] = None
    planned_quantity: Optional[Decimal]
    actual_quantity: Optional[Decimal]
    modified_by_username: Optional[str] = None

    class Config:
        from_attributes = True


class DeliveryCreate(BaseModel):
    destination_id: int
    scheduled_order_id: Optional[int] = None
    delivery_date: date
    delivery_time: Optional[time] = None
    notes: Optional[str] = None
    products: Optional[List[DeliveryProductCreate]] = []


class DeliveryUpdate(BaseModel):
    delivery_time: Optional[time] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class DeliveryResponse(BaseModel):
    id: int
    destination_id: int
    destination_name: Optional[str] = None
    scheduled_order_id: Optional[int]
    delivery_date: date
    delivery_time: Optional[time]
    status: str
    notes: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    products: List[DeliveryProductResponse] = []

    class Config:
        from_attributes = True