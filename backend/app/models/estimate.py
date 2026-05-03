from pydantic import BaseModel
from typing import Optional


class CostBreakdown(BaseModel):
    procedure: list[int]
    consultation: list[int]
    hospital_stay: list[int]
    diagnostics: list[int]
    medicines: list[int]
    contingency: list[int]


class EstimateResponse(BaseModel):
    condition: str
    procedure: str
    hospital_name: str
    hospital_tier: str
    city: str
    total_range: list[int]
    breakdown: CostBreakdown
    confidence_score: float
    key_drivers: list[str]
    risk_flags: list[str]
    notes: list[str]
    disclaimer: str
    urgency: str = "low"
    urgency_reason: Optional[str] = None
    applicable_schemes: list[dict] = []
    financial_signals: Optional[dict] = None
