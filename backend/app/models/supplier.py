from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.db.database import Base
import json


class SupplierProfile(Base):
    __tablename__ = "supplier_profiles"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, nullable=False, index=True, unique=True)
    business_name = Column(String(255), nullable=False)
    contact_person = Column(String(120), nullable=False)
    county = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=False)
    email = Column(String(255), nullable=False)
    kra_pin = Column(String(50), nullable=False)
    categories = Column(String, default="[]")  # Store as JSON string
    payment_mpesa_till = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    
    def get_categories(self):
        """Parse categories from JSON string"""
        if isinstance(self.categories, str):
            return json.loads(self.categories) if self.categories else []
        return self.categories or []
    
    def set_categories(self, categories):
        """Store categories as JSON string"""
        self.categories = json.dumps(categories) if isinstance(categories, list) else categories
