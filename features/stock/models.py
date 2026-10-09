from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, TEXT, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base

item_type_enum = ENUM('product', 'raw_material', name='item_type', create_type=True)
movement_type_enum = ENUM(
    'purchase', 'production_in', 'production_out',
    'delivery', 'adjustment', 'waste',
    name='movement_type', create_type=True
)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(item_type_enum, nullable=False)
    item_id = Column(Integer, nullable=False)
    movement_type = Column(movement_type_enum, nullable=False)
    quantity = Column(DECIMAL(10, 3), nullable=False)
    reference_id = Column(Integer, nullable=True)
    notes = Column(TEXT, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    created_by_user = relationship("User", foreign_keys=[created_by])
    product = relationship(
        "Product",
        primaryjoin="and_(StockMovement.item_type=='product', StockMovement.item_id==Product.id)",
        foreign_keys="[StockMovement.item_id]",
        overlaps="raw_material,stock_movements"
    )
    raw_material = relationship(
        "RawMaterial",
        primaryjoin="and_(StockMovement.item_type=='raw_material', StockMovement.item_id==RawMaterial.id)",
        foreign_keys="[StockMovement.item_id]",
        overlaps="product,stock_movements"
    )