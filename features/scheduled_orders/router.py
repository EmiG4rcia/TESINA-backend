from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from features.scheduled_orders.service import (
    get_scheduled_orders, get_scheduled_order_by_id,
    create_scheduled_order, update_scheduled_order,
    update_order_item, delete_scheduled_order,
    _order_to_response
)
from core.database import get_db
from core.dependencies import get_current_admin
from features.scheduled_orders.schemas import (
    ScheduledOrderCreate, ScheduledOrderUpdate,
    ScheduledOrderResponse, ScheduledOrderItemUpdate, ScheduledOrderItemResponse
)
from features.scheduled_orders.service import (
    get_scheduled_orders, get_scheduled_order_by_id,
    create_scheduled_order, update_scheduled_order,
    update_order_item, delete_scheduled_order
)

router = APIRouter()


@router.get("", response_model=list[ScheduledOrderResponse])
def list_orders(
    destination_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return get_scheduled_orders(db, destination_id=destination_id,
                                 date_from=date_from, date_to=date_to, status=status)


@router.get("/{order_id}", response_model=ScheduledOrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return _order_to_response(get_scheduled_order_by_id(db, order_id))


@router.post("", response_model=ScheduledOrderResponse)
def create(
    data: ScheduledOrderCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return create_scheduled_order(db, data)


@router.patch("/{order_id}", response_model=ScheduledOrderResponse)
def update(
    order_id: int,
    data: ScheduledOrderUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return update_scheduled_order(db, order_id, data)


@router.patch("/{order_id}/items/{item_id}", response_model=ScheduledOrderItemResponse)
def update_item(
    order_id: int,
    item_id: int,
    data: ScheduledOrderItemUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return update_order_item(db, order_id, item_id, data)


@router.delete("/{order_id}")
def delete(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    delete_scheduled_order(db, order_id)
    return {"message": f"Pedido agendado {order_id} eliminado correctamente"}