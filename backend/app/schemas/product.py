from datetime import datetime

from pydantic import BaseModel, Field, field_validator

ALLOWED_PRODUCT_CATEGORIES = {"feed", "vaccine", "equipment", "chicks", "eggs", "broilers", "other"}


def _required_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


class ProductCreate(BaseModel):
    name: str
    category: str
    description: str | None = None
    unit_price: float = Field(gt=0)
    product_image: str
    unit_of_measure: str = "unit"
    stock_quantity: int = Field(default=0, ge=0)
    visible_to_farmers_only: bool = False

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _required_text(value, "Name")

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_PRODUCT_CATEGORIES:
            raise ValueError("Invalid category")
        return cleaned

    @field_validator("unit_of_measure")
    @classmethod
    def validate_unit_of_measure(cls, value: str) -> str:
        return _required_text(value, "Unit of measure")

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    unit_price: float | None = Field(default=None, gt=0)
    product_image: str | None = None
    unit_of_measure: str | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    visible_to_farmers_only: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _required_text(value, "Name")

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_PRODUCT_CATEGORIES:
            raise ValueError("Invalid category")
        return cleaned

    @field_validator("unit_of_measure")
    @classmethod
    def validate_unit_of_measure(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _required_text(value, "Unit of measure")

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ProductResponse(BaseModel):
    id: int
    supplier_id: int | None = None
    farmer_id: int | None = None
    product_source: str = "supplier"
    name: str
    category: str
    description: str | None
    unit_price: float
    product_image: str
    unit_of_measure: str
    stock_quantity: int
    is_active: bool
    visible_to_farmers_only: bool
    created_at: datetime
    updated_at: datetime


class BuyerProductSearchResponse(BaseModel):
    id: int
    supplier_id: int | None = None
    supplier_name: str | None = None
    farmer_id: int | None = None
    farmer_name: str | None = None
    product_source: str = "supplier"
    name: str
    category: str
    description: str | None
    product_image: str
    unit_price: float
    unit_of_measure: str
    stock_quantity: int
    visible_to_farmers_only: bool


# ════════════════════════════════════
# SUPPLIER ONBOARDING REGISTRATION
# ════════════════════════════════════

class SupplierRegisterRequest(BaseModel):
    """Simplified supplier onboarding registration"""
    business_name: str
    contact_person: str
    county: str
    phone: str
    email: str
    kra_pin: str
    categories: list[str] = []
    payment_mpesa_till: str


class BuyerRegisterRequest(BaseModel):
    """Simplified buyer onboarding registration"""
    full_name: str
    business_name: str
    county: str
    phone: str
    email: str
    buyer_type: str
    preferred_payment: str
