from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_admin, require_owner
from features.auth.schemas import (
    LoginRequest, TokenResponse, UserCreate,
    UserUpdate, UserResponse, ChangePasswordRequest
)
from features.auth.service import (
    authenticate_user, get_users, get_user_by_id,
    create_user, update_user, delete_user, change_password
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return authenticate_user(db, data.username, data.password)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_owner),
):
    return get_users(db)


@router.post("/users", response_model=UserResponse)
def create_new_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_owner),
):
    return create_user(db, data)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_existing_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_owner),
):
    return update_user(db, user_id, data)


@router.delete("/users/{user_id}")
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_owner),
):
    delete_user(db, user_id, current_user.id)
    return {"message": f"Usuario {user_id} eliminado correctamente"}


@router.post("/change-password")
def change_my_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    change_password(db, current_user, data.current_password, data.new_password)
    return {"message": "Contraseña actualizada correctamente"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_admin)):
    return current_user