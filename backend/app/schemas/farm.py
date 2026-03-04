from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _validate_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


class FarmCreate(BaseModel):
    farm_name: str
    location: str
    size: float = Field(gt=0, description="Farm size in hectares or acres")

    @field_validator("farm_name")
    @classmethod
    def validate_farm_name(cls, value: str) -> str:
        return _validate_text(value, "Farm name")

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str) -> str:
        return _validate_text(value, "Location")


class FarmUpdate(BaseModel):
    farm_name: str | None = None
    location: str | None = None
    size: float | None = Field(None, gt=0, description="Farm size in hectares or acres")

    @field_validator("farm_name")
    @classmethod
    def validate_farm_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_text(value, "Farm name")

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_text(value, "Location")


class FarmResponse(BaseModel):
    id: int
    farmer_id: int
    farm_name: str
    location: str
    size: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
