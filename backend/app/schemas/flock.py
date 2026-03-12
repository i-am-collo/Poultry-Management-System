from datetime import datetime

from pydantic import BaseModel, Field, field_validator

ALLOWED_HEALTH_STATUSES = {"healthy", "monitor", "sick", "quarantine"}


def _validate_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


class FlockCreate(BaseModel):
    breed: str
    bird_type: str | None = None
    quantity: int = Field(gt=0)
    age_weeks: int | None = None
    purpose: str | None = None
    health_status: str = "healthy"
    daily_feed_kg: float = Field(default=0, ge=0)
    notes: str | None = None

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, value: str) -> str:
        return _validate_text(value, "Breed")

    @field_validator("health_status")
    @classmethod
    def validate_health_status(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_HEALTH_STATUSES:
            raise ValueError("Invalid health status")
        return cleaned


class FlockUpdate(BaseModel):
    breed: str | None = None
    bird_type: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    age_weeks: int | None = None
    purpose: str | None = None
    health_status: str | None = None
    daily_feed_kg: float | None = Field(default=None, ge=0)
    notes: str | None = None

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_text(value, "Breed")

    @field_validator("health_status")
    @classmethod
    def validate_health_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_HEALTH_STATUSES:
            raise ValueError("Invalid health status")
        return cleaned


class FlockResponse(BaseModel):
    id: int
    farmer_id: int
    breed: str
    bird_type: str | None
    quantity: int
    age_weeks: int | None
    purpose: str | None
    health_status: str
    daily_feed_kg: float
    notes: str | None
    created_at: datetime
    updated_at: datetime
