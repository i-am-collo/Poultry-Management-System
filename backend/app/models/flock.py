from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db.database import Base


class Flock(Base):
    __tablename__ = "flocks"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    bird_type = Column(String(50), nullable=False)
    breed = Column(String(120), nullable=False)
    quantity = Column(Integer, nullable=False)
    age_weeks = Column(Integer, nullable=False, default=0)
    health_status = Column(String(30), nullable=False, default="healthy")
    daily_feed_kg = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
