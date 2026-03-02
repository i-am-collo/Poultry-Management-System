from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.crud.product import (
    create_product,
    delete_product,
    get_product_by_id_for_supplier,
    get_products_by_supplier,
    update_product,
)
from app.db.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


def serialize_product(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        supplier_id=product.supplier_id,
        name=product.name,
        category=product.category,
        description=product.description,
        price_per_unit=product.price_per_unit,
        unit=product.unit,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.post("/products", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def add_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    product = create_product(db, current_user.id, payload)
    return serialize_product(product)


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    products = get_products_by_supplier(db, current_user.id)
    return [serialize_product(product) for product in products]


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product_record(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    product = get_product_by_id_for_supplier(db, product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    updated = update_product(db, product, payload)
    return serialize_product(updated)


@router.delete("/products/{product_id}", response_model=MessageResponse)
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    product = get_product_by_id_for_supplier(db, product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    delete_product(db, product)
    return {"message": "Product deleted successfully"}
