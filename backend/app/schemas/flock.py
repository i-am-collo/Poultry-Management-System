from datetime import datetime

from pydantic import BaseModel, Field, field_validator

ALLOWED_HEALTH_STATUSES = {"healthy", "monitor", "sick", "quarantine"}


def _validate_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


class FlockCreate(BaseModel):
    bird_type: str
    breed: str
    quantity: int = Field(gt=0)
    age_weeks: int = Field(ge=0)
    health_status: str = "healthy"
    daily_feed_kg: float = Field(default=0, ge=0)
    notes: str | None = None

    @field_validator("bird_type")
    @classmethod
    def validate_bird_type(cls, value: str) -> str:
        return _validate_text(value, "Bird type")

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

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class FlockUpdate(BaseModel):
    bird_type: str | None = None
    breed: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    age_weeks: int | None = Field(default=None, ge=0)
    health_status: str | None = None
    daily_feed_kg: float | None = Field(default=None, ge=0)
    notes: str | None = None

    @field_validator("bird_type")
    @classmethod
    def validate_bird_type(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_text(value, "Bird type")

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

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class FlockResponse(BaseModel):
    id: int
    farmer_id: int
    bird_type: str
    breed: str
    quantity: int
    age_weeks: int
    health_status: str
    daily_feed_kg: float
    notes: str | None
    created_at: datetime
    updated_at: datetime
