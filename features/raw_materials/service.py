from typing import List
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from features.raw_materials.models import RawMaterial
from features.raw_materials.schemas import RawMaterialCreate, RawMaterialUpdate, RawMaterialResponse


def _to_response(rm: RawMaterial) -> RawMaterialResponse:
    data = RawMaterialResponse.model_validate(rm)
    data.is_low_stock = (
        rm.alert_enabled
        and rm.stock_quantity is not None
        and rm.stock_min_alert is not None
        and float(rm.stock_quantity) <= float(rm.stock_min_alert)
    )
    return data


def get_raw_materials(db: Session, include_inactive: bool = False) -> List[RawMaterialResponse]:
    query = db.query(RawMaterial).filter(RawMaterial.deleted_at == None)
    if not include_inactive:
        query = query.filter(RawMaterial.is_active == True)
    return [_to_response(rm) for rm in query.order_by(RawMaterial.name).all()]


def get_raw_material_by_id(db: Session, rm_id: int) -> RawMaterial:
    rm = db.query(RawMaterial).filter(
        RawMaterial.id == rm_id,
        RawMaterial.deleted_at == None
    ).first()
    if not rm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Materia prima {rm_id} no encontrada")
    return rm


def create_raw_material(db: Session, data: RawMaterialCreate) -> RawMaterialResponse:
    existing = db.query(RawMaterial).filter(RawMaterial.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe una materia prima con el nombre '{data.name}'")
    rm = RawMaterial(**data.model_dump())
    db.add(rm)
    db.commit()
    db.refresh(rm)
    return _to_response(rm)


def update_raw_material(db: Session, rm_id: int, data: RawMaterialUpdate) -> RawMaterialResponse:
    rm = get_raw_material_by_id(db, rm_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rm, key, value)
    db.commit()
    db.refresh(rm)
    return _to_response(rm)


def delete_raw_material(db: Session, rm_id: int) -> None:
    from datetime import datetime
    rm = get_raw_material_by_id(db, rm_id)
    rm.deleted_at = datetime.now()
    db.commit()