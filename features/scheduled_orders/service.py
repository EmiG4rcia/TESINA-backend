from datetime import datetime, date
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from features.scheduled_orders.models import ScheduledOrder, ScheduledOrderItem
from features.scheduled_orders.schemas import (
    ScheduledOrderCreate, ScheduledOrderUpdate,
    ScheduledOrderResponse, ScheduledOrderItemCreate,
    ScheduledOrderItemUpdate, ScheduledOrderItemResponse
)


def _item_to_response(item: ScheduledOrderItem) -> ScheduledOrderItemResponse:
    return ScheduledOrderItemResponse(
        id=item.id,
        product_id=item.product_id,
        planned_quantity=item.planned_quantity,
        product_name=item.product.name if item.product else None,
        product_unit=item.product.unit if item.product else None,
        modified_by_username=item.modified_by_user.username if item.modified_by_user else None,
        modified_at=item.modified_at,
    )


def _order_to_response(order: ScheduledOrder) -> ScheduledOrderResponse:
    return ScheduledOrderResponse(
        id=order.id,
        destination_id=order.destination_id,
        destination_name=order.destination.name if order.destination else None,
        scheduled_date=order.scheduled_date,
        status=order.status,
        notes=order.notes,
        created_at=order.created_at,
        items=[_item_to_response(i) for i in order.items],
    )


def get_scheduled_orders(
    db: Session,
    destination_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[str] = None,
) -> List[ScheduledOrderResponse]:
    query = db.query(ScheduledOrder).options(
        joinedload(ScheduledOrder.destination),
        joinedload(ScheduledOrder.items),
    ).filter(ScheduledOrder.deleted_at == None)

    if destination_id:
        query = query.filter(ScheduledOrder.destination_id == destination_id)
    if date_from:
        query = query.filter(ScheduledOrder.scheduled_date >= date_from)
    if date_to:
        query = query.filter(ScheduledOrder.scheduled_date <= date_to)
    if status:
        query = query.filter(ScheduledOrder.status == status)

    return [_order_to_response(o) for o in query.order_by(ScheduledOrder.scheduled_date).all()]


def get_scheduled_order_by_id(db: Session, order_id: int) -> ScheduledOrder:
    order = db.query(ScheduledOrder).options(
        joinedload(ScheduledOrder.destination),
        joinedload(ScheduledOrder.items),
    ).filter(
        ScheduledOrder.id == order_id,
        ScheduledOrder.deleted_at == None
    ).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Pedido agendado {order_id} no encontrado")
    return order


def create_scheduled_order(
    db: Session, data: ScheduledOrderCreate, created_by: int = None
) -> ScheduledOrderResponse:
    existing = db.query(ScheduledOrder).filter(
        ScheduledOrder.destination_id == data.destination_id,
        ScheduledOrder.scheduled_date == data.scheduled_date,
        ScheduledOrder.deleted_at == None,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ya existe un pedido para ese destino en esa fecha")

    order = ScheduledOrder(
        destination_id=data.destination_id,
        scheduled_date=data.scheduled_date,
        notes=data.notes,
        created_by=created_by,
    )
    db.add(order)
    db.flush()

    for item_data in (data.items or []):
        item = ScheduledOrderItem(
            scheduled_order_id=order.id,
            product_id=item_data.product_id,
            planned_quantity=item_data.planned_quantity,
        )
        db.add(item)

    db.commit()
    db.refresh(order)
    return _order_to_response(order)


def update_scheduled_order(
    db: Session, order_id: int, data: ScheduledOrderUpdate
) -> ScheduledOrderResponse:
    order = get_scheduled_order_by_id(db, order_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(order, key, value)
    db.commit()
    db.refresh(order)
    return _order_to_response(order)


def update_order_item(
    db: Session, order_id: int, item_id: int,
    data: ScheduledOrderItemUpdate, modified_by: int = None
) -> ScheduledOrderItemResponse:
    item = db.query(ScheduledOrderItem).filter(
        ScheduledOrderItem.id == item_id,
        ScheduledOrderItem.scheduled_order_id == order_id,
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Item no encontrado")
    item.planned_quantity = data.planned_quantity
    item.modified_by = modified_by
    item.modified_at = datetime.now()
    db.commit()
    db.refresh(item)
    return _item_to_response(item)


def delete_scheduled_order(db: Session, order_id: int) -> None:
    order = get_scheduled_order_by_id(db, order_id)
    order.deleted_at = datetime.now()
    db.commit()