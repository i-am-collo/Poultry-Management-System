from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from math import ceil

from app.core.deps import require_role
from app.crud.product import get_product_by_id, search_active_products
from app.crud.buyer import create_buyer_profile, buyer_profile_exists
from app.db.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.farms import Farm
from app.models.supplier import SupplierProfile
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
    buyer = order.user if order.user else None
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        buyer_email=buyer.email if buyer else None,
        buyer_farm_name=buyer.name if buyer else None,
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


# ════════════════════════════════════
# 1. GET /buyers/products - PAGINATED PRODUCT LIST
# ════════════════════════════════════

@router.get("/products")
def list_products(
    category: str | None = Query(None),
    source: str | None = Query(None),  # "supplier" or "farmer"
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    in_stock: bool | None = Query(None),
    search: str | None = Query(None, min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    """
    Paginated product list with filtering.
    Returns: { items: [...], total: int, page: int, pages: int }
    """
    # Base query: active products not hidden from buyers
    query = db.query(Product).filter(
        Product.is_active == True,
        Product.visible_to_farmers_only == False
    )
    
    # Apply filters
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    
    if source:
        if source.lower() == "supplier":
            query = query.filter(Product.supplier_id.isnot(None))
        elif source.lower() == "farmer":
            query = query.filter(Product.farmer_id.isnot(None))
    
    if min_price is not None:
        query = query.filter(Product.unit_price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.unit_price <= max_price)
    
    if in_stock is True:
        query = query.filter(Product.stock_quantity > 0)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.description.ilike(f"%{search}%")) |
            (Product.category.ilike(f"%{search}%"))
        )
    
    # Get total count before pagination
    total = query.count()
    pages = ceil(total / limit) if total > 0 else 1
    
    # Apply pagination
    products = query.offset((page - 1) * limit).limit(limit).all()
    
    # Get seller names
    supplier_ids = {p.supplier_id for p in products if p.supplier_id}
    farmer_ids = {p.farmer_id for p in products if p.farmer_id}
    
    suppliers = db.query(User).filter(User.id.in_(supplier_ids)).all() if supplier_ids else []
    farmers = db.query(User).filter(User.id.in_(farmer_ids)).all() if farmer_ids else []
    
    supplier_names = {s.id: s.name for s in suppliers}
    farmer_names = {f.id: f.name for f in farmers}
    
    items = [
        BuyerProductSearchResponse(
            id=p.id,
            supplier_id=p.supplier_id,
            supplier_name=supplier_names.get(p.supplier_id),
            farmer_id=p.farmer_id,
            farmer_name=farmer_names.get(p.farmer_id),
            product_source=p.product_source,
            name=p.name,
            category=p.category,
            description=p.description,
            product_image=p.product_image,
            unit_price=p.unit_price,
            unit_of_measure=p.unit_of_measure,
            stock_quantity=p.stock_quantity,
            visible_to_farmers_only=p.visible_to_farmers_only,
        )
        for p in products
    ]
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages,
    }


# ════════════════════════════════════
# 2. GET /buyers/products/{product_id} - SINGLE PRODUCT DETAIL
# ════════════════════════════════════

@router.get("/products/{product_id}")
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    """
    Get single product detail with seller information.
    Returns: BuyerProductSearchResponse + farm_name, farm_location, seller_description
    """
    product = get_product_by_id(db, product_id)
    if not product or not product.is_active or product.visible_to_farmers_only:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get seller info
    seller_name = None
    seller_description = None
    farm_name = None
    farm_location = None
    
    if product.supplier_id:
        seller = db.query(User).filter(User.id == product.supplier_id).first()
        if seller:
            seller_name = seller.name
        supplier_profile = db.query(SupplierProfile).filter(
            SupplierProfile.supplier_id == product.supplier_id
        ).first()
        if supplier_profile:
            seller_description = supplier_profile.business_name
    
    elif product.farmer_id:
        seller = db.query(User).filter(User.id == product.farmer_id).first()
        if seller:
            seller_name = seller.name
        farm = db.query(Farm).filter(Farm.farmer_id == product.farmer_id).first()
        if farm:
            farm_name = farm.farm_name
            farm_location = farm.location
            seller_description = farm.description
    
    return {
        "id": product.id,
        "supplier_id": product.supplier_id,
        "supplier_name": seller_name if product.supplier_id else None,
        "farmer_id": product.farmer_id,
        "farmer_name": seller_name if product.farmer_id else None,
        "product_source": product.product_source,
        "name": product.name,
        "category": product.category,
        "description": product.description,
        "product_image": product.product_image,
        "unit_price": product.unit_price,
        "unit_of_measure": product.unit_of_measure,
        "stock_quantity": product.stock_quantity,
        "visible_to_farmers_only": product.visible_to_farmers_only,
        "farm_name": farm_name,
        "farm_location": farm_location,
        "seller_description": seller_description,
    }


# ════════════════════════════════════
# 3. GET /buyers/sellers/{seller_id} - SELLER PROFILE WITH PRODUCTS
# ════════════════════════════════════

@router.get("/sellers/{seller_id}")
def get_seller_profile(
    seller_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    """
    Get seller profile (supplier or farmer) with their products.
    Returns: { seller_id, name, role, business_name, county, description, products: [...] }
    """
    seller = db.query(User).filter(User.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Build response based on seller role
    seller_role = seller.role.value if hasattr(seller.role, 'value') else str(seller.role)
    response = {
        "seller_id": seller.id,
        "name": seller.name,
        "role": seller_role,
        "business_name": None,
        "county": None,
        "description": None,
        "products": [],
    }
    
    if seller_role == "supplier":
        supplier_profile = db.query(SupplierProfile).filter(
            SupplierProfile.supplier_id == seller_id
        ).first()
        if supplier_profile:
            response["business_name"] = supplier_profile.business_name
            response["county"] = supplier_profile.county
        
        # Get supplier's products
        products = db.query(Product).filter(
            Product.supplier_id == seller_id,
            Product.is_active == True,
            Product.visible_to_farmers_only == False
        ).all()
    
    elif seller_role == "farmer":
        farm = db.query(Farm).filter(Farm.farmer_id == seller_id).first()
        if farm:
            response["business_name"] = farm.farm_name
            response["county"] = farm.location
            response["description"] = farm.description
        
        # Get farmer's products
        products = db.query(Product).filter(
            Product.farmer_id == seller_id,
            Product.is_active == True,
            Product.visible_to_farmers_only == False
        ).all()
    
    else:
        raise HTTPException(status_code=400, detail="Seller is not a supplier or farmer")
    
    # Serialize products
    response["products"] = [
        BuyerProductSearchResponse(
            id=p.id,
            supplier_id=p.supplier_id,
            supplier_name=seller.name if p.supplier_id else None,
            farmer_id=p.farmer_id,
            farmer_name=seller.name if p.farmer_id else None,
            product_source=p.product_source,
            name=p.name,
            category=p.category,
            description=p.description,
            product_image=p.product_image,
            unit_price=p.unit_price,
            unit_of_measure=p.unit_of_measure,
            stock_quantity=p.stock_quantity,
            visible_to_farmers_only=p.visible_to_farmers_only,
        )
        for p in products
    ]
    
    return response


# ════════════════════════════════════
# 4. GET /buyers/products/{product_id}/stock - STOCK POLLING
# ════════════════════════════════════

@router.get("/products/{product_id}/stock")
def check_product_stock(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    """
    Check current stock for a product (polling endpoint, no mutation).
    Returns: { product_id, stock_quantity, is_active }
    """
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product_id": product.id,
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active,
    }


# ════════════════════════════════════
# 5. POST /buyers/orders/{order_id}/cancel - CANCEL ORDER
# ════════════════════════════════════

@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer", "farmer")),
):
    """
    Cancel an order. Only allowed if order_status is 'pending'.
    Buyer can only cancel their own orders.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify ownership
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own orders")
    
    # Check order status
    order_status_value = order.order_status.value if hasattr(order.order_status, 'value') else str(order.order_status)
    if order_status_value != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order with status '{order_status_value}'. Only pending orders can be cancelled."
        )
    
    # Update order status and restore stock
    order.order_status = "cancelled"
    for item in order.items:
        item.product.stock_quantity += item.quantity
        db.add(item.product)
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return serialize_order(order)
