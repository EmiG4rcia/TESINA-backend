from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_admin
from features.stock.schemas import StockMovementResponse, StockPurchase, StockAdjustment
from features.stock.service import get_movements, register_purchase, register_adjustment

router = APIRouter()


@router.get("", response_model=list[StockMovementResponse])
def list_movements(
    item_type: Optional[str] = Query(None),
    item_id: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return get_movements(db, item_type=item_type, item_id=item_id, skip=skip, limit=limit)


@router.post("/purchase", response_model=StockMovementResponse)
def purchase(
    data: StockPurchase,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return register_purchase(db, data)


@router.post("/adjustment", response_model=StockMovementResponse)
def adjustment(
    data: StockAdjustment,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return register_adjustment(db, data)