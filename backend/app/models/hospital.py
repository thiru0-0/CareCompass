from pydantic import BaseModel, Field
from typing import Optional


class Hospital(BaseModel):
    id: str
    name: str
    city: str
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    specializations: list[str]
    rating: float = Field(3.5, ge=0, le=5)
    review_count: int = 0
    nabh_accredited: bool = False
    tier: str = "mid"  # premium | mid | budget
    distance_km: Optional[float] = None
    score: Optional[float] = None
    score_breakdown: Optional[dict] = None


class RankedHospital(Hospital):
    estimated_cost_range: list[int] = [75000, 150000]
    strengths: list[str] = []
    warnings: list[str] = []
