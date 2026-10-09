from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from features.deliveries.service import (
     get_deliveries, get_delivery_by_id,
    create_delivery, complete_delivery,
    update_delivery, delete_delivery,
    _delivery_to_response
)
from core.database import get_db
from core.dependencies import get_current_admin
from features.deliveries.schemas import (
    DeliveryCreate, DeliveryUpdate, DeliveryResponse
)
from features.deliveries.service import (
    get_deliveries, get_delivery_by_id,
    create_delivery, complete_delivery,
    update_delivery, delete_delivery
)

router = APIRouter()


@router.get("", response_model=list[DeliveryResponse])
def list_deliveries(
    destination_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return get_deliveries(db, destination_id=destination_id,
                          date_from=date_from, date_to=date_to, status=status)


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return _delivery_to_response(get_delivery_by_id(db, delivery_id))


@router.post("", response_model=DeliveryResponse)
def create(
    data: DeliveryCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return create_delivery(db, data)


@router.post("/{delivery_id}/complete", response_model=DeliveryResponse)
def complete(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return complete_delivery(db, delivery_id)


@router.patch("/{delivery_id}", response_model=DeliveryResponse)
def update(
    delivery_id: int,
    data: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return update_delivery(db, delivery_id, data)


@router.delete("/{delivery_id}")
def delete(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    delete_delivery(db, delivery_id)
    return {"message": f"Entrega {delivery_id} eliminada correctamente"}