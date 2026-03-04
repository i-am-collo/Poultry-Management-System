from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.database import Base


class HealthRecord(Base):
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    flock_id = Column(Integer, ForeignKey("flocks.id"), index=True, nullable=False)
    vaccination_type = Column(String(100), nullable=False)
    medication = Column(String(255), nullable=True)
    date_administered = Column(DateTime, nullable=False)
    next_due_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    veterinarian_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    flock = relationship("Flock", back_populates="health_records")
    