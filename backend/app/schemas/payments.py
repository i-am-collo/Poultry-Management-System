from datetime import datetime

from pydantic import BaseModel, Field, field_validator


ALLOWED_PAYMENT_METHODS = {"credit_card", "bank_transfer", "cash", "mobile_money"}
ALLOWED_PAYMENT_STATUSES = {"pending", "completed", "failed"}


def _validate_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


class PaymentCreate(BaseModel):
    order_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    transaction_reference: str
    payment_method: str

    @field_validator("transaction_reference")
    @classmethod
    def validate_transaction_reference(cls, value: str) -> str:
        return _validate_text(value, "Transaction reference")

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method. Allowed: {', '.join(ALLOWED_PAYMENT_METHODS)}")
        return cleaned


class PaymentUpdate(BaseModel):
    amount: float | None = Field(None, gt=0)
    transaction_reference: str | None = None
    payment_method: str | None = None
    payment_status: str | None = None

    @field_validator("transaction_reference")
    @classmethod
    def validate_transaction_reference(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_text(value, "Transaction reference")

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method. Allowed: {', '.join(ALLOWED_PAYMENT_METHODS)}")
        return cleaned

    @field_validator("payment_status")
    @classmethod
    def validate_payment_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_PAYMENT_STATUSES:
            raise ValueError(f"Invalid payment status. Allowed: {', '.join(ALLOWED_PAYMENT_STATUSES)}")
        return cleaned


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    transaction_reference: str
    payment_method: str
    payment_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
