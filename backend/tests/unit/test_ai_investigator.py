import pytest
from app.services.ai.investigator import InvestigatorService
from app.services.ai.mock_provider import MockAIProvider
from app.services.trace_engine import TraceEngine
from app.core.database import get_transaction, get_events_for_transaction, get_ledger_entries_for_transaction
from app.schemas.investigation import ConfidenceLevel


@pytest.mark.asyncio
async def test_ai_investigator_generates_structured_output():
    # Primary demo transaction dec_987654321
    tx = get_transaction("dec_987654321")
    assert tx is not None
    events = get_events_for_transaction("dec_987654321")
    ledger = get_ledger_entries_for_transaction("dec_987654321")

    trace = TraceEngine.reconstruct_trace(tx, events, ledger)
    investigator = InvestigatorService(provider=MockAIProvider())

    result = await investigator.investigate(trace)

    assert result.summary is not None
    assert result.failure_stage == "BENEFICIARY_BANK"
    assert "E1042" in result.root_cause or "BENEFICIARY_BANK_UNAVAILABLE" in result.root_cause
    assert len(result.evidence) > 0
    assert result.confidence == ConfidenceLevel.HIGH
    assert any(e.event_id == "evt_fail_004" for e in result.evidence)


def test_ai_context_contains_no_mutation_mechanisms():
    tx = get_transaction("dec_987654321")
    events = get_events_for_transaction("dec_987654321")
    ledger = get_ledger_entries_for_transaction("dec_987654321")

    trace = TraceEngine.reconstruct_trace(tx, events, ledger)
    investigator = InvestigatorService()
    ctx = investigator.build_trace_context(trace)

    assert "transaction" in ctx
    assert "canonical_events" in ctx
    assert "lifecycle" in ctx
    assert "failure_analysis" in ctx
    assert "reconciliation" in ctx
    # Ensure raw DB connection/secrets are never passed
    assert "db" not in ctx
    assert "session" not in ctx
