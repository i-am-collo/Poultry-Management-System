from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class FarmInvitationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    farmName: str = Field(..., min_length=1, max_length=120)
    farmerName: str = Field(..., min_length=1, max_length=120)
    farmerEmail: str = Field(..., min_length=1, max_length=255)
    farmerPhone: str | None = Field(None, max_length=30)
    farmLocation: str | None = Field(None, max_length=255)
    farmType: str | None = Field(None, max_length=50)
    message: str | None = Field(None, max_length=500)

    @field_validator("farmerEmail")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email is required")
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email address")
        return v


class FarmInvitationResponse(BaseModel):
    id: int
    supplier_id: int
    farm_name: str
    farmer_name: str
    farmer_email: str
    farmer_phone: str | None
    farm_location: str | None
    farm_type: str | None
    message: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
