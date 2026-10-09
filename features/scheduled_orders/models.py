from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, TEXT, ForeignKey, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base

order_status_enum = ENUM('pending', 'completed', 'cancelled', name='order_status', create_type=True)


class ScheduledOrder(Base):
    __tablename__ = "scheduled_orders"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    status = Column(order_status_enum, default='pending')
    notes = Column(TEXT, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    __table_args__ = (
        UniqueConstraint('destination_id', 'scheduled_date', name='uq_scheduled_order'),
    )

    destination = relationship("Destination", back_populates="scheduled_orders")
    created_by_user = relationship("User", foreign_keys=[created_by])
    items = relationship("ScheduledOrderItem", back_populates="scheduled_order")
    deliveries = relationship("Delivery", back_populates="scheduled_order")


class ScheduledOrderItem(Base):
    __tablename__ = "scheduled_order_items"

    id = Column(Integer, primary_key=True, index=True)
    scheduled_order_id = Column(Integer, ForeignKey("scheduled_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    planned_quantity = Column(DECIMAL(10, 3), nullable=False)
    modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    modified_at = Column(TIMESTAMP, nullable=True)

    scheduled_order = relationship("ScheduledOrder", back_populates="items")
    product = relationship("Product", back_populates="scheduled_items")
    modified_by_user = relationship("User", foreign_keys=[modified_by])