"""
POST /api/query
Accepts a free-text user query and returns parsed medical intent.
"""
from fastapi import APIRouter, HTTPException
from app.models.query import UserQuery, ParsedQuery
from app.services.nlp_service import parse_query

router = APIRouter()


@router.post("/", response_model=ParsedQuery)
async def parse_user_query(payload: UserQuery):
    try:
        return await parse_query(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
