from fastapi import APIRouter, Depends, HTTPException, status as http_status, Body
from sqlalchemy.orm import Session
from sqlalchemy import distinct
import json

from app.core.deps import require_role
from app.crud.product import (
    create_product,
    delete_product,
    get_product_by_id_for_supplier,
    get_products_by_supplier,
    update_product,
)
from app.crud.supplier import create_supplier_profile, get_supplier_profile, supplier_profile_exists
from app.crud.farm_invitation import create_farm_invitation
from app.db.database import get_db
from app.models.product import Product
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.farm_invitation import FarmInvitation
from app.schemas.auth import MessageResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate, SupplierRegisterRequest
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
        visible_to_farmers_only=product.visible_to_farmers_only,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def serialize_order_item(item: OrderItem) -> dict:
    """Serialize OrderItem to dict with product name"""
    return {
        "id": item.id,
        "order_id": item.order_id,
        "product_id": item.product_id,
        "product_name": item.product.name if item.product else "Unknown Product",
        "quantity": item.quantity,
        "unit_price": item.unit_price,
        "total_price": item.total_price,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def serialize_order(order: Order) -> dict:
    """Serialize Order to dict with buyer and item details"""
    buyer = order.user if order.user else None
    return {
        "id": order.id,
        "user_id": order.user_id,
        "buyer_email": buyer.email if buyer else None,
        "buyer_farm_name": buyer.name if buyer else "Unknown",
        "total_amount": order.total_amount,
        "order_status": order.order_status.value if hasattr(order.order_status, 'value') else str(order.order_status),
        "payment_status": order.payment_status.value if hasattr(order.payment_status, 'value') else str(order.payment_status),
        "items": [serialize_order_item(item) for item in order.items],
        "note": order.note,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.post("/products", status_code=http_status.HTTP_201_CREATED, response_model=ProductResponse)
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

@router.post("/invite-farm", status_code=http_status.HTTP_201_CREATED, response_model=FarmInvitationResponse)
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
    
    return [serialize_order(order) for order in orders]


@router.patch("/orders/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    """Update order status (supplier can approve/reject orders)"""
    from app.models.order import OrderStatus
    
    # Verify order exists and supplier has products in this order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify supplier has products in this order
    has_products = db.query(OrderItem).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        OrderItem.order_id == order_id,
        Product.supplier_id == current_user.id
    ).first()
    
    if not has_products:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have products in this order"
        )
    
    # Validate status
    try:
        order_status = OrderStatus[status]
    except KeyError:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed values: {', '.join([s.value for s in OrderStatus])}"
        )
    
    # Update order status
    order.order_status = order_status
    db.commit()
    db.refresh(order)
    
    return serialize_order(order)


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


@router.get("/all-farms")
def get_all_available_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    """Get all farms available for invitation"""
    # Get all farmer users who haven't been invited yet
    all_farmers = db.query(User).filter(User.role == 'farmer').all()
    
    # Get already invited farm emails
    invited_emails = db.query(FarmInvitation.farmer_email).filter(
        FarmInvitation.supplier_id == current_user.id
    ).all()
    invited_emails = {email[0] for email in invited_emails}
    
    # Build response with farm info
    response = []
    for farmer in all_farmers:
        # Skip if already invited
        if farmer.email in invited_emails:
            continue
        
        # Try to get farm profile details
        farm_info = {
            "id": farmer.id,
            "farmer_name": farmer.name,
            "farmer_email": farmer.email,
            "farm_name": farmer.name,  # Default to farmer name if no profile
            "location": farmer.phone or "Not specified",
            "flock_count": 0,
            "size_acres": "—",
        }
        
        response.append(farm_info)
    
    return response


# ════════════════════════════════════
# ONBOARDING REGISTRATION ENDPOINT
# ════════════════════════════════════

@router.post("/register", status_code=http_status.HTTP_201_CREATED)
def supplier_complete_registration(
    payload: SupplierRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    """
    Complete supplier onboarding registration in a single call.
    Stores supplier profile information.
    """
    try:
        # Check if profile already exists
        if supplier_profile_exists(db, current_user.id):
            raise HTTPException(status_code=400, detail="Supplier profile already exists for this user")
        
        # Create supplier profile
        profile = create_supplier_profile(db, current_user.id, payload)
        
        return {
            "message": "Supplier registration completed successfully",
            "supplier_id": current_user.id,
            "business_name": profile.business_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@router.get("/profile", response_model=dict)
def get_supplier_profile_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    """Get supplier profile"""
    profile = get_supplier_profile(db, current_user.id)
    
    if not profile:
        # If profile doesn't exist yet, return basic info
        products = get_products_by_supplier(db, current_user.id)
        return {
            "supplier_id": current_user.id,
            "email": current_user.email,
            "phone": current_user.phone or "",
            "products_count": len(products),
            "products": [serialize_product(p) for p in products[:10]]
        }
    
    products = get_products_by_supplier(db, current_user.id)
    categories = json.loads(profile.categories) if isinstance(profile.categories, str) else profile.categories
    
    return {
        "supplier_id": current_user.id,
        "business_name": profile.business_name,
        "contact_person": profile.contact_person,
        "email": profile.email,
        "phone": profile.phone,
        "county": profile.county,
        "kra_pin": profile.kra_pin,
        "categories": categories,
        "payment_mpesa_till": profile.payment_mpesa_till,
        "products_count": len(products),
        "products": [serialize_product(p) for p in products[:10]]
    }