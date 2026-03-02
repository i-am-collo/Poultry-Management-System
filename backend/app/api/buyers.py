from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.crud.product import get_product_by_id, search_active_products
from app.db.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.product import BuyerProductSearchResponse

router = APIRouter(prefix="/buyers", tags=["Buyers"])


def serialize_order(order: Order, product_name: str) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        supplier_id=order.supplier_id,
        product_id=order.product_id,
        product_name=product_name,
        quantity=order.quantity,
        unit_price=order.unit_price,
        total_price=order.total_price,
        status=order.status,
        note=order.note,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("/search", response_model=list[BuyerProductSearchResponse])
def search_products(
    q: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("buyer")),
):
    products = search_active_products(db, q)
    if not products:
        return []

    supplier_ids = {product.supplier_id for product in products}
    suppliers = db.query(User).filter(User.id.in_(supplier_ids)).all() if supplier_ids else []
    supplier_name_by_id = {supplier.id: supplier.name for supplier in suppliers}

    return [
        BuyerProductSearchResponse(
            id=product.id,
            supplier_id=product.supplier_id,
            supplier_name=supplier_name_by_id.get(product.supplier_id, "Unknown supplier"),
            name=product.name,
            category=product.category,
            description=product.description,
            price_per_unit=product.price_per_unit,
            unit=product.unit,
            stock_quantity=product.stock_quantity,
        )
        for product in products
    ]


@router.post("/orders", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer")),
):
    product = get_product_by_id(db, payload.product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock_quantity < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock for this order")

    total_price = payload.quantity * product.price_per_unit
    order = Order(
        buyer_id=current_user.id,
        supplier_id=product.supplier_id,
        product_id=product.id,
        quantity=payload.quantity,
        unit_price=product.price_per_unit,
        total_price=total_price,
        status="pending",
        note=payload.note,
    )

    product.stock_quantity -= payload.quantity
    db.add(product)
    db.add(order)
    db.commit()
    db.refresh(order)

    return serialize_order(order, product.name)


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer")),
):
    orders = (
        db.query(Order)
        .filter(Order.buyer_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    if not orders:
        return []

    product_ids = {order.product_id for order in orders}
    products = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
    product_name_by_id = {product.id: product.name for product in products}

    return [
        serialize_order(order, product_name_by_id.get(order.product_id, "Unknown product"))
        for order in orders
    ]


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("buyer")),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.buyer_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    product = get_product_by_id(db, order.product_id)
    product_name = product.name if product else "Unknown product"
    return serialize_order(order, product_name)
