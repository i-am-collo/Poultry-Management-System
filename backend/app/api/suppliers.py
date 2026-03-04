from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import distinct

from app.core.deps import require_role
from app.crud.product import (
    create_product,
    delete_product,
    get_product_by_id_for_supplier,
    get_products_by_supplier,
    update_product,
)
from app.crud.farm_invitation import create_farm_invitation
from app.db.database import get_db
from app.models.product import Product
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.farm_invitation import FarmInvitation
from app.schemas.auth import MessageResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.farm_invitation import FarmInvitationCreate, FarmInvitationResponse
from app.schemas.order import OrderResponse

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


def serialize_product(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        supplier_id=product.supplier_id,
        name=product.name,
        category=product.category,
        description=product.description,
        product_image=product.product_image,
        unit_price=product.unit_price,
        unit_of_measure=product.unit_of_measure,
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

@router.post("/invite-farm", status_code=status.HTTP_201_CREATED, response_model=FarmInvitationResponse)
def invite_farm(
    payload: FarmInvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    """Send an invitation to a farm"""
    invitation = create_farm_invitation(db, current_user.id, payload)
    return invitation


@router.get("/orders", response_model=list[OrderResponse])
def get_supplier_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    """Get all orders containing products from this supplier"""
    # Get all distinct orders that include products from the current supplier
    orders = db.query(Order).join(
        OrderItem, Order.id == OrderItem.order_id
    ).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        Product.supplier_id == current_user.id
    ).distinct().all()
    
    return orders


@router.get("/customers")
def get_supplier_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    """Get all farms/customers who have ordered from this supplier"""
    # Get all distinct users who placed orders containing this supplier's products
    customers = db.query(User).join(
        Order, User.id == Order.user_id
    ).join(
        OrderItem, Order.id == OrderItem.order_id
    ).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        Product.supplier_id == current_user.id
    ).distinct().all()
    
    # Build response with customer info and order stats
    response = []
    for customer in customers:
        # Count orders and calculate lifetime value
        customer_orders = db.query(Order).filter(Order.user_id == customer.id).join(
            OrderItem, Order.id == OrderItem.order_id
        ).join(
            Product, OrderItem.product_id == Product.id
        ).filter(Product.supplier_id == current_user.id).all()
        
        lifetime_value = sum(order.total_amount for order in customer_orders)
        
        response.append({
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "role": customer.role,
            "order_count": len(customer_orders),
            "lifetime_value": lifetime_value,
            "created_at": customer.created_at,
        })
    
    return response