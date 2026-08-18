from datetime import datetime, timezone
from app.models.transaction import Transaction
from app.models.event import Event
from app.models.ledger import LedgerEntry
from app.models.enums import (
    TransferType,
    TransactionStatus,
    EventType,
    EventSource,
    LedgerEntryType,
    FailureStage,
)
from app.services.trace_engine import TraceEngine
from app.services.reconciliation import ReconciliationEngine


def create_sample_tx(tx_id: str = "dec_test", amount: float = 25000.0) -> Transaction:
    return Transaction(
        id=tx_id,
        reference_id="ref_test",
        amount=amount,
        currency="INR",
        transfer_type=TransferType.IMPS,
        beneficiary_id="ben_test",
        created_at=datetime(2026, 8, 18, 10, 0, 0, tzinfo=timezone.utc)
    )


# Test 1: Successful lifecycle
def test_successful_lifecycle_reconstruction():
    tx = create_sample_tx()
    events = [
        Event(
            id="e1",
            transaction_id=tx.id,
            event_type=EventType.PAYOUT_INITIATED,
            source=EventSource.API_CLIENT,
            status=TransactionStatus.INITIATED,
            occurred_at=datetime(2026, 8, 18, 10, 0, 1, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 0, 1, tzinfo=timezone.utc),
            sequence=1
        ),
        Event(
            id="e2",
            transaction_id=tx.id,
            event_type=EventType.PAYOUT_ACCEPTED,
            source=EventSource.DECENTRO_GATEWAY,
            status=TransactionStatus.PENDING,
            occurred_at=datetime(2026, 8, 18, 10, 0, 2, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 0, 2, tzinfo=timezone.utc),
            sequence=2
        ),
        Event(
            id="e3",
            transaction_id=tx.id,
            event_type=EventType.PROVIDER_PROCESSING,
            source=EventSource.BANK_PARTNER_GATEWAY,
            status=TransactionStatus.PROCESSING,
            occurred_at=datetime(2026, 8, 18, 10, 0, 3, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 0, 3, tzinfo=timezone.utc),
            sequence=3
        ),
        Event(
            id="e4",
            transaction_id=tx.id,
            event_type=EventType.PAYOUT_STATUS_CALLBACK,
            source=EventSource.BANK_PARTNER_CALLBACK,
            status=TransactionStatus.SUCCESS,
            occurred_at=datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc),
            sequence=4
        )
    ]
    ledger = [
        LedgerEntry(
            id="l1",
            transaction_id=tx.id,
            entry_type=LedgerEntryType.DEBIT,
            amount=25000.0,
            currency="INR",
            occurred_at=datetime(2026, 8, 18, 10, 0, 1, tzinfo=timezone.utc),
            reference_id="ref_test"
        )
    ]

    trace = TraceEngine.reconstruct_trace(tx, events, ledger)
    assert trace.lifecycle.final_status == TransactionStatus.SUCCESS
    assert trace.failure_analysis.failed is False
    assert trace.reconciliation.reconciled is True
    assert trace.reconciliation.net_impact == 25000.0
    assert trace.integrity.is_clean is True


# Test 2: Failure + reversal (Primary Loom Scenario)
def test_failure_and_reversal_scenario():
    tx = create_sample_tx("dec_987654321", 25000.0)
    events = [
        Event(
            id="e1",
            transaction_id=tx.id,
            event_type=EventType.PAYOUT_INITIATED,
            source=EventSource.API_CLIENT,
            status=TransactionStatus.INITIATED,
            occurred_at=datetime(2026, 8, 18, 10, 31, 2, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 31, 2, tzinfo=timezone.utc),
            sequence=1
        ),
        Event(
            id="e2",
            transaction_id=tx.id,
            event_type=EventType.PAYOUT_ACCEPTED,
            source=EventSource.DECENTRO_GATEWAY,
            status=TransactionStatus.PENDING,
            occurred_at=datetime(2026, 8, 18, 10, 31, 3, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 31, 3, tzinfo=timezone.utc),
            sequence=2
        ),
        Event(
            id="e3",
            transaction_id=tx.id,
            event_type=EventType.PROVIDER_PROCESSING,
            source=EventSource.BANK_PARTNER_GATEWAY,
            status=TransactionStatus.PROCESSING,
            occurred_at=datetime(2026, 8, 18, 10, 31, 8, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 31, 8, tzinfo=timezone.utc),
            sequence=3
        ),
        Event(
            id="e4",
            transaction_id=tx.id,
            event_type=EventType.PAYOUT_STATUS_CALLBACK,
            source=EventSource.BANK_PARTNER_CALLBACK,
            status=TransactionStatus.FAILURE,
            occurred_at=datetime(2026, 8, 18, 10, 31, 14, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 31, 14, tzinfo=timezone.utc),
            sequence=4,
            payload={"provider_error_code": "E1042", "provider_error_message": "BENEFICIARY_BANK_UNAVAILABLE"}
        ),
        Event(
            id="e5",
            transaction_id=tx.id,
            event_type=EventType.LEDGER_REVERSAL,
            source=EventSource.DECENTRO_LEDGER,
            status=TransactionStatus.REVERSED,
            occurred_at=datetime(2026, 8, 18, 10, 31, 15, tzinfo=timezone.utc),
            received_at=datetime(2026, 8, 18, 10, 31, 15, tzinfo=timezone.utc),
            sequence=5
        )
    ]
    ledger = [
        LedgerEntry(
            id="l1",
            transaction_id=tx.id,
            entry_type=LedgerEntryType.DEBIT,
            amount=25000.0,
            currency="INR",
            occurred_at=datetime(2026, 8, 18, 10, 31, 2, tzinfo=timezone.utc),
            reference_id="payroll_4821"
        ),
        LedgerEntry(
            id="l2",
            transaction_id=tx.id,
            entry_type=LedgerEntryType.REVERSAL,
            amount=25000.0,
            currency="INR",
            occurred_at=datetime(2026, 8, 18, 10, 31, 15, tzinfo=timezone.utc),
            reference_id="payroll_4821"
        )
    ]

    trace = TraceEngine.reconstruct_trace(tx, events, ledger)
    assert trace.failure_analysis.failed is True
    assert trace.failure_analysis.failure_stage == FailureStage.BENEFICIARY_BANK
    assert trace.failure_analysis.observed_error_code == "E1042"
    assert trace.reconciliation.reconciled is True
    assert trace.reconciliation.net_impact == 0.0


# Test 3: Duplicate webhook
def test_duplicate_webhook_is_removed_from_canonical_trace():
    tx = create_sample_tx()
    callback_time = datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc)
    events = [
        Event(
            id="e1",
            transaction_id=tx.id,
            event_type=EventType.PAYOUT_STATUS_CALLBACK,
            source=EventSource.BANK_PARTNER_CALLBACK,
            status=TransactionStatus.FAILURE,
            occurred_at=callback_time,
            received_at=datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc),
            correlation_id="rrn_123",
            sequence=1
        ),
        Event(
            id="e1_dup",
            transaction_id=tx.id,
            event_type=EventType.PAYOUT_STATUS_CALLBACK,
            source=EventSource.BANK_PARTNER_CALLBACK,
            status=TransactionStatus.FAILURE,
            occurred_at=callback_time,
            received_at=datetime(2026, 8, 18, 10, 0, 7, tzinfo=timezone.utc),
            correlation_id="rrn_123",
            sequence=1
        )
    ]
    trace = TraceEngine.reconstruct_trace(tx, events, [])
    assert trace.integrity.canonical_events_count == 1
    assert trace.integrity.duplicate_events_count == 1
    assert len(trace.duplicate_events) == 1


# Test 4: Out-of-order arrival
def test_out_of_order_events_are_reconstructed_by_occurrence_time():
    tx = create_sample_tx()
    t1 = datetime(2026, 8, 18, 10, 0, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 8, 18, 10, 0, 2, tzinfo=timezone.utc)
    t3 = datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc)

    # Ingestion order: t3 arrived first, then t1, then t2
    events = [
        Event(id="e3", transaction_id=tx.id, event_type=EventType.PAYOUT_STATUS_CALLBACK, source=EventSource.BANK_PARTNER_CALLBACK, status=TransactionStatus.FAILURE, occurred_at=t3, received_at=datetime(2026, 8, 18, 10, 0, 10, tzinfo=timezone.utc), sequence=3),
        Event(id="e1", transaction_id=tx.id, event_type=EventType.PAYOUT_INITIATED, source=EventSource.API_CLIENT, status=TransactionStatus.INITIATED, occurred_at=t1, received_at=datetime(2026, 8, 18, 10, 0, 12, tzinfo=timezone.utc), sequence=1),
        Event(id="e2", transaction_id=tx.id, event_type=EventType.PAYOUT_ACCEPTED, source=EventSource.DECENTRO_GATEWAY, status=TransactionStatus.PENDING, occurred_at=t2, received_at=datetime(2026, 8, 18, 10, 0, 14, tzinfo=timezone.utc), sequence=2),
    ]

    trace = TraceEngine.reconstruct_trace(tx, events, [])
    assert trace.integrity.out_of_order_received is True
    assert [e.id for e in trace.canonical_events] == ["e1", "e2", "e3"]


# Test 5: Missing intermediate event
def test_missing_event_detected():
    tx = create_sample_tx()
    events = [
        Event(id="e1", transaction_id=tx.id, event_type=EventType.PAYOUT_INITIATED, source=EventSource.API_CLIENT, status=TransactionStatus.INITIATED, occurred_at=datetime(2026, 8, 18, 10, 0, 1, tzinfo=timezone.utc), received_at=datetime(2026, 8, 18, 10, 0, 1, tzinfo=timezone.utc), sequence=1),
        Event(id="e3", transaction_id=tx.id, event_type=EventType.PAYOUT_STATUS_CALLBACK, source=EventSource.BANK_PARTNER_CALLBACK, status=TransactionStatus.FAILURE, occurred_at=datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc), received_at=datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc), sequence=2),
    ]
    trace = TraceEngine.reconstruct_trace(tx, events, [])
    assert len(trace.integrity.missing_expected_events) > 0
    assert any("PROVIDER_PROCESSING" in m for m in trace.integrity.missing_expected_events)


# Test 6: Conflicting observations
def test_conflicting_statuses_are_flagged():
    tx = create_sample_tx()
    events = [
        Event(id="e1", transaction_id=tx.id, event_type=EventType.PAYOUT_STATUS_CALLBACK, source=EventSource.BANK_PARTNER_CALLBACK, status=TransactionStatus.FAILURE, occurred_at=datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc), received_at=datetime(2026, 8, 18, 10, 0, 5, tzinfo=timezone.utc), sequence=1),
        Event(id="e2", transaction_id=tx.id, event_type=EventType.STATUS_CHECK, source=EventSource.DECENTRO_STATUS_POLLER, status=TransactionStatus.SUCCESS, occurred_at=datetime(2026, 8, 18, 10, 0, 7, tzinfo=timezone.utc), received_at=datetime(2026, 8, 18, 10, 0, 7, tzinfo=timezone.utc), sequence=2),
    ]
    trace = TraceEngine.reconstruct_trace(tx, events, [])
    assert len(trace.integrity.state_conflicts) == 1
    assert trace.integrity.state_conflicts[0].event_1_status == TransactionStatus.FAILURE
    assert trace.integrity.state_conflicts[0].event_2_status == TransactionStatus.SUCCESS


# Test 7: Reconciliation mismatch
def test_reconciliation_mismatch():
    ledger = [
        LedgerEntry(id="l1", transaction_id="dec_test", entry_type=LedgerEntryType.DEBIT, amount=25000.0, currency="INR", occurred_at=datetime(2026, 8, 18, 10, 0, 1, tzinfo=timezone.utc), reference_id="ref_test"),
        LedgerEntry(id="l2", transaction_id="dec_test", entry_type=LedgerEntryType.REVERSAL, amount=20000.0, currency="INR", occurred_at=datetime(2026, 8, 18, 10, 0, 2, tzinfo=timezone.utc), reference_id="ref_test")
    ]
    res = ReconciliationEngine.calculate(ledger, TransactionStatus.FAILURE, 25000.0)
    assert res.reconciled is False
    assert res.net_impact == 5000.0
