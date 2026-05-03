def scale_confidence(raw: float, label: bool = False):
    if not label:
        return round(raw, 2)
    if raw >= 0.75:
        return "High"
    if raw >= 0.55:
        return "Moderate"
    return "Low"
