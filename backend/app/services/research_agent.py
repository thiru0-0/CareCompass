"""
Agent 2: Autonomous Hospital Research Agent
Fills missing hospital data by dynamically calling external data tools.
"""
import os
import time
import json
import logging
import httpx
import asyncio

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCIk-bkRgIgveP_G2x-S9RsRR5MLsVRI4Q")
GEMINI_MODEL = "gemini-flash-latest"

# ─── Tool Implementations (Simulated for this implementation) ─────────────

async def query_nha_database(hospital_id: str) -> dict:
    """Checks NHA empanelment and NABH status."""
    await asyncio.sleep(0.5)
    return {"nabh_accredited": True, "nha_empaneled": True}

async def search_google_maps(hospital_name: str, city: str) -> dict:
    """Gets rating, review count, and phone number."""
    await asyncio.sleep(0.8)
    return {"rating": 4.5, "review_count": 1200, "phone": "+91-9876543210"}

async def fetch_hospital_website(hospital_name: str) -> dict:
    """Scrapes department list and pricing tiers."""
    await asyncio.sleep(1.0)
    return {"tier": "mid", "specializations": ["general", "cardiology"]}

# Tool dispatch mapping
TOOL_DISPATCH = {
    "query_nha_database": query_nha_database,
    "search_google_maps": search_google_maps,
    "fetch_hospital_website": fetch_hospital_website,
}

# ─── Gemini Tool Definitions ──────────────────────────────────────────────

TOOLS_DEF = [
    {
        "functionDeclarations": [
            {
                "name": "query_nha_database",
                "description": "Query the National Health Authority database to check if a hospital is NABH accredited.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "hospital_id": {"type": "STRING"}
                    },
                    "required": ["hospital_id"]
                }
            },
            {
                "name": "search_google_maps",
                "description": "Search Google Maps to retrieve the hospital's rating and review count.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "hospital_name": {"type": "STRING"},
                        "city": {"type": "STRING"}
                    },
                    "required": ["hospital_name", "city"]
                }
            },
            {
                "name": "fetch_hospital_website",
                "description": "Fetch the hospital's website to determine its pricing tier (premium, mid, budget) and specializations.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "hospital_name": {"type": "STRING"}
                    },
                    "required": ["hospital_name"]
                }
            }
        ]
    }
]

SYSTEM_PROMPT = """You are an Autonomous Hospital Research Agent.
Your goal is to fill in missing information for hospitals so they can be properly scored.
Look at the missing fields, and call the appropriate tools to find the missing information.
Once you have the information, or if you cannot find it, return the final filled JSON object.
NEVER make up data. Only use the data returned by the tools.
"""

async def run_research_agent(hospital: dict, missing_fields: list[str], timeout: int = 8) -> dict:
    """
    Agentic Loop:
    1. Send hospital info and missing fields to Gemini.
    2. Gemini decides which tools to call.
    3. We execute the tools and return the results to Gemini.
    4. Gemini synthesizes the final filled hospital object.
    Enforces a strict timeout.
    """
    logger.info(f"[Agent 2] Researching {hospital['name']} for missing fields: {missing_fields}")
    start_time = time.time()
    
    messages = [
        {
            "role": "user",
            "parts": [{"text": f"Hospital: {json.dumps(hospital)}\nMissing Fields: {missing_fields}\nPlease find the missing information and return the updated hospital JSON object."}]
        }
    ]
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            while time.time() - start_time < timeout:
                payload = {
                    "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                    "contents": messages,
                    "tools": TOOLS_DEF,
                }
                
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                
                candidate = data["candidates"][0]
                parts = candidate["content"]["parts"]
                
                # Find if any part is a function call
                function_call_part = next((p for p in parts if "functionCall" in p), None)
                
                # Check if it's a function call
                if function_call_part:
                    function_call = function_call_part["functionCall"]
                    tool_name = function_call["name"]
                    tool_args = function_call.get("args", {})
                    
                    logger.info(f"[Agent 2] Calling tool {tool_name} with args {tool_args}")
                    
                    # Append the model's FULL response (including thoughts) to history
                    messages.append({
                        "role": "model",
                        "parts": parts
                    })
                    
                    # Execute tool
                    if tool_name in TOOL_DISPATCH:
                        tool_result = await TOOL_DISPATCH[tool_name](**tool_args)
                    else:
                        tool_result = {"error": "Tool not found"}
                        
                    # Append the tool response to history
                    messages.append({
                        "role": "user",
                        "parts": [{
                            "functionResponse": {
                                "name": tool_name,
                                "response": {"result": tool_result}
                            }
                        }]
                    })
                else:
                    # It's a text response, presumably the final JSON
                    text_resp = next((p.get("text", "") for p in parts if "text" in p), "")
                    clean_json = text_resp.replace("```json", "").replace("```", "").strip()
                    try:
                        updated_hospital = json.loads(clean_json)
                        logger.info(f"[Agent 2] Research complete in {time.time() - start_time:.2f}s")
                        return updated_hospital
                    except json.JSONDecodeError:
                        logger.warning("[Agent 2] Failed to parse final output as JSON")
                        return hospital
            
            logger.warning("[Agent 2] Time budget exhausted")
            return hospital
            
    except httpx.HTTPStatusError as e:
        logger.error(f"[Agent 2] API Error: {e.response.text}")
        return hospital
    except Exception as e:
        logger.error(f"[Agent 2] Error during research: {e}")
        return hospital
