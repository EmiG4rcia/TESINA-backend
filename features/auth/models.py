from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base

user_role_enum = ENUM('owner', 'employee', name='user_role', create_type=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(user_role_enum, nullable=False, default='employee')
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)