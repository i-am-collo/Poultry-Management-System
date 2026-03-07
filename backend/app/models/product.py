from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(120), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    product_image = Column(String(255), nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_of_measure = Column(String(30), nullable=False, default="unit")
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    visible_to_farmers_only = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
