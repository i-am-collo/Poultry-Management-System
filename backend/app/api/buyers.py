from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.crud.product import get_product_by_id, search_active_products
from app.crud.buyer import create_buyer_profile, buyer_profile_exists
from app.db.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse
from app.schemas.product import BuyerProductSearchResponse, BuyerRegisterRequest

router = APIRouter(prefix="/buyers", tags=["Buyers"])


def serialize_order_item(item: OrderItem) -> OrderItemResponse:
    return OrderItemResponse(
        id=item.id,
        order_id=item.order_id,
        product_id=item.product_id,
        product_name=item.product.name if item.product else "Unknown Product",
        quantity=item.quantity,
        unit_price=item.unit_price,
        total_price=item.total_price,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def serialize_order(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total_amount=order.total_amount,
        order_status=order.order_status.value if hasattr(order.order_status, 'value') else str(order.order_status),
        payment_status=order.payment_status.value if hasattr(order.payment_status, 'value') else str(order.payment_status),
        items=[serialize_order_item(item) for item in order.items],
        note=order.note,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("/search", response_model=list[BuyerProductSearchResponse])
def search_products(
    q: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    # Get all active products (both supplier and farmer)
    query = db.query(Product).filter(Product.is_active == True)
    
    if q:
        query = query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.description.ilike(f"%{q}%")) |
            (Product.category.ilike(f"%{q}%"))
        )
    
    products = query.all()
    
    if not products:
        return []

    # Get supplier and farmer names
    supplier_ids = {product.supplier_id for product in products if product.supplier_id}
    farmer_ids = {product.farmer_id for product in products if product.farmer_id}
    
    suppliers = db.query(User).filter(User.id.in_(supplier_ids)).all() if supplier_ids else []
    farmers = db.query(User).filter(User.id.in_(farmer_ids)).all() if farmer_ids else []
    
    supplier_name_by_id = {supplier.id: supplier.name for supplier in suppliers}
    farmer_name_by_id = {farmer.id: farmer.name for farmer in farmers}

    return [
        BuyerProductSearchResponse(
            id=product.id,
            supplier_id=product.supplier_id,
            supplier_name=supplier_name_by_id.get(product.supplier_id, "Unknown supplier") if product.supplier_id else None,
            farmer_id=product.farmer_id,
            farmer_name=farmer_name_by_id.get(product.farmer_id, "Unknown farmer") if product.farmer_id else None,
            product_source=product.product_source,
            name=product.name,
            category=product.category,
            description=product.description,
            product_image=product.product_image,
            unit_price=product.unit_price,
            unit_of_measure=product.unit_of_measure,
            stock_quantity=product.stock_quantity,
            visible_to_farmers_only=product.visible_to_farmers_only,
        )
        for product in products
    ]


@router.post("/orders", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    # Validate all products exist and have sufficient stock
    total_amount = 0.0
    items_data = []
    
    for item_payload in payload.items:
        product = get_product_by_id(db, item_payload.product_id)
        if not product or not product.is_active:
            raise HTTPException(status_code=404, detail=f"Product {item_payload.product_id} not found")

        if product.stock_quantity < item_payload.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
        
        item_total = item_payload.quantity * product.unit_price
        total_amount += item_total
        items_data.append({
            "product": product,
            "quantity": item_payload.quantity,
            "unit_price": product.unit_price,
            "total_price": item_total,
        })
    
    # Create order
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        note=payload.note,
    )
    db.add(order)
    db.flush()  # Flush to get the order ID without committing
    
    # Create order items and reduce stock
    for item_data in items_data:
        product = item_data["product"]
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total_price=item_data["total_price"],
        )
        product.stock_quantity -= item_data["quantity"]
        db.add(order_item)
        db.add(product)
    
    db.commit()
    db.refresh(order)
    
    return serialize_order(order)


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return [serialize_order(order) for order in orders]


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return serialize_order(order)


# ════════════════════════════════════
# ONBOARDING REGISTRATION ENDPOINT
# ════════════════════════════════════

@router.post("/register", status_code=status.HTTP_201_CREATED)
def buyer_complete_registration(
    payload: BuyerRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer")),
):
    """
    Complete buyer onboarding registration in a single call.
    Stores buyer profile information.
    """
    try:
        # Check if profile already exists
        if buyer_profile_exists(db, current_user.id):
            raise HTTPException(status_code=400, detail="Buyer profile already exists for this user")
        
        # Create buyer profile
        profile = create_buyer_profile(db, current_user.id, payload)
        
        return {
            "message": "Buyer registration completed successfully",
            "buyer_id": current_user.id,
            "business_name": profile.business_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@router.get("/profile", response_model=dict)
def get_buyer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer")),
):
    """Get buyer profile and order history"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    
    return {
        "buyer_id": current_user.id,
        "email": current_user.email,
        "phone": current_user.phone or "",
        "orders_count": len(orders),
        "total_spent": sum(order.total_amount for order in orders),
        "recent_orders": [serialize_order(o) for o in orders[-5:]]  # Last 5 orders
    }
