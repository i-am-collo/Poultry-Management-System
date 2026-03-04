from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _validate_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class ReviewCreate(BaseModel):
    reviewee_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: str | None = Field(None, max_length=500)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str | None) -> str | None:
        return _validate_text(value, "Comment")


class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: str | None = Field(None, max_length=500)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str | None) -> str | None:
        return _validate_text(value, "Comment")


class ReviewResponse(BaseModel):
    id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
