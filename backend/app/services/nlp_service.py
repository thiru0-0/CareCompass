"""
NLP Service: Translates free-text user queries into structured medical concepts.
Uses an LLM to extract condition, procedure, location, budget, and maps to ICD-10.
Falls back to local keyword parsing when no API key is configured.
"""
import os
import json
import re
import logging
import httpx
from app.models.query import UserQuery, ParsedQuery

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCIk-bkRgIgveP_G2x-S9RsRR5MLsVRI4Q")
GEMINI_MODEL = "gemini-flash-latest"

SYSTEM_PROMPT = """You are a medical query parser for CareCompass, an Indian healthcare navigation platform. Your job is to extract structured clinical and logistical information from natural language queries written by Indian patients or their family members.

Queries may be in English, Hinglish, or informal language. Always interpret charitably — "sugar" means diabetes, "BP" means hypertension, "stone" means kidney/gallbladder stone, "blockage" means arterial blockage, "fits" means seizures/epilepsy.

Respond ONLY with a valid JSON object. No markdown. No explanation. No preamble. No trailing text.

Output schema:
{
  "primary_condition": {
    "name": "Full medical condition name in English (e.g., Coronary Artery Disease)",
    "icd10_code": "ICD-10 code (e.g., I25.1) or null if uncertain",
    "confidence": 0.0-1.0
  },
  "secondary_conditions": [
    {
      "name": "Comorbidity or secondary condition name",
      "icd10_code": "ICD-10 code or null"
    }
  ],
  "recommended_procedure": {
    "name": "Most likely required procedure (e.g., Coronary Angioplasty)",
    "procedure_type": "surgical | diagnostic | medical_management | consultation",
    "is_elective": true
  },
  "patient": {
    "age_estimate": integer estimated age or null,
    "age_group": "pediatric | adult | senior | unknown",
    "relation": "self | parent | spouse | child | sibling | other | unknown"
  },
  "location": {
    "city": "City name as stated (e.g., Lucknow) or null",
    "state": "Indian state if inferable (e.g., Uttar Pradesh) or null",
    "area": "Locality or area if mentioned (e.g., Banjara Hills) or null"
  },
  "budget": {
    "max_inr": integer or null,
    "preference": "cheapest | best | balanced | unknown"
  },
  "urgency": {
    "level": "emergency | high | medium | low",
    "reason": "one sentence explaining urgency classification"
  },
  "intent": {
    "primary_intent": "find_hospital | cost_estimate | second_opinion | home_care | teleconsult | loan_only | general_info",
    "wants_loan": false
  },
  "financial_signals": {
    "has_insurance": true or false or null,
    "insurer_name": "insurance company name or null",
    "is_govt_employee": true or false or null,
    "is_esi_eligible": true or false or null,
    "income_signal": "below_poverty | low | middle | unknown",
    "budget_sentiment": "desperate | constrained | comfortable | unknown"
  },
  "flags": {
    "ambiguous_condition": false,
    "missing_location": false,
    "multiple_conditions": false,
    "needs_clarification": false,
    "clarification_question": "A single, specific follow-up question to ask the user if needs_clarification is true, else null"
  }
}

Urgency classification rules — apply strictly:
- "emergency": chest pain, breathlessness, stroke symptoms, unconsciousness, heavy bleeding, accident, heart attack, severe head injury
- "high": cancer diagnosis received, active infection, recent abnormal test results, kidney failure, dialysis needed, rapidly worsening symptoms
- "medium": scheduled surgery, planned treatment, chronic condition management, test results pending
- "low": routine checkup, vaccination, health screening, elective cosmetic or non-urgent procedure

Age group rules:
- "pediatric": stated or implied age under 18, or "child", "baby", "bachcha", "beti", "beta"
- "senior": stated or implied age over 60, or "father", "mother", "daadi", "naana", "nani", "uncle" (when context implies elderly)
- "adult": all other adults
- "unknown": no age or relation signal

Budget extraction rules:
- "1 lakh" or "1L" -> 100000
- "1.5 lakh" -> 150000
- "5 lakh" or "5L" -> 500000
- "1 crore" -> 10000000
- If range given ("3 to 5 lakh"), use the upper value as max_inr
- If "affordable" or "cheap" with no number, set max_inr to null and preference to "cheapest"
- If "best" or "no compromise", set max_inr to null and preference to "best"

Procedure type rules:
- "surgical": any operation, transplant, bypass, removal, repair
- "diagnostic": scan, biopsy, endoscopy, blood test, ECG, MRI
- "medical_management": ongoing medication, chemotherapy, dialysis, physiotherapy
- "consultation": second opinion, specialist visit, general checkup

Financial signal rules:
- income_signal = "below_poverty" if user says "garib", "BPL", "no money", "can't afford", "very poor"
- income_signal = "low" if budget stated is under ₹2 lakhs for a major procedure
- is_esi_eligible = true if user mentions "factory worker", "private job", "salary under 21000"
- budget_sentiment = "desperate" if user uses words like "please help", "only option", "last resort"

Comorbidity extraction — always check for and include:
- Diabetes / Type 2 DM / sugar
- Hypertension / BP
- Chronic Kidney Disease / CKD
- Heart disease / previous MI
- Obesity / overweight
- Thyroid disorders
- COPD / asthma
- Cancer history
- Neurological conditions

If the primary condition or location is unclear and confidence is below 0.75, set needs_clarification to true and write a clarification_question that asks the single most important missing detail to improve confidence.

Never invent a city or condition. If genuinely unknown, use null.
"""

# ─── Local fallback keyword maps ───────────────────────────────────────────────
PROCEDURE_MAP = {
    "knee replacement":    ("Osteoarthritis of Knee", "Knee Replacement", "M17.1"),
    "hip replacement":     ("Osteoarthritis of Hip", "Hip Replacement", "M16.1"),
    "angioplasty":         ("Coronary Artery Disease", "Angioplasty", "I25.1"),
    "bypass":              ("Coronary Artery Disease", "Bypass Surgery (CABG)", "I25.1"),
    "cataract":            ("Cataract", "Cataract Surgery", "H25.9"),
    "appendectomy":        ("Appendicitis", "Appendectomy", "K35.8"),
    "appendix":            ("Appendicitis", "Appendectomy", "K35.8"),
    "gallbladder":         ("Cholelithiasis", "Gallbladder Removal", "K80.2"),
    "angiography":         ("Coronary Artery Disease", "Angiography", "I25.1"),
    "ct scan":             ("Diagnostic Imaging", "CT Scan", None),
    "mri":                 ("Diagnostic Imaging", "MRI", None),
    "dialysis":            ("Chronic Kidney Disease", "Dialysis", "N18.6"),
    "chemotherapy":        ("Cancer", "Chemotherapy", "C80.1"),
    "radiation":           ("Cancer", "Radiation Therapy", "C80.1"),
    "spinal":              ("Spinal Disorder", "Spinal Surgery", "M48.0"),
    "spine":               ("Spinal Disorder", "Spinal Surgery", "M48.0"),
    "heart":               ("Coronary Artery Disease", "Angioplasty", "I25.1"),
    "cardiac":             ("Coronary Artery Disease", "Angioplasty", "I25.1"),
}

CITY_KEYWORDS = [
    "chennai", "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad",
    "nagpur", "pune", "kolkata", "jaipur", "lucknow", "ahmedabad", "bhopal",
    "tamil nadu", "maharashtra", "karnataka", "telangana", "west bengal",
]


def _local_parse(user_query: UserQuery) -> ParsedQuery:
    """Keyword-based fallback parser — works without any API key."""
    text_lower = user_query.text.lower()

    # Match procedure
    condition, procedure, icd10 = "General Medical Condition", "Consultation", None
    for keyword, (cond, proc, code) in PROCEDURE_MAP.items():
        if keyword in text_lower:
            condition, procedure, icd10 = cond, proc, code
            break

    # Extract location from text
    location = user_query.location
    if not location:
        for city in CITY_KEYWORDS:
            if city in text_lower:
                location = city.title()
                break
    location = location or "India"

    # Extract budget from text
    budget = user_query.budget
    if not budget:
        # "under 3 lakh" / "3 lakh" / "300000"
        lakh_match = re.search(r"(\d+)\s*lakh", text_lower)
        if lakh_match:
            budget = int(lakh_match.group(1)) * 100_000
        else:
            num_match = re.search(r"under\s+(\d{4,})", text_lower)
            if num_match:
                budget = int(num_match.group(1))

    # Determine if clarification is needed
    needs_clarification = False
    clarification_question = None
    
    # Ask clarification if location is missing or unclear
    if not user_query.location and location == "India":
        needs_clarification = True
        clarification_question = "Which city or location do you prefer for treatment?"
    # Ask clarification if budget is missing for major procedures
    elif not budget and procedure in ["Knee Replacement", "Bypass Surgery (CABG)", "Angioplasty"]:
        needs_clarification = True
        clarification_question = "What is your approximate budget for this procedure?"
    # Ask clarification if condition is unclear
    elif condition == "General Medical Condition":
        needs_clarification = True
        clarification_question = "Can you describe your symptoms or condition more specifically?"

    flags = {
        "ambiguous_condition": condition == "General Medical Condition",
        "missing_location": not user_query.location and location == "India",
        "multiple_conditions": False,
        "needs_clarification": needs_clarification,
        "clarification_question": clarification_question
    }

    # Mock financial signals for testing
    fin_signals = {}
    if any(x in text_lower for x in ["poor", "bpl", "garib", "no money", "cannot afford"]):
        fin_signals["income_signal"] = "below_poverty"
        fin_signals["budget_sentiment"] = "desperate"
    if any(x in text_lower for x in ["factory worker", "private job"]):
        fin_signals["is_esi_eligible"] = True
    if "government employee" in text_lower or "cghs" in text_lower:
        fin_signals["is_govt_employee"] = True
        
    urgency = "low"
    if any(x in text_lower for x in ["emergency", "severe", "now", "chest pain", "breathlessness"]):
        urgency = "emergency"

    logger.info(f"[LOCAL PARSER] Extracted: {condition} / {procedure} / {location} / needs_clarification={needs_clarification}")
    return ParsedQuery(
        original_text=user_query.text,
        condition=condition,
        procedure=procedure,
        icd10_code=icd10,
        location=location,
        lat=user_query.lat,
        lng=user_query.lng,
        budget=budget,
        age=user_query.age,
        comorbidities=user_query.comorbidities or [],
        urgency=urgency,
        urgency_reason="Locally flagged as emergency due to keywords" if urgency == "emergency" else "",
        flags=flags,
        financial_signals=fin_signals
    )


async def parse_query(user_query: UserQuery) -> ParsedQuery:
    # Fall back to local parsing if no API key is configured
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-api-key-here":
        logger.warning("No Gemini API key — using local keyword parser")
        return _local_parse(user_query)

    prompt = f"""User query: "{user_query.text}"
Additional context:
- Location hint: {user_query.location or 'not provided'}
- Age: {user_query.age or 'not provided'}
- Comorbidities: {', '.join(user_query.comorbidities) if user_query.comorbidities else 'none'}
"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                },
            )
            response.raise_for_status()
            data = response.json()

        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        # Strip any accidental markdown fences
        clean = re.sub(r"```json|```", "", raw).strip()
        parsed = json.loads(clean)

        loc_data = parsed.get("location", {})
        location = loc_data.get("city") or user_query.location or "India"
        
        primary_cond = parsed.get("primary_condition", {})
        procedure_obj = parsed.get("recommended_procedure", {})
        budget_obj = parsed.get("budget", {})
        patient_obj = parsed.get("patient", {})
        urgency_obj = parsed.get("urgency", {})
        flags = parsed.get("flags", {})
        financial_signals = parsed.get("financial_signals", {})
        
        condition = primary_cond.get("name", "Unknown Condition")
        icd10 = primary_cond.get("icd10_code")
        procedure = procedure_obj.get("name", "Consultation")
        
        budget = budget_obj.get("max_inr") or user_query.budget
        age = patient_obj.get("age_estimate") or user_query.age
        
        secondary = parsed.get("secondary_conditions", [])
        comorbidities = [c.get("name") for c in secondary if "name" in c]
        if not comorbidities:
            comorbidities = user_query.comorbidities or []

        return ParsedQuery(
            original_text=user_query.text,
            condition=condition,
            procedure=procedure,
            icd10_code=icd10,
            location=location,
            lat=user_query.lat,
            lng=user_query.lng,
            budget=budget,
            age=age,
            comorbidities=comorbidities,
            urgency=urgency_obj.get("level", "low"),
            urgency_reason=urgency_obj.get("reason", ""),
            flags=flags,
            financial_signals=financial_signals,
        )
    except Exception as e:
        logger.error(f"Gemini API failed ({e}), falling back to local parser")
        return _local_parse(user_query)
