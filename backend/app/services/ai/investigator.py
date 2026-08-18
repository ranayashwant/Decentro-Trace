from typing import Optional
from app.models.trace import Trace
from app.schemas.investigation import InvestigationResult
from app.services.ai.base import AIProvider
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai.llm_provider import LLMProvider
from app.services.ai.gemini_provider import GeminiAIProvider
from app.core.config import settings


class InvestigatorService:
    """
    Coordinates AI investigation:
    1. Prepares a sanitized, deterministic context dict from the canonical Trace.
    2. Invokes the isolated AIProvider.
    3. Returns validated InvestigationResult.
    """

    def __init__(self, provider: Optional[AIProvider] = None):
        if provider:
            self.provider = provider
        elif (settings.AI_PROVIDER == "gemini" or settings.GEMINI_API_KEY) and settings.GEMINI_API_KEY:
            self.provider = GeminiAIProvider(api_key=settings.GEMINI_API_KEY)
        elif (settings.AI_PROVIDER == "openai" or settings.OPENAI_API_KEY) and settings.OPENAI_API_KEY:
            self.provider = LLMProvider(api_key=settings.OPENAI_API_KEY)
        else:
            self.provider = MockAIProvider()

    def build_trace_context(self, trace: Trace) -> dict:
        """
        Extracts only allowed deterministic facts for the LLM.
        Direct DB access or mutation abilities are strictly avoided.
        """
        return {
            "transaction": {
                "id": trace.transaction.id,
                "reference_id": trace.transaction.reference_id,
                "amount": trace.transaction.amount,
                "currency": trace.transaction.currency,
                "transfer_type": trace.transaction.transfer_type.value,
                "beneficiary_id": trace.transaction.beneficiary_id,
                "created_at": trace.transaction.created_at.isoformat()
            },
            "lifecycle": {
                "initial_status": trace.lifecycle.initial_status.value if trace.lifecycle.initial_status else None,
                "final_status": trace.lifecycle.final_status.value,
                "is_terminal": trace.lifecycle.is_terminal,
                "duration_ms": trace.lifecycle.duration_ms
            },
            "failure_analysis": {
                "failed": trace.failure_analysis.failed,
                "failure_stage": trace.failure_analysis.failure_stage.value,
                "observed_status": trace.failure_analysis.observed_status.value if trace.failure_analysis.observed_status else None,
                "observed_error_code": trace.failure_analysis.observed_error_code,
                "observed_error_message": trace.failure_analysis.observed_error_message,
                "failure_event_id": trace.failure_analysis.failure_event_id,
                "failure_timestamp": trace.failure_analysis.failure_timestamp.isoformat() if trace.failure_analysis.failure_timestamp else None
            },
            "canonical_events": [
                {
                    "id": e.id,
                    "event_type": e.event_type.value,
                    "source": e.source.value,
                    "status": e.status.value,
                    "occurred_at": e.occurred_at.isoformat(),
                    "sequence": e.sequence,
                    "payload": e.payload
                }
                for e in trace.canonical_events
            ],
            "integrity": {
                "total_events_received": trace.integrity.total_events_received,
                "canonical_events_count": trace.integrity.canonical_events_count,
                "duplicate_events_count": trace.integrity.duplicate_events_count,
                "out_of_order_received": trace.integrity.out_of_order_received,
                "missing_expected_events": trace.integrity.missing_expected_events,
                "state_conflicts": [
                    {
                        "event_1_id": c.event_1_id,
                        "event_1_status": c.event_1_status.value,
                        "event_2_id": c.event_2_id,
                        "event_2_status": c.event_2_status.value,
                        "description": c.description
                    }
                    for c in trace.integrity.state_conflicts
                ]
            },
            "reconciliation": {
                "debited_amount": trace.reconciliation.debited_amount,
                "reversed_amount": trace.reconciliation.reversed_amount,
                "net_impact": trace.reconciliation.net_impact,
                "reconciled": trace.reconciliation.reconciled
            }
        }

    async def investigate(self, trace: Trace) -> InvestigationResult:
        context = self.build_trace_context(trace)
        return await self.provider.investigate(context)
