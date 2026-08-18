import json
import httpx
from typing import Any
from app.services.ai.base import AIProvider
from app.schemas.investigation import InvestigationResult, ConfidenceLevel
from app.core.config import settings

SYSTEM_PROMPT = """You are Decentro Trace's Transaction Debugger AI.
You are analyzing an ALREADY DETERMINISTICALLY RECONSTRUCTED fintech payout trace.

CRITICAL RULES:
1. The supplied trace is the deterministic source of truth.
2. DO NOT invent events, statuses, timestamps, amounts, provider responses, or ledger entries.
3. Explicitly separate observed facts from inference.
4. Support your findings with references to specific event IDs (e.g. evt_proc_003).
5. Never resolve deterministic conflicts yourself or guess a winner.
6. Never claim an operational action is safe when evidence does not establish that.
7. You must output ONLY a valid JSON object strictly adhering to the specified schema.

JSON SCHEMA:
{
  "summary": "Concise 2-sentence technical summary of the lifecycle and failure",
  "failure_stage": "CLIENT_REQUEST | DECENTRO_GATEWAY | PROVIDER_ROUTING | BENEFICIARY_SWITCH | BENEFICIARY_BANK | LEDGER_EXECUTION | null",
  "root_cause": "Evidence-backed root cause explanation based strictly on observed codes/payloads",
  "evidence": [
    {
      "event_id": "string",
      "reason": "string"
    }
  ],
  "recommended_action": "Specific, safe engineering/ops recommendation (e.g. retry safety, beneficiary contact, manual bank lookup)",
  "confidence": "high" | "medium" | "low",
  "uncertainty": "string or null"
}
"""


class LLMProvider(AIProvider):
    """
    Live LLM Provider using OpenAI or Gemini standard API.
    Sends deterministic trace facts and validates structured output.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def investigate(self, trace_context: dict[str, Any]) -> InvestigationResult:
        if not self.api_key:
            raise ValueError("LLM API key is not configured.")

        user_content = json.dumps(trace_context, indent=2, default=str)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Analyze this transaction trace context:\n\n{user_content}"}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }
            )

            if response.status_code != 200:
                raise RuntimeError(f"LLM API request failed with status {response.status_code}: {response.text}")

            res_json = response.json()
            raw_content = res_json["choices"][0]["message"]["content"]
            parsed_data = json.loads(raw_content)

            # Validate against Pydantic schema
            return InvestigationResult.model_validate(parsed_data)
