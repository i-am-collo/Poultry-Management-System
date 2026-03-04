from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.db.database import Base

from sqlalchemy.orm import relationship

notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
user = relationship("User", back_populates="notifications")
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
