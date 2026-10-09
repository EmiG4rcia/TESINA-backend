from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    address = Column(TEXT, nullable=True)
    contact = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    scheduled_orders = relationship("ScheduledOrder", back_populates="destination")
    deliveries = relationship("Delivery", back_populates="destination")