"""
Scheme Eligibility Service
Checks for applicable financial assistance across 4 tiers:
1. Full Government Coverage (PM-JAY, State schemes)
2. Disease-Specific National Programmes
3. Employer and Insurance Coverage (CGHS, ESI)
4. NGO, Trust and CSR Funds
"""

def check_eligibility(parsed_query) -> list[dict]:
    schemes = []
    
    condition = parsed_query.condition.lower()
    procedure = parsed_query.procedure.lower()
    state = parsed_query.location.lower()
    budget = parsed_query.budget
    fin_signals = parsed_query.financial_signals or {}
    
    # Tier 1: Full Government Coverage
    # Check income signals and budget
    income_signal = fin_signals.get("income_signal")
    if budget is None or budget <= 150000 or income_signal in ["below_poverty", "low"]:
        schemes.append({
            "tier": 1,
            "name": "Ayushman Bharat PM-JAY",
            "description": "Provides up to ₹5 lakhs per family per year for secondary and tertiary hospitalisation. Applicable at empanelled hospitals if you meet income criteria.",
            "type": "Government Scheme"
        })
    
    # State specific schemes (basic matching)
    if any(x in state or x in condition for x in ["tamil nadu", "chennai"]):
        schemes.append({
            "tier": 1,
            "name": "CM's Comprehensive Health Insurance Scheme (CMCHIS)",
            "description": "State scheme covering up to ₹5 lakhs for residents of Tamil Nadu.",
            "type": "State Scheme"
        })
    elif any(x in state or x in condition for x in ["west bengal", "kolkata"]):
        schemes.append({
            "tier": 1,
            "name": "Swasthya Sathi",
            "description": "Basic health cover up to ₹5 lakh per annum per family in West Bengal.",
            "type": "State Scheme"
        })
    elif any(x in state or x in condition for x in ["telangana", "hyderabad", "andhra"]):
        schemes.append({
            "tier": 1,
            "name": "Aarogyasri",
            "description": "State scheme providing financial protection to families living below poverty line.",
            "type": "State Scheme"
        })
        
    # Tier 2: Disease-Specific National Programmes
    if "tuberculosis" in condition or "tb" in condition:
        schemes.append({
            "tier": 2,
            "name": "National TB Elimination Programme (NTEP)",
            "description": "All tuberculosis treatment is free at government facilities. Includes diagnosis, drugs, and nutrition support.",
            "type": "National Programme"
        })
    if any(x in condition for x in ["cancer", "diabetes", "cardio", "stroke", "heart", "coronary", "artery"]):
        schemes.append({
            "tier": 2,
            "name": "NPCDCS Programme",
            "description": "Free screening, early detection, and management for Cancer, Diabetes, CVD, and Stroke at district hospitals.",
            "type": "National Programme"
        })
    if "cataract" in procedure:
        schemes.append({
            "tier": 2,
            "name": "National Programme for Control of Blindness (NPCB)",
            "description": "Provides completely free cataract surgeries at government facilities.",
            "type": "National Programme"
        })
        
    # Tier 3: Employer/Insurance
    if fin_signals.get("is_govt_employee"):
        schemes.append({
            "tier": 3,
            "name": "Central Government Health Scheme (CGHS)",
            "description": "As a government employee, you and your dependents are eligible for cashless treatment at empanelled hospitals at fixed rates.",
            "type": "Employer Benefits"
        })
    elif fin_signals.get("is_esi_eligible"):
        schemes.append({
            "tier": 3,
            "name": "Employees' State Insurance (ESI)",
            "description": "Based on your employment profile, your entire medical care may be completely free at ESI hospitals.",
            "type": "Employer Benefits"
        })
    else:
        schemes.append({
            "tier": 3,
            "name": "CGHS / ESI Coverage Check",
            "description": "Are you a government employee (CGHS) or earning under ₹21,000/month in a private job (ESI)? Your treatment could be fully covered.",
            "type": "Employer Benefits"
        })
        
    if fin_signals.get("has_insurance"):
        insurer = fin_signals.get("insurer_name") or "your insurance provider"
        schemes.append({
            "tier": 3,
            "name": f"Private Health Insurance ({insurer})",
            "description": f"You mentioned having insurance. A significant portion of this procedure will likely be covered. Check your policy limits.",
            "type": "Insurance"
        })
    
    # Tier 4: NGO/Trusts (Only if budget is low and specific conditions match)
    if (budget is not None and budget <= 100000) or income_signal in ["below_poverty", "low"]:
        if "cancer" in condition:
            schemes.append({
                "tier": 4,
                "name": "Tata Trusts / HCG Foundation",
                "description": "Application-based financial assistance for cancer patients who cannot afford treatment.",
                "type": "NGO / Trust"
            })
        if any(x in condition or x in procedure for x in ["heart", "cardio", "coronary", "bypass"]):
            schemes.append({
                "tier": 4,
                "name": "Narayana Hrudayalaya Foundation",
                "description": "Charitable fund operating a sliding scale fee structure for patients who cannot afford cardiac surgery.",
                "type": "NGO / Trust"
            })
            
    return schemes
