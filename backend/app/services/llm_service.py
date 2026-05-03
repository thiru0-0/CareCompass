"""
LLM Service
Uses Claude to generate human-readable explanations for cost estimates and
hospital recommendations. All outputs are framed as decision support, never diagnosis.
Falls back to template-based explanations when no API key is configured.
"""
import os
import json
import re
import logging
import httpx

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCIk-bkRgIgveP_G2x-S9RsRR5MLsVRI4Q")
GEMINI_MODEL = "gemini-flash-latest"

EXPLANATION_SYSTEM = """You are a helpful medical cost advisor for an Indian healthcare platform.
Generate a brief, warm, non-alarming explanation for a cost estimate.
Respond ONLY with a JSON object — no markdown, no preamble.

JSON schema:
{
  "summary": "2-sentence plain-English summary of the estimate",
  "notes": ["array", "of", "important", "notes"],
  "disclaimer": "One-sentence responsible AI disclaimer"
}

Rules:
- NEVER give a diagnosis or treatment recommendation
- Always frame as 'decision support'
- Use simple language suitable for patients in Tier 2 cities
- Mention that actual costs vary and professional consultation is needed
"""


def _fmt_inr(n: int) -> str:
    if n >= 100_000:
        return f"₹{n/100_000:.1f}L"
    if n >= 1_000:
        return f"₹{n/1_000:.0f}K"
    return f"₹{n}"


def _local_explanation(
    condition: str,
    procedure: str,
    hospital_name: str,
    total_range: list[int],
    comorbidities: list[str],
) -> dict:
    """Template-based fallback — works without any API key."""
    low, high = _fmt_inr(total_range[0]), _fmt_inr(total_range[1])
    comor_note = (
        f"Your reported conditions ({', '.join(comorbidities)}) may affect recovery time and costs."
        if comorbidities
        else "No pre-existing conditions were reported, which is a positive factor."
    )
    return {
        "summary": (
            f"Based on our analysis, {procedure} at {hospital_name} is estimated "
            f"to cost between {low} and {high}. "
            f"This range accounts for hospital tier, city pricing, and patient profile."
        ),
        "notes": [
            f"The estimate covers procedure fees, hospital stay, diagnostics, medicines, and contingency.",
            comor_note,
            "Actual costs may vary based on specific clinical requirements and doctor recommendations.",
            "We recommend getting a detailed quote directly from the hospital before making a decision.",
        ],
        "disclaimer": "This is AI-powered decision support only — not medical advice. Always consult a qualified healthcare professional.",
    }


async def generate_explanation(
    condition: str,
    procedure: str,
    hospital_name: str,
    total_range: list[int],
    comorbidities: list[str],
) -> dict:
    # Fall back to local template if no API key
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-api-key-here":
        logger.warning("No Gemini API key — using template explanation")
        return _local_explanation(condition, procedure, hospital_name, total_range, comorbidities)

    prompt = f"""
Condition: {condition}
Procedure: {procedure}
Hospital: {hospital_name}
Estimated cost range: ₹{total_range[0]:,} – ₹{total_range[1]:,}
Comorbidities: {', '.join(comorbidities) if comorbidities else 'None'}
"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "system_instruction": {"parts": [{"text": EXPLANATION_SYSTEM}]},
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                },
            )
            response.raise_for_status()
            data = response.json()

        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception as e:
        logger.error(f"Gemini API failed ({e}), falling back to template explanation")
        return _local_explanation(condition, procedure, hospital_name, total_range, comorbidities)
