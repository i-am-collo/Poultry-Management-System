from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _validate_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class HealthRecordCreate(BaseModel):
    flock_id: int = Field(gt=0)
    vaccination_type: str
    medication: str | None = None
    date_administered: datetime
    next_due_date: datetime | None = None
    notes: str | None = None
    veterinarian_name: str | None = None

    @field_validator("vaccination_type")
    @classmethod
    def validate_vaccination_type(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Vaccination type is required")
        return cleaned

    @field_validator("medication")
    @classmethod
    def validate_medication(cls, value: str | None) -> str | None:
        return _validate_text(value, "Medication")

    @field_validator("veterinarian_name")
    @classmethod
    def validate_veterinarian_name(cls, value: str | None) -> str | None:
        return _validate_text(value, "Veterinarian name")

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        return _validate_text(value, "Notes")

    @field_validator("next_due_date")
    @classmethod
    def validate_next_due_date(cls, value: datetime | None, info) -> datetime | None:
        if value is None:
            return None
        date_administered = info.data.get("date_administered")
        if date_administered and value <= date_administered:
            raise ValueError("Next due date must be after the date administered")
        return value


class HealthRecordUpdate(BaseModel):
    vaccination_type: str | None = None
    medication: str | None = None
    date_administered: datetime | None = None
    next_due_date: datetime | None = None
    notes: str | None = None
    veterinarian_name: str | None = None

    @field_validator("vaccination_type")
    @classmethod
    def validate_vaccination_type(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Vaccination type is required")
        return cleaned

    @field_validator("medication")
    @classmethod
    def validate_medication(cls, value: str | None) -> str | None:
        return _validate_text(value, "Medication")

    @field_validator("veterinarian_name")
    @classmethod
    def validate_veterinarian_name(cls, value: str | None) -> str | None:
        return _validate_text(value, "Veterinarian name")

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        return _validate_text(value, "Notes")

    @field_validator("next_due_date")
    @classmethod
    def validate_next_due_date(cls, value: datetime | None, info) -> datetime | None:
        if value is None:
            return None
        date_administered = info.data.get("date_administered")
        if date_administered and value <= date_administered:
            raise ValueError("Next due date must be after the date administered")
        return value


class HealthRecordResponse(BaseModel):
    id: int
    flock_id: int
    vaccination_type: str
    medication: str | None
    date_administered: datetime
    next_due_date: datetime | None
    notes: str | None
    veterinarian_name: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
