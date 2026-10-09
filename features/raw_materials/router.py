from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_admin
from features.raw_materials.schemas import RawMaterialCreate, RawMaterialUpdate, RawMaterialResponse
from features.raw_materials.service import (
    get_raw_materials, get_raw_material_by_id,
    create_raw_material, update_raw_material, delete_raw_material
)

router = APIRouter()


@router.get("", response_model=list[RawMaterialResponse])
def list_raw_materials(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return get_raw_materials(db, include_inactive=include_inactive)


@router.get("/{rm_id}", response_model=RawMaterialResponse)
def get_raw_material(
    rm_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    from features.raw_materials.service import _to_response
    return _to_response(get_raw_material_by_id(db, rm_id))


@router.post("", response_model=RawMaterialResponse)
def create(
    data: RawMaterialCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return create_raw_material(db, data)


@router.patch("/{rm_id}", response_model=RawMaterialResponse)
def update(
    rm_id: int,
    data: RawMaterialUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return update_raw_material(db, rm_id, data)


@router.delete("/{rm_id}")
def delete(
    rm_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    delete_raw_material(db, rm_id)
    return {"message": f"Materia prima {rm_id} eliminada correctamente"}