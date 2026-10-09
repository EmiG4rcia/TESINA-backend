from datetime import datetime
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from features.destinations.models import Destination
from features.destinations.schemas import DestinationCreate, DestinationUpdate, DestinationResponse


def get_destinations(db: Session, include_inactive: bool = False) -> List[DestinationResponse]:
    query = db.query(Destination).filter(Destination.deleted_at == None)
    if not include_inactive:
        query = query.filter(Destination.is_active == True)
    return [DestinationResponse.model_validate(d) for d in query.order_by(Destination.name).all()]


def get_destination_by_id(db: Session, destination_id: int) -> Destination:
    destination = db.query(Destination).filter(
        Destination.id == destination_id,
        Destination.deleted_at == None
    ).first()
    if not destination:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Destino {destination_id} no encontrado")
    return destination


def create_destination(db: Session, data: DestinationCreate) -> DestinationResponse:
    existing = db.query(Destination).filter(Destination.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe un destino con el nombre '{data.name}'")
    destination = Destination(**data.model_dump())
    db.add(destination)
    db.commit()
    db.refresh(destination)
    return DestinationResponse.model_validate(destination)


def update_destination(db: Session, destination_id: int, data: DestinationUpdate) -> DestinationResponse:
    destination = get_destination_by_id(db, destination_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(destination, key, value)
    db.commit()
    db.refresh(destination)
    return DestinationResponse.model_validate(destination)


def delete_destination(db: Session, destination_id: int) -> None:
    destination = get_destination_by_id(db, destination_id)
    destination.deleted_at = datetime.now()
    db.commit()