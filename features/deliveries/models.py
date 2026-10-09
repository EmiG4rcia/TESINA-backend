from sqlalchemy import Column, Integer, DECIMAL, TIMESTAMP, TEXT, ForeignKey, Date, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False)
    scheduled_order_id = Column(Integer, ForeignKey("scheduled_orders.id"), nullable=True)
    delivery_date = Column(Date, nullable=False)
    delivery_time = Column(Time, nullable=True)
    status = Column(ENUM('pending', 'completed', 'cancelled',
                         name='order_status', create_type=False), default='pending')
    notes = Column(TEXT, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)

    __table_args__ = (
        UniqueConstraint('destination_id', 'delivery_date', name='uq_delivery'),
    )

    destination = relationship("Destination", back_populates="deliveries")
    scheduled_order = relationship("ScheduledOrder", back_populates="deliveries")
    created_by_user = relationship("User", foreign_keys=[created_by])
    products = relationship("DeliveryProduct", back_populates="delivery")


class DeliveryProduct(Base):
    __tablename__ = "delivery_products"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    planned_quantity = Column(DECIMAL(10, 3), nullable=True)
    actual_quantity = Column(DECIMAL(10, 3), nullable=True)
    modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    delivery = relationship("Delivery", back_populates="products")
    product = relationship("Product", back_populates="delivery_products")
    modified_by_user = relationship("User", foreign_keys=[modified_by])