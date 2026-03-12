from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Message(Base):
    """Message between farmer and supplier"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], viewonly=True)
    receiver = relationship("User", foreign_keys=[receiver_id], viewonly=True)

    def __repr__(self):
        return f"<Message id={self.id} sender_id={self.sender_id} receiver_id={self.receiver_id}>"
