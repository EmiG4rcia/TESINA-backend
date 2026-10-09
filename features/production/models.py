from sqlalchemy import Column, Integer, DECIMAL, TIMESTAMP, TEXT, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class ProductionLog(Base):
    __tablename__ = "production_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    produced_quantity = Column(DECIMAL(10, 3), nullable=False)
    estimated_quantity = Column(DECIMAL(10, 3), nullable=True)
    notes = Column(TEXT, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    product = relationship("Product", back_populates="production_logs")
    created_by_user = relationship("User", foreign_keys=[created_by])
    inputs = relationship("ProductionLogInput", back_populates="production_log")


class ProductionLogInput(Base):
    __tablename__ = "production_log_inputs"

    id = Column(Integer, primary_key=True, index=True)
    production_log_id = Column(Integer, ForeignKey("production_logs.id", ondelete="CASCADE"), nullable=False)
    raw_material_id = Column(Integer, ForeignKey("raw_materials.id"), nullable=False)
    quantity_used = Column(DECIMAL(10, 3), nullable=False)
    estimated_quantity = Column(DECIMAL(10, 3), nullable=True)

    production_log = relationship("ProductionLog", back_populates="inputs")
    raw_material = relationship("RawMaterial", back_populates="production_inputs")