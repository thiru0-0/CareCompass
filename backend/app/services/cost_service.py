"""
Cost Estimation Engine
Produces itemized cost RANGES (not point estimates) for medical procedures.
"""
from typing import Optional

PROCEDURE_COSTS = {
    "angioplasty":         [120_000, 200_000],
    "bypass surgery":      [250_000, 450_000],
    "knee replacement":    [180_000, 320_000],
    "hip replacement":     [200_000, 350_000],
    "appendectomy":        [40_000,  80_000],
    "gallbladder removal": [35_000,  70_000],
    "cataract surgery":    [15_000,  45_000],
    "angiography":         [15_000,  35_000],
    "ct scan":             [3_000,   8_000],
    "mri":                 [6_000,   14_000],
    "dialysis":            [2_500,   5_000],
    "chemotherapy":        [40_000,  120_000],
    "radiation therapy":   [80_000,  200_000],
    "spinal surgery":      [200_000, 400_000],
    "consultation":        [500,     2_000],
    "default":             [50_000,  150_000],
}

TIER_MULTIPLIER = {"premium": 1.4, "mid": 1.0, "budget": 0.6}

GEO_INDEX = {
    "mumbai": 1.35, "delhi": 1.30, "bangalore": 1.25, "hyderabad": 1.20,
    "chennai": 1.20, "pune": 1.15, "kolkata": 1.10, "ahmedabad": 1.05,
    "nagpur": 0.90, "jaipur": 0.90, "lucknow": 0.85, "bhopal": 0.80,
}

COMORBIDITY_SURCHARGE = {
    "diabetes": 0.12, "hypertension": 0.08, "cardiac history": 0.18,
    "obesity": 0.10, "ckd": 0.20, "copd": 0.12,
}


def _get_procedure_key(procedure: str) -> str:
    proc_lower = procedure.lower()
    # Try longest match first (multi-word keys before single-word)
    for key in sorted(PROCEDURE_COSTS.keys(), key=len, reverse=True):
        if key == "default":
            continue
        if key in proc_lower:
            return key
        # Also check if all words of the key appear in the procedure string
        if all(w in proc_lower for w in key.split()):
            return key
    return "default"


def _geo_factor(city: str) -> float:
    city_lower = city.lower()
    for key, factor in GEO_INDEX.items():
        if key in city_lower:
            return factor
    return 1.0


def _age_risk_factor(age: Optional[int]) -> float:
    if not age:
        return 1.0
    if age < 30: return 0.95
    if age < 50: return 1.0
    if age < 65: return 1.10
    return 1.25


def _comorbidity_factor(comorbidities: list[str]) -> float:
    total = 0.0
    joined = " ".join(comorbidities).lower()
    for key, surcharge in COMORBIDITY_SURCHARGE.items():
        if key in joined:
            total += surcharge
    return 1.0 + min(total, 0.50)


def estimate_cost_range(procedure, hospital_tier, city, age=None, comorbidities=None) -> list[int]:
    comorbidities = comorbidities or []
    key = _get_procedure_key(procedure)
    base_low, base_high = PROCEDURE_COSTS[key]
    mul = TIER_MULTIPLIER.get(hospital_tier, 1.0) * _geo_factor(city) * _age_risk_factor(age) * _comorbidity_factor(comorbidities)
    return [int(base_low * mul), int(base_high * mul)]


def full_cost_breakdown(procedure, hospital_tier, city, age=None, comorbidities=None) -> dict:
    low, high = estimate_cost_range(procedure, hospital_tier, city, age, comorbidities)
    return {
        "procedure":     [int(low * 0.45), int(high * 0.45)],
        "consultation":  [int(low * 0.05), int(high * 0.05)],
        "hospital_stay": [int(low * 0.20), int(high * 0.20)],
        "diagnostics":   [int(low * 0.10), int(high * 0.10)],
        "medicines":     [int(low * 0.08), int(high * 0.08)],
        "contingency":   [int(low * 0.12), int(high * 0.12)],
    }


def compute_confidence(procedure, comorbidities, age) -> float:
    base = 0.75
    if _get_procedure_key(procedure) == "default":
        base -= 0.15
    if len(comorbidities) > 2:
        base -= 0.05
    if age and age > 70:
        base -= 0.05
    return round(max(base, 0.45), 2)


def get_risk_flags(comorbidities, age, hospital_tier) -> list[str]:
    flags = []
    joined = " ".join(comorbidities).lower()
    if "diabetes" in joined:
        flags.append("Diabetes may extend recovery time and increase costs")
    if "cardiac history" in joined:
        flags.append("Cardiac history increases ICU likelihood")
    if age and age > 65:
        flags.append("Age-related surgical risk — anaesthesia consultation recommended")
    if hospital_tier == "budget":
        flags.append("Budget hospitals may have limited ICU infrastructure")
    return flags


def get_key_drivers(procedure, city, hospital_tier) -> list[str]:
    drivers = [f"Procedure: {procedure}"]
    geo = _geo_factor(city)
    if geo > 1.2:
        drivers.append(f"Metro city pricing premium ({city})")
    elif geo < 0.9:
        drivers.append(f"Tier-2 city pricing advantage ({city})")
    drivers.append(f"Hospital tier: {hospital_tier}")
    return drivers
