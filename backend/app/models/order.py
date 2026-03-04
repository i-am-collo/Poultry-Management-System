from datetime import datetime, timezone
import enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class OrderStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"    


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    order_status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False, index=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False, index=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    


# Order items model
class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    