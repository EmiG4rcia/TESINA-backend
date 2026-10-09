from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from features.deliveries.models import Delivery, DeliveryProduct
from features.deliveries.schemas import (
    DeliveryCreate, DeliveryUpdate, DeliveryResponse,
    DeliveryProductCreate, DeliveryProductUpdate, DeliveryProductResponse
)
from features.stock.models import StockMovement


def _product_to_response(p: DeliveryProduct) -> DeliveryProductResponse:
    return DeliveryProductResponse(
        id=p.id,
        product_id=p.product_id,
        product_name=p.product.name if p.product else None,
        product_unit=p.product.unit if p.product else None,
        planned_quantity=p.planned_quantity,
        actual_quantity=p.actual_quantity,
        modified_by_username=p.modified_by_user.username if p.modified_by_user else None,
    )


def _delivery_to_response(d: Delivery) -> DeliveryResponse:
    return DeliveryResponse(
        id=d.id,
        destination_id=d.destination_id,
        destination_name=d.destination.name if d.destination else None,
        scheduled_order_id=d.scheduled_order_id,
        delivery_date=d.delivery_date,
        delivery_time=d.delivery_time,
        status=d.status,
        notes=d.notes,
        created_at=d.created_at,
        completed_at=d.completed_at,
        products=[_product_to_response(p) for p in d.products],
    )


def get_deliveries(
    db: Session,
    destination_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[str] = None,
) -> List[DeliveryResponse]:
    query = db.query(Delivery).options(
        joinedload(Delivery.destination),
        joinedload(Delivery.products),
    ).filter(Delivery.deleted_at == None)

    if destination_id:
        query = query.filter(Delivery.destination_id == destination_id)
    if date_from:
        query = query.filter(Delivery.delivery_date >= date_from)
    if date_to:
        query = query.filter(Delivery.delivery_date <= date_to)
    if status:
        query = query.filter(Delivery.status == status)

    return [_delivery_to_response(d) for d in query.order_by(Delivery.delivery_date.desc()).all()]


def get_delivery_by_id(db: Session, delivery_id: int) -> Delivery:
    delivery = db.query(Delivery).options(
        joinedload(Delivery.destination),
        joinedload(Delivery.products),
    ).filter(
        Delivery.id == delivery_id,
        Delivery.deleted_at == None
    ).first()
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Entrega {delivery_id} no encontrada")
    return delivery


def create_delivery(db: Session, data: DeliveryCreate, created_by: int = None) -> DeliveryResponse:
    existing = db.query(Delivery).filter(
        Delivery.destination_id == data.destination_id,
        Delivery.delivery_date == data.delivery_date,
        Delivery.deleted_at == None,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ya existe una entrega para ese destino en esa fecha")

    delivery = Delivery(
        destination_id=data.destination_id,
        scheduled_order_id=data.scheduled_order_id,
        delivery_date=data.delivery_date,
        delivery_time=data.delivery_time,
        notes=data.notes,
        created_by=created_by,
    )
    db.add(delivery)
    db.flush()

    for p in (data.products or []):
        dp = DeliveryProduct(
            delivery_id=delivery.id,
            product_id=p.product_id,
            planned_quantity=p.planned_quantity,
            actual_quantity=p.actual_quantity,
        )
        db.add(dp)

    db.commit()
    db.refresh(delivery)
    return _delivery_to_response(delivery)


def complete_delivery(db: Session, delivery_id: int, created_by: int = None) -> DeliveryResponse:
    delivery = get_delivery_by_id(db, delivery_id)

    if delivery.status == "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Esta entrega ya fue completada")

    # Discount stock for each product
    for dp in delivery.products:
        qty = dp.actual_quantity or dp.planned_quantity
        if not qty:
            continue

        from features.products.models import Product
        product = db.query(Product).filter(Product.id == dp.product_id).first()
        if product:
            product.stock_quantity = max(
                Decimal("0"),
                (product.stock_quantity or Decimal("0")) - qty
            )

            movement = StockMovement(
                item_type="product",
                item_id=dp.product_id,
                movement_type="delivery",
                quantity=-qty,
                reference_id=delivery_id,
                notes=f"Entrega a {delivery.destination.name}",
                created_by=created_by,
            )
            db.add(movement)

    delivery.status = "completed"
    delivery.completed_at = datetime.now()
    db.commit()
    db.refresh(delivery)
    return _delivery_to_response(delivery)


def update_delivery(db: Session, delivery_id: int, data: DeliveryUpdate) -> DeliveryResponse:
    delivery = get_delivery_by_id(db, delivery_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(delivery, key, value)
    db.commit()
    db.refresh(delivery)
    return _delivery_to_response(delivery)


def delete_delivery(db: Session, delivery_id: int) -> None:
    delivery = get_delivery_by_id(db, delivery_id)
    delivery.deleted_at = datetime.now()
    db.commit()