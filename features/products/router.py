from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_admin
from features.products.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    RecipeItemCreate, RecipeItemResponse
)
from features.products.service import (
    get_products, get_product_by_id, create_product,
    update_product, delete_product,
    get_recipe, add_recipe_item, remove_recipe_item
)

router = APIRouter()


@router.get("", response_model=list[ProductResponse])
def list_products(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return get_products(db, include_inactive=include_inactive)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    from features.products.service import _to_response
    return _to_response(get_product_by_id(db, product_id))


@router.post("", response_model=ProductResponse)
def create(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return create_product(db, data)


@router.patch("/{product_id}", response_model=ProductResponse)
def update(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return update_product(db, product_id, data)


@router.delete("/{product_id}")
def delete(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    delete_product(db, product_id)
    return {"message": f"Producto {product_id} eliminado correctamente"}


@router.get("/{product_id}/recipe", response_model=list[RecipeItemResponse])
def list_recipe(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return get_recipe(db, product_id)


@router.post("/{product_id}/recipe", response_model=RecipeItemResponse)
def add_to_recipe(
    product_id: int,
    data: RecipeItemCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    return add_recipe_item(db, product_id, data)


@router.delete("/{product_id}/recipe/{recipe_item_id}")
def remove_from_recipe(
    product_id: int,
    recipe_item_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    remove_recipe_item(db, product_id, recipe_item_id)
    return {"message": "Item de receta eliminado correctamente"}