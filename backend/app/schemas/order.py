from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class OrderCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    note: str | None = None

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    supplier_id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    status: str
    note: str | None
    created_at: datetime
    updated_at: datetime
