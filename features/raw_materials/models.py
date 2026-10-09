from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base

unit_enum = ENUM('kg', 'g', 'l', 'ml', 'unidad', name='unit_type', create_type=True)


class RawMaterial(Base):
    __tablename__ = "raw_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    unit = Column(unit_enum, nullable=False)
    stock_quantity = Column(DECIMAL(10, 3), default=0)
    stock_min_alert = Column(DECIMAL(10, 3), default=0)
    alert_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    recipes = relationship("ProductRecipe", back_populates="raw_material")
    production_inputs = relationship("ProductionLogInput", back_populates="raw_material")
    stock_movements = relationship("StockMovement", back_populates="raw_material",
                                   primaryjoin="and_(StockMovement.item_type=='raw_material', "
                                               "StockMovement.item_id==RawMaterial.id)",
                                   foreign_keys="[StockMovement.item_id]",
                                   overlaps="product")