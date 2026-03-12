from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.db.database import Base


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, nullable=False, index=True, unique=True)
    full_name = Column(String(120), nullable=False)
    business_name = Column(String(255), nullable=False)
    county = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=False)
    email = Column(String(255), nullable=False)
    buyer_type = Column(String(100), nullable=False)
    preferred_payment = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
