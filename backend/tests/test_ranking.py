import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services.ranking_service import rank_hospitals, haversine_km, clinical_score
from app.models.query import ParsedQuery

def make_parsed(location="Chennai", procedure="angioplasty"):
    return ParsedQuery(original_text="test", condition="CAD", procedure=procedure,
                       icd10_code=None, location=location, lat=None, lng=None,
                       budget=None, age=None, comorbidities=[])

def test_returns_results():
    assert len(rank_hospitals(make_parsed(), top_n=3)) > 0

def test_scores_descending():
    results = rank_hospitals(make_parsed(), top_n=5)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)

def test_haversine():
    d = haversine_km(13.08, 80.27, 21.15, 79.09)
    assert 900 < d < 1100

def test_clinical_score():
    h = {"specializations": ["cardiology", "neurology"]}
    assert 0 <= clinical_score(h, "angioplasty") <= 1

if __name__ == "__main__":
    test_returns_results(); print("✓ returns results")
    test_scores_descending(); print("✓ scores descending")
    test_haversine(); print("✓ haversine distance")
    test_clinical_score(); print("✓ clinical score")
    print("\nAll ranking tests passed!")
