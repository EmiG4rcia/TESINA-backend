from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from features.stock.models import StockMovement
from features.stock.schemas import StockMovementResponse, StockPurchase, StockAdjustment
from features.products.models import Product
from features.raw_materials.models import RawMaterial


def _get_item(db: Session, item_type: str, item_id: int):
    if item_type == "product":
        item = db.query(Product).filter(Product.id == item_id).first()
    elif item_type == "raw_material":
        item = db.query(RawMaterial).filter(RawMaterial.id == item_id).first()
    else:
        raise HTTPException(status_code=400, detail="item_type inválido")
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item


def _to_response(db: Session, movement: StockMovement) -> StockMovementResponse:
    item = _get_item(db, movement.item_type, movement.item_id)
    user = movement.created_by_user
    return StockMovementResponse(
        id=movement.id,
        item_type=movement.item_type,
        item_id=movement.item_id,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        reference_id=movement.reference_id,
        notes=movement.notes,
        created_at=movement.created_at,
        item_name=item.name if item else None,
        created_by_username=user.username if user else None,
    )


def get_movements(
    db: Session,
    item_type: Optional[str] = None,
    item_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[StockMovementResponse]:
    query = db.query(StockMovement)
    if item_type:
        query = query.filter(StockMovement.item_type == item_type)
    if item_id:
        query = query.filter(StockMovement.item_id == item_id)
    movements = query.order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()
    return [_to_response(db, m) for m in movements]


def register_purchase(db: Session, data: StockPurchase, created_by: int = None) -> StockMovementResponse:
    item = _get_item(db, data.item_type, data.item_id)
    item.stock_quantity = (item.stock_quantity or Decimal("0")) + data.quantity
    db.commit()

    movement = StockMovement(
        item_type=data.item_type,
        item_id=data.item_id,
        movement_type="purchase",
        quantity=data.quantity,
        notes=data.notes,
        created_by=created_by,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return _to_response(db, movement)


def register_adjustment(db: Session, data: StockAdjustment, created_by: int = None) -> StockMovementResponse:
    item = _get_item(db, data.item_type, data.item_id)
    item.stock_quantity = max(
        Decimal("0"),
        (item.stock_quantity or Decimal("0")) + data.quantity
    )
    db.commit()

    movement_type = "adjustment" if data.quantity >= 0 else "waste"
    movement = StockMovement(
        item_type=data.item_type,
        item_id=data.item_id,
        movement_type=movement_type,
        quantity=data.quantity,
        notes=data.notes,
        created_by=created_by,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return _to_response(db, movement)