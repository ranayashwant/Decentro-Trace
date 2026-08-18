from fastapi import APIRouter, HTTPException, status
from app.models.trace import Trace
from app.models.transaction import Transaction
from app.schemas.investigation import InvestigationResult
from app.core.database import (
    get_transaction,
    list_transactions,
    get_events_for_transaction,
    get_ledger_entries_for_transaction
)
from app.services.trace_engine import TraceEngine
from app.services.ai.investigator import InvestigatorService

router = APIRouter(prefix="/transactions", tags=["Transactions & Traces"])


@router.get("", response_model=list[Transaction])
def get_all_transactions():
    """
    Returns all seeded/recorded transactions for quick selection in the UI.
    """
    return list_transactions()


@router.get("/{transaction_id}/trace", response_model=Trace)
def get_transaction_trace(transaction_id: str):
    """
    Deterministically reconstructs the full canonical trace for the given transaction ID.
    Performs event normalization, duplicate detection, temporal sorting,
    anomaly detection, lifecycle evaluation, and ledger reconciliation.
    """
    tx = get_transaction(transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' was not found."
        )

    raw_events = get_events_for_transaction(transaction_id)
    ledger_entries = get_ledger_entries_for_transaction(transaction_id)

    canonical_trace = TraceEngine.reconstruct_trace(
        transaction=tx,
        raw_events=raw_events,
        ledger_entries=ledger_entries
    )

    return canonical_trace


@router.post("/{transaction_id}/investigate", response_model=InvestigationResult)
async def investigate_transaction(transaction_id: str):
    """
    Uses the AI Investigator layer to generate a structured, evidence-backed
    explanation and recommended next action based solely on the canonical deterministic trace.
    """
    tx = get_transaction(transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' was not found."
        )

    raw_events = get_events_for_transaction(transaction_id)
    ledger_entries = get_ledger_entries_for_transaction(transaction_id)

    canonical_trace = TraceEngine.reconstruct_trace(
        transaction=tx,
        raw_events=raw_events,
        ledger_entries=ledger_entries
    )

    investigator = InvestigatorService()
    try:
        result = await investigator.investigate(canonical_trace)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI Investigation failed: {str(e)}"
        )
