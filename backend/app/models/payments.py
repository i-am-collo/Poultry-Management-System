from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Enum

from app.db.database import Base
from sqlalchemy.orm import relationship


class PaymentMethod(enum.Enum):
    credit_card = "credit_card"
    bank_transfer = "bank_transfer"
    cash = "cash"
    mobile_money = "mobile_money"


class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_reference = Column(String(255), nullable=False, unique=True)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order = relationship("Order", back_populates="payment")
    