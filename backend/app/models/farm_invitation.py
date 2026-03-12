from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.database import Base


class InvitationStatus(Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class FarmInvitation(Base):
    __tablename__ = "farm_invitations"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)  # Farmer sending the invitation
    supplier_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # Supplier being invited
    farm_name = Column(String(120), nullable=False)
    farmer_name = Column(String(120), nullable=False)
    farmer_email = Column(String(255), index=True, nullable=False)
    farmer_phone = Column(String(30), nullable=True)
    farm_location = Column(String(255), nullable=True)
    farm_type = Column(String(50), nullable=True)  # layer, broiler, mixed, other
    message = Column(Text, nullable=True)
    status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.pending, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    supplier = relationship("User", foreign_keys=[supplier_id])
    farmer = relationship("User", foreign_keys=[farmer_id], viewonly=True)
