from typing import List
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from features.products.models import Product, ProductRecipe
from features.products.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    RecipeItemCreate, RecipeItemResponse
)


def _to_response(product: Product) -> ProductResponse:
    data = ProductResponse.model_validate(product)
    data.is_low_stock = (
        product.alert_enabled
        and product.stock_quantity is not None
        and product.stock_min_alert is not None
        and float(product.stock_quantity) <= float(product.stock_min_alert)
    )
    return data


def get_products(db: Session, include_inactive: bool = False) -> List[ProductResponse]:
    query = db.query(Product).filter(Product.deleted_at == None)
    if not include_inactive:
        query = query.filter(Product.is_active == True)
    return [_to_response(p) for p in query.order_by(Product.name).all()]


def get_product_by_id(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.deleted_at == None
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Producto {product_id} no encontrado")
    return product


def create_product(db: Session, data: ProductCreate) -> ProductResponse:
    existing = db.query(Product).filter(Product.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe un producto con el nombre '{data.name}'")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return _to_response(product)


def update_product(db: Session, product_id: int, data: ProductUpdate) -> ProductResponse:
    product = get_product_by_id(db, product_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return _to_response(product)


def delete_product(db: Session, product_id: int) -> None:
    product = get_product_by_id(db, product_id)
    product.deleted_at = datetime.now()
    db.commit()


def get_recipe(db: Session, product_id: int) -> List[RecipeItemResponse]:
    items = db.query(ProductRecipe).filter(
        ProductRecipe.product_id == product_id,
        ProductRecipe.deleted_at == None
    ).all()
    return [
        RecipeItemResponse(
            id=item.id,
            raw_material_id=item.raw_material_id,
            estimated_quantity=item.estimated_quantity,
            unit=item.unit,
            yield_quantity=item.yield_quantity,
            yield_unit=item.yield_unit,
            raw_material_name=item.raw_material.name if item.raw_material else None,
        )
        for item in items
    ]


def add_recipe_item(db: Session, product_id: int, data: RecipeItemCreate) -> RecipeItemResponse:
    existing = db.query(ProductRecipe).filter(
        ProductRecipe.product_id == product_id,
        ProductRecipe.raw_material_id == data.raw_material_id,
        ProductRecipe.deleted_at == None
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Esta materia prima ya está en la receta")
    item = ProductRecipe(product_id=product_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return RecipeItemResponse(
        id=item.id,
        raw_material_id=item.raw_material_id,
        estimated_quantity=item.estimated_quantity,
        unit=item.unit,
        yield_quantity=item.yield_quantity,
        yield_unit=item.yield_unit,
        raw_material_name=item.raw_material.name if item.raw_material else None,
    )


def remove_recipe_item(db: Session, product_id: int, recipe_item_id: int) -> None:
    item = db.query(ProductRecipe).filter(
        ProductRecipe.id == recipe_item_id,
        ProductRecipe.product_id == product_id
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Item de receta no encontrado")
    item.deleted_at = datetime.now()
    db.commit()