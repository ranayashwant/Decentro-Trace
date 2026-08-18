from typing import Optional
from app.models.transaction import Transaction
from app.models.event import Event
from app.models.ledger import LedgerEntry
from app.models.enums import TransactionStatus, FailureStage, EventType, EventSource
from app.models.trace import (
    Trace,
    LifecycleAnalysis,
    LifecycleTransition,
    FailureAnalysis,
    TraceIntegrity,
)
from app.services.anomaly_detector import AnomalyDetector
from app.services.reconciliation import ReconciliationEngine
from app.services.event_normalizer import EventNormalizer


class TraceEngine:
    """
    Deterministic Trace Reconstruction Engine.
    Executes the canonical pipeline:
    Normalizes -> Deduplicates -> Sorts -> Evaluates Lifecycle -> Detects Anomalies -> Reconciles Money.
    """

    @staticmethod
    def order_events(events: list[Event]) -> list[Event]:
        """
        Deterministic event ordering:
        Primary: occurred_at ASC
        Tie-breaker 1: sequence ASC
        Tie-breaker 2: id ASC
        """
        return sorted(events, key=lambda e: (e.occurred_at, e.sequence, e.id))

    @staticmethod
    def classify_failure_stage(failing_event: Optional[Event]) -> FailureStage:
        """
        Deterministically classifies the failure stage based on event source,
        error code, and payload evidence.
        """
        if not failing_event:
            return FailureStage.UNKNOWN

        payload = failing_event.payload
        code = str(payload.get("provider_error_code", "")).upper()
        msg = str(payload.get("provider_error_message", "")).upper()

        if failing_event.source == EventSource.API_CLIENT:
            return FailureStage.CLIENT_REQUEST
        if failing_event.source == EventSource.DECENTRO_GATEWAY:
            return FailureStage.DECENTRO_GATEWAY
        if "BENEFICIARY_BANK" in msg or code in ("E1042", "91", "U30"):
            return FailureStage.BENEFICIARY_BANK
        if "INVALID_BENEFICIARY" in msg or code in ("E3001", "INVALID_ACCOUNT"):
            return FailureStage.BENEFICIARY_SWITCH
        if failing_event.source in (EventSource.BANK_PARTNER_GATEWAY, EventSource.BANK_PARTNER_CALLBACK):
            return FailureStage.PROVIDER_ROUTING

        return FailureStage.PROVIDER_ROUTING

    @classmethod
    def build_lifecycle_analysis(cls, canonical_events: list[Event]) -> LifecycleAnalysis:
        transitions: list[LifecycleTransition] = []
        last_status: Optional[TransactionStatus] = None

        for evt in canonical_events:
            transitions.append(
                LifecycleTransition(
                    from_status=last_status,
                    to_status=evt.status,
                    event_id=evt.id,
                    event_type=evt.event_type.value,
                    occurred_at=evt.occurred_at
                )
            )
            last_status = evt.status

        initial_status = transitions[0].to_status if transitions else None
        final_status = last_status if last_status else TransactionStatus.INITIATED
        is_terminal = final_status in (TransactionStatus.SUCCESS, TransactionStatus.FAILURE, TransactionStatus.REVERSED)

        duration_ms: Optional[int] = None
        if len(canonical_events) >= 2:
            start = canonical_events[0].occurred_at
            end = canonical_events[-1].occurred_at
            duration_ms = int((end - start).total_seconds() * 1000)

        return LifecycleAnalysis(
            initial_status=initial_status,
            final_status=final_status,
            is_terminal=is_terminal,
            duration_ms=duration_ms,
            transitions=transitions
        )

    @classmethod
    def build_failure_analysis(cls, canonical_events: list[Event]) -> FailureAnalysis:
        # Locate failing event (status == FAILURE or error payload)
        failing_event = next(
            (e for e in canonical_events if e.status == TransactionStatus.FAILURE or "error" in str(e.payload).lower()),
            None
        )

        if not failing_event:
            return FailureAnalysis(
                failed=False,
                failure_stage=FailureStage.UNKNOWN,
                observed_status=None,
                observed_error_code=None,
                observed_error_message=None,
                failure_event_id=None,
                failure_timestamp=None
            )

        code, msg = EventNormalizer.extract_error_details(failing_event)
        stage = cls.classify_failure_stage(failing_event)

        return FailureAnalysis(
            failed=True,
            failure_stage=stage,
            observed_status=failing_event.status,
            observed_error_code=code,
            observed_error_message=msg,
            failure_event_id=failing_event.id,
            failure_timestamp=failing_event.occurred_at
        )

    @classmethod
    def reconstruct_trace(
        cls,
        transaction: Transaction,
        raw_events: list[Event],
        ledger_entries: list[LedgerEntry]
    ) -> Trace:
        """
        Reconstructs the full canonical trace from raw database records.
        """
        # 1. Deduplicate
        canonical_raw, duplicates = AnomalyDetector.detect_duplicates(raw_events)

        # 2. Deterministic ordering by occurred_at
        canonical_events = cls.order_events(canonical_raw)

        # 3. Anomaly detection
        is_ooo = AnomalyDetector.detect_out_of_order(raw_events, canonical_events)
        missing_events = AnomalyDetector.detect_missing_events(canonical_events)
        conflicts = AnomalyDetector.detect_state_conflicts(canonical_events)

        is_clean = len(duplicates) == 0 and not is_ooo and len(missing_events) == 0 and len(conflicts) == 0

        integrity = TraceIntegrity(
            total_events_received=len(raw_events),
            canonical_events_count=len(canonical_events),
            duplicate_events_count=len(duplicates),
            out_of_order_received=is_ooo,
            missing_expected_events=missing_events,
            state_conflicts=conflicts,
            is_clean=is_clean
        )

        # 4. Lifecycle analysis
        lifecycle = cls.build_lifecycle_analysis(canonical_events)

        # 5. Failure stage detection
        failure_analysis = cls.build_failure_analysis(canonical_events)

        # 6. Financial Reconciliation
        reconciliation = ReconciliationEngine.calculate(
            entries=ledger_entries,
            final_status=lifecycle.final_status,
            expected_amount=transaction.amount
        )

        return Trace(
            transaction=transaction,
            canonical_events=canonical_events,
            duplicate_events=duplicates,
            lifecycle=lifecycle,
            failure_analysis=failure_analysis,
            integrity=integrity,
            reconciliation=reconciliation
        )
