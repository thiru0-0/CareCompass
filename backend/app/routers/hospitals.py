"""
POST /api/hospitals
Returns ranked list of hospitals for a parsed query.
"""
from fastapi import APIRouter, HTTPException
from app.models.query import ParsedQuery
from app.models.hospital import RankedHospital
from app.services.ranking_service import rank_hospitals

router = APIRouter()


@router.post("/", response_model=list[RankedHospital])
async def get_ranked_hospitals(parsed: ParsedQuery, top_n: int = 5):
    try:
        return await rank_hospitals(parsed, top_n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
