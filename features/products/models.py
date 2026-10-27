from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    unit = Column(ENUM('kg', 'g', 'l', 'ml', 'unidad',
                       name='unit_type', create_type=False), nullable=False)
    stock_quantity = Column(DECIMAL(10, 3), default=0)
    stock_min_alert = Column(DECIMAL(10, 3), default=0)
    alert_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    recipes = relationship("ProductRecipe", back_populates="product")
    production_logs = relationship("ProductionLog", back_populates="product")
    scheduled_items = relationship("ScheduledOrderItem", back_populates="product")
    delivery_products = relationship("DeliveryProduct", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product",
                                   primaryjoin="and_(StockMovement.item_type=='product', "
                                               "StockMovement.item_id==Product.id)",
                                   foreign_keys="[StockMovement.item_id]",
                                   overlaps="raw_material")


class ProductRecipe(Base):
    __tablename__ = "product_recipes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    raw_material_id = Column(Integer, ForeignKey("raw_materials.id", ondelete="CASCADE"), nullable=False)
    estimated_quantity = Column(DECIMAL(10, 3), nullable=False)
    unit = Column(String(20), nullable=False)
    yield_quantity = Column(DECIMAL(10, 3), nullable=False, default=1)
    deleted_at = Column(TIMESTAMP, nullable=True)
    yield_unit = Column(String(20), nullable=False, default='unidad')
    product = relationship("Product", back_populates="recipes")
    raw_material = relationship("RawMaterial", back_populates="recipes")   