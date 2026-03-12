from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db.database import Base
from sqlalchemy.orm import relationship


class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    farm_name = Column(String(120), nullable=False)
    location = Column(String(255), nullable=False)
    size = Column(Float, nullable=False)
    phone = Column(String(30), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    farmer = relationship("User", back_populates="farms") 