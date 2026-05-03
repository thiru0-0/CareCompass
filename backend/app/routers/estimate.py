"""
POST /api/estimate
Full end-to-end: parse query → rank hospitals → estimate costs → explain.
"""
from fastapi import APIRouter, HTTPException
from app.models.query import UserQuery
from app.models.estimate import EstimateResponse, CostBreakdown
from app.services.nlp_service import parse_query
from app.services.ranking_service import rank_hospitals
from app.services.cost_service import (
    full_cost_breakdown,
    compute_confidence,
    get_risk_flags,
    get_key_drivers,
)
from app.services.llm_service import generate_explanation
from app.services.scheme_service import check_eligibility

router = APIRouter()


@router.post("/", response_model=EstimateResponse)
async def full_estimate(payload: UserQuery):
    try:
        # Step 1: Parse intent
        parsed = await parse_query(payload)

        # Step 2: Rank hospitals
        ranked = await rank_hospitals(parsed, top_n=1)
        if not ranked:
            raise HTTPException(status_code=404, detail="No hospitals found for the given location.")

        top_hospital = ranked[0]

        # Step 3: Detailed cost breakdown
        breakdown_raw = full_cost_breakdown(
            parsed.procedure,
            top_hospital.tier,
            parsed.location,
            parsed.age,
            parsed.comorbidities,
        )
        total = [
            sum(v[0] for v in breakdown_raw.values()),
            sum(v[1] for v in breakdown_raw.values()),
        ]

        # Step 4: Confidence + flags
        confidence = compute_confidence(parsed.procedure, parsed.comorbidities, parsed.age)
        risk_flags = get_risk_flags(parsed.comorbidities, parsed.age, top_hospital.tier)
        key_drivers = get_key_drivers(parsed.procedure, parsed.location, top_hospital.tier)

        # Step 5: LLM explanation
        explanation = await generate_explanation(
            parsed.condition,
            parsed.procedure,
            top_hospital.name,
            total,
            parsed.comorbidities,
        )

        # Step 6: Scheme Eligibility
        schemes = check_eligibility(parsed)

        return EstimateResponse(
            condition=parsed.condition,
            procedure=parsed.procedure,
            hospital_name=top_hospital.name,
            hospital_tier=top_hospital.tier,
            city=top_hospital.city,
            total_range=total,
            breakdown=CostBreakdown(**breakdown_raw),
            confidence_score=confidence,
            key_drivers=key_drivers,
            risk_flags=risk_flags,
            notes=explanation.get("notes", []),
            disclaimer=explanation.get("disclaimer", "This is decision support only, not medical advice."),
            urgency=parsed.urgency,
            urgency_reason=parsed.urgency_reason,
            applicable_schemes=schemes,
            financial_signals=parsed.financial_signals,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
