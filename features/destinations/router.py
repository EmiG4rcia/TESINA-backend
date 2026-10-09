from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_admin
from features.destinations.schemas import DestinationCreate, DestinationUpdate, DestinationResponse
from features.destinations.service import (
    get_destinations, get_destination_by_id,
    create_destination, update_destination, delete_destination
)

router = APIRouter()


@router.get("", response_model=list[DestinationResponse])
def list_destinations(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return get_destinations(db, include_inactive=include_inactive)


@router.get("/{destination_id}", response_model=DestinationResponse)
def get_destination(
    destination_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return DestinationResponse.model_validate(
        get_destination_by_id(db, destination_id)
    )


@router.post("", response_model=DestinationResponse)
def create(
    data: DestinationCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return create_destination(db, data)


@router.patch("/{destination_id}", response_model=DestinationResponse)
def update(
    destination_id: int,
    data: DestinationUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return update_destination(db, destination_id, data)


@router.delete("/{destination_id}")
def delete(
    destination_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    delete_destination(db, destination_id)
    return {"message": f"Destino {destination_id} eliminado correctamente"}