from pydantic import BaseModel, Field
from typing import Optional


class UserQuery(BaseModel):
    text: str = Field(..., description="Free-text query from user")
    location: Optional[str] = Field(None, description="City or pincode")
    lat: Optional[float] = None
    lng: Optional[float] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    comorbidities: Optional[list[str]] = Field(default_factory=list)
    budget: Optional[int] = Field(None, description="Max budget in INR")


class ParsedQuery(BaseModel):
    original_text: str
    condition: str
    procedure: str
    icd10_code: Optional[str]
    location: str
    lat: Optional[float]
    lng: Optional[float]
    budget: Optional[int]
    age: Optional[int]
    comorbidities: list[str]
    urgency: Optional[str] = "low"
    urgency_reason: Optional[str] = None
    flags: Optional[dict] = None
    financial_signals: Optional[dict] = None
