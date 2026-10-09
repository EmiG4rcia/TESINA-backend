from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    from features.auth.models import User
    user = db.query(User).filter(
        User.username == username,
        User.is_active == True,
        User.deleted_at == None,
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )

    return user


def get_current_admin(
    current_user=Depends(get_current_user),
):
    return current_user


def require_owner(
    current_user=Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de dueño para esta operación",
        )
    return current_user