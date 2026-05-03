"""
Hospital Ranking Service - CareCompass
Complete scoring engine with 4 components:
  - Clinical Capability (40 pts)
  - Cost Fit (30 pts)
  - Distance (20 pts)
  - Patient Sentiment (10 pts)
"""
import json
import os
from app.models.hospital import RankedHospital
from app.models.query import ParsedQuery

# Load PMJAY hospitals
PMJAY_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/pmjay_hospitals.json")

def _load_pmjay_hospitals():
    try:
        with open(PMJAY_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

SAMPLE_HOSPITALS = _load_pmjay_hospitals()

# Procedure to Speciality mapping
PROCEDURE_TO_SPECIALITY = {
    "bypass": "cardiology", "angioplasty": "cardiology", "angiography": "cardiology",
    "cataract": "ophthalmology", "lasik": "ophthalmology",
    "knee replacement": "orthopaedics", "hip replacement": "orthopaedics",
    "mastectomy": "oncology", "chemotherapy": "oncology",
    "dialysis": "nephrology", "kidney transplant": "nephrology",
    "appendectomy": "general surgery", "hernia": "general surgery",
    "root canal": "dentistry", "dental": "dentistry",
    "mri": "diagnostics", "ct scan": "diagnostics",
    "delivery": "gynaecology", "caesarean": "gynaecology",
}

# Premium chain hospitals
PREMIUM_CHAINS = ["apollo", "fortis", "max", "medanta", "narayana", "manipal", "kokilaben", "nanavati", "miot", "yashoda", "aster"]

# Comorbidity cost rules
COMORBIDITY_RULES = {
    "diabetes": {"cost_increase_pct": 18, "flag": "Diabetes increases surgical risk."},
    "hypertension": {"cost_increase_pct": 10, "flag": "Hypertension may require monitoring."},
    "kidney": {"cost_increase_pct": 25, "flag": "CKD increases surgical complexity."},
    "obesity": {"cost_increase_pct": 12, "flag": "Obesity raises anaesthesia risk."},
    "heart": {"cost_increase_pct": 20, "flag": "Heart condition increases complexity."},
}


def get_speciality(procedure: str) -> str:
    if not procedure:
        return "general"
    proc_lower = procedure.lower()
    return PROCEDURE_TO_SPECIALITY.get(proc_lower, "general")


def get_base_cost(ownership: str) -> int:
    return {"government": 75000, "trust": 120000, "private": 200000}.get(ownership, 100000)


async def rank_hospitals(parsed: ParsedQuery, top_n: int = 10) -> list[RankedHospital]:
    """Main ranking function - returns top_n hospitals ranked by fit score."""
    
    results = []
    query_city = (parsed.location or "").lower()
    budget = parsed.budget
    
    for h in SAMPLE_HOSPITALS:
        # Skip labs
        if h.get("entity_type") == "lab":
            continue
        
        # Geographic filter
        hospital_state = (h.get("state") or "").lower()
        hospital_district = (h.get("district") or "").lower()
        
        geo_match = False
        if query_city:
            if query_city in hospital_state or query_city in hospital_district:
                geo_match = True
            elif hospital_state in query_city or hospital_district in query_city:
                geo_match = True
        else:
            geo_match = True
        
        if not geo_match:
            continue
        
        # === SCORING ===
        score = 0
        breakdown = {}
        
        # Clinical (40 pts max)
        clinical = 0
        if h.get("pmjay_empanelled"):
            clinical += 12
        if h.get("nabh_accredited"):
            clinical += 12
        required_spec = get_speciality(parsed.procedure)
        hospital_specs = h.get("specialities", [])
        if isinstance(hospital_specs, str):
            hospital_specs = [hospital_specs]
        for spec in hospital_specs:
            if required_spec in spec.lower():
                clinical += 10
                break
        name_lower = (h.get("name") or "").lower()
        if any(chain in name_lower for chain in PREMIUM_CHAINS):
            clinical += 6
        clinical = min(clinical, 40)
        score += clinical
        breakdown["clinical"] = clinical
        
        # Cost fit (30 pts max)
        ownership = h.get("ownership", "unknown")
        base_cost = get_base_cost(ownership)
        
        # Comorbidity adjustment
        comor_mult = 1.0
        comor_flags = []
        for com in (parsed.comorbidities or []):
            com_lower = com.lower()
            for rule_key, rule in COMORBIDITY_RULES.items():
                if rule_key in com_lower:
                    comor_mult *= 1 + (rule["cost_increase_pct"] / 100)
                    comor_flags.append(rule["flag"])
                    break
        
        cost_min = int(base_cost * comor_mult * 0.8)
        cost_max = int(base_cost * comor_mult * 1.2)
        
        if not budget:
            cost_score = 15
        elif cost_max <= budget:
            cost_score = 30
        elif cost_min <= budget <= cost_max:
            cost_score = 20
        elif cost_min <= budget * 1.2:
            cost_score = 12
        else:
            cost_score = 4
        
        score += cost_score
        breakdown["cost"] = cost_score
        
        # Distance (20 pts) - neutral since no coords
        distance_score = 10
        score += distance_score
        breakdown["distance"] = distance_score
        
        # Sentiment (10 pts) - neutral for PMJAY
        sentiment_score = 5
        score += sentiment_score
        breakdown["sentiment"] = sentiment_score
        
        # Build strengths and warnings
        strengths = []
        warnings = []
        
        if h.get("pmjay_empanelled"):
            strengths.append("PMJAY Eligible")
        if h.get("ownership") == "government":
            strengths.append("Government Hospital")
        elif h.get("ownership") == "trust":
            strengths.append("Trust/NGO Hospital")
        
        if comor_flags:
            warnings.extend(comor_flags[:2])
        
        results.append(RankedHospital(
            id=(h.get("pmjay_id", "")[-10:]) or "",
            name=h.get("name", ""),
            city=h.get("district", "") or h.get("state", ""),
            address=f"{h.get('district', '')}, {h.get('state', '')}",
            specializations=hospital_specs if hospital_specs else ["multispeciality"],
            rating=3.5,
            review_count=0,
            nabh_accredited=False,
            tier="premium" if ownership == "government" else "mid",
            distance_km=None,
            score=score,
            score_breakdown=breakdown,
            estimated_cost_range=[cost_min, cost_max],
            strengths=strengths,
            warnings=warnings,
        ))
    
    # Sort by score
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:top_n]