from datetime import datetime
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from features.auth.models import User
from features.auth.schemas import UserCreate, UserUpdate, UserResponse
from core.security import create_access_token, get_password_hash, verify_password


def authenticate_user(db: Session, username: str, password: str) -> dict:
    user = db.query(User).filter(
        User.username == username,
        User.is_active == True,
        User.deleted_at == None,
    ).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    user.last_login = datetime.now()
    db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
    }


def get_users(db: Session) -> List[UserResponse]:
    users = db.query(User).filter(User.deleted_at == None).order_by(User.username).all()
    return [UserResponse.model_validate(u) for u in users]


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at == None,
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {user_id} no encontrado",
        )
    return user


def create_user(db: Session, data: UserCreate) -> UserResponse:
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario con el nombre '{data.username}'",
        )

    if data.role not in ("owner", "employee"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Valores permitidos: owner, employee",
        )

    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def update_user(db: Session, user_id: int, data: UserUpdate) -> UserResponse:
    user = get_user_by_id(db, user_id)
    update_data = data.model_dump(exclude_unset=True)

    if "role" in update_data and update_data["role"] not in ("owner", "employee"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Valores permitidos: owner, employee",
        )

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def delete_user(db: Session, user_id: int, current_user_id: int) -> None:
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No podés eliminar tu propio usuario",
        )
    user = get_user_by_id(db, user_id)
    user.deleted_at = datetime.now()
    db.commit()


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta",
        )
    user.password_hash = get_password_hash(new_password)
    db.commit()