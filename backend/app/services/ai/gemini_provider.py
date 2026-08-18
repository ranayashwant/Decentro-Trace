import json
import httpx
from typing import Any
from app.services.ai.base import AIProvider
from app.schemas.investigation import InvestigationResult
from app.services.ai.llm_provider import SYSTEM_PROMPT


class GeminiAIProvider(AIProvider):
    """
    Google Gemini API Provider.
    Calls Gemini's GenerateContent endpoint with structured JSON output and temperature 0.1.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    async def investigate(self, trace_context: dict[str, Any]) -> InvestigationResult:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        user_content = json.dumps(trace_context, indent=2, default=str)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        request_body = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [{"text": f"Analyze this reconstructed transaction trace context:\n\n{user_content}"}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=request_body)

            if response.status_code != 200:
                # Fallback to gemini-1.5-flash if 2.5-flash is not available for this key
                fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                response = await client.post(fallback_url, json=request_body)
                if response.status_code != 200:
                    raise RuntimeError(f"Gemini API request failed with status {response.status_code}: {response.text}")

            res_json = response.json()
            raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
            parsed_data = json.loads(raw_text)

            return InvestigationResult.model_validate(parsed_data)
