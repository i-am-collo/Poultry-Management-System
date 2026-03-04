from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _validate_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_items=1)
    note: str | None = None

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return _validate_text(value, "Note")


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    created_at: datetime
    updated_at: datetime


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    order_status: str
    payment_status: str
    items: list[OrderItemResponse]
    note: str | None
    created_at: datetime
    updated_at: datetime
