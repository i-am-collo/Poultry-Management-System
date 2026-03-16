from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.crud.flock import (
    create_flock,
    delete_flock,
    get_flock_by_id_for_farmer,
    get_flocks_by_farmer,
    update_flock,
)
from app.crud.farm import (
    create_farm,
    get_farm_by_farmer,
    update_farm,
)
from app.db.database import get_db
from app.models.flock import Flock
from app.models.farms import Farm
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.farm_invitation import FarmInvitation
from app.models.message import Message
from app.schemas.auth import MessageResponse
from app.schemas.flock import FlockCreate, FlockResponse, FlockUpdate
from app.schemas.farm import FarmCreate, FarmResponse, FarmUpdate, FarmerRegisterRequest
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.order import OrderResponse, OrderItemResponse

router = APIRouter(prefix="/farmers", tags=["Farmers"])


def serialize_flock(flock: Flock) -> FlockResponse:
    return FlockResponse(
        id=flock.id,
        farmer_id=flock.farmer_id,
        breed=flock.breed,
        bird_type=flock.bird_type,
        quantity=flock.quantity,
        age_weeks=flock.age_weeks,
        purpose=flock.purpose,
        health_status=flock.health_status,
        daily_feed_kg=flock.daily_feed_kg,
        notes=flock.notes,
        created_at=flock.created_at,
        updated_at=flock.updated_at,
    )


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
        buyer_farm_name=buyer.email.split('@')[0] if buyer and buyer.email else "Unknown",
        total_amount=order.total_amount,
        order_status=order.order_status.value if hasattr(order.order_status, 'value') else str(order.order_status),
        payment_status=order.payment_status.value if hasattr(order.payment_status, 'value') else str(order.payment_status),
        items=[serialize_order_item(item) for item in order.items],
        note=order.note,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("/orders", response_model=list[OrderResponse])
def get_farmer_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get all orders containing products from this farmer"""
    orders = db.query(Order).join(
        OrderItem, Order.id == OrderItem.order_id
    ).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        Product.farmer_id == current_user.id
    ).distinct().all()
    
    return [serialize_order(order) for order in orders]


@router.put("/orders/{order_id}/dispatch", response_model=OrderResponse)
def dispatch_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Update order status to shipped when farmer confirms and dispatches"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Verify this farmer owns products in this order
    order_has_farmer_products = db.query(OrderItem).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        OrderItem.order_id == order_id,
        Product.farmer_id == current_user.id
    ).first()
    
    if not order_has_farmer_products:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to dispatch this order")
    
    # Update order status to shipped
    from app.models.order import OrderStatus
    order.order_status = OrderStatus.shipped
    db.commit()
    db.refresh(order)
    
    return serialize_order(order)


@router.post("/register-flock", status_code=status.HTTP_201_CREATED, response_model=FlockResponse)
def register_flock(
    payload: FlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    try:
        flock = create_flock(db, current_user.id, payload)
        return serialize_flock(flock)
    except Exception as e:
        import traceback
        print(f"❌ Error creating flock: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create flock: {str(e)}"
        )


@router.get("/flocks", response_model=list[FlockResponse])
def list_flocks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    flocks = get_flocks_by_farmer(db, current_user.id)
    return [serialize_flock(flock) for flock in flocks]


@router.get("/flocks/{flock_id}", response_model=FlockResponse)
def get_flock(
    flock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get a specific flock by ID"""
    flock = get_flock_by_id_for_farmer(db, flock_id, current_user.id)
    if not flock:
        raise HTTPException(status_code=404, detail="Flock not found")
    return serialize_flock(flock)


@router.put("/flocks/{flock_id}", response_model=FlockResponse)
def update_flock_record(
    flock_id: int,
    payload: FlockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    flock = get_flock_by_id_for_farmer(db, flock_id, current_user.id)
    if not flock:
        raise HTTPException(status_code=404, detail="Flock not found")

    updated = update_flock(db, flock, payload)
    return serialize_flock(updated)


@router.delete("/flocks/{flock_id}", response_model=MessageResponse)
def remove_flock(
    flock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    flock = get_flock_by_id_for_farmer(db, flock_id, current_user.id)
    if not flock:
        raise HTTPException(status_code=404, detail="Flock not found")

    delete_flock(db, flock)
    return {"message": "Flock deleted successfully"}


# ════════ FARM PROFILE ENDPOINTS ════════

@router.get("/farm-profile", response_model=FarmResponse)
def get_farm_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get the farm profile for the current farmer"""
    farm = get_farm_by_farmer(db, current_user.id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm profile not found")
    return farm


@router.post("/farm-profile", status_code=status.HTTP_201_CREATED, response_model=FarmResponse)
def create_farm_profile(
    payload: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Create a farm profile for the current farmer"""
    # Check if farm already exists
    existing_farm = get_farm_by_farmer(db, current_user.id)
    if existing_farm:
        raise HTTPException(status_code=400, detail="Farm profile already exists")
    
    farm = create_farm(db, current_user.id, payload)
    return farm


@router.put("/farm-profile", response_model=FarmResponse)
def update_farm_profile(
    payload: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Update the farm profile for the current farmer"""
    farm = get_farm_by_farmer(db, current_user.id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm profile not found")
    
    updated_farm = update_farm(db, farm, payload)
    return updated_farm


# ════════ FARMER PRODUCT ENDPOINTS ════════

def serialize_product(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        supplier_id=product.supplier_id,
        farmer_id=product.farmer_id,
        product_source=product.product_source,
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


@router.post("/products", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def add_farmer_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Farmer adds a product (e.g., surplus birds, eggs)"""
    product = Product(
        farmer_id=current_user.id,
        product_source="farmer",
        name=payload.name,
        category=payload.category,
        description=payload.description,
        product_image=payload.product_image,
        unit_price=payload.unit_price,
        unit_of_measure=payload.unit_of_measure,
        stock_quantity=payload.stock_quantity,
        is_active=True,
        visible_to_farmers_only=payload.visible_to_farmers_only,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return serialize_product(product)


@router.get("/products", response_model=list[ProductResponse])
def list_farmer_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get all products added by this farmer"""
    products = db.query(Product).filter(Product.farmer_id == current_user.id).all()
    return [serialize_product(p) for p in products]


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_farmer_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Update a farmer's product"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.farmer_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if value is not None:
            setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return serialize_product(product)


@router.delete("/products/{product_id}", response_model=MessageResponse)
def delete_farmer_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Delete a farmer's product"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.farmer_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


# ════════════════════════════════════
# COMPREHENSIVE ONBOARDING ENDPOINT
# ════════════════════════════════════

@router.post("/register", status_code=status.HTTP_201_CREATED)
def farmer_complete_registration(
    payload: FarmerRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """
    Complete farmer onboarding registration in a single call.
    Creates farm profile and registers flocks.
    """
    try:
        # Check if farm already exists
        existing_farm = get_farm_by_farmer(db, current_user.id)
        if existing_farm:
            raise HTTPException(status_code=400, detail="Farm profile already exists for this user")
        
        # Create farm profile with data from onboarding
        farm_data = FarmCreate(
            farm_name=payload.farm_name,
            location=payload.county,  # Map county to location
            size=payload.farm_size or 1.0,  # Default to 1.0 if not provided (must be > 0)
            phone=payload.phone,
            description=payload.description
        )
        farm = create_farm(db, current_user.id, farm_data)
        print(f"✓ Farm created successfully: {farm.id} for farmer {current_user.id}")
        
        # Create flocks if provided
        flock_ids = []
        if payload.flocks:
            for flock_data in payload.flocks:
                from app.schemas.flock import FlockCreate
                flock_obj = FlockCreate(
                    bird_type=flock_data.breed,  # Store breed in bird_type field
                    breed=flock_data.breed,
                    quantity=flock_data.quantity,
                    age_weeks=flock_data.age_weeks,
                    health_status=flock_data.health_status,
                    daily_feed_kg=flock_data.feed_per_day_kg,
                    notes=""
                )
                flock = create_flock(db, current_user.id, flock_obj)
                flock_ids.append(flock.id)
            print(f"✓ Created {len(flock_ids)} flocks for farmer {current_user.id}")
        
        return {
            "message": "Farmer registration completed successfully",
            "farm_id": farm.id,
            "flock_ids": flock_ids
        }
        
    except Exception as e:
        print(f"✗ Farmer registration failed for user {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@router.get("/profile", response_model=dict)
def get_farmer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get complete farmer profile including farm and flocks"""
    farm = get_farm_by_farmer(db, current_user.id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm profile not found")
    
    flocks = get_flocks_by_farmer(db, current_user.id)
    
    return {
        "full_name": current_user.email.split('@')[0],  # Basic name extraction
        "farm_name": farm.farm_name,
        "county": farm.location,
        "phone": farm.phone,
        "farm_size": farm.size,
        "description": farm.description,
        "flocks": [
            {
                "id": f.id,
                "breed": f.breed,
                "quantity": f.quantity,
                "age_weeks": f.age_weeks,
                "health_status": f.health_status,
            }
            for f in flocks
        ]
    }


# ════════════════════════════════════
# FARMER INVITATIONS & MESSAGING
# ════════════════════════════════════

@router.get("/invitations/pending", response_model=list[dict])
def get_pending_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get all pending supplier invitations for this farmer"""
    invitations = db.query(FarmInvitation).filter(
        FarmInvitation.farmer_email == current_user.email,
        FarmInvitation.status == "pending"
    ).all()
    
    result = []
    for inv in invitations:
        supplier = db.query(User).filter(User.id == inv.supplier_id).first()
        result.append({
            "id": inv.id,
            "supplier_id": inv.supplier_id,
            "supplier_name": supplier.email if supplier else "Unknown",
            "farm_id": inv.farm_id,
            "message": inv.message or "",
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        })
    
    return result


@router.put("/invitations/{invitation_id}/accept", response_model=MessageResponse)
def accept_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Accept a supplier invitation"""
    invitation = db.query(FarmInvitation).filter(
        FarmInvitation.id == invitation_id,
        FarmInvitation.farmer_id == current_user.id,
        FarmInvitation.status == "pending"
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already processed")
    
    invitation.status = "accepted"
    db.commit()
    
    return {"message": "Invitation accepted successfully"}


@router.put("/invitations/{invitation_id}/decline", response_model=MessageResponse)
def decline_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Decline a supplier invitation"""
    invitation = db.query(FarmInvitation).filter(
        FarmInvitation.id == invitation_id,
        FarmInvitation.farmer_id == current_user.id,
        FarmInvitation.status == "pending"
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already processed")
    
    invitation.status = "declined"
    db.commit()
    
    return {"message": "Invitation declined successfully"}


@router.get("/suppliers/connected", response_model=list[dict])
def get_connected_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get all suppliers with accepted invitations"""
    acceptedInvites = db.query(FarmInvitation).filter(
        FarmInvitation.farmer_id == current_user.id,
        FarmInvitation.status == "accepted"
    ).all()
    
    suppliers = []
    for inv in acceptedInvites:
        supplier = db.query(User).filter(User.id == inv.supplier_id).first()
        if supplier:
            suppliers.append({
                "id": supplier.id,
                "name": supplier.email,
                "email": supplier.email,
            })
    
    return suppliers


@router.get("/messages/{supplier_id}", response_model=list[dict])
def get_messages_with_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get all messages between farmer and a specific supplier"""
    messages = db.query(Message).filter(
        (
            (Message.sender_id == current_user.id) & (Message.receiver_id == supplier_id)
        ) |
        (
            (Message.sender_id == supplier_id) & (Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "is_read": msg.is_read,
        })
    
    return result


@router.post("/messages/{supplier_id}", status_code=status.HTTP_201_CREATED, response_model=dict)
def send_message_to_supplier(
    supplier_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Send a message to a supplier"""
    # Verify supplier exists
    supplier = db.query(User).filter(User.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Extract content from payload
    content = payload.get("content") or payload.get("message")
    if not content:
        raise HTTPException(status_code=400, detail="Message content is required")
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=supplier_id,
        content=content,
        is_read=0
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "content": message.content,
        "created_at": message.created_at.isoformat() if message.created_at else None,
        "is_read": message.is_read,
    }


# ════════════════════════════════════
# GET ALL SUPPLIERS & SEND REQUESTS
# ════════════════════════════════════

@router.get("/all-suppliers", response_model=list[dict])
def get_all_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get all suppliers in the system"""
    suppliers = db.query(User).filter(User.role == "supplier").all()
    
    result = []
    for supplier in suppliers:
        # Check if already connected or invited
        existing_invite = db.query(FarmInvitation).filter(
            (FarmInvitation.farmer_id == current_user.id) & (FarmInvitation.supplier_id == supplier.id)
        ).first()
        
        status = "connected"
        if existing_invite:
            status = existing_invite.status  # pending, accepted, or declined
        
        result.append({
            "id": supplier.id,
            "name": supplier.name,
            "email": supplier.email,
            "phone": supplier.phone,
            "connection_status": status,  # connected, pending, accepted, declined
        })
    
    return result


@router.post("/suppliers/{supplier_id}/request-connection", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
def request_supplier_connection(
    supplier_id: int,
    payload: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Farmer requests to connect with a supplier by sending farm details"""
    # Verify supplier exists
    supplier = db.query(User).filter(User.id == supplier_id, User.role == "supplier").first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Check if invitation already exists
    existing = db.query(FarmInvitation).filter(
        FarmInvitation.farmer_id == current_user.id,
        FarmInvitation.supplier_id == supplier_id
    ).first()
    
    if existing:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="Already connected with this supplier")
        elif existing.status == "pending":
            raise HTTPException(status_code=400, detail="Connection request already sent")
        else:
            # If previously declined, allow new request
            existing.status = "pending"
            db.commit()
            return {"message": "Connection request sent successfully"}
    
    # Extract farm details from payload
    farm_name = ""
    farmer_name = ""
    farmer_email = ""
    phone = ""
    location = ""
    farm_type = ""
    message = ""
    
    if payload and isinstance(payload, dict):
        farm_name = payload.get("farm_name", "").strip()
        farmer_name = payload.get("farmer_name", "").strip()
        farmer_email = payload.get("email", "").strip()
        phone = payload.get("phone") or ""
        location = payload.get("farm_location") or ""
        farm_type = payload.get("farm_type") or ""
        message = payload.get("message") or ""
    
    # Validate required fields
    if not farm_name:
        raise HTTPException(status_code=400, detail="farm_name is required")
    if not farmer_name:
        raise HTTPException(status_code=400, detail="farmer_name is required")
    if not farmer_email:
        raise HTTPException(status_code=400, detail="email is required")
    
    # Create invitation with farm details
    invitation = FarmInvitation(
        farmer_id=current_user.id,
        supplier_id=supplier_id,
        farm_name=farm_name,
        farmer_name=farmer_name,
        farmer_email=farmer_email,
        farmer_phone=phone,
        farm_location=location,
        farm_type=farm_type,
        message=message,
        status="pending"
    )
    db.add(invitation)
    db.commit()
    
    return {"message": "Connection request sent successfully"}
