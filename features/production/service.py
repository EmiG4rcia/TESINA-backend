from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from features.production.models import ProductionLog, ProductionLogInput
from features.production.schemas import (
    ProductionLogCreate, ProductionLogResponse, ProductionInputResponse
)
from features.stock.models import StockMovement


def _input_to_response(inp: ProductionLogInput) -> ProductionInputResponse:
    return ProductionInputResponse(
        id=inp.id,
        raw_material_id=inp.raw_material_id,
        raw_material_name=inp.raw_material.name if inp.raw_material else None,
        raw_material_unit=inp.raw_material.unit if inp.raw_material else None,
        quantity_used=inp.quantity_used,
        estimated_quantity=inp.estimated_quantity,
    )


def _log_to_response(log: ProductionLog) -> ProductionLogResponse:
    yield_pct = None
    if log.estimated_quantity and log.estimated_quantity > 0:
        yield_pct = round(
            float(log.produced_quantity) / float(log.estimated_quantity) * 100, 2
        )

    return ProductionLogResponse(
        id=log.id,
        product_id=log.product_id,
        product_name=log.product.name if log.product else None,
        product_unit=log.product.unit if log.product else None,
        produced_quantity=log.produced_quantity,
        estimated_quantity=log.estimated_quantity,
        notes=log.notes,
        created_by_username=log.created_by_user.username if log.created_by_user else None,
        created_at=log.created_at,
        inputs=[_input_to_response(i) for i in log.inputs],
        yield_percentage=yield_pct,
    )


def get_production_logs(
    db: Session,
    product_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[ProductionLogResponse]:
    query = db.query(ProductionLog).options(
        joinedload(ProductionLog.product),
        joinedload(ProductionLog.inputs),
        joinedload(ProductionLog.created_by_user),
    ).filter(ProductionLog.deleted_at == None)

    if product_id:
        query = query.filter(ProductionLog.product_id == product_id)

    logs = query.order_by(ProductionLog.created_at.desc()).offset(skip).limit(limit).all()
    return [_log_to_response(log) for log in logs]


def get_production_log_by_id(db: Session, log_id: int) -> ProductionLog:
    log = db.query(ProductionLog).options(
        joinedload(ProductionLog.product),
        joinedload(ProductionLog.inputs),
        joinedload(ProductionLog.created_by_user),
    ).filter(
        ProductionLog.id == log_id,
        ProductionLog.deleted_at == None
    ).first()

    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Lote de producción {log_id} no encontrado")
    return log


def create_production_log(
    db: Session,
    data: ProductionLogCreate,
    created_by: int = None,
) -> ProductionLogResponse:
    from features.products.models import Product, ProductRecipe
    from features.raw_materials.models import RawMaterial

    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Producto no encontrado")

    # Calculate estimated quantity from recipe
    recipe = db.query(ProductRecipe).filter(
        ProductRecipe.product_id == data.product_id,
        ProductRecipe.deleted_at == None
    ).all()

    estimated_qty = None
    if recipe:
        estimated_qty = data.produced_quantity

    log = ProductionLog(
        product_id=data.product_id,
        produced_quantity=data.produced_quantity,
        estimated_quantity=estimated_qty,
        notes=data.notes,
        created_by=created_by,
    )
    db.add(log)
    db.flush()

    # Add inputs and discount raw material stock
    for inp_data in data.inputs:
        raw_material = db.query(RawMaterial).filter(
            RawMaterial.id == inp_data.raw_material_id
        ).first()
        if not raw_material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Materia prima {inp_data.raw_material_id} no encontrada")

        # Find estimated from recipe
        recipe_item = next(
            (r for r in recipe if r.raw_material_id == inp_data.raw_material_id), None
        )
        estimated = None
        if recipe_item:
            estimated = recipe_item.estimated_quantity * data.produced_quantity

        inp = ProductionLogInput(
            production_log_id=log.id,
            raw_material_id=inp_data.raw_material_id,
            quantity_used=inp_data.quantity_used,
            estimated_quantity=estimated,
        )
        db.add(inp)

        # Discount raw material stock
        raw_material.stock_quantity = max(
            Decimal("0"),
            (raw_material.stock_quantity or Decimal("0")) - inp_data.quantity_used
        )

        # Record stock movement for raw material
        movement_out = StockMovement(
            item_type="raw_material",
            item_id=inp_data.raw_material_id,
            movement_type="production_out",
            quantity=-inp_data.quantity_used,
            reference_id=log.id,
            notes=f"Uso en producción de {product.name}",
            created_by=created_by,
        )
        db.add(movement_out)

    # Add product stock
    product.stock_quantity = (product.stock_quantity or Decimal("0")) + data.produced_quantity

    # Record stock movement for product
    movement_in = StockMovement(
        item_type="product",
        item_id=data.product_id,
        movement_type="production_in",
        quantity=data.produced_quantity,
        reference_id=log.id,
        notes=f"Producción de lote #{log.id}",
        created_by=created_by,
    )
    db.add(movement_in)

    db.commit()
    db.refresh(log)
    return _log_to_response(log)


def delete_production_log(db: Session, log_id: int) -> None:
    from datetime import datetime
    log = get_production_log_by_id(db, log_id)
    log.deleted_at = datetime.now()
    db.commit()