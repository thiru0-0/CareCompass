"""Geo utilities — geocoding city names to lat/lng."""
from typing import Optional

CITY_COORDS = {
    "chennai":   (13.0827, 80.2707),
    "mumbai":    (19.0760, 72.8777),
    "delhi":     (28.6139, 77.2090),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "nagpur":    (21.1458, 79.0882),
    "pune":      (18.5204, 73.8567),
    "kolkata":   (22.5726, 88.3639),
    "jaipur":    (26.9124, 75.7873),
    "lucknow":   (26.8467, 80.9462),
}

def city_to_coords(city: str) -> Optional[tuple[float, float]]:
    return CITY_COORDS.get(city.lower().strip())

def format_inr(amount: int) -> str:
    if amount >= 100_000:
        return f"₹{amount/100_000:.1f}L"
    if amount >= 1_000:
        return f"₹{amount/1_000:.0f}K"
    return f"₹{amount}"
