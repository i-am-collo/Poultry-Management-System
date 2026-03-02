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


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    buyer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False, index=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    buyer = relationship("User", foreign_keys=[buyer_id])
    supplier = relationship("User", foreign_keys=[supplier_id])
    product = relationship("Product")