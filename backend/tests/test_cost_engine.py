import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services.cost_service import estimate_cost_range, full_cost_breakdown, compute_confidence, get_risk_flags, _get_procedure_key

def test_procedure_key_matching():
    assert _get_procedure_key("Total knee replacement surgery") == "knee replacement"
    assert _get_procedure_key("coronary angioplasty") == "angioplasty"
    assert _get_procedure_key("something unknown") == "default"

def test_estimate_returns_range():
    low, high = estimate_cost_range("angioplasty", "mid", "nagpur")
    assert low < high and low > 0

def test_premium_more_than_budget():
    low_p, _ = estimate_cost_range("knee replacement", "premium", "chennai")
    low_b, _ = estimate_cost_range("knee replacement", "budget", "chennai")
    assert low_p > low_b

def test_metro_more_than_tier2():
    low_m, _ = estimate_cost_range("angioplasty", "mid", "mumbai")
    low_t, _ = estimate_cost_range("angioplasty", "mid", "nagpur")
    assert low_m > low_t

def test_comorbidity_increases_cost():
    base_low, _ = estimate_cost_range("angioplasty", "mid", "chennai")
    comor_low, _ = estimate_cost_range("angioplasty", "mid", "chennai", comorbidities=["diabetes", "cardiac history"])
    assert comor_low > base_low

def test_confidence_lower_for_unknown():
    c1 = compute_confidence("angioplasty", [], None)
    c2 = compute_confidence("some unknown procedure xyz", [], None)
    assert c1 > c2

def test_risk_flags_diabetes():
    flags = get_risk_flags(["diabetes"], 40, "mid")
    assert any("diabetes" in f.lower() for f in flags)

if __name__ == "__main__":
    test_procedure_key_matching(); print("✓ procedure key")
    test_estimate_returns_range(); print("✓ range")
    test_premium_more_than_budget(); print("✓ premium > budget")
    test_metro_more_than_tier2(); print("✓ metro > tier2")
    test_comorbidity_increases_cost(); print("✓ comorbidity surcharge")
    test_confidence_lower_for_unknown(); print("✓ confidence")
    test_risk_flags_diabetes(); print("✓ risk flags")
    print("\nAll cost engine tests passed!")
