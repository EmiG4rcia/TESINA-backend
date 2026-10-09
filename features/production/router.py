from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_admin
from features.production.schemas import ProductionLogCreate, ProductionLogResponse
from features.production.service import (
    get_production_logs,
    get_production_log_by_id,
    create_production_log,
    delete_production_log,
)

router = APIRouter()


@router.get("", response_model=list[ProductionLogResponse])
def list_logs(
    product_id: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return get_production_logs(db, product_id=product_id, skip=skip, limit=limit)


@router.get("/{log_id}", response_model=ProductionLogResponse)
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    from features.production.service import _log_to_response
    return _log_to_response(get_production_log_by_id(db, log_id))


@router.post("", response_model=ProductionLogResponse)
def create(
    data: ProductionLogCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return create_production_log(db, data)


@router.delete("/{log_id}")
def delete(
    log_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    delete_production_log(db, log_id)
    return {"message": f"Lote de producción {log_id} eliminado correctamente"}